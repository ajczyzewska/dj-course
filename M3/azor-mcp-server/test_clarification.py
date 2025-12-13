#!/usr/bin/env python3
"""
Test script for ask_for_clarification tool.

Demonstrates how the AI agent can ask the user for more specific information
when a question is too vague.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from azor_mcp.server import handle_ask_for_clarification


async def test_clarification_simple():
    """Test simple clarification request."""
    print("\n" + "="*60)
    print("TEST: Simple clarification (without context)")
    print("="*60)
    print("\nAgent wykrył niejasne pytanie i prosi o doprecyzowanie...\n")

    # Simulate what the AI agent would do
    result = await handle_ask_for_clarification({
        "question": "Które sesje AZØRA chcesz usunąć?",
    })

    print("\n" + "="*60)
    print("Odpowiedź zwrócona do agenta AI:")
    print("="*60)
    print(result[0].text)


async def test_clarification_with_context():
    """Test clarification request with context."""
    print("\n" + "="*60)
    print("TEST: Clarification with context")
    print("="*60)
    print("\nAgent wykrył niejasne pytanie i wyjaśnia dlaczego potrzebuje więcej info...\n")

    # Simulate what the AI agent would do
    result = await handle_ask_for_clarification({
        "question": "Z jakiego okresu czasu chcesz usunąć sesje? (ostatni dzień, tydzień, miesiąc?)",
        "context": "Użytkownik poprosił 'usuń stare sesje', ale nie określił co znaczy 'stare'."
    })

    print("\n" + "="*60)
    print("Odpowiedź zwrócona do agenta AI:")
    print("="*60)
    print(result[0].text)


async def main():
    """Run clarification tests."""
    print("\n🤖 AZØR MCP Server - Test narzędzia ask_for_clarification")
    print("="*60)
    print("\nTo narzędzie pozwala agentowi AI dopytać użytkownika o szczegóły.")
    print("Po uruchomieniu, wpisz odpowiedź i naciśnij Enter.\n")

    # Choose test
    print("Wybierz test:")
    print("1. Proste pytanie doprecyzowujące")
    print("2. Pytanie z kontekstem")
    print("3. Oba testy po kolei")

    choice = input("\nTwój wybór (1/2/3): ").strip()

    if choice == "1":
        await test_clarification_simple()
    elif choice == "2":
        await test_clarification_with_context()
    elif choice == "3":
        await test_clarification_simple()
        print("\n" + "="*60)
        input("Naciśnij Enter aby kontynuować do następnego testu...")
        await test_clarification_with_context()
    else:
        print("Nieprawidłowy wybór!")
        return

    print("\n" + "="*60)
    print("✅ Test zakończony!")
    print("="*60)
    print("\nTak właśnie będzie działać agent AI w AZØRZE:")
    print("- Wykryje niejasne pytanie")
    print("- Zapyta użytkownika o więcej szczegółów")
    print("- Użyje odpowiedzi do wykonania zadania")


if __name__ == "__main__":
    asyncio.run(main())
