#!/usr/bin/env python3
"""
Test script for role-playing functionality.
Tests autonomous conversation between two personas.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from assistant import get_assistant
from roleplay import RolePlayingSession

def test_roleplay():
    """Test role-playing session with Sparring Partner and Angel Investor."""

    print("🧪 Testing Role-Playing Session...")
    print("=" * 80)

    try:
        # Get assistants
        sparring = get_assistant("sparring-partner")
        angel = get_assistant("angel-investor")

        print(f"✓ Loaded Sparring Partner: {sparring.name}")
        print(f"✓ Loaded Angel Investor: {angel.name}")
        print()

        # Create session
        session = RolePlayingSession.create(sparring, angel)
        print("✓ Created RolePlayingSession")
        print()

        # Test prompt
        initial_prompt = """Mam pomysł na startup: platforma AI do automatycznego
generowania dokumentacji technicznej z kodu źródłowego.
Czy to ma sens biznesowy?"""

        print("Initial Prompt:")
        print(initial_prompt)
        print()

        # Start conversation (max 6 turns for testing)
        session.start_conversation(initial_prompt, max_turns=6)

        print("\n" + "=" * 80)
        print("✓ Test completed successfully!")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_roleplay()
    sys.exit(0 if success else 1)
