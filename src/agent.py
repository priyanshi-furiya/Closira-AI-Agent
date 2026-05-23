"""Core agent orchestrator — manages the conversation state machine.

The ClosiraAgent class is the heart of the system. It:
  1. Maintains conversation state (GREETING → FAQ → QUALIFYING → ESCALATED/ENDED)
  2. Makes Gemini API calls with structured JSON output
  3. Runs escalation detection as a parallel check on every message
  4. Manages the lead qualification question flow
  5. Generates end-of-session summaries
"""

import json
from mistralai import Mistral

from .config import (
    MISTRAL_API_KEY,
    MODEL_NAME,
    CONFIDENCE_THRESHOLD,
    MAX_UNANSWERED_QUESTIONS,
    MAX_FAQ_TURNS_BEFORE_QUALIFY,
    QUALIFICATION_QUESTIONS,
    SOP_DATA_PATH,
)
from .models import (
    ConversationState,
    EscalationType,
    Message,
    EscalationEvent,
    LeadQualification,
    AgentResponse,
    ConversationSummary,
)
from .sop_loader import load_sop, format_sop_for_prompt
from .prompts.templates import (
    SYSTEM_PROMPT,
    GREETING_MESSAGE,
    QUALIFICATION_INTRO,
    QUALIFICATION_COMPLETE,
    ESCALATION_MESSAGE,
    SUMMARY_PROMPT,
)
from .stages.escalation import check_escalation, format_escalation_log
from .stages.qualification import (
    get_next_question,
    process_qualification_answer,
    format_qualification_summary,
)
from .stages.faq import is_exit_command


class ClosiraAgent:
    """AI-powered customer support agent for Bloom Aesthetics Clinic.

    Implements a state-machine conversation flow with four stages:
      Stage 1 — FAQ Answering (grounded in SOP)
      Stage 2 — Lead Qualification (structured questions)
      Stage 3 — Escalation Detection (parallel check on every message)
      Stage 4 — Conversation Summary (generated at session end)
    """

    def __init__(self):
        """Initialise the agent: configure API, load SOP, build prompts."""
        # ── Configure Mistral API ───────────────────────────────────────
        if not MISTRAL_API_KEY:
            raise ValueError(
                "MISTRAL_API_KEY is not set. Please set it in your .env file "
                "or as an environment variable."
            )
        self.client = Mistral(api_key=MISTRAL_API_KEY)

        # ── Load SOP data ─────────────────────────────────────────────
        sop_data = load_sop(SOP_DATA_PATH)
        sop_text = format_sop_for_prompt(sop_data)

        # ── Build system prompt with SOP injected ─────────────────────
        self.system_prompt = SYSTEM_PROMPT.format(sop_data=sop_text)

        # ── Conversation state ────────────────────────────────────────
        self.state = ConversationState.GREETING
        self.conversation_history: list[Message] = []
        self.escalation_events: list[EscalationEvent] = []
        self.lead_qualification = LeadQualification()
        self.consecutive_unanswered = 0
        self.faq_turn_count = 0
        self.qualification_offered = False

    # ══════════════════════════════════════════════════════════════════════
    #  PUBLIC API
    # ══════════════════════════════════════════════════════════════════════

    @property
    def is_ended(self) -> bool:
        """Check whether the conversation has ended."""
        return self.state == ConversationState.ENDED

    def get_greeting(self) -> str:
        """Return the initial greeting and transition to FAQ_ANSWERING."""
        self.state = ConversationState.FAQ_ANSWERING
        self.conversation_history.append(
            Message(role="assistant", content=GREETING_MESSAGE)
        )
        return GREETING_MESSAGE

    def process_message(self, user_input: str) -> tuple[str, AgentResponse | None]:
        """Process a customer message and return the agent's response.

        Args:
            user_input: The customer's message text.

        Returns:
            A tuple of (response_text, agent_response_metadata).
            agent_response_metadata is None for exit/escalated states.
        """
        # ── Record user message ───────────────────────────────────────
        self.conversation_history.append(Message(role="user", content=user_input))

        # ── Check for exit commands ───────────────────────────────────
        if is_exit_command(user_input):
            self.state = ConversationState.ENDED
            farewell = (
                "Thank you for chatting with Bloom Aesthetics! 🌸 "
                "We hope to see you soon. Have a lovely day!"
            )
            self.conversation_history.append(
                Message(role="assistant", content=farewell)
            )
            return farewell, None

        # ── If already escalated, repeat escalation message ───────────
        if self.state == ConversationState.ESCALATED:
            msg = (
                "Our team has been notified and will be with you shortly. "
                "In the meantime, you can reach us at +44 7700 900123 on "
                "WhatsApp. Thank you for your patience! 🌸"
            )
            self.conversation_history.append(
                Message(role="assistant", content=msg)
            )
            return msg, None

        # ── Build context prefix for the model ────────────────────────
        context_prefix = self._build_context_prefix()
        augmented_input = (
            f"{context_prefix}\n\nCustomer message: {user_input}"
            if context_prefix
            else user_input
        )

        # ── Call Mistral API ──────────────────────────────────────────
        agent_response = self._call_mistral(augmented_input)

        # ── Stage 3: Escalation detection (runs on EVERY message) ─────
        escalation_event = check_escalation(
            agent_response, user_input, self.consecutive_unanswered
        )

        if escalation_event:
            self.escalation_events.append(escalation_event)
            self.state = ConversationState.ESCALATED
            response_text = (
                f"{agent_response.response_text}\n\n{ESCALATION_MESSAGE}"
            )
            self.conversation_history.append(
                Message(role="assistant", content=response_text)
            )
            return response_text, agent_response

        # ── Track consecutive unanswered questions ────────────────────
        if not agent_response.is_in_sop:
            self.consecutive_unanswered += 1
        else:
            self.consecutive_unanswered = 0

        # ── Check max unanswered threshold ────────────────────────────
        if self.consecutive_unanswered > MAX_UNANSWERED_QUESTIONS:
            event = EscalationEvent(
                reason=(
                    f"More than {MAX_UNANSWERED_QUESTIONS} consecutive "
                    "questions could not be answered from the SOP"
                ),
                trigger_type=EscalationType.MAX_UNANSWERED,
                customer_message=user_input,
            )
            self.escalation_events.append(event)
            self.state = ConversationState.ESCALATED
            response_text = (
                f"{agent_response.response_text}\n\n{ESCALATION_MESSAGE}"
            )
            self.conversation_history.append(
                Message(role="assistant", content=response_text)
            )
            return response_text, agent_response

        # ── State-specific handling ───────────────────────────────────
        if self.state == ConversationState.FAQ_ANSWERING:
            return self._handle_faq_state(agent_response)

        elif self.state == ConversationState.QUALIFYING:
            return self._handle_qualifying_state(agent_response, user_input)

        # ── Default fallback ──────────────────────────────────────────
        self.conversation_history.append(
            Message(role="assistant", content=agent_response.response_text)
        )
        return agent_response.response_text, agent_response

    def generate_summary(self) -> ConversationSummary:
        """Generate a structured summary of the entire conversation.

        Uses a separate Gemini model call (with a summary-focused prompt)
        to analyse the full conversation history and produce a summary.

        Returns:
            A ConversationSummary dataclass with all fields populated.
        """
        # ── Format conversation history ───────────────────────────────
        history_text = "\n".join(
            [
                f"{'Customer' if msg.role == 'user' else 'Agent'}: {msg.content}"
                for msg in self.conversation_history
            ]
        )

        # ── Format qualification data ─────────────────────────────────
        qual_data = (
            json.dumps(self.lead_qualification.responses, indent=2)
            if self.lead_qualification.responses
            else "No qualification data collected"
        )

        # ── Format escalation events ──────────────────────────────────
        esc_data = (
            format_escalation_log(self.escalation_events)
            if self.escalation_events
            else "No escalations during this session"
        )

        # ── Build summary prompt ──────────────────────────────────────
        summary_prompt = SUMMARY_PROMPT.format(
            conversation_history=history_text,
            qualification_data=qual_data,
            escalation_events=esc_data,
        )

        try:
            summary_system_instruction = (
                "You are a conversation analyst. Generate accurate, "
                "structured summaries of customer support conversations. "
                "Respond in JSON format only. Be factual — only include "
                "information actually present in the conversation."
            )
            response = self.client.chat.complete(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": summary_system_instruction},
                    {"role": "user", "content": summary_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            result = json.loads(response.choices[0].message.content)

            return ConversationSummary(
                customer_intent=result.get("customer_intent", "Unknown"),
                key_details=result.get("key_details", []),
                sop_gaps=result.get("sop_gaps", []),
                recommended_next_action=result.get(
                    "recommended_next_action", "Follow up with customer"
                ),
                lead_qualification=self.lead_qualification.responses,
                escalation_events=[
                    {
                        "reason": e.reason,
                        "type": e.trigger_type.value,
                        "time": e.timestamp,
                    }
                    for e in self.escalation_events
                ],
                total_messages=len(self.conversation_history),
            )
        except Exception as e:
            # Graceful fallback if summary generation fails
            return ConversationSummary(
                customer_intent="Error generating summary",
                key_details=[f"Error: {str(e)}"],
                sop_gaps=[],
                recommended_next_action="Manual review required",
                lead_qualification=self.lead_qualification.responses,
                escalation_events=[
                    {
                        "reason": ev.reason,
                        "type": ev.trigger_type.value,
                        "time": ev.timestamp,
                    }
                    for ev in self.escalation_events
                ],
                total_messages=len(self.conversation_history),
            )

    # ══════════════════════════════════════════════════════════════════════
    #  PRIVATE HELPERS
    # ══════════════════════════════════════════════════════════════════════

    def _handle_faq_state(
        self, agent_response: AgentResponse
    ) -> tuple[str, AgentResponse]:
        """Handle message processing in the FAQ_ANSWERING state."""
        self.faq_turn_count += 1
        response_text = agent_response.response_text

        # After enough FAQ turns, transition to lead qualification
        if (
            self.faq_turn_count >= MAX_FAQ_TURNS_BEFORE_QUALIFY
            and not self.qualification_offered
        ):
            self.qualification_offered = True
            self.state = ConversationState.QUALIFYING
            q = get_next_question(self.lead_qualification)
            response_text += f"\n\n{QUALIFICATION_INTRO}\n\n{q}"

        self.conversation_history.append(
            Message(role="assistant", content=response_text)
        )
        return response_text, agent_response

    def _handle_qualifying_state(
        self, agent_response: AgentResponse, user_input: str
    ) -> tuple[str, AgentResponse]:
        """Handle message processing in the QUALIFYING state."""
        # Store the answer to the current question
        process_qualification_answer(self.lead_qualification, user_input)

        # Check for next question
        next_q = get_next_question(self.lead_qualification)
        if next_q:
            # Acknowledge answer and ask next question
            response_text = f"{agent_response.response_text}\n\n{next_q}"
        else:
            # All questions answered — complete qualification
            self.lead_qualification.is_complete = True
            summary = format_qualification_summary(self.lead_qualification)
            self.lead_qualification.summary = summary
            response_text = QUALIFICATION_COMPLETE.format(summary=summary)
            self.state = ConversationState.FAQ_ANSWERING

        self.conversation_history.append(
            Message(role="assistant", content=response_text)
        )
        return response_text, agent_response

    def _build_context_prefix(self) -> str:
        """Build contextual information to prepend to the user message.

        This gives the model awareness of the current stage so it can
        respond appropriately (e.g., acknowledging a qualification answer).
        """
        if self.state == ConversationState.QUALIFYING:
            q_index = self.lead_qualification.current_question_index
            total = len(QUALIFICATION_QUESTIONS)
            if q_index < total:
                parts = [
                    f"[CONTEXT: The customer is answering lead qualification "
                    f"question {q_index + 1} of {total}. Acknowledge their "
                    f"response warmly and briefly.]"
                ]
                if self.lead_qualification.responses:
                    parts.append(
                        f"[Previous answers: "
                        f"{json.dumps(self.lead_qualification.responses)}]"
                    )
                return "\n".join(parts)
        return ""

    def _call_mistral(self, message: str) -> AgentResponse:
        """Make a call to the Mistral API and parse the structured JSON response.

        Args:
            message: The (potentially augmented) user message.

        Returns:
            A parsed AgentResponse dataclass.
        """
        # Build message history for Mistral API call
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        # Include previous messages in the conversation (excluding the last one which was just appended)
        for msg in self.conversation_history[:-1]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        # Add the current turn with the augmented input (context prefix included)
        messages.append({
            "role": "user",
            "content": message
        })

        response = None
        try:
            response = self.client.chat.complete(
                model=MODEL_NAME,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            response_text = response.choices[0].message.content
            result = json.loads(response_text)

            # Parse escalation type if present
            escalation_type = None
            if result.get("escalation_type"):
                try:
                    escalation_type = EscalationType(result["escalation_type"])
                except ValueError:
                    pass

            return AgentResponse(
                response_text=result.get(
                    "response_text",
                    "I'm here to help! Could you please rephrase your question?",
                ),
                confidence=float(result.get("confidence", 0.5)),
                escalation_needed=bool(result.get("escalation_needed", False)),
                escalation_reason=result.get("escalation_reason", ""),
                escalation_type=escalation_type,
                is_in_sop=bool(result.get("is_in_sop", True)),
                detected_intent=result.get("detected_intent", ""),
            )

        except json.JSONDecodeError:
            # Model returned non-JSON — extract text and treat as low-confidence
            try:
                text = response.choices[0].message.content if response else ""
            except Exception:
                text = "I apologise for the inconvenience. Could you try again?"

            return AgentResponse(
                response_text=text,
                confidence=0.5,
                escalation_needed=False,
            )

        except Exception as e:
            # Network / API error — graceful fallback
            return AgentResponse(
                response_text=(
                    "I'm experiencing a technical issue. Please try again "
                    "or contact us directly at +44 7700 900123."
                ),
                confidence=0.0,
                escalation_needed=True,
                escalation_reason=f"Technical error: {str(e)}",
                escalation_type=EscalationType.LOW_CONFIDENCE,
                is_in_sop=False,
                detected_intent="error",
            )
