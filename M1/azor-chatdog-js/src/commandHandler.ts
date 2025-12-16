/**
 * Command handler for slash commands
 */

import { displayHelp, printError, printInfo, printSuccess } from './cli/console.js';
import { displaySessionList } from './commands/sessionList.js';
import { displaySessionHistory } from './commands/sessionDisplay.js';
import { removeCurrentSession } from './commands/sessionRemove.js';
import { selectSessionInteractive } from './commands/sessionSwitch.js';
import type { SessionManager } from './session/sessionManager.js';

/**
 * Valid slash commands
 */
const VALID_SLASH_COMMANDS = [
  '/exit',
  '/quit',
  '/switch',
  '/help',
  '/session',
  '/pdf',
];

/**
 * Handle a slash command
 * @returns true if should exit, false otherwise
 */
export async function handleCommand(
  userInput: string,
  manager: SessionManager
): Promise<boolean> {
  const parts = userInput.trim().split(/\s+/);
  const command = parts[0].toLowerCase();
  const args = parts.slice(1);

  // Check if it's a valid command
  if (!VALID_SLASH_COMMANDS.some((cmd) => command.startsWith(cmd))) {
    printError(`Unknown command: ${command}`);
    printInfo('Type /help for available commands');
    return false;
  }

  // Handle commands
  switch (command) {
    case '/exit':
    case '/quit':
      printInfo('Do widzenia!');
      return true;

    case '/help':
      displayHelp(manager.getCurrentSession().id);
      return false;

    case '/session':
      handleSessionSubcommand(args, manager);
      return false;

    case '/switch':
      await handleSwitchCommand(args, manager);
      return false;

    case '/pdf':
      printError('PDF export not yet implemented');
      return false;

    default:
      printError(`Unknown command: ${command}`);
      return false;
  }
}

/**
 * Handle /switch command with interactive dropdown
 */
async function handleSwitchCommand(
  args: string[],
  manager: SessionManager
): Promise<void> {
  let sessionId: string | null = null;

  // If session ID provided as argument, use it directly
  if (args.length > 0) {
    sessionId = args[0];
  } else {
    // Show interactive dropdown
    sessionId = await selectSessionInteractive();

    if (!sessionId) {
      // User cancelled or no sessions available
      return;
    }
  }

  // Switch to the selected session
  const result = manager.switchToSession(sessionId);

  if (result.loadSuccessful) {
    const session = result.session;
    const title = session.getTitle();
    const displayName = title || sessionId;

    printSuccess(`Switched to session: ${displayName}`);

    if (result.hasHistory) {
      const tokenInfo = session.getTokenInfo();
      printInfo(
        `Session has ${session.getHistory().length} messages (${tokenInfo.total} tokens)`
      );
    }
  } else {
    printError(`Failed to switch: ${result.error}`);
  }
}

/**
 * Handle /session subcommands
 */
function handleSessionSubcommand(args: string[], manager: SessionManager): void {
  if (args.length === 0) {
    printError('Usage: /session <list|display|new|clear|pop|remove>');
    return;
  }

  const subcommand = args[0].toLowerCase();

  switch (subcommand) {
    case 'list':
      displaySessionList();
      break;

    case 'display':
      displaySessionHistory(manager.getCurrentSession());
      break;

    case 'new':
      const createResult = manager.createNewSession(true);
      printSuccess(`Created new session: ${createResult.session.id}`);
      break;

    case 'clear':
      manager.getCurrentSession().clearHistory();
      printSuccess('Session history cleared');
      break;

    case 'pop':
      if (manager.getCurrentSession().popLastExchange()) {
        printSuccess('Removed last message exchange');
      } else {
        printInfo('No messages to remove');
      }
      break;

    case 'remove':
      removeCurrentSession(manager);
      break;

    default:
      printError(`Unknown subcommand: ${subcommand}`);
      printInfo('Available: list, display, new, clear, pop, remove');
  }
}
