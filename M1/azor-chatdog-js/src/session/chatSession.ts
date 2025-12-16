/**
 * ChatSession - Manages a single chat session
 */

import { v4 as uuidv4 } from 'uuid';
import type { Assistant } from '../assistant/assistant.js';
import type {
  ILLMClient,
  ILLMChatSession,
  Message,
  LLMResponse,
  TokenInfo,
  Result,
} from '../types/index.js';
import { loadSessionHistory, saveSessionHistory } from '../files/sessionFiles.js';
import { appendToWAL } from '../files/wal.js';
import { MAX_CONTEXT_TOKENS } from '../files/config.js';
import { GeminiLLMClient } from '../llm/geminiClient.js';
import { LlamaClient } from '../llm/llamaClient.js';
import { CLARIFICATION_TOOL_DEFINITION, CLARIFICATION_TOOLS_MAP } from '../tools/clarificationTool.js';

/**
 * Engine mapping for LLM client selection
 */
const ENGINE_MAPPING: Record<string, typeof GeminiLLMClient | typeof LlamaClient> = {
  LLAMA_CPP: LlamaClient,
  GEMINI: GeminiLLMClient,
};

/**
 * Get the selected LLM client based on ENGINE environment variable
 */
function getSelectedLLMClient(): ILLMClient {
  const engine = (process.env.ENGINE || 'GEMINI').toUpperCase();
  const SelectedClientClass = ENGINE_MAPPING[engine] || GeminiLLMClient;
  return SelectedClientClass.fromEnvironment();
}

/**
 * ChatSession class - represents and manages a single chat session
 */
export class ChatSession {
  private sessionId: string;
  private history: Message[] = [];
  private llmClient: ILLMClient;
  private llmChatSession: ILLMChatSession;
  private assistant: Assistant;
  private title?: string;

  constructor(assistant: Assistant, sessionId?: string, history?: Message[], title?: string) {
    this.sessionId = sessionId || uuidv4();
    this.assistant = assistant;
    this.history = history || [];
    this.title = title;

    // Initialize LLM client
    this.llmClient = getSelectedLLMClient();

    // Create chat session with tools support for Gemini
    if (this.llmClient instanceof GeminiLLMClient) {
      this.llmChatSession = this.llmClient.createChatSession(
        assistant.systemPrompt,
        this.history,
        undefined,
        [CLARIFICATION_TOOL_DEFINITION],
        CLARIFICATION_TOOLS_MAP
      );
    } else {
      // LlamaClient doesn't support tools yet
      this.llmChatSession = this.llmClient.createChatSession(
        assistant.systemPrompt,
        this.history
      );
    }
  }

  /**
   * Load session from file
   */
  static loadFromFile(
    assistant: Assistant,
    sessionId: string
  ): Result<ChatSession, string> {
    const result = loadSessionHistory(sessionId);

    if (!result.success) {
      return { success: false, error: result.error };
    }

    const { history, title } = result.value;
    const session = new ChatSession(assistant, sessionId, history, title);

    return { success: true, value: session };
  }

  /**
   * Save session to file
   */
  saveToFile(): Result<boolean, string> {
    return saveSessionHistory(
      this.sessionId,
      this.history,
      this.assistant.systemPrompt,
      this.llmClient.getModelName(),
      this.title
    );
  }

  /**
   * Send a message and get response
   */
  async sendMessage(text: string): Promise<LLMResponse> {
    // Send message to LLM
    const response = await this.llmChatSession.sendMessage(text);

    // Sync history from LLM session (it updates internally)
    this.history = this.llmChatSession.getHistory();

    // Log to WAL
    const totalTokens = this.countTokens();
    appendToWAL(
      this.sessionId,
      text,
      response.text,
      totalTokens,
      this.llmClient.getModelName()
    );

    return response;
  }

  /**
   * Get conversation history
   */
  getHistory(): Message[] {
    return this.history;
  }

  /**
   * Clear all history
   */
  clearHistory(): void {
    this.history = [];
    // Recreate chat session with empty history
    if (this.llmClient instanceof GeminiLLMClient) {
      this.llmChatSession = this.llmClient.createChatSession(
        this.assistant.systemPrompt,
        [],
        undefined,
        [CLARIFICATION_TOOL_DEFINITION],
        CLARIFICATION_TOOLS_MAP
      );
    } else {
      this.llmChatSession = this.llmClient.createChatSession(
        this.assistant.systemPrompt,
        []
      );
    }
  }

  /**
   * Remove last user-assistant exchange
   */
  popLastExchange(): boolean {
    if (this.history.length < 2) {
      return false;
    }

    // Remove last two messages (user + assistant)
    this.history.splice(this.history.length - 2, 2);

    // Recreate chat session with updated history
    if (this.llmClient instanceof GeminiLLMClient) {
      this.llmChatSession = this.llmClient.createChatSession(
        this.assistant.systemPrompt,
        this.history,
        undefined,
        [CLARIFICATION_TOOL_DEFINITION],
        CLARIFICATION_TOOLS_MAP
      );
    } else {
      this.llmChatSession = this.llmClient.createChatSession(
        this.assistant.systemPrompt,
        this.history
      );
    }

    return true;
  }

  /**
   * Count total tokens in history
   */
  countTokens(): number {
    return this.llmClient.countHistoryTokens(this.history);
  }

  /**
   * Check if session is empty
   */
  isEmpty(): boolean {
    return this.history.length === 0;
  }

  /**
   * Get remaining tokens in context
   */
  getRemainingTokens(): number {
    const used = this.countTokens();
    return MAX_CONTEXT_TOKENS - used;
  }

  /**
   * Get token information
   */
  getTokenInfo(): TokenInfo {
    const total = this.countTokens();
    const remaining = this.getRemainingTokens();
    return {
      total,
      remaining,
      max: MAX_CONTEXT_TOKENS,
    };
  }

  /**
   * Get assistant name
   */
  get assistantName(): string {
    return this.assistant.name;
  }

  /**
   * Get session ID
   */
  get id(): string {
    return this.sessionId;
  }

  /**
   * Get model name
   */
  get modelName(): string {
    return this.llmClient.getModelName();
  }

  /**
   * Get session title
   */
  getTitle(): string | undefined {
    return this.title;
  }

  /**
   * Set session title
   */
  setTitle(title: string): void {
    this.title = title;
  }
}
