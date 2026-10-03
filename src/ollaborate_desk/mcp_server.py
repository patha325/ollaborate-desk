"""Read-only stdio MCP companion for local clients such as Odysseus."""
from __future__ import annotations

import json

from . import app as desk


def search_files(query: str) -> dict:
    """Search the indexed local documents and return short cited excerpts."""
    if not query.strip() or len(query) > 2000:
        raise ValueError("query must contain 1 to 2000 nonblank characters")
    if not desk.SOURCE.is_dir():
        raise ValueError("Configured source folder does not exist")
    answer = desk.knowledge().ask(query)
    return {
        "answer": str(answer.text)[:4000],
        "warning": str(answer.warning)[:500] if answer.warning else None,
        "evidence": [
            {"path": str(c.location), "excerpt": str(c.excerpt)[:1000], "score": c.score}
            for c in answer.citations[:6]
        ],
    }


def list_drafts(limit: int = 10) -> list[dict]:
    """List recent Desk tasks without exposing document excerpts or draft bodies."""
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    with desk.connect() as conn:
        rows = conn.execute(
            "SELECT id, created, instruction, status FROM tasks ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def get_draft(task_id: int) -> dict:
    """Read a Desk draft and its source citations by task ID."""
    if task_id < 1:
        raise ValueError("task_id must be positive")
    with desk.connect() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if row is None:
        raise ValueError("Task not found")
    return dict(row) | {"evidence": json.loads(row["evidence"])}


def create_server():
    # Imported only by the optional entry point; ordinary Desk needs no MCP SDK.
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("Ollaborate Desk")
    server.tool()(search_files)
    server.tool()(list_drafts)
    server.tool()(get_draft)
    return server


def main():
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
