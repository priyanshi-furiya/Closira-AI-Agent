"""Stage 2: Lead Qualification — question flow and response tracking.

Manages the structured qualification questions asked to the customer
to collect lead information (treatment interest, experience, source).
"""

from ..models import LeadQualification
from ..config import QUALIFICATION_QUESTIONS


def get_next_question(qualification: LeadQualification) -> str | None:
    """Get the next qualification question to ask the customer.

    Args:
        qualification: Current qualification state.

    Returns:
        The next question string, or None if all questions have been asked.
    """
    idx = qualification.current_question_index
    if idx < len(QUALIFICATION_QUESTIONS):
        return QUALIFICATION_QUESTIONS[idx]
    return None


def process_qualification_answer(
    qualification: LeadQualification, answer: str
) -> None:
    """Store the customer's answer to the current qualification question.

    Advances the question index so the next call to get_next_question()
    returns the following question.

    Args:
        qualification: Current qualification state (mutated in place).
        answer: The customer's response to the current question.
    """
    idx = qualification.current_question_index
    if idx < len(QUALIFICATION_QUESTIONS):
        question = QUALIFICATION_QUESTIONS[idx]
        qualification.responses[question] = answer
        qualification.current_question_index += 1


def format_qualification_summary(qualification: LeadQualification) -> str:
    """Format collected qualification answers into a readable summary.

    Args:
        qualification: Completed qualification state.

    Returns:
        Formatted string with questions and answers.
    """
    lines = []
    for question, answer in qualification.responses.items():
        lines.append(f"• **{question}**\n  → {answer}")
    return "\n".join(lines)
