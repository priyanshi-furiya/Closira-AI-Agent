# 🌸 Closira AI — Customer Support Workflow

An AI-powered customer support agent for **Bloom Aesthetics Clinic**, built as part of the Closira AI Engineering Internship assignment. The system handles inbound customer enquiries end-to-end across four stages: FAQ answering, lead qualification, escalation detection, and conversation summarisation.

## Architecture

The agent is implemented as a **state machine** orchestrated by `ClosiraAgent`:

```
┌─────────────┐     ┌──────────────────┐     ┌───────────────┐
│  GREETING   │────▶│  FAQ_ANSWERING   │────▶│  QUALIFYING   │
└─────────────┘     └──────────────────┘     └───────────────┘
                           │                        │
                           ▼                        ▼
                    ┌──────────────┐          (returns to FAQ)
                    │  ESCALATED   │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    ENDED     │ ──▶ Summary Generation
                    └──────────────┘
```

**Escalation detection runs as a parallel check on every message**, regardless of the current state. This ensures that complaints, angry sentiment, or explicit handoff requests are caught immediately.

## The Four Stages

| Stage | Description |
|-------|-------------|
| **1. FAQ Answering** | Answers customer questions using only the SOP data. The model is instructed to never invent information. Confidence scores are reported for every response. |
| **2. Lead Qualification** | After 3 FAQ turns, asks 3 structured questions to qualify the lead (treatment interest, experience level, acquisition channel). Stores and summarises responses. |
| **3. Escalation Detection** | Runs on every message with a 3-layer detection system: (1) model self-reported flags, (2) confidence threshold check, (3) keyword-based backup. Logs all escalation events with reasons. |
| **4. Conversation Summary** | On session end, generates a structured summary including customer intent, key details, SOP gaps, lead qualification data, and recommended next action. |

## Setup

### Prerequisites
- **Python 3.10+** (uses `match/case` syntax and `X | Y` type unions)
- **Gemini API key** from [Google AI Studio](https://aistudio.google.com/)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd "AI Agent"

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ | — | Your Google Gemini API key |
| `MODEL_NAME` | ❌ | `gemini-2.0-flash` | Gemini model to use |

## How to Run

```bash
python -m src.main
```

This launches an interactive CLI conversation with the AI agent. Type your messages and press Enter. Type `quit`, `bye`, or `exit` to end the session and see the conversation summary.

### CLI Features
- 🎨 **Coloured terminal output** (via `rich` library)
- 📊 **Real-time metadata** — confidence scores, detected intent, escalation flags
- 📋 **Auto-generated summary** on session end
- ⌨️ **Ctrl+C support** — graceful exit with summary generation

## Project Structure

```
AI Agent/
├── README.md                          # This file
├── prompt_design.md                   # Prompt engineering documentation
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variable template
├── .gitignore                         # Git ignore rules
│
├── sop_data/
│   └── bloom_aesthetics.json          # SOP source data (JSON)
│
├── src/
│   ├── __init__.py
│   ├── main.py                        # CLI entry point (rich terminal UI)
│   ├── agent.py                       # Core orchestrator (state machine)
│   ├── config.py                      # Configuration & constants
│   ├── models.py                      # Data models (dataclasses + enums)
│   ├── sop_loader.py                  # SOP JSON loader & formatter
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── templates.py               # All prompt templates
│   └── stages/
│       ├── __init__.py
│       ├── faq.py                     # Stage 1: FAQ utilities
│       ├── qualification.py           # Stage 2: Lead qualification flow
│       ├── escalation.py              # Stage 3: Escalation detection
│       └── summary.py                 # Stage 4: Summary formatting
│
├── test_transcripts/                  # Sample conversations (5 scenarios)
│   ├── 01_in_sop_question.md
│   ├── 02_out_of_scope_question.md
│   ├── 03_escalation_trigger.md
│   ├── 04_lead_qualification.md
│   └── 05_conversation_summary.md
│
└── tests/
    ├── __init__.py
    └── smoke_test.py                  # Automated smoke test
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `google-generativeai` | ≥0.8.0 | Google Gemini API SDK |
| `rich` | ≥13.0.0 | Terminal UI with colours, panels, and markdown |
| `python-dotenv` | ≥1.0.0 | Environment variable loading from `.env` |

## SOP Data

The AI operates on a structured JSON SOP file (`sop_data/bloom_aesthetics.json`) for a fictional business:

- **Business**: Bloom Aesthetics Clinic (London)
- **Hours**: Mon–Sat, 9 AM – 7 PM
- **Services**: Botox (from £200), Dermal Fillers (from £250), Free Consultation
- **Booking**: Via WhatsApp or website, £50 deposit, 24hr cancellation policy
- **Escalation triggers**: Complaints, medical questions, pricing negotiation, >2 unanswered questions

The SOP is loaded at startup and injected into the system prompt. The AI is strictly instructed to answer only from this data.

## Trade-offs & Known Limitations

1. **Free-tier rate limits**: The Gemini free tier has request-per-minute limits. For rapid-fire testing, you may hit 429 errors. The agent handles these gracefully with fallback responses.

2. **Single SOP file**: The current design loads one SOP file. For multi-business support, the `sop_loader` would need to be extended.

3. **No persistent storage**: Conversation history and qualification data are stored in memory only. A production system would persist these to a database.

4. **Qualification timing**: Lead qualification is triggered after a fixed number of FAQ turns (3). A more sophisticated system would detect natural transition points.

5. **Sentiment detection**: Angry sentiment is detected primarily by the model's interpretation. The keyword-based backup layer covers explicit escalation requests but not nuanced frustration.

6. **No authentication**: The CLI has no user authentication. A production system would integrate with WhatsApp/email channel APIs.

## Evaluation Criteria Alignment

| Criterion | Implementation |
|-----------|---------------|
| **AI workflow structure** | Clean 4-stage state machine with logical transitions |
| **Prompt quality** | Detailed system prompt with persona, SOP grounding, and structured output |
| **Reliability & safety** | 6-rule hallucination prevention, confidence scoring, graceful error handling |
| **Escalation logic** | 3-layer detection (model flags → confidence threshold → keywords), logged with reasons |
| **SOP understanding** | Rich SOP data with FAQs, policies, services — responses reflect real SMB context |
| **Clarity of reasoning** | See `prompt_design.md` for detailed design documentation |
