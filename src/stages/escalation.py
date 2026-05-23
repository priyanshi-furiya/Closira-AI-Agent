"""Stage 3: Escalation Detection — parallel analyser on every message.

Runs as a check on every customer message to detect when the AI should
hand off to a human agent. Combines model self-reported confidence with
keyword-based backup detection.
"""

from ..models import AgentResponse, EscalationEvent, EscalationType
from ..config import CONFIDENCE_THRESHOLD


# ── Keyword-based backup detection ─────────────────────────────────────────
EXPLICIT_ESCALATION_KEYWORDS = [
    "speak to a human",
    "talk to someone",
    "real person",
    "speak to a manager",
    "talk to manager",
    "human agent",
    "speak to someone real",
    "get me a person",
    "representative",
    "talk to a real",
    "i want a human",
    "connect me to",
    "transfer me",
    "let me talk to",
]


def check_escalation(
    response: AgentResponse,
    user_input: str,
    consecutive_unanswered: int,
) -> EscalationEvent | None:
    """Check if the current exchange should trigger escalation.

    This function acts as a layered escalation detector:
    1. First checks the model's own escalation flags (self-reported).
    2. Then checks for low confidence scores.
    3. Finally applies keyword-based backup detection for explicit requests.

    Args:
        response: The structured response from the AI model.
        user_input: The customer's raw input message.
        consecutive_unanswered: Count of consecutive questions not answered from SOP.

    Returns:
        An EscalationEvent if escalation is triggered, or None.
    """
    # ── Layer 1: Model explicitly flagged escalation ───────────────────
    if response.escalation_needed and response.escalation_type:
        return EscalationEvent(
            reason=response.escalation_reason or "AI detected escalation trigger",
            trigger_type=response.escalation_type,
            customer_message=user_input,
        )

    # ── Layer 2: Low confidence score ──────────────────────────────────
    if response.confidence < CONFIDENCE_THRESHOLD:
        return EscalationEvent(
            reason=f"Low confidence score: {response.confidence:.2f} (threshold: {CONFIDENCE_THRESHOLD})",
            trigger_type=EscalationType.LOW_CONFIDENCE,
            customer_message=user_input,
        )

    # ── Layer 3: Keyword-based backup for explicit requests ────────────
    user_lower = user_input.lower()
    for keyword in EXPLICIT_ESCALATION_KEYWORDS:
        if keyword in user_lower:
            return EscalationEvent(
                reason="Customer explicitly requested to speak with a human agent",
                trigger_type=EscalationType.EXPLICIT_REQUEST,
                customer_message=user_input,
            )

    return None


def format_escalation_log(events: list[EscalationEvent]) -> str:
    """Format escalation events into a readable log string.

    Args:
        events: List of escalation events.

    Returns:
        Formatted multi-line log string.
    """
    lines = []
    for i, event in enumerate(events, 1):
        lines.append(f"Escalation #{i}:")
        lines.append(f"  Type: {event.trigger_type.value}")
        lines.append(f"  Reason: {event.reason}")
        lines.append(f"  Customer Message: \"{event.customer_message}\"")
        lines.append(f"  Timestamp: {event.timestamp}")
        lines.append("")
    return "\n".join(lines)
