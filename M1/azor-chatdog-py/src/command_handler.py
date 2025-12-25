from session import get_session_manager
from cli import console
from commands.session_list import list_sessions_command
from commands.session_display import display_full_session
from commands.session_to_pdf import export_session_to_pdf
from commands.session_to_audio import export_last_response_to_audio
from commands.session_remove import remove_session_command
from commands.session_switch import select_session_interactive
from commands.roleplay import roleplay_command
from assistant import get_assistant, list_assistants, get_all_assistants

VALID_SLASH_COMMANDS = ['/exit', '/quit', '/switch', '/help', '/session', '/pdf', '/audio', '/assistant', '/roleplay']

def handle_command(user_input: str) -> bool:
    """
    Handles slash commands. Returns True if the program should exit.
    """
    parts = user_input.split()
    command = parts[0].lower()

    manager = get_session_manager()

    # Check if the main command is valid
    if command not in VALID_SLASH_COMMANDS:
        console.print_error(f"Błąd: Nieznana komenda: {command}. Użyj /help.")
        current = manager.get_current_session()
        console.display_help(current.session_id)
        return False
    
    # Help command
    elif command == '/help':
        current = manager.get_current_session()
        console.display_help(current.session_id)
    
    # Exit commands
    if command in ['/exit', '/quit']:
        console.print_info("\nZakończenie czatu. Uruchamianie procedury finalnego zapisu...")
        return True
    
    # Switch command
    elif command == '/switch':
        # If no argument provided, show interactive dropdown
        if len(parts) == 1:
            new_id = select_session_interactive()
            if not new_id:
                # User cancelled or no sessions available
                return False
        elif len(parts) == 2:
            new_id = parts[1]
        else:
            console.print_error("Błąd: Użycie: /switch [SESSION-ID]")
            return False

        # Perform the switch
        current = manager.get_current_session()
        if new_id == current.session_id:
            console.print_info("Jesteś już w tej sesji.")
        else:
            new_session, save_attempted, previous_session_id, load_successful, load_error, has_history = manager.switch_to_session(new_id)

            # Handle console output for save attempt
            if save_attempted:
                console.print_info(f"\nZapisuję bieżącą sesję: {previous_session_id}...")

            # Handle load result
            if not load_successful:
                console.print_error(f"Nie można wczytać sesji o ID: {new_id}. {load_error}")
            else:
                # Successfully switched - show title if available
                display_name = new_session.title if new_session.title else new_session.session_id
                console.print_info(f"\n--- Przełączono na sesję: {display_name} ---")
                console.display_help(new_session.session_id)

                # Display history summary if session has content
                if has_history:
                    from commands.session_summary import display_history_summary
                    display_history_summary(new_session.get_history(), new_session.assistant_name, new_session.title)
            
    # Session subcommands
    elif command == '/session':
        if len(parts) < 2:
            console.print_error("Błąd: Komenda /session wymaga podkomendy (list, display, pop, clear, new, rename).")
        else:
            handle_session_subcommand(parts, manager)

    elif command == '/pdf':
        current = manager.get_current_session()
        export_session_to_pdf(current.get_history(), current.session_id, current.assistant_name)

    elif command == '/audio':
        current = manager.get_current_session()
        export_last_response_to_audio(current.get_history(), current.session_id, current.assistant_name)

    elif command == '/assistant':
        handle_assistant_command(parts, manager)

    elif command == '/roleplay':
        roleplay_command()

    return False


def handle_assistant_command(parts: list, manager):
    """Handles /assistant command for switching assistants."""
    current = manager.get_current_session()

    if len(parts) < 2:
        # Show list of available assistants
        console.print_help("\n--- Dostępni asystenci ---")
        assistants = get_all_assistants()
        for key, assistant in assistants.items():
            if key == current.assistant_key:
                console.print_info(f"  * {key.upper()} - {assistant.name} (aktywny)")
            else:
                console.print_help(f"    {key.upper()} - {assistant.name}")
        console.print_help("\nUżycie: /assistant <nazwa>")
        console.print_help("--------------------------")
        return

    assistant_key = parts[1].lower()

    if assistant_key not in list_assistants():
        console.print_error(f"Błąd: Nieznany asystent '{assistant_key}'.")
        console.print_help(f"Dostępni asystenci: {', '.join(list_assistants())}")
        return

    if assistant_key == current.assistant_key:
        console.print_info(f"Już rozmawiasz z asystentem {current.assistant_name}.")
        return

    # Switch assistant
    new_assistant = get_assistant(assistant_key)
    old_name = current.assistant_name
    current.switch_assistant(new_assistant, assistant_key)

    console.print_info(f"\n--- Przełączono asystenta ---")
    console.print_info(f"Z: {old_name} -> Na: {new_assistant.name}")
    console.print_help(f"Nowy asystent: {new_assistant.name}")


def handle_session_subcommand(parts: list, manager):
    """Handles /session subcommands."""
    subcommand = parts[1].lower()
    current = manager.get_current_session()

    if subcommand == 'list':
        list_sessions_command()

    elif subcommand == 'display':
        display_full_session(current.get_history(), current.session_id, current.assistant_name)

    elif subcommand == 'pop':
        success = current.pop_last_exchange()
        if success:
            from commands.session_summary import display_history_summary
            console.print_info(f"Usunięto ostatnią parę wpisów (TY i {current.assistant_name}).")
            display_history_summary(current.get_history(), current.assistant_name, current.title)
        else:
            console.print_error("Błąd: Historia jest pusta lub niekompletna (wymaga co najmniej jednej pary).")

    elif subcommand == 'clear':
        current.clear_history()
        console.print_info("Historia bieżącej sesji została wyczyszczona.")

    elif subcommand == 'new':
        new_session, save_attempted, previous_session_id, save_error = manager.create_new_session(save_current=True)

        # Handle console output for save attempt
        if save_attempted:
            console.print_info(f"\nZapisuję bieżącą sesję: {previous_session_id} przed rozpoczęciem nowej...")
            if save_error:
                console.print_error(f"Błąd podczas zapisu: {save_error}")

        # Display new session info
        console.print_info(f"\n--- Rozpoczęto nową sesję: {new_session.session_id} ---")
        console.display_help(new_session.session_id)

    elif subcommand == 'remove':
        remove_session_command(manager)

    elif subcommand == 'rename':
        if len(parts) < 3:
            console.print_error("Błąd: Użycie: /session rename <nowy-tytuł>")
        else:
            new_title = ' '.join(parts[2:])
            old_title = current.title
            current.title = new_title
            current.save_to_file()
            if old_title:
                console.print_info(f"Zmieniono tytuł z '{old_title}' na '{new_title}'")
            else:
                console.print_info(f"Ustawiono tytuł: '{new_title}'")

    else:
        console.print_error(f"Błąd: Nieznana podkomenda dla /session: {subcommand}. Użyj /help.")
