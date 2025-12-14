"""
MCP Session Management Tools
Provides tools for listing, viewing, and deleting AZOR sessions.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


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


def list_sessions() -> str:
    """
    List all AZØR chat sessions with metadata.

    Returns:
        JSON string with sessions metadata
    """
    session_files = get_session_files()

    if not session_files:
        return json.dumps({"sessions": [], "message": "No AZØR sessions found"})

    sessions_metadata = []
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

            if "title" in session_data:
                session_info["title"] = session_data["title"]

            sessions_metadata.append(session_info)
        except Exception as e:
            sessions_metadata.append({
                "file": session_file.name,
                "error": f"Failed to read: {str(e)}"
            })

    return json.dumps({"sessions": sessions_metadata, "count": len(sessions_metadata)}, indent=2, ensure_ascii=False)


def get_session(session_id: str) -> str:
    """
    Get detailed metadata and content for a specific AZØR session.

    Args:
        session_id: The session ID to retrieve

    Returns:
        JSON string with session details
    """
    session_files = get_session_files()
    target_file = None

    # Find the session file by ID
    for f in session_files:
        if f.name.startswith(session_id):
            target_file = f
            break

    if not target_file:
        return json.dumps({"error": "Session not found"})

    session_data = load_session(target_file)
    session_data["last_modified"] = get_file_mtime(target_file).isoformat()

    return json.dumps(session_data, indent=2, ensure_ascii=False)


def delete_sessions(session_ids: List[str] = None, last_hours: int = None,
                   last_days: int = None, confirm: bool = False) -> str:
    """
    Delete AZØR session files based on criteria.

    Args:
        session_ids: List of session IDs to delete
        last_hours: Delete sessions modified in the last N hours
        last_days: Delete sessions modified in the last N days
        confirm: Must be True to actually delete (safety check)

    Returns:
        JSON string with deletion results
    """
    if not confirm:
        return json.dumps({"error": "Must set 'confirm: true' to delete sessions (safety check)"})

    now = datetime.now()
    files_to_delete: List[Path] = []

    # Filter by last_hours or last_days
    if last_hours is not None or last_days is not None:
        for f in get_session_files():
            mtime = get_file_mtime(f)
            if last_hours is not None and now - mtime < timedelta(hours=last_hours):
                files_to_delete.append(f)
            elif last_days is not None and now - mtime < timedelta(days=last_days):
                files_to_delete.append(f)
    # Filter by session_ids
    elif session_ids:
        for f in get_session_files():
            try:
                session_data = load_session(f)
                sid = session_data.get("session_id")
                if sid in session_ids:
                    files_to_delete.append(f)
            except Exception:
                pass

    if not files_to_delete:
        return json.dumps({"deleted_count": 0, "message": "No sessions found matching the criteria"})

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
            errors.append(f"Error deleting {file_path.name}: {e}")

    result = {
        "deleted_count": len(deleted),
        "deleted": deleted,
        "status": "Completed with errors" if errors else "Completed successfully"
    }

    if errors:
        result["errors"] = errors

    return json.dumps(result, indent=2, ensure_ascii=False)


# Define tools for Gemini function calling
TOOLS_DEFINITIONS = [
    {
        "name": "list_sessions",
        "description": "Lists all AZØR chat sessions from ~/.azor/*.json with their update dates and basic metadata. Use this to see what sessions exist before performing operations on them.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_session",
        "description": "Returns full metadata and content (conversation history) for a specific AZØR session. Use this to view details of a particular session.",
        "parameters": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The UUID session ID (e.g., '0432f3da-42fd-40c7-8b7d-52afaabf9ca5')"
                }
            },
            "required": ["session_id"]
        }
    },
    {
        "name": "delete_sessions",
        "description": "Deletes one or more AZØR session files. Can filter by session IDs or time period (e.g., last 24 hours). ALWAYS requires confirm=true for safety.",
        "parameters": {
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
                    "description": "Must be set to true to actually delete files (safety check)"
                }
            },
            "required": ["confirm"]
        }
    }
]


# Map function names to actual functions
TOOLS_MAP = {
    "list_sessions": list_sessions,
    "get_session": get_session,
    "delete_sessions": delete_sessions
}
