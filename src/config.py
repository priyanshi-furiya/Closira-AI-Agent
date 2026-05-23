"""Configuration and constants for the Closira AI agent."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─── API Configuration ────────────────────────────────────────────────
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "mistral-large-latest")

# ─── Paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
SOP_DATA_PATH = PROJECT_ROOT / "sop_data" / "bloom_aesthetics.json"

# ─── Agent Behaviour Thresholds ────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.6        # Below this → escalate for low confidence
MAX_UNANSWERED_QUESTIONS = 2      # More than this consecutive → escalate
MAX_FAQ_TURNS_BEFORE_QUALIFY = 3  # After this many FAQ turns, offer qualification

# ─── Lead Qualification Questions ──────────────────────────────────────
QUALIFICATION_QUESTIONS = [
    "What type of treatment are you most interested in?",
    "Is this your first time considering aesthetic treatments, or have you had similar treatments before?",
    "How did you hear about Bloom Aesthetics Clinic?",
]
