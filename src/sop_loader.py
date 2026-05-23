"""SOP data loader and formatter for prompt injection."""

import json
from pathlib import Path


def load_sop(sop_path: Path) -> dict:
    """Load SOP data from a JSON file.

    Args:
        sop_path: Path to the SOP JSON file.

    Returns:
        Parsed SOP data as a dictionary.

    Raises:
        FileNotFoundError: If the SOP file does not exist.
        json.JSONDecodeError: If the SOP file is not valid JSON.
    """
    with open(sop_path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_sop_for_prompt(sop_data: dict) -> str:
    """Format SOP data as a readable string for injection into the system prompt.

    Converts the structured JSON SOP into a flat, readable text format that
    the AI model can easily reference when answering customer questions.

    Args:
        sop_data: Parsed SOP dictionary.

    Returns:
        Formatted SOP string ready for prompt injection.
    """
    lines = []

    # ── Business Information ──────────────────────────────────────────
    biz = sop_data["business"]
    lines.append("=== BUSINESS INFORMATION ===")
    lines.append(f"Business Name: {biz['name']}")
    lines.append(f"Tagline: {biz['tagline']}")
    lines.append(f"Hours: {biz['hours']['weekdays']}")
    lines.append(f"Closed: {biz['hours']['closed']}")
    lines.append(f"Location: {biz['location']}")
    lines.append(f"Phone: {biz['contact']['phone']}")
    lines.append(f"WhatsApp: {biz['contact']['whatsapp']}")
    lines.append(f"Email: {biz['contact']['email']}")
    lines.append(f"Website: {biz['contact']['website']}")

    # ── Services ──────────────────────────────────────────────────────
    lines.append("\n=== SERVICES ===")
    for svc in sop_data["services"]:
        lines.append(f"\n--- {svc['name']} ---")
        price_key = "starting_price" if "starting_price" in svc else "price"
        lines.append(f"Price: {svc[price_key]}")
        lines.append(f"Description: {svc['description']}")
        lines.append(f"Duration: {svc.get('duration', 'N/A')}")
        if "results" in svc:
            lines.append(f"Results: {svc['results']}")
        if "longevity" in svc:
            lines.append(f"Longevity: {svc['longevity']}")
        if "note" in svc:
            lines.append(f"Note: {svc['note']}")

    # ── Booking Information ───────────────────────────────────────────
    booking = sop_data["booking"]
    lines.append("\n=== BOOKING INFORMATION ===")
    lines.append(f"Booking Channels: {', '.join(booking['channels'])}")
    lines.append(f"How to Book: {booking['how_to_book']}")
    lines.append(f"Cancellation Policy: {booking['cancellation_policy']}")
    lines.append(f"Deposit: {booking['deposit']}")

    # ── FAQs ──────────────────────────────────────────────────────────
    lines.append("\n=== FREQUENTLY ASKED QUESTIONS ===")
    for faq in sop_data["faqs"]:
        lines.append(f"\nQ: {faq['question']}")
        lines.append(f"A: {faq['answer']}")

    # ── Policies ──────────────────────────────────────────────────────
    policies = sop_data["policies"]
    lines.append("\n=== POLICIES ===")
    lines.append(f"Age Requirement: {policies['age_requirement']}")
    lines.append(f"Aftercare: {policies['aftercare']}")
    lines.append(f"Patch Test: {policies['patch_test']}")

    # ── Escalation Rules ──────────────────────────────────────────────
    esc = sop_data["escalation_rules"]
    lines.append("\n=== ESCALATION RULES ===")
    lines.append("Escalate to a human agent when:")
    for trigger in esc["triggers"]:
        lines.append(f"  - {trigger}")
    lines.append(f"Escalation Action: {esc['action']}")

    return "\n".join(lines)
