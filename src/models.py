"""Data models for the Closira AI agent using dataclasses."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ConversationState(Enum):
    """Possible states in the conversation state machine."""
    GREETING = "greeting"
    FAQ_ANSWERING = "faq_answering"
    QUALIFYING = "qualifying"
    ESCALATED = "escalated"
    ENDED = "ended"


class EscalationType(Enum):
    """Types of escalation triggers."""
    LOW_CONFIDENCE = "low_confidence"
    OUT_OF_SCOPE = "out_of_scope"
    ANGRY_SENTIMENT = "angry_sentiment"
    EXPLICIT_REQUEST = "explicit_request"
    MEDICAL_QUESTION = "medical_question"
    PRICING_NEGOTIATION = "pricing_negotiation"
    COMPLAINT = "complaint"
    MAX_UNANSWERED = "max_unanswered"


@dataclass
class Message:
    """A single message in the conversation history."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EscalationEvent:
    """A logged escalation event with reason and context."""
    reason: str
    trigger_type: EscalationType
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    customer_message: str = ""


@dataclass
class LeadQualification:
    """Tracks the lead qualification question flow."""
    responses: dict = field(default_factory=dict)
    is_complete: bool = False
    current_question_index: int = 0
    summary: str = ""


@dataclass
class AgentResponse:
    """Structured response from the AI model."""
    response_text: str
    confidence: float = 1.0
    escalation_needed: bool = False
    escalation_reason: str = ""
    escalation_type: Optional[EscalationType] = None
    is_in_sop: bool = True
    detected_intent: str = ""


@dataclass
class ConversationSummary:
    """End-of-session structured summary."""
    customer_intent: str = ""
    key_details: list = field(default_factory=list)
    sop_gaps: list = field(default_factory=list)
    recommended_next_action: str = ""
    lead_qualification: dict = field(default_factory=dict)
    escalation_events: list = field(default_factory=list)
    total_messages: int = 0
