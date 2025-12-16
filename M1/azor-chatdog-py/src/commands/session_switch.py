"""
Interactive session switcher using prompt_toolkit.
"""

from prompt_toolkit.shortcuts import radiolist_dialog
from files import session_files
from cli import console


def select_session_interactive():
    """
    Display an interactive dropdown to select a session.

    Returns:
        str: Selected session ID or None if cancelled
    """
    sessions = session_files.list_sessions()

    if not sessions:
        console.print_help("\nBrak zapisanych sesji.")
        return None

    if len(sessions) == 1:
        console.print_error("Tylko jedna sesja dostępna. Nie można przełączyć.")
        return None

    # Create choices for radiolist_dialog
    choices = []
    for session in sessions:
        if session.get('error'):
            # Skip sessions with errors
            continue

        # Format display text
        title = session.get('title')
        session_id = session['id']
        messages_count = session['messages_count']
        last_activity = session['last_activity']

        if title:
            # Show title with short ID
            short_id = session_id[:8]
            display_text = f"{title} ({messages_count} msg, {last_activity}, ID: {short_id}...)"
        else:
            # Show full ID if no title
            display_text = f"{session_id} ({messages_count} msg, {last_activity})"

        choices.append((session_id, display_text))

    if not choices:
        console.print_error("Brak dostępnych sesji do przełączenia.")
        return None

    try:
        # Show interactive dialog
        result = radiolist_dialog(
            title="Wybierz sesję",
            text="Użyj strzałek ↑↓ do nawigacji, SPACE aby zaznaczyć, ENTER aby potwierdzić:",
            values=choices
        ).run()

        return result
    except (KeyboardInterrupt, EOFError):
        # User cancelled
        return None
