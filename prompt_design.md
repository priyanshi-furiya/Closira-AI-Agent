# Prompt Design Document — Closira AI Agent

This document covers the full prompt engineering strategy for the Closira AI customer support agent, including the system prompt, hallucination prevention approach, escalation logic, and tone design.

---

## 1. System Prompt

The system prompt is the core artefact that defines the AI's behaviour. It is located in [`src/prompts/templates.py`](src/prompts/templates.py) and consists of seven sections:

### 1.1 Identity & Role

```
You are **Bloom**, the friendly and professional AI assistant for **Bloom Aesthetics Clinic**.
You handle customer enquiries via chat with warmth, clarity, and precision.
```

**Design reasoning**: Giving the AI a named persona ("Bloom") makes interactions feel more personal and consistent. The name aligns with the clinic's brand. We explicitly state the AI is NOT a medical professional to set safety boundaries.

### 1.2 SOP Data Injection

The entire SOP is injected directly into the system prompt as formatted plain text:

```
## SOP DATA — Your ONLY Source of Truth
The following is the complete Standard Operating Procedure (SOP) data for the business.
You must answer ALL customer questions using ONLY the information provided below.
This is exhaustive — if something is not mentioned here, you do not know it.

{sop_data}
```

**Design reasoning**: Injecting the SOP directly (rather than using RAG/embeddings) ensures:
- The model always has full context — no retrieval failures
- Simpler architecture with fewer failure points
- Deterministic grounding — the same SOP always produces the same boundary
- Appropriate for small SOP sizes (under 2000 tokens)

### 1.3 Hallucination Prevention Rules

```
## CRITICAL RULES — HALLUCINATION PREVENTION
1. NEVER invent, fabricate, or guess any information not explicitly stated in the SOP data above.
2. NEVER make up prices, services, practitioner names, medical claims, or policies.
3. If a customer asks something NOT covered by the SOP data, you MUST:
   - Acknowledge that you don't have that specific information
   - Offer to connect them with a team member
   - DO NOT attempt to answer with general knowledge or assumptions
4. If you are even slightly unsure, err on the side of caution and flag as out of scope.
5. When quoting prices, ALWAYS include "starting from" or "from".
6. Do NOT extrapolate or combine SOP data points to create new claims.
```

### 1.4 Escalation Rules

Six explicit escalation triggers are codified in the prompt:
1. **Complaint** — dissatisfaction or negative experience
2. **Medical Question** — medical advice, side effects, contraindications
3. **Pricing Negotiation** — discounts, price matching
4. **Consecutive Unanswered** — >2 questions not answerable from SOP
5. **Explicit Request** — customer asks for human/manager
6. **Angry Sentiment** — aggressive language, profanity, strong frustration

### 1.5 Tone & Persona

```
- Warm and welcoming: Make the customer feel valued
- Professional but approachable: Not overly formal
- Concise: Clear and to the point
- Empathetic: Show understanding of concerns
- Proactive: Suggest logical next steps
- British English: Use British spelling
- Use emojis sparingly: A 🌸 or ✨ occasionally
```

### 1.6 Structured JSON Response Format

```json
{
    "response_text": "Your message to the customer",
    "confidence": 0.0 to 1.0,
    "escalation_needed": true/false,
    "escalation_reason": "reason or empty string",
    "escalation_type": "type or empty string",
    "is_in_sop": true/false,
    "detected_intent": "brief label"
}
```

### 1.7 Confidence Scoring Guidelines

```
0.9–1.0: Direct SOP match — exact answer available
0.7–0.89: Related to SOP but requires interpretation
0.5–0.69: Partially related — may be incomplete, flag for review
Below 0.5: Outside SOP scope — MUST escalate
```

---

## 2. Hallucination Prevention Strategy

Our approach to hallucination prevention operates on **three layers**:

### Layer 1: Prompt-Level Grounding (Primary)

The system prompt contains **six explicit negative instructions** that tell the model what NOT to do. This "negative prompting" approach is more effective than only positive instructions because:

- It directly addresses the failure mode (fabrication)
- Uses absolute language ("NEVER") to create hard boundaries
- Lists specific categories that must not be invented (prices, services, names, medical claims)
- Instructs the model to prefer "I don't know" over guessing

### Layer 2: Structured Output Enforcement

By requiring JSON output with `is_in_sop` and `confidence` fields, we force the model to explicitly assess its own grounding on every response. This self-assessment acts as a metacognitive check:

- The model must decide `is_in_sop: true/false` before responding
- It must assign a numeric confidence score
- These fields are machine-readable, enabling programmatic escalation

### Layer 3: Programmatic Confidence Threshold

The agent code (`src/stages/escalation.py`) enforces a **hard confidence threshold of 0.6**. Even if the model doesn't flag escalation itself, any response below 60% confidence is automatically escalated. This acts as a safety net against the model's tendency to be overconfident.

### Why This Works for SMB Context

For an SMB like a beauty clinic, hallucinated information could be:
- **Dangerous** — wrong medical advice
- **Costly** — incorrect pricing leading to disputes
- **Reputation-damaging** — false promises about results

Our approach prioritises safety over helpfulness: it's better to say "I don't have that information" than to guess wrong.

---

## 3. Confidence-Based Escalation Logic

### Architecture: 3-Layer Detection

Escalation detection is implemented as a **parallel analyser** that runs on every customer message, regardless of conversation state:

```
Customer Message
       │
       ▼
┌─────────────────────────────────────────┐
│  Layer 1: Model Self-Report             │
│  Does the model flag escalation_needed? │
│  Does it set an escalation_type?        │
│──────────────────────────── ────────────│
│  Layer 2: Confidence Threshold          │
│  Is confidence < 0.6?                   │
│─────────────────────────────────────────│
│  Layer 3: Keyword Backup                │
│  Does the message contain explicit      │
│  escalation phrases?                    │
└─────────────────────────────────────────┘
       │
       ▼
  EscalationEvent (logged with reason, type, timestamp)
```

### Layer Details

**Layer 1 — Model Self-Report**: The Gemini model evaluates each customer message against the 6 escalation rules in the system prompt. If it detects a trigger, it sets `escalation_needed: true` with a reason and type. This catches the majority of escalation cases including nuanced sentiment detection.

**Layer 2 — Confidence Threshold**: A programmatic check on the model's self-reported confidence score. Any response with `confidence < 0.6` triggers automatic escalation, even if the model didn't explicitly flag it. This guards against the model being overconfident about responses it shouldn't be giving.

**Layer 3 — Keyword Backup**: A deterministic keyword scan for explicit escalation requests ("speak to a human", "talk to manager", "real person", etc.). This ensures these requests are never missed, even if the model fails to detect them.

### Consecutive Unanswered Tracking

A separate counter tracks consecutive questions that the model marks as `is_in_sop: false`. When this exceeds 2, escalation is triggered with type `max_unanswered`. The counter resets when an in-SOP question is successfully answered.

### Escalation Logging

Every escalation event is logged as an `EscalationEvent` dataclass with:
- **reason**: Human-readable explanation
- **trigger_type**: Enum value (one of 8 types)
- **timestamp**: ISO 8601 timestamp
- **customer_message**: The message that triggered escalation

These logs are included in the conversation summary and can be reviewed for quality assurance.

---

## 4. Tone & Persona Design

### Target Audience

Bloom Aesthetics Clinic serves SMB customers — individuals considering aesthetic treatments. The typical customer:
- May be nervous or unsure about treatments
- Expects professional but not clinical communication
- Values trust and transparency (especially for cosmetic procedures)
- May be comparing clinics

### Persona Design Decisions

| Decision | Reasoning |
|----------|-----------|
| **Named persona ("Bloom")** | Creates personal connection; aligns with brand |
| **Warm but professional** | Aesthetics is personal — cold/clinical tone would deter customers |
| **British English** | The clinic is London-based; matches customer expectations |
| **Concise responses** | Chat context demands brevity; long responses feel like walls of text |
| **Proactive suggestions** | Guides customers toward booking without being pushy |
| **Sparing emoji use** | One 🌸 per message maximum — maintains professionalism while adding warmth |

### Tone Calibration

The tone sits between two extremes:

```
❌ Too formal:  "Dear valued customer, we appreciate your enquiry regarding..."
✅ Just right:  "Great question! Botox treatments start from £200..."
❌ Too casual:  "Hey! Yeah we totally do Botox lol, it's like £200ish"
```

---

## 5. Response Format Design

### Why Structured JSON?

We use Gemini's `response_mime_type="application/json"` to enforce structured output. This provides:

1. **Reliable parsing** — no regex/string extraction needed
2. **Metadata alongside responses** — confidence, intent, and escalation flags in one call
3. **Programmatic decision-making** — agent code can inspect fields without additional API calls
4. **Audit trail** — every response has self-assessed confidence and intent

### Why Not Function Calling?

Gemini supports function calling, but structured JSON is simpler for this use case:
- We don't need the model to invoke external tools
- We just need structured metadata alongside the response
- JSON mode has lower latency than function calling

### Temperature Setting

We use `temperature=0.3` (low) because:
- Customer support requires consistent, accurate responses
- We don't want creative variation in pricing or policy information
- Low temperature reduces hallucination risk
- Summary generation uses even lower temperature (0.2) for maximum accuracy

---

## 6. Key Design Trade-offs

### Grounding vs. Helpfulness

We chose **strict grounding** — the model refuses to answer anything outside the SOP, even if it could give a generally helpful response. This trades helpfulness for safety, which is the correct trade-off for an SMB support context where wrong information can cause real harm.

### Single API Call vs. Multi-Call Pipeline

We process each message with a **single Gemini API call** that returns both the response and metadata. An alternative would be separate calls for (1) response generation, (2) escalation detection, (3) sentiment analysis. We chose single-call because:
- Lower latency (one round-trip vs. three)
- Lower cost (fewer tokens consumed)
- The model is capable of multi-task output in a single call
- The keyword backup layer provides redundancy for escalation detection

### Fixed Qualification Timing vs. Dynamic

Lead qualification is triggered after a **fixed 3 FAQ turns**. A more sophisticated system would detect natural transition points (e.g., customer expressing booking intent). We chose fixed timing for:
- Simplicity and predictability
- Reliable testing — the transition always happens at the same point
- Acceptable UX — 3 turns is enough to establish rapport before asking questions
