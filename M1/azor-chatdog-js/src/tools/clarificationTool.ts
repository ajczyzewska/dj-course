/**
 * Clarification Tool
 * Allows the model to ask for clarification when user's question is not precise enough.
 */

import { getUserInput } from '../cli/prompt.js';
import { printAssistant, printInfo } from '../cli/console.js';

/**
 * Ask the user for clarification when the question is not precise enough.
 *
 * This tool allows the model to interactively request more details from the user
 * when their initial question is ambiguous, lacks context, or needs refinement.
 *
 * @param question - The clarifying question to ask the user
 * @returns The user's answer/clarification
 *
 * @example
 * Model receives: "zrób to"
 * Model calls: askForClarification("Co dokładnie chcesz, żebym zrobił?")
 * User responds: "Napisz funkcję do sortowania listy"
 * Model continues with full context
 */
export async function askForClarification(question: string): Promise<string> {
  // Display the clarification request
  printInfo('🤔 AZØR potrzebuje doprecyzowania...');
  printAssistant(`\n${question}`);

  // Get user's response
  const userResponse = await getUserInput();

  if (!userResponse) {
    return 'Użytkownik nie podał odpowiedzi.';
  }

  return userResponse;
}

/**
 * Tool definition for Gemini function calling
 */
export interface ToolDefinition {
  name: string;
  description: string;
  parameters: {
    type: string;
    properties: Record<string, any>;
    required: string[];
  };
}

export const CLARIFICATION_TOOL_DEFINITION: ToolDefinition = {
  name: 'ask_for_clarification',
  description: `Use this tool when the user's question or request is unclear, ambiguous, or lacks necessary details.

Call this function when you need to:
- Understand vague or incomplete requests (e.g., "zrób to", "napraw błąd")
- Clarify which option the user prefers when multiple valid approaches exist
- Get specific parameters or details that are missing
- Resolve ambiguity in the user's intent

DO NOT use this for simple questions you can answer directly. Use it only when you genuinely need more information to provide a helpful response.

The user will see your clarifying question and provide an answer, which will be returned to you.`,
  parameters: {
    type: 'object',
    properties: {
      question: {
        type: 'string',
        description:
          "The clarifying question to ask the user. Be specific and helpful. Examples: 'Którą funkcję chcesz, żebym poprawił?', 'Czy mam użyć podejścia A czy B?', 'Jakie dane wejściowe powinna przyjmować ta funkcja?'",
      },
    },
    required: ['question'],
  },
};

/**
 * Map function name to actual function
 */
export const CLARIFICATION_TOOLS_MAP: Record<string, (args: any) => Promise<string>> = {
  ask_for_clarification: async (args: { question: string }) => askForClarification(args.question),
};
