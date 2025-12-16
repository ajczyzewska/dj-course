/**
 * Session switch command with interactive dropdown
 */

import { listSessions } from '../files/sessionFiles.js';
import { selectFromList } from '../cli/prompt.js';
import { printHelp, printError } from '../cli/console.js';

/**
 * Display a formatted session choice
 */
function formatSessionChoice(session: {
  session_id: string;
  title?: string;
  message_count: number;
  last_modified: Date;
  model: string;
}): string {
  const title = session.title || session.session_id;
  const date = session.last_modified.toLocaleString('pl-PL', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
  return `${title} (${session.message_count} msg, ${date}, ${session.model})`;
}

/**
 * Show interactive dropdown to select a session
 * @returns Selected session ID or null if cancelled
 */
export async function selectSessionInteractive(): Promise<string | null> {
  const sessions = listSessions();

  if (sessions.length === 0) {
    printHelp('\nBrak zapisanych sesji.');
    return null;
  }

  if (sessions.length === 1) {
    printError('Tylko jedna sesja dostępna. Nie można przełączyć.');
    return null;
  }

  // Create choices for inquirer
  const choices = sessions.map((session) => ({
    name: formatSessionChoice(session),
    value: session.session_id,
  }));

  try {
    const selectedId = await selectFromList<string>(
      'Wybierz sesję do przełączenia:',
      choices
    );
    return selectedId;
  } catch (error) {
    // User cancelled (Ctrl+C)
    return null;
  }
}
