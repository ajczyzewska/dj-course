#!/usr/bin/env python3
"""
Direct test of clarification tool with Gemini API
"""

import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

from llm.gemini_client import GeminiLLMClient
from tools.clarification_tool import CLARIFICATION_TOOL_DEFINITION, CLARIFICATION_TOOLS_MAP
from assistant.azor import create_azor_assistant

print("=" * 60)
print("🧪 TEST: Bezpośrednie wywołanie z narzędziem clarification")
print("=" * 60)
print()

# Create LLM client
print("🤖 Tworzenie klienta Gemini...")
client = GeminiLLMClient.from_environment()
print(f"✅ {client.ready_for_use_message()}")
print()

# Create assistant
assistant = create_azor_assistant()
print(f"🐕 Utworzono asystenta: {assistant.name}")
print()

# Create chat session with tools
print("🔧 Tworzenie sesji z narzędziem ask_for_clarification...")
session = client.create_chat_session(
    system_instruction=assistant.system_prompt,
    tools=[CLARIFICATION_TOOL_DEFINITION],
    tools_map=CLARIFICATION_TOOLS_MAP
)
print("✅ Sesja utworzona")
print()

# Test messages
test_messages = [
    "zrób to",
    "pomóż mi",
    "napisz kod",
]

print("=" * 60)
print("📤 Wysyłanie testowych pytań")
print("=" * 60)
print()

for msg in test_messages:
    print(f"👤 USER: {msg}")
    print()

    try:
        response = session.send_message(msg)
        print(f"🤖 AZOR: {response.text}")
        print()
        print("-" * 60)
        print()
    except Exception as e:
        print(f"❌ BŁĄD: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("-" * 60)
        print()

print("=" * 60)
print("✅ Test zakończony")
print("=" * 60)
