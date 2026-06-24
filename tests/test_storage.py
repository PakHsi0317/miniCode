import sqlite3
from pathlib import Path

import pytest

from devnotes.storage import (
    SCHEMA,
    connect,
    count_files,
    count_keywords,
    search_files,
    upsert_file,
)


@pytest.fixture
def db():
    """Fresh in-memory database for each test."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    yield conn
    conn.close()


def test_upsert_file_inserts_new(db):
    upsert_file(db, Path("/x/a.py"), 10, [("hello", 2), ("world", 1)])
    assert count_files(db) == 1
    assert count_keywords(db) == 2


def test_upsert_file_is_idempotent(db):
    upsert_file(db, Path("/x/a.py"), 10, [("hello", 2)])
    upsert_file(db, Path("/x/a.py"), 10, [("hello", 2)])

    assert count_files(db) == 1
    assert count_keywords(db) == 1


def test_upsert_file_preserves_id(db):
    fid1 = upsert_file(db, Path("/x/a.py"), 10, [("hello", 2)])
    fid2 = upsert_file(db, Path("/x/a.py"), 20, [("world", 5)])

    assert fid1 == fid2


def test_upsert_file_replaces_keywords(db):
    upsert_file(db, Path("/x/a.py"), 10, [("hello", 2)])
    upsert_file(db, Path("/x/a.py"), 10, [("world", 5)])

    rows = db.execute("SELECT keyword FROM keywords").fetchall()
    assert {r["keyword"] for r in rows} == {"world"}


def test_search_files_returns_ranked_by_score(db):
    upsert_file(db, Path("/x/a.py"), 10, [("hello", 5)])
    upsert_file(db, Path("/x/b.py"), 20, [("hello", 10)])
    upsert_file(db, Path("/x/c.py"), 30, [("other", 1)])

    results = search_files(db, "hello")

    assert len(results) == 2
    assert results[0]["score"] == 10
    assert results[1]["score"] == 5


def test_search_files_returns_empty_for_no_match(db):
    upsert_file(db, Path("/x/a.py"), 10, [("hello", 5)])
    assert search_files(db, "missing") == []


def test_search_files_case_insensitive(db):
    upsert_file(db, Path("/x/a.py"), 10, [("hello", 5)])
    results = search_files(db, "HELLO")
    assert len(results) == 1


def test_search_files_partial_match(db):
    upsert_file(db, Path("/x/a.py"), 10, [("database", 5), ("data", 3)])
    results = search_files(db, "data")

    assert len(results) == 1
    assert results[0]["score"] == 8
    assert results[0]["matched_keywords"] == 2


def test_cascade_delete_removes_keywords(db):
    upsert_file(db, Path("/x/a.py"), 10, [("hello", 2), ("world", 3)])
    db.execute("DELETE FROM files WHERE path = ?", (str(Path("/x/a.py")),))

    assert count_files(db) == 0
    assert count_keywords(db) == 0


def test_path_uniqueness(db):
    upsert_file(db, Path("/x/a.py"), 10, [])
    upsert_file(db, Path("/x/a.py"), 20, [])

    rows = db.execute("SELECT * FROM files").fetchall()
    assert len(rows) == 1
    assert rows[0]["line_count"] == 20


def test_connect_creates_schema(tmp_path):
    db_path = tmp_path / "test.db"
    conn = connect(db_path)
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = {row["name"] for row in tables}
        assert "files" in table_names
        assert "keywords" in table_names
    finally:
        conn.close()


def test_connect_enables_foreign_keys(tmp_path):
    db_path = tmp_path / "test.db"
    conn = connect(db_path)
    try:
        fk_status = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        assert fk_status == 1
    finally:
        conn.close()


def test_connect_creates_parent_directory(tmp_path):
    db_path = tmp_path / "nested" / "deep" / "test.db"
    conn = connect(db_path)
    try:
        assert db_path.exists()
        assert db_path.parent.is_dir()
    finally:
        conn.close()
