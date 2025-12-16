#!/usr/bin/env python3
"""
Skrypt do tworzenia testowych sesji dla demonstracji funkcji /switch.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Katalog sesji
SESSIONS_DIR = Path.home() / ".azor-chat" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

def create_test_session(session_id, title, messages, model="gemini-2.0-flash-exp"):
    """Tworzy testową sesję z podanymi parametrami."""

    session_data = {
        "session_id": session_id,
        "model": model,
        "system_role": "Jesteś pomocnym asystentem AI.",
        "title": title,
        "history": []
    }

    # Dodaj wiadomości z timestampami
    for i, (role, text) in enumerate(messages):
        timestamp = datetime.now().isoformat()
        session_data["history"].append({
            "role": role,
            "timestamp": timestamp,
            "text": text
        })

    # Zapisz sesję
    filename = f"{session_id}-log.json"
    filepath = SESSIONS_DIR / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Utworzono sesję: {title} ({session_id})")


# Utwórz 3 testowe sesje
create_test_session(
    "test-session-weather",
    "Rozmowa o pogodzie",
    [
        ("user", "Jaka jest pogoda?"),
        ("model", "Niestety nie mam dostępu do aktualnych danych pogodowych. Jestem modelem językowym bez dostępu do internetu.")
    ]
)

create_test_session(
    "test-session-typescript",
    "Nauka TypeScript",
    [
        ("user", "Jak działa TypeScript?"),
        ("model", "TypeScript to nadzbiór JavaScript z typowaniem statycznym. Pozwala na wykrywanie błędów na etapie kompilacji.")
    ]
)

create_test_session(
    "test-session-python",
    None,  # Sesja bez tytułu
    [
        ("user", "Cześć!"),
        ("model", "Witaj! Jak mogę Ci pomóc?"),
        ("user", "Czym się różni Python od JavaScript?"),
        ("model", "Python i JavaScript to dwa różne języki programowania z odmiennymi paradygmatami i zastosowaniami...")
    ]
)

print("\n" + "="*60)
print("Testowe sesje zostały utworzone!")
print("="*60)
print("\nTeraz możesz uruchomić AZØRA:")
print("  cd /Users/agnieszka/repos/dj/dj-course/M1/azor-chatdog-py")
print("  source .venv/bin/activate")
print("  python src/run.py")
print("\nI przetestować komendę:")
print("  /switch        ← pokaże interaktywny dropdown")
print("  /switch test-session-weather  ← bezpośrednie przełączenie")
