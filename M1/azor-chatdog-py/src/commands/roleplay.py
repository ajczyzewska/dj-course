"""
Role-playing command - starts autonomous conversation between two personas.
"""

from typing import Optional, Tuple
from assistant import get_assistant, get_all_assistants, Assistant
from roleplay import RolePlayingSession
from cli import console


def roleplay_command() -> None:
    """
    Starts an interactive role-playing session between two personas.
    Prompts user to select two assistants and provide initial prompt.
    """
    console.print_info("\n🎭 Role-Playing Session Setup")
    console.print_info("=" * 80)

    # Get available assistants
    assistants = get_all_assistants()
    assistant_keys = list(assistants.keys())

    if len(assistant_keys) < 2:
        console.print_error("Błąd: Potrzebujesz co najmniej 2 asystentów do rozpoczęcia sesji role-playing.")
        return

    # Display available assistants
    console.print_help("\nDostępni asystenci:")
    for i, (key, assistant) in enumerate(assistants.items(), 1):
        console.print_help(f"  {i}. {key.upper()} - {assistant.name}")

    # Select first persona
    persona_a_key = _select_assistant(
        prompt="\nWybierz pierwszego asystenta (numer lub nazwa)",
        assistants=assistants,
        assistant_keys=assistant_keys
    )

    if not persona_a_key:
        console.print_info("Anulowano.")
        return

    # Select second persona (different from first)
    remaining_keys = [k for k in assistant_keys if k != persona_a_key]
    if len(remaining_keys) == 0:
        console.print_error("Błąd: Brak dostępnych asystentów dla drugiej persony.")
        return

    remaining_assistants = {k: assistants[k] for k in remaining_keys}

    persona_b_key = _select_assistant(
        prompt=f"\nWybierz drugiego asystenta (różnego od {persona_a_key.upper()})",
        assistants=remaining_assistants,
        assistant_keys=remaining_keys
    )

    if not persona_b_key:
        console.print_info("Anulowano.")
        return

    # Get initial prompt
    console.print_info("\n" + "=" * 80)
    initial_prompt = input("Podaj temat/pytanie startowe dla rozmowy:\n> ").strip()

    if not initial_prompt:
        console.print_info("Anulowano - nie podano tematu.")
        return

    # Create and start session
    try:
        assistant_a = get_assistant(persona_a_key)
        assistant_b = get_assistant(persona_b_key)

        session = RolePlayingSession.create(assistant_a, assistant_b)
        session.start_conversation(initial_prompt, max_turns=None)

    except KeyboardInterrupt:
        console.print_info("\n\n🛑 Sesja przerwana przez użytkownika (Ctrl+C)")
    except Exception as e:
        console.print_error(f"\n\nBłąd podczas sesji role-playing: {e}")
        import traceback
        traceback.print_exc()


def _select_assistant(
    prompt: str,
    assistants: dict,
    assistant_keys: list
) -> Optional[str]:
    """
    Prompts user to select an assistant by number or name.

    Args:
        prompt: Prompt message to display
        assistants: Dictionary of available assistants
        assistant_keys: List of assistant keys

    Returns:
        str or None: Selected assistant key, or None if cancelled
    """
    while True:
        user_input = input(f"{prompt}: ").strip().lower()

        if not user_input:
            return None

        # Try as number
        if user_input.isdigit():
            index = int(user_input) - 1
            if 0 <= index < len(assistant_keys):
                return assistant_keys[index]
            else:
                console.print_error(f"Błąd: Numer musi być między 1 a {len(assistant_keys)}")
                continue

        # Try as assistant key
        if user_input in assistant_keys:
            return user_input

        console.print_error(f"Błąd: Nieznany asystent '{user_input}'. Spróbuj ponownie.")
