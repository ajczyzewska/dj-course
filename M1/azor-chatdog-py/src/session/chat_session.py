import uuid
from typing import List, Any, Union, Optional, Tuple
import os
from files import session_files
from files.wal import append_to_wal
from llm.gemini_client import GeminiLLMClient
from llm.llama_client import LlamaClient
from assistant import Assistant
from cli import console
from tools.mcp_tools import TOOLS_DEFINITIONS, TOOLS_MAP
from tools.clarification_tool import CLARIFICATION_TOOL_DEFINITION, CLARIFICATION_TOOLS_MAP

# Context token limit

# Engine to Client Class mapping
ENGINE_MAPPING = {
    'LLAMA_CPP': LlamaClient,
    'GEMINI': GeminiLLMClient,
}


class ChatSession:
    """
    Manages everything related to a single chat session.
    Encapsulates session ID, conversation history, assistant, and LLM chat session.
    """
    
    def __init__(self, assistant: Assistant, session_id: Optional[str] = None, history: Optional[List[Any]] = None,
                 interactive_config: bool = True, title: Optional[str] = None, assistant_key: Optional[str] = None):
        """
        Initialize a chat session.

        Args:
            assistant: Assistant instance that defines the behavior and model for this session
            session_id: Unique session identifier. If None, generates a new UUID.
            history: Initial conversation history. If None, starts empty.
            interactive_config: If True, ask for generation parameters interactively (only for new sessions)
            title: Optional title for the session. If None for new sessions, will be auto-generated.
            assistant_key: Key identifying the assistant in the registry.
        """
        self.assistant = assistant
        self._assistant_key = assistant_key or "azor"
        self.session_id = session_id or str(uuid.uuid4())
        self._history = history or []
        self._title = title
        self._llm_client: Optional[Union[GeminiLLMClient, LlamaClient]] = None
        self._llm_chat_session = None
        self._max_context_tokens = 32768
        # Only ask for config if it's a new session (no history)
        self._interactive_config = interactive_config and not history
        self._initialize_llm_session()
    
    def _initialize_llm_session(self):
        """
        Creates or recreates the LLM chat session with current history.
        This should be called after any history modification.
        """
        # Walidacja zmiennej ENGINE
        engine = os.getenv('ENGINE', 'GEMINI').upper()
        if engine not in ENGINE_MAPPING:
            valid_engines = ', '.join(ENGINE_MAPPING.keys())
            raise ValueError(f"ENGINE musi być jedną z wartości: {valid_engines}, otrzymano: {engine}")
        
        # Initialize LLM client if not already created
        if self._llm_client is None:
            SelectedClientClass = ENGINE_MAPPING.get(engine, GeminiLLMClient)
            console.print_info(SelectedClientClass.preparing_for_use_message())
            # Pass interactive flag to from_environment()
            self._llm_client = SelectedClientClass.from_environment(interactive=self._interactive_config)
            console.print_info(self._llm_client.ready_for_use_message())
        
        # Add tools only for Gemini (LlamaClient doesn't support tools parameter)
        if isinstance(self._llm_client, GeminiLLMClient):
            # Combine all tools and tools maps
            all_tools = TOOLS_DEFINITIONS + [CLARIFICATION_TOOL_DEFINITION]
            all_tools_map = {**TOOLS_MAP, **CLARIFICATION_TOOLS_MAP}

            # Debug: Show loaded tools (helpful for verification)
            tool_names = [t['name'] for t in all_tools]
            console.print_info(f"🔧 Załadowano narzędzia: {', '.join(tool_names)}")

            self._llm_chat_session = self._llm_client.create_chat_session(
                system_instruction=self.assistant.system_prompt,
                history=self._history,
                thinking_budget=0,
                tools=all_tools,
                tools_map=all_tools_map
            )
        else:
            self._llm_chat_session = self._llm_client.create_chat_session(
                system_instruction=self.assistant.system_prompt,
                history=self._history,
                thinking_budget=0
            )
    
    
    @classmethod
    def load_from_file(cls, assistant: Assistant, session_id: str) -> Tuple[Optional['ChatSession'], Optional[str]]:
        """
        Loads a session from disk.

        Args:
            assistant: Assistant instance to use for this session
            session_id: ID of the session to load

        Returns:
            tuple: (ChatSession object or None, error_message or None)
        """
        history, title, assistant_key, error = session_files.load_session_history(session_id)

        if error:
            return None, error

        session = cls(assistant=assistant, session_id=session_id, history=history, title=title, assistant_key=assistant_key)
        return session, None
    
    def save_to_file(self) -> Tuple[bool, Optional[str]]:
        """
        Saves this session to disk.
        Only saves if history has at least one complete exchange.

        Returns:
            tuple: (success: bool, error_message: str | None)
        """
        # Sync history from LLM session before saving
        if self._llm_chat_session:
            self._history = self._llm_chat_session.get_history()

        return session_files.save_session_history(
            self.session_id,
            self._history,
            self.assistant.system_prompt,
            self._llm_client.get_model_name(),
            self._title,
            self._assistant_key
        )
    
    def send_message(self, text: str):
        """
        Sends a message to the LLM and returns the response.
        Updates internal history automatically and logs to WAL.
        Generates title automatically on first message.

        Args:
            text: User's message

        Returns:
            Response object from Google GenAI
        """
        if not self._llm_chat_session:
            raise RuntimeError("LLM session not initialized")

        # Check if this is the first message (before sending)
        is_first_message = len(self._history) == 0

        response = self._llm_chat_session.send_message(text)

        # Sync history after message
        self._history = self._llm_chat_session.get_history()

        # Log to WAL
        total_tokens = self.count_tokens()
        success, error = append_to_wal(
            session_id=self.session_id,
            prompt=text,
            response_text=response.text,
            total_tokens=total_tokens,
            model_name=self._llm_client.get_model_name()
        )

        if not success and error:
            # We don't want to fail the entire message sending because of WAL issues
            # Just log the error to stderr or similar - but for now we'll silently continue
            pass

        # Generate title after first message if not already set
        if is_first_message and self._title is None:
            self._title = self._generate_title(text, response.text)
            console.print_info(f"📝 Tytuł wątku: {self._title}")

        return response
    
    def get_history(self) -> List[Any]:
        """Returns the current conversation history."""
        # Always sync from LLM session to ensure consistency
        if self._llm_chat_session:
            self._history = self._llm_chat_session.get_history()
        return self._history
    
    def clear_history(self):
        """Clears all conversation history and reinitializes the LLM session."""
        self._history = []
        self._initialize_llm_session()
        self.save_to_file()
    
    def pop_last_exchange(self) -> bool:
        """
        Removes the last user-assistant exchange from history.
        
        Returns:
            bool: True if successful, False if insufficient history
        """
        current_history = self.get_history()
        
        if len(current_history) < 2:
            return False
        
        # Remove last 2 entries (user + assistant)
        self._history = current_history[:-2]
        
        # Reinitialize LLM session with modified history
        self._initialize_llm_session()
        
        self.save_to_file()
        
        return True
    
    def count_tokens(self) -> int:
        """
        Counts total tokens in the conversation history.
        
        Returns:
            int: Total token count
        """
        if not self._llm_client:
            return 0
        return self._llm_client.count_history_tokens(self._history)
    
    def is_empty(self) -> bool:
        """
        Checks if session has any complete exchanges.
        
        Returns:
            bool: True if history has less than 2 entries
        """
        return len(self._history) < 2
    
    def get_remaining_tokens(self) -> int:
        """
        Calculates remaining tokens based on context limit.
        
        Returns:
            int: Remaining token count
        """
        total = self.count_tokens()
        return self._max_context_tokens - total
    
    def get_token_info(self) -> tuple[int, int, int]:
        """
        Gets comprehensive token information for this session.
        
        Returns:
            tuple: (total_tokens, remaining_tokens, max_tokens)
        """
        total_tokens = self.count_tokens()
        remaining_tokens = self._max_context_tokens - total_tokens
        max_tokens = self._max_context_tokens
        return total_tokens, remaining_tokens, max_tokens
    
    @property
    def assistant_name(self) -> str:
        """
        Gets the display name of the assistant.

        Returns:
            str: The assistant's display name
        """
        return self.assistant.name

    @property
    def assistant_key(self) -> str:
        """
        Gets the key identifying the current assistant.

        Returns:
            str: The assistant's registry key
        """
        return self._assistant_key

    def switch_assistant(self, new_assistant: Assistant, new_key: str):
        """
        Switches to a different assistant while preserving history.

        Args:
            new_assistant: The new Assistant instance to use
            new_key: The registry key of the new assistant
        """
        self.assistant = new_assistant
        self._assistant_key = new_key
        # Reinitialize LLM session with new system prompt
        self._initialize_llm_session()
        # Save session with new assistant info
        self.save_to_file()

    @property
    def title(self) -> Optional[str]:
        """
        Gets the session title.

        Returns:
            str or None: The session title, or None if not set
        """
        return self._title

    @title.setter
    def title(self, value: str):
        """
        Sets the session title.

        Args:
            value: New title for the session
        """
        self._title = value

    def _generate_title(self, user_prompt: str, assistant_response: str) -> str:
        """
        Generates a short title for the session based on first exchange.

        Args:
            user_prompt: The user's first message
            assistant_response: The assistant's first response

        Returns:
            str: Generated title (max 5 words)
        """
        title_prompt = f"""Na podstawie poniższej wymiany wygeneruj krótki tytuł (maksymalnie 5 słów) opisujący temat rozmowy.

User: {user_prompt[:500]}
Assistant: {assistant_response[:500]}

Odpowiedz TYLKO tytułem, bez cudzysłowów, bez dodatkowego tekstu, bez kropki na końcu."""

        try:
            # Use the LLM client to generate title
            title_response = self._llm_client.generate_single(title_prompt)
            return title_response.strip().strip('"').strip("'").rstrip('.')
        except Exception:
            # Fallback: use first few words of user prompt
            words = user_prompt.split()[:5]
            return ' '.join(words)