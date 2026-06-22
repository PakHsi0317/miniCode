import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(".devnotes/index.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    path      TEXT UNIQUE NOT NULL,
    filename  TEXT NOT NULL,
    extension TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_files_filename ON files(filename);
"""


def connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open (or create) the SQLite database and return a connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def upsert_file(conn: sqlite3.Connection, path: Path) -> int:
    """Insert or update one file row. Returns the row id."""
    cur = conn.execute(
        "INSERT OR REPLACE INTO files (path, filename, extension) VALUES (?, ?, ?)",
        (str(path), path.name, path.suffix),
    )
    return cur.lastrowid


def search_files(conn: sqlite3.Connection, query: str) -> list[sqlite3.Row]:
    """Return all rows whose filename contains query (case-insensitive)."""
    return conn.execute(
        "SELECT * FROM files WHERE filename LIKE ? ORDER BY filename",
        (f"%{query}%",),
    ).fetchall()


def count_files(conn: sqlite3.Connection) -> int:
    """Return the total number of indexed files."""
    return conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
