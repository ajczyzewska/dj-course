"""
Google Gemini LLM Client Implementation
Encapsulates all Google Gemini AI interactions.
"""

import os
import sys
import json
from typing import Optional, List, Any, Dict, Callable
from google import genai
from google.genai import types
from dotenv import load_dotenv
from cli import console
from .gemini_validation import GeminiConfig

class GeminiChatSessionWrapper:
    """
    Wrapper for Gemini chat session that provides universal dictionary-based history format.
    This ensures compatibility with LlamaClient's history format.
    Supports function calling.
    """

    def __init__(self, gemini_session, tools_map: Optional[Dict[str, Callable]] = None):
        """
        Initialize wrapper with Gemini chat session.

        Args:
            gemini_session: The actual Gemini chat session object
            tools_map: Dictionary mapping tool names to callable functions
        """
        self.gemini_session = gemini_session
        self.tools_map = tools_map or {}

    def send_message(self, text: str) -> Any:
        """
        Forwards message to Gemini session with function calling support.

        Args:
            text: User's message

        Returns:
            Response object from Gemini
        """
        response = self.gemini_session.send_message(text)

        # Handle function calls if present
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                # Check for function calls in the response
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        # Execute the function call
                        response = self._handle_function_call(part.function_call)

        return response

    def _handle_function_call(self, function_call):
        """
        Handle function call from the model.

        Args:
            function_call: FunctionCall object from Gemini

        Returns:
            Response from the model after function execution
        """
        function_name = function_call.name
        function_args = dict(function_call.args) if hasattr(function_call, 'args') else {}

        console.print_info(f"🔧 Wywołanie narzędzia: {function_name}({json.dumps(function_args, ensure_ascii=False)})")

        # Execute the tool function
        if function_name in self.tools_map:
            try:
                tool_function = self.tools_map[function_name]
                result = tool_function(**function_args)
                console.print_info(f"✅ Narzędzie {function_name} wykonane")

                # Send function result back to the model
                function_response = types.Part.from_function_response(
                    name=function_name,
                    response={"result": result}
                )

                # Continue the conversation with the function result
                return self.gemini_session.send_message(function_response)
            except Exception as e:
                error_msg = f"Error executing {function_name}: {str(e)}"
                console.print_error(f"❌ {error_msg}")

                # Send error back to the model
                function_response = types.Part.from_function_response(
                    name=function_name,
                    response={"error": error_msg}
                )
                return self.gemini_session.send_message(function_response)
        else:
            error_msg = f"Unknown function: {function_name}"
            console.print_error(f"❌ {error_msg}")
            function_response = types.Part.from_function_response(
                name=function_name,
                response={"error": error_msg}
            )
            return self.gemini_session.send_message(function_response)
    
    def get_history(self) -> List[Dict]:
        """
        Gets conversation history in universal dictionary format.
        
        Returns:
            List of dictionaries with format: {"role": "user|model", "parts": [{"text": "..."}]}
        """
        gemini_history = self.gemini_session.get_history()
        universal_history = []
        
        for content in gemini_history:
            # Convert Gemini Content object to universal dictionary format
            text_part = ""
            if hasattr(content, 'parts') and content.parts:
                for part in content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_part = part.text
                        break
            
            if text_part:
                universal_content = {
                    "role": content.role,
                    "parts": [{"text": text_part}]
                }
                universal_history.append(universal_content)
        
        return universal_history

class GeminiLLMClient:
    """
    Encapsulates all Google Gemini AI interactions.
    Provides a clean interface for chat sessions, token counting, and configuration.
    """
    
    def __init__(self, model_name: str, api_key: str):
        """
        Initialize the Gemini LLM client with explicit parameters.
        
        Args:
            model_name: Model to use (e.g., 'gemini-2.5-flash')
            api_key: Google Gemini API key
        
        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key:
            raise ValueError("API key cannot be empty or None")
        
        self.model_name = model_name
        self.api_key = api_key
        
        # Initialize the client during construction
        self._client = self._initialize_client()
    
    @staticmethod
    def preparing_for_use_message() -> str:
        """
        Returns a message indicating that Gemini client is being prepared.
        
        Returns:
            Formatted preparation message string
        """
        return "🤖 Przygotowywanie klienta Gemini..."
    
    @classmethod
    def from_environment(cls, interactive: bool = True) -> 'GeminiLLMClient':
        """
        Factory method that creates a GeminiLLMClient instance from environment variables.

        Args:
            interactive: Ignored for Gemini (compatibility parameter)

        Returns:
            GeminiLLMClient instance initialized with environment variables

        Raises:
            ValueError: If required environment variables are not set
        """
        load_dotenv()

        # Walidacja z Pydantic
        config = GeminiConfig(
            model_name=os.getenv('MODEL_NAME', 'gemini-2.5-flash'),
            gemini_api_key=os.getenv('GEMINI_API_KEY', '')
        )

        return cls(model_name=config.model_name, api_key=config.gemini_api_key)
    
    def _initialize_client(self) -> genai.Client:
        """
        Initializes the Google GenAI client.
        
        Returns:
            Initialized GenAI client
            
        Raises:
            SystemExit: If client initialization fails
        """
        try:
            return genai.Client()
        except Exception as e:
            console.print_error(f"Błąd inicjalizacji klienta Gemini: {e}")
            sys.exit(1)
    
    def create_chat_session(self,
                          system_instruction: str,
                          history: Optional[List[Dict]] = None,
                          thinking_budget: int = 0,
                          tools: Optional[List[Dict]] = None,
                          tools_map: Optional[Dict[str, Callable]] = None) -> GeminiChatSessionWrapper:
        """
        Creates a new chat session with the specified configuration.

        Args:
            system_instruction: System role/prompt for the assistant
            history: Previous conversation history (optional, in universal dict format)
            thinking_budget: Thinking budget for the model
            tools: List of tool definitions for function calling
            tools_map: Dictionary mapping tool names to callable functions

        Returns:
            GeminiChatSessionWrapper with universal dictionary-based interface
        """
        if not self._client:
            raise RuntimeError("LLM client not initialized")

        # Convert universal dict format to Gemini Content objects
        gemini_history = []
        if history:
            for entry in history:
                if isinstance(entry, dict) and 'role' in entry and 'parts' in entry:
                    text = entry['parts'][0].get('text', '') if entry['parts'] else ''
                    if text:
                        content = types.Content(
                            role=entry['role'],
                            parts=[types.Part.from_text(text=text)]
                        )
                        gemini_history.append(content)

        # Convert tool definitions to Gemini Tool objects
        gemini_tools = None
        if tools:
            function_declarations = []
            for tool in tools:
                # Convert tool dict to FunctionDeclaration
                func_decl = types.FunctionDeclaration(
                    name=tool['name'],
                    description=tool['description'],
                    parameters=tool.get('parameters', {})
                )
                function_declarations.append(func_decl)

            gemini_tools = [types.Tool(function_declarations=function_declarations)]

        # Create config with tools if provided
        config_params = {
            "system_instruction": system_instruction,
            "thinking_config": types.ThinkingConfig(thinking_budget=thinking_budget)
        }

        if gemini_tools:
            config_params["tools"] = gemini_tools

        gemini_session = self._client.chats.create(
            model=self.model_name,
            history=gemini_history,
            config=types.GenerateContentConfig(**config_params)
        )

        return GeminiChatSessionWrapper(gemini_session, tools_map=tools_map)
    
    def count_history_tokens(self, history: List[Dict]) -> int:
        """
        Counts tokens for the given conversation history.
        
        Args:
            history: Conversation history in universal dict format
            
        Returns:
            Total token count
        """
        if not history:
            return 0
        
        try:
            # Convert universal dict format to Gemini Content objects for token counting
            gemini_history = []
            for entry in history:
                if isinstance(entry, dict) and 'role' in entry and 'parts' in entry:
                    text = entry['parts'][0].get('text', '') if entry['parts'] else ''
                    if text:
                        content = types.Content(
                            role=entry['role'],
                            parts=[types.Part.from_text(text=text)]
                        )
                        gemini_history.append(content)
            
            response = self._client.models.count_tokens(
                model=self.model_name,
                contents=gemini_history
            )
            return response.total_tokens
        except Exception as e:
            console.print_error(f"Błąd podczas liczenia tokenów: {e}")
            return 0
    
    def get_model_name(self) -> str:
        """Returns the currently configured model name."""
        return self.model_name
    
    def is_available(self) -> bool:
        """
        Checks if the LLM service is available and properly configured.
        
        Returns:
            True if client is properly initialized and has API key
        """
        return self._client is not None and bool(self.api_key)
    
    def ready_for_use_message(self) -> str:
        """
        Returns a ready-to-use message with model info and masked API key.

        Returns:
            Formatted message string for display
        """
        # Mask API key - show first 4 and last 4 characters
        if len(self.api_key) <= 8:
            masked_key = "****"
        else:
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}"

        return f"✅ Klient Gemini gotowy do użycia (Model: {self.model_name}, Key: {masked_key})"

    def generate_single(self, prompt: str) -> str:
        """
        Generates a single response without chat context.
        Useful for one-off generations like title generation.

        Args:
            prompt: The prompt to generate a response for

        Returns:
            Generated text response
        """
        if not self._client:
            raise RuntimeError("LLM client not initialized")

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text
    
    @property
    def client(self):
        """
        Provides access to the underlying GenAI client for backwards compatibility.
        This property should be used sparingly and eventually removed.
        """
        return self._client
