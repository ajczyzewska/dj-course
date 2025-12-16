"""
Clarification Tool
Allows the model to ask for clarification when user's question is not precise enough.
"""

from cli import console
from cli.prompt import get_user_input


def ask_for_clarification(question: str) -> str:
    """
    Ask the user for clarification when the question is not precise enough.

    This tool allows the model to interactively request more details from the user
    when their initial question is ambiguous, lacks context, or needs refinement.

    Args:
        question: The clarifying question to ask the user

    Returns:
        str: The user's answer/clarification

    Example:
        Model receives: "zrób to"
        Model calls: ask_for_clarification("Co dokładnie chcesz, żebym zrobił?")
        User responds: "Napisz funkcję do sortowania listy"
        Model continues with full context
    """
    # Display the clarification request
    console.print_info("🤔 AZØR potrzebuje doprecyzowania...")
    console.print_assistant(f"\n{question}")

    # Get user's response
    user_response = get_user_input()

    if not user_response:
        return "Użytkownik nie podał odpowiedzi."

    return user_response


# Tool definition for Gemini function calling
CLARIFICATION_TOOL_DEFINITION = {
    "name": "ask_for_clarification",
    "description": """CALL THIS IMMEDIATELY when user's question is vague, unclear, or missing details.

Examples when to call:
- "zrób to" - unclear what to do
- "pomóż mi" - unclear with what
- "napisz kod" - missing language and purpose
- Question with pronouns like "to", "tamto" without context

This pauses the conversation, asks user for details, and returns their answer.""",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "Your clarifying question in Polish. Examples: 'Co konkretnie chcesz, żebym zrobił?', 'W czym mogę Ci pomóc?', 'Jaki kod mam napisać i w jakim języku?'"
            }
        },
        "required": ["question"]
    }
}


# Map function name to actual function
CLARIFICATION_TOOLS_MAP = {
    "ask_for_clarification": ask_for_clarification
}
