from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional


class Storage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self):
        self.conn = sqlite3.connect(str(self.path))
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self._init()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def _init(self) -> None:
        assert self.conn is not None
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fetch_cache (
                url TEXT PRIMARY KEY,
                status INTEGER,
                checked_at TEXT
            )
            """
        )
        self.conn.commit()
