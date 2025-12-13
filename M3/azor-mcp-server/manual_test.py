#!/usr/bin/env python3
"""Manual test script for AZØR MCP Server tools."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from azor_mcp.server import (
    handle_list_sessions,
    handle_get_session,
    handle_delete_sessions,
)


async def test_list_sessions():
    """Test list_sessions tool."""
    print("=" * 60)
    print("TEST 1: list_sessions")
    print("=" * 60)
    result = await handle_list_sessions()
    print(result[0].text)
    print()


async def test_get_session():
    """Test get_session tool."""
    print("=" * 60)
    print("TEST 2: get_session")
    print("=" * 60)

    # First get a session ID
    sessions = await handle_list_sessions()
    import json
    sessions_data = json.loads(sessions[0].text.split("\n\n", 1)[1])

    if sessions_data:
        session_id = sessions_data[0]["session_id"]
        print(f"Testing with session_id: {session_id}")
        result = await handle_get_session({"session_id": session_id})
        print(result[0].text[:500] + "..." if len(result[0].text) > 500 else result[0].text)
    else:
        print("No sessions found to test with")
    print()


async def test_delete_sessions_dry_run():
    """Test delete_sessions without confirm (should fail)."""
    print("=" * 60)
    print("TEST 3: delete_sessions (dry run - should fail)")
    print("=" * 60)
    result = await handle_delete_sessions({
        "last_hours": 24,
        "confirm": False
    })
    print(result[0].text)
    print()


async def main():
    """Run all tests."""
    print("\n🧪 AZØR MCP Server - Manual Tests\n")

    await test_list_sessions()
    await test_get_session()
    await test_delete_sessions_dry_run()

    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\nNote: To test actual deletion, use:")
    print("  - delete_sessions with confirm=True")
    print("  - Or use mcp-inspector for interactive testing")


if __name__ == "__main__":
    asyncio.run(main())
