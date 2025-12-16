/**
 * Google Gemini API LLM Client
 */

import { GoogleGenerativeAI, Content, FunctionCall } from '@google/generative-ai';
import type {
  ILLMClient,
  ILLMChatSession,
  Message,
  LLMResponse,
  ToolDefinition,
} from '../types/index.js';
import { validateGeminiConfig } from './geminiValidation.js';
import { printInfo, printError } from '../cli/console.js';

/**
 * Wrapper for Gemini chat session to provide universal interface
 */
class GeminiChatSessionWrapper implements ILLMChatSession {
  private geminiSession: any;
  private history: Message[] = [];
  private toolsMap?: Record<string, (args: any) => Promise<string>>;

  constructor(
    geminiSession: any,
    initialHistory?: Message[],
    toolsMap?: Record<string, (args: any) => Promise<string>>
  ) {
    this.geminiSession = geminiSession;
    this.history = initialHistory || [];
    this.toolsMap = toolsMap;
  }

  async sendMessage(text: string): Promise<LLMResponse> {
    const result = await this.geminiSession.sendMessage(text);
    const response = result.response;

    // Check for function calls
    const functionCalls = this.extractFunctionCalls(response);

    if (functionCalls.length > 0 && this.toolsMap) {
      // Handle function calls
      return await this.handleFunctionCalls(functionCalls);
    }

    const responseText = response.text();

    // Add to history
    this.history.push({
      role: 'user',
      parts: [{ text }],
    });
    this.history.push({
      role: 'model',
      parts: [{ text: responseText }],
    });

    return { text: responseText };
  }

  private extractFunctionCalls(response: any): FunctionCall[] {
    const functionCalls: FunctionCall[] = [];

    if (response.candidates && response.candidates.length > 0) {
      const candidate = response.candidates[0];
      if (candidate.content && candidate.content.parts) {
        for (const part of candidate.content.parts) {
          if (part.functionCall) {
            functionCalls.push(part.functionCall);
          }
        }
      }
    }

    return functionCalls;
  }

  private async handleFunctionCalls(functionCalls: FunctionCall[]): Promise<LLMResponse> {
    for (const functionCall of functionCalls) {
      const functionName = functionCall.name;
      const functionArgs = functionCall.args || {};

      printInfo(`🔧 Wywołanie narzędzia: ${functionName}(${JSON.stringify(functionArgs)})`);

      if (this.toolsMap && functionName in this.toolsMap) {
        try {
          const toolFunction = this.toolsMap[functionName];
          const result = await toolFunction(functionArgs);
          printInfo(`✅ Narzędzie ${functionName} wykonane`);

          // Send function result back to the model
          const functionResponse = {
            functionResponse: {
              name: functionName,
              response: { result },
            },
          };

          const nextResult = await this.geminiSession.sendMessage([functionResponse]);
          const nextResponse = nextResult.response;
          const responseText = nextResponse.text();

          // Update history
          this.history.push({
            role: 'model',
            parts: [{ text: responseText }],
          });

          return { text: responseText };
        } catch (error) {
          const errorMsg = `Error executing ${functionName}: ${(error as Error).message}`;
          printError(`❌ ${errorMsg}`);

          // Send error back to the model
          const errorResponse = {
            functionResponse: {
              name: functionName,
              response: { error: errorMsg },
            },
          };

          const nextResult = await this.geminiSession.sendMessage([errorResponse]);
          const nextResponse = nextResult.response;
          const responseText = nextResponse.text();

          this.history.push({
            role: 'model',
            parts: [{ text: responseText }],
          });

          return { text: responseText };
        }
      } else {
        const errorMsg = `Unknown function: ${functionName}`;
        printError(`❌ ${errorMsg}`);

        const errorResponse = {
          functionResponse: {
            name: functionName,
            response: { error: errorMsg },
          },
        };

        const nextResult = await this.geminiSession.sendMessage([errorResponse]);
        const nextResponse = nextResult.response;
        const responseText = nextResponse.text();

        this.history.push({
          role: 'model',
          parts: [{ text: responseText }],
        });

        return { text: responseText };
      }
    }

    // Fallback (should not reach here)
    return { text: '' };
  }

  getHistory(): Message[] {
    return this.history;
  }
}

/**
 * Gemini LLM Client implementation
 */
export class GeminiLLMClient implements ILLMClient {
  private genAI: GoogleGenerativeAI;
  private modelName: string;
  private apiKey: string;

  constructor(modelName: string, apiKey: string) {
    this.modelName = modelName;
    this.apiKey = apiKey;
    this.genAI = new GoogleGenerativeAI(apiKey);
  }

  /**
   * Create client from environment variables
   */
  static fromEnvironment(): GeminiLLMClient {
    const config = validateGeminiConfig();
    return new GeminiLLMClient(config.modelName, config.geminiApiKey);
  }

  /**
   * Create a chat session
   */
  createChatSession(
    systemInstruction: string,
    history?: Message[],
    thinkingBudget?: number,
    tools?: ToolDefinition[],
    toolsMap?: Record<string, (args: any) => Promise<string>>
  ): ILLMChatSession {
    // Convert universal Message format to Gemini Content format
    const geminiHistory: Content[] = (history || []).map((msg) => ({
      role: msg.role === 'model' ? 'model' : 'user',
      parts: msg.parts.map((part) => ({ text: part.text })),
    }));

    // Create model configuration
    const modelConfig: any = {
      model: this.modelName,
      systemInstruction: {
        role: 'system',
        parts: [{ text: systemInstruction }],
      },
    };

    // Add thinking budget if specified
    if (thinkingBudget !== undefined) {
      modelConfig.generationConfig = {
        thinkingBudget: thinkingBudget,
      };
    }

    // Add tools if specified
    if (tools && tools.length > 0) {
      const functionDeclarations = tools.map((tool) => ({
        name: tool.name,
        description: tool.description,
        parameters: tool.parameters,
      }));

      modelConfig.tools = [{ functionDeclarations }];
    }

    const model = this.genAI.getGenerativeModel(modelConfig);

    const geminiSession = model.startChat({
      history: geminiHistory,
    });

    return new GeminiChatSessionWrapper(geminiSession, history, toolsMap);
  }

  /**
   * Count tokens in history
   */
  countHistoryTokens(history: Message[]): number {
    // Convert to Gemini format and count
    // For now, use rough estimation (will implement actual token counting)
    let totalTokens = 0;
    for (const msg of history) {
      for (const part of msg.parts) {
        // Rough estimation: 1 token ≈ 4 characters
        totalTokens += Math.ceil(part.text.length / 4);
      }
    }
    return totalTokens;
  }

  getModelName(): string {
    return this.modelName;
  }

  isAvailable(): boolean {
    return !!this.apiKey && this.apiKey.length > 0;
  }

  preparingForUseMessage(): string {
    return `Preparing Gemini model ${this.modelName}...`;
  }

  readyForUseMessage(): string {
    const maskedKey = this.apiKey
      ? `${this.apiKey.substring(0, 8)}...${this.apiKey.substring(this.apiKey.length - 4)}`
      : 'NOT SET';
    return `Gemini ${this.modelName} ready (API Key: ${maskedKey})`;
  }
}
