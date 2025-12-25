"""
Persona class - wrapper around Assistant for role-playing sessions.
Manages conversation history and LLM interactions for a single persona.
"""

from typing import List, Any, Optional
from assistant import Assistant
from llm.gemini_client import GeminiLLMClient
import os


class Persona:
    """
    Represents a single persona in a role-playing conversation.
    Wraps an Assistant and manages its conversation history.
    """

    def __init__(self, assistant: Assistant, llm_client: Optional[GeminiLLMClient] = None):
        """
        Initialize a Persona.

        Args:
            assistant: The Assistant instance defining this persona's role
            llm_client: Optional shared LLM client. If None, will be created.
        """
        self.assistant = assistant
        self._llm_client = llm_client
        self._conversation_history: List[Any] = []

    @property
    def name(self) -> str:
        """Get the persona's display name."""
        return self.assistant.name

    @property
    def system_prompt(self) -> str:
        """Get the persona's system prompt."""
        return self.assistant.system_prompt

    def get_history(self) -> List[Any]:
        """Get the current conversation history for this persona."""
        return self._conversation_history.copy()

    def add_to_history(self, role: str, text: str):
        """
        Add a message to this persona's conversation history.

        Args:
            role: Either 'user' or 'model'
            text: The message content
        """
        from google.genai import types

        self._conversation_history.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=text)]
            )
        )

    def generate_response(self, llm_client: GeminiLLMClient) -> str:
        """
        Generate a response from this persona based on current history.

        Args:
            llm_client: The LLM client to use for generation

        Returns:
            str: The generated response text
        """
        from google.genai import types

        response = llm_client.client.models.generate_content(
            model=llm_client.get_model_name(),
            contents=self._conversation_history,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                max_output_tokens=512
            ),
        )

        return response.text
