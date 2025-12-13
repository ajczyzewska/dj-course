"""AZØR MCP Server implementation."""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Dict

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio


AZOR_DIR = Path.home() / ".azor"


def get_session_files() -> List[Path]:
    """Get all AZØR session files (*.json, excluding azor-wal.json)."""
    if not AZOR_DIR.exists():
        return []

    return [
        f for f in AZOR_DIR.glob("*.json")
        if f.name != "azor-wal.json" and f.name.endswith("-log.json")
    ]


def load_session(session_file: Path) -> Dict[str, Any]:
    """Load session data from JSON file."""
    with open(session_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_file_mtime(file_path: Path) -> datetime:
    """Get file modification time."""
    return datetime.fromtimestamp(file_path.stat().st_mtime)


app = Server("azor-mcp-server")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available AZØR MCP tools."""
    return [
        Tool(
            name="list_sessions",
            description="Lists all AZØR chat sessions from ~/.azor/*.json with their update dates and basic metadata",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_session",
            description="Returns full metadata and content (conversation history) for a specific AZØR session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The UUID session ID (e.g., '0432f3da-42fd-40c7-8b7d-52afaabf9ca5')"
                    }
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="delete_sessions",
            description="Deletes one or more AZØR session files. Can filter by session IDs or time period (e.g., last 24 hours)",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of session IDs to delete (optional if using time filter)"
                    },
                    "last_hours": {
                        "type": "number",
                        "description": "Delete sessions modified in the last N hours (optional)"
                    },
                    "last_days": {
                        "type": "number",
                        "description": "Delete sessions modified in the last N days (optional)"
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Must be set to true to actually delete files (safety check)",
                        "default": False
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="ask_for_clarification",
            description="Ask the user for clarification when their question is too vague or ambiguous. Use this when you need more specific information to provide a good answer.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The clarifying question to ask the user"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context explaining why clarification is needed"
                    }
                },
                "required": ["question"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls."""

    if name == "list_sessions":
        return await handle_list_sessions()
    elif name == "get_session":
        return await handle_get_session(arguments)
    elif name == "delete_sessions":
        return await handle_delete_sessions(arguments)
    elif name == "ask_for_clarification":
        return await handle_ask_for_clarification(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_list_sessions() -> List[TextContent]:
    """Handle list_sessions tool call."""
    session_files = get_session_files()

    if not session_files:
        return [TextContent(
            type="text",
            text="No AZØR sessions found in ~/.azor/"
        )]

    sessions_info = []
    for session_file in sorted(session_files, key=get_file_mtime, reverse=True):
        try:
            session_data = load_session(session_file)
            mtime = get_file_mtime(session_file)

            session_info = {
                "session_id": session_data.get("session_id", "unknown"),
                "file": session_file.name,
                "last_modified": mtime.isoformat(),
                "model": session_data.get("model", "unknown"),
                "message_count": len(session_data.get("history", []))
            }

            # Add title if available (from M2 homework)
            if "title" in session_data:
                session_info["title"] = session_data["title"]

            sessions_info.append(session_info)
        except Exception as e:
            sessions_info.append({
                "file": session_file.name,
                "error": f"Failed to read: {str(e)}"
            })

    result_text = f"Found {len(sessions_info)} AZØR session(s):\n\n"
    result_text += json.dumps(sessions_info, indent=2, ensure_ascii=False)

    return [TextContent(type="text", text=result_text)]


async def handle_get_session(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_session tool call."""
    session_id = arguments.get("session_id")

    if not session_id:
        return [TextContent(
            type="text",
            text="Error: session_id parameter is required"
        )]

    # Find session file
    session_file = AZOR_DIR / f"{session_id}-log.json"

    if not session_file.exists():
        return [TextContent(
            type="text",
            text=f"Error: Session '{session_id}' not found in ~/.azor/"
        )]

    try:
        session_data = load_session(session_file)
        mtime = get_file_mtime(session_file)

        result = {
            "session_id": session_data.get("session_id"),
            "file": session_file.name,
            "last_modified": mtime.isoformat(),
            "metadata": {
                "model": session_data.get("model"),
                "system_role": session_data.get("system_role"),
                "title": session_data.get("title"),
            },
            "history": session_data.get("history", []),
            "message_count": len(session_data.get("history", []))
        }

        result_text = f"Session: {session_id}\n\n"
        result_text += json.dumps(result, indent=2, ensure_ascii=False)

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error reading session: {str(e)}"
        )]


async def handle_delete_sessions(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle delete_sessions tool call."""
    session_ids = arguments.get("session_ids", [])
    last_hours = arguments.get("last_hours")
    last_days = arguments.get("last_days")
    confirm = arguments.get("confirm", False)

    if not confirm:
        return [TextContent(
            type="text",
            text="Error: Must set 'confirm: true' to delete sessions (safety check)"
        )]

    # Determine which sessions to delete
    files_to_delete = []

    if session_ids:
        # Delete specific session IDs
        for session_id in session_ids:
            session_file = AZOR_DIR / f"{session_id}-log.json"
            if session_file.exists():
                files_to_delete.append(session_file)

    if last_hours is not None or last_days is not None:
        # Delete by time period
        cutoff_time = datetime.now()
        if last_hours is not None:
            cutoff_time -= timedelta(hours=last_hours)
        if last_days is not None:
            cutoff_time -= timedelta(days=last_days)

        for session_file in get_session_files():
            mtime = get_file_mtime(session_file)
            if mtime >= cutoff_time:
                if session_file not in files_to_delete:
                    files_to_delete.append(session_file)

    if not files_to_delete:
        return [TextContent(
            type="text",
            text="No sessions found matching the criteria"
        )]

    # Delete files
    deleted = []
    errors = []

    for file_path in files_to_delete:
        try:
            session_data = load_session(file_path)
            session_id = session_data.get("session_id", "unknown")
            file_path.unlink()
            deleted.append({
                "session_id": session_id,
                "file": file_path.name
            })
        except Exception as e:
            errors.append({
                "file": file_path.name,
                "error": str(e)
            })

    result = {
        "deleted_count": len(deleted),
        "deleted_sessions": deleted
    }

    if errors:
        result["errors"] = errors

    result_text = f"Deleted {len(deleted)} session(s)\n\n"
    result_text += json.dumps(result, indent=2, ensure_ascii=False)

    return [TextContent(type="text", text=result_text)]


async def handle_ask_for_clarification(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle ask_for_clarification tool call.

    This tool allows the AI agent to ask the user for more specific information
    when the original question is too vague or ambiguous.
    """
    question = arguments.get("question")
    context = arguments.get("context", "")

    if not question:
        return [TextContent(
            type="text",
            text="Error: question parameter is required"
        )]

    # Format the clarification request
    clarification_text = "🤔 **Prośba o doprecyzowanie pytania**\n\n"

    if context:
        clarification_text += f"**Kontekst:** {context}\n\n"

    clarification_text += f"**Pytanie:** {question}\n\n"
    clarification_text += "---\n"
    clarification_text += "**Instrukcja:** Proszę podać odpowiedź na powyższe pytanie doprecyzowujące.\n"
    clarification_text += "Agent AI czeka na Twoją odpowiedź, aby móc kontynuować.\n\n"

    # Print to stderr so it doesn't interfere with MCP protocol on stdout
    print(clarification_text, file=sys.stderr)
    print("\n💬 Twoja odpowiedź: ", file=sys.stderr, end='', flush=True)

    # Read user input from stdin
    # Note: In MCP context, this will block until user provides input
    try:
        user_response = input().strip()

        if not user_response:
            return [TextContent(
                type="text",
                text="User provided empty response to clarification request."
            )]

        result = {
            "clarification_question": question,
            "context": context,
            "user_response": user_response
        }

        result_text = "User clarification received:\n\n"
        result_text += json.dumps(result, indent=2, ensure_ascii=False)

        return [TextContent(type="text", text=result_text)]

    except EOFError:
        return [TextContent(
            type="text",
            text="Error: Could not read user input (EOF)"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error reading user clarification: {str(e)}"
        )]


async def main():
    """Run the AZØR MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
