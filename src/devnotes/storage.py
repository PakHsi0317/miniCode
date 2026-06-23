import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(".devnotes/index.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    path       TEXT UNIQUE NOT NULL,
    filename   TEXT NOT NULL,
    extension  TEXT NOT NULL,
    line_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS keywords (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id   INTEGER NOT NULL,
    keyword   TEXT NOT NULL,
    frequency INTEGER NOT NULL,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_files_filename    ON files(filename);
CREATE INDEX IF NOT EXISTS idx_keywords_keyword  ON keywords(keyword);
CREATE INDEX IF NOT EXISTS idx_keywords_file_id  ON keywords(file_id);
"""


def connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open (or create) the SQLite database and return a connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def upsert_file(
    conn: sqlite3.Connection,
    path: Path,
    line_count: int,
    keywords: list[tuple[str, int]],
) -> int:
    """Insert or update one file plus its keywords. Returns the file id."""
    row = conn.execute("SELECT id FROM files WHERE path = ?", (str(path),)).fetchone()

    if row is None:
        cur = conn.execute(
            """INSERT INTO files (path, filename, extension, line_count)
               VALUES (?, ?, ?, ?)""",
            (str(path), path.name, path.suffix, line_count),
        )
        file_id = cur.lastrowid
    else:
        file_id = row["id"]
        conn.execute(
            """UPDATE files SET filename = ?, extension = ?, line_count = ?
               WHERE id = ?""",
            (path.name, path.suffix, line_count, file_id),
        )

    conn.execute("DELETE FROM keywords WHERE file_id = ?", (file_id,))
    conn.executemany(
        "INSERT INTO keywords (file_id, keyword, frequency) VALUES (?, ?, ?)",
        [(file_id, kw, freq) for kw, freq in keywords],
    )
    return file_id


def search_files(conn: sqlite3.Connection, query: str) -> list[sqlite3.Row]:
    """Search files by keyword content. Ranked by total matched frequency."""
    return conn.execute(
        """SELECT f.path, f.filename, f.extension, f.line_count,
                  SUM(k.frequency) AS score,
                  COUNT(DISTINCT k.keyword) AS matched_keywords
           FROM files f
           JOIN keywords k ON f.id = k.file_id
           WHERE k.keyword LIKE ?
           GROUP BY f.id
           ORDER BY score DESC, f.filename""",
        (f"%{query.lower()}%",),
    ).fetchall()


def count_files(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]


def count_keywords(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM keywords").fetchone()[0]
