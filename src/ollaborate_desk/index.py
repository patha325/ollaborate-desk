"""A small replaceable retrieval adapter backed by SQLite FTS5."""
from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

EXTENSIONS = {".txt", ".md", ".csv", ".json", ".pdf"}


def extract(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        return "\n".join(f"[Page {i}]\n{page.extract_text() or ''}" for i, page in enumerate(PdfReader(str(path)).pages, 1))
    if path.suffix.lower() == ".json":
        return json.dumps(json.loads(path.read_text(encoding="utf-8")), ensure_ascii=False, indent=2)
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return "\n".join(" | ".join(row) for row in csv.reader(stream))
    return path.read_text(encoding="utf-8")


class FileIndex:
    def __init__(self, db: Path, source: Path):
        self.db = db
        self.source = source.resolve()
        self.db.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(path UNINDEXED, body)")

    def connect(self):
        return sqlite3.connect(self.db)

    def rebuild(self) -> dict:
        files, chunks, errors = 0, 0, []
        records = []
        for path in sorted(self.source.rglob("*")):
            if not path.is_file() or path.is_symlink() or path.suffix.lower() not in EXTENSIONS:
                continue
            try:
                if path.stat().st_size > 20 * 1024 * 1024:
                    raise ValueError("file exceeds 20 MiB limit")
                content = extract(path)
                parts = [content[i:i + 1800] for i in range(0, len(content), 1500)]
                records.extend((str(path.relative_to(self.source)), part) for part in parts if part.strip())
                files += 1
                chunks += len(parts)
            except Exception as exc:
                errors.append(f"{path.relative_to(self.source)}: {exc}")
        with self.connect() as conn:
            conn.execute("DELETE FROM chunks")
            conn.executemany("INSERT INTO chunks(path, body) VALUES (?, ?)", records)
        return {"files": files, "chunks": chunks, "errors": errors}

    def search(self, query: str, limit: int = 6) -> list[dict]:
        import re

        terms = re.findall(r"[^\W_]+", query, flags=re.UNICODE)[:12]
        if not terms:
            return []
        expression = " OR ".join('"' + term.replace('"', '""') + '"' for term in terms)
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT path, body FROM chunks WHERE chunks MATCH ? ORDER BY rank LIMIT ?",
                (expression, min(max(limit, 1), 12)),
            ).fetchall()
        return [{"path": path, "excerpt": body[:1000]} for path, body in rows]
