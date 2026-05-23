"""Stage 4: Conversation Summary — end-of-session structured summary.

Generates a comprehensive summary of the conversation including
customer intent, key details, SOP gaps, and recommended next actions.
"""

from ..models import ConversationSummary


def format_summary_display(summary: ConversationSummary) -> str:
    """Format the conversation summary for rich terminal display.

    Args:
        summary: The generated conversation summary.

    Returns:
        Formatted multi-line string for terminal output.
    """
    lines = [
        "",
        "🎯 [bold]Customer Intent[/bold]",
        f"   {summary.customer_intent}",
        "",
        "📝 [bold]Key Details Collected[/bold]",
    ]

    if summary.key_details:
        for detail in summary.key_details:
            lines.append(f"   • {detail}")
    else:
        lines.append("   • No specific details collected")

    lines.append("")
    lines.append("📊 [bold]Lead Qualification[/bold]")
    if summary.lead_qualification:
        for q, a in summary.lead_qualification.items():
            lines.append(f"   • {q}")
            lines.append(f"     → {a}")
    else:
        lines.append("   • Not completed")

    lines.append("")
    lines.append("⚠️  [bold]SOP Gaps Identified[/bold]")
    if summary.sop_gaps:
        for gap in summary.sop_gaps:
            lines.append(f"   • {gap}")
    else:
        lines.append("   • None — all questions were answerable from the SOP")

    lines.append("")
    lines.append("🚨 [bold]Escalation Events[/bold]")
    if summary.escalation_events:
        for event in summary.escalation_events:
            etype = event.get("type", "unknown")
            reason = event.get("reason", "N/A")
            lines.append(f"   • [{etype}] {reason}")
    else:
        lines.append("   • No escalations during this session")

    lines.append("")
    lines.append(f"➡️  [bold]Recommended Next Action[/bold]")
    lines.append(f"   {summary.recommended_next_action}")

    lines.append("")
    lines.append(f"💬 [bold]Total Messages[/bold]: {summary.total_messages}")

    return "\n".join(lines)
