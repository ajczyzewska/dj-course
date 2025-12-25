"""
RolePlayingSession - manages autonomous conversation between two personas.
"""

from typing import Optional
from .persona import Persona
from assistant import Assistant
from llm.gemini_client import GeminiLLMClient
from cli import console
from colorama import Fore, Style


class RolePlayingSession:
    """
    Manages an autonomous conversation between two personas.

    The conversation alternates between two personas, with each persona
    responding to the previous persona's message. The conversation history
    is managed separately for each persona to maintain proper context.
    """

    def __init__(self, persona_a: Persona, persona_b: Persona, llm_client: GeminiLLMClient):
        """
        Initialize a role-playing session.

        Args:
            persona_a: First persona in the conversation
            persona_b: Second persona in the conversation
            llm_client: Shared LLM client for both personas
        """
        self.persona_a = persona_a
        self.persona_b = persona_b
        self.llm_client = llm_client
        self._turn_count = 0
        self._max_turns = 20  # Safety limit to prevent infinite loops

    @classmethod
    def create(cls, assistant_a: Assistant, assistant_b: Assistant) -> 'RolePlayingSession':
        """
        Create a new role-playing session from two assistants.

        Args:
            assistant_a: First assistant
            assistant_b: Second assistant

        Returns:
            RolePlayingSession: Initialized session
        """
        # Create shared LLM client
        llm_client = GeminiLLMClient.from_environment(interactive=False)

        # Create personas
        persona_a = Persona(assistant_a, llm_client)
        persona_b = Persona(assistant_b, llm_client)

        return cls(persona_a, persona_b, llm_client)

    def start_conversation(self, initial_prompt: str, max_turns: Optional[int] = None) -> None:
        """
        Start the autonomous conversation between two personas.

        Args:
            initial_prompt: The topic/question to start the conversation
            max_turns: Maximum number of turns (None for interactive mode)
        """
        if max_turns is not None:
            self._max_turns = max_turns

        console.print_info(f"\n{'='*80}")
        console.print_info(f"🎭 Role-Playing Session Started")
        console.print_info(f"Persona A: {self.persona_a.name}")
        console.print_info(f"Persona B: {self.persona_b.name}")
        console.print_info(f"{'='*80}\n")

        print(f"{Fore.CYAN}INITIAL PROMPT{Style.RESET_ALL}: {initial_prompt}\n")

        # Turn 1: Persona A responds to initial prompt
        self._execute_turn(
            responding_persona=self.persona_a,
            other_persona=self.persona_b,
            initial_message=initial_prompt,
            is_first_turn=True
        )

        # Continue with alternating turns
        while self._turn_count < self._max_turns:
            # Ask user if they want to continue (in interactive mode)
            if max_turns is None:
                user_input = input(f"\n{Fore.YELLOW}Continue? (Enter = yes, 'stop' = no):{Style.RESET_ALL} ").strip().lower()
                if user_input in ['stop', 'exit', 'quit', 'n', 'no']:
                    console.print_info("\n🛑 Conversation stopped by user")
                    break

            # Determine which persona responds
            if self._turn_count % 2 == 1:
                # Odd turn: Persona B responds
                responding_persona = self.persona_b
                other_persona = self.persona_a
            else:
                # Even turn: Persona A responds
                responding_persona = self.persona_a
                other_persona = self.persona_b

            self._execute_turn(responding_persona, other_persona)

        if self._turn_count >= self._max_turns:
            console.print_info(f"\n⏱️  Maximum turns ({self._max_turns}) reached")

        console.print_info(f"\n{'='*80}")
        console.print_info(f"🎭 Role-Playing Session Ended")
        console.print_info(f"Total turns: {self._turn_count}")
        console.print_info(f"{'='*80}\n")

    def _execute_turn(
        self,
        responding_persona: Persona,
        other_persona: Persona,
        initial_message: Optional[str] = None,
        is_first_turn: bool = False
    ) -> None:
        """
        Execute a single turn in the conversation.

        Args:
            responding_persona: The persona that will respond
            other_persona: The other persona in the conversation
            initial_message: Message to respond to (for first turn only)
            is_first_turn: True if this is the first turn
        """
        self._turn_count += 1

        # For first turn, add initial prompt to responding persona's history
        if is_first_turn and initial_message:
            responding_persona.add_to_history('user', initial_message)

        # Generate response
        try:
            response = responding_persona.generate_response(self.llm_client)
        except Exception as e:
            console.print_error(f"Error generating response: {e}")
            return

        # Display the response with colored output
        color = Fore.GREEN if responding_persona == self.persona_a else Fore.YELLOW
        print(f"{color}{responding_persona.name}{Style.RESET_ALL}: {response}\n")

        # Add response to responding persona's history as model response
        responding_persona.add_to_history('model', response)

        # Add the exchange to other persona's history
        if is_first_turn:
            # For first turn, other persona sees both initial prompt and response
            other_persona.add_to_history('user', initial_message)
            other_persona.add_to_history('user', response)
        else:
            # For subsequent turns, add as user message to other persona
            other_persona.add_to_history('user', response)

    def get_full_conversation(self) -> str:
        """
        Get the full conversation as a formatted string.

        Returns:
            str: Formatted conversation history
        """
        lines = [
            f"Role-Playing Session: {self.persona_a.name} & {self.persona_b.name}",
            "=" * 80,
            ""
        ]

        # Reconstruct conversation from persona A's perspective
        history_a = self.persona_a.get_history()
        for i, content in enumerate(history_a):
            role_name = self.persona_a.name if content.role == 'model' else "Other"
            text = content.parts[0].text if content.parts else ""
            lines.append(f"{role_name}: {text}")
            lines.append("")

        return "\n".join(lines)
