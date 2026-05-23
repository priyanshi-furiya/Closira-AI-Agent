"""Quick smoke test — verifies agent initialization and a single API call."""

import sys
import os

# Fix Windows encoding
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, ".")

from src.agent import ClosiraAgent

def smoke_test():
    print("=" * 50)
    print("SMOKE TEST - Closira AI Agent")
    print("=" * 50)

    # Test 1: Agent initialization
    print("\n[1] Initialising agent...")
    try:
        agent = ClosiraAgent()
        print("    OK - Agent initialised successfully")
    except Exception as e:
        print(f"    FAIL: {e}")
        return

    # Test 2: Greeting
    print("\n[2] Getting greeting...")
    greeting = agent.get_greeting()
    print(f"    OK - Greeting received ({len(greeting)} chars)")

    # Test 3: In-SOP question
    print("\n[3] Testing in-SOP question: 'What are your Botox prices?'")
    response, meta = agent.process_message("What are your Botox prices?")
    print(f"    OK - Response received ({len(response)} chars)")
    if meta:
        print(f"    Confidence: {meta.confidence:.0%} | In SOP: {meta.is_in_sop} | Intent: {meta.detected_intent}")

    # Test 4: Out-of-scope question
    print("\n[4] Testing out-of-scope question: 'Do you offer laser hair removal?'")
    response, meta = agent.process_message("Do you offer laser hair removal?")
    print(f"    OK - Response received ({len(response)} chars)")
    if meta:
        print(f"    Confidence: {meta.confidence:.0%} | In SOP: {meta.is_in_sop} | Escalation: {meta.escalation_needed}")

    # Test 5: Exit and summary
    print("\n[5] Testing exit and summary generation...")
    response, meta = agent.process_message("bye")
    print(f"    OK - Farewell received")

    summary = agent.generate_summary()
    print(f"    Summary - Intent: {summary.customer_intent}")
    print(f"    Summary - Key Details: {summary.key_details}")
    print(f"    Summary - SOP Gaps: {summary.sop_gaps}")
    print(f"    Summary - Next Action: {summary.recommended_next_action}")

    print("\n" + "=" * 50)
    print("ALL SMOKE TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    smoke_test()
