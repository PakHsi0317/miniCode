# devnotes

[![CI](https://github.com/PakHsi0317/devnotes/actions/workflows/ci.yml/badge.svg)](https://github.com/PakHsi0317/devnotes/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A local developer notes indexer with **inverted-index keyword search** over `.py` / `.md` / `.txt` files. Built as a single CLI binary with SQLite-backed persistence — no external services required.

## Features

- Recursive scan with configurable extensions and ignore directories
- Persistent SQLite storage with **upsert + cascade delete** semantics
- **Inverted-index search** ranked by keyword frequency (the same data structure used by Lucene, Elasticsearch, etc.)
- YAML config with **deep merge over built-in defaults** — zero-config out of the box
- **stderr/stdout separated logging** so output is pipe-friendly
- `--verbose` flag for debug-level tracing
- 40+ pytest tests with ~95% coverage on core modules

## Install

```bash
git clone https://github.com/PakHsi0317/devnotes.git
cd devnotes
python -m venv .venv
.venv\Scripts\Activate.ps1     # Windows PowerShell
# source .venv/bin/activate    # macOS / Linux
pip install -e .
```

## Usage

```bash
# Scan a directory and persist the index
devnotes index ./my_project

# Search by content (returns ranked matches)
devnotes search "database connection"

# Limit results
devnotes search "auth" --limit 5

# Show detailed execution logs
devnotes index . --verbose

# Use a custom config file
devnotes index . --config ./my_config.yaml
```

Example output:

```
[score=  15  matched=3]  src/auth/middleware.py    (128 lines)
[score=   9  matched=2]  src/auth/handlers.py      (94 lines)
[score=   4  matched=1]  README.md                 (52 lines)

3/3 match(es) shown.
```

`score` = sum of matched keyword frequencies. `matched` = distinct keywords hit by the query.

## Configuration

Copy the example to start customizing:

```bash
cp config.example.yaml config.yaml
```

```yaml
scan:
  extensions: [".py", ".md", ".txt", ".rst"]
  ignore_dirs: [".git", "node_modules", "build"]

keywords:
  max_per_file: 200       # cap keywords per file (controls recall vs index size)

storage:
  db_path: ".devnotes/index.db"

logging:
  level: "INFO"           # DEBUG / INFO / WARNING / ERROR
```

Precedence (highest first): **CLI flag → config.yaml → built-in defaults**.

## Architecture

```
src/devnotes/
├── cli.py            # typer entry point, bootstrap config + logging
├── config.py         # YAML loader + deep merge over defaults
├── logging_setup.py  # stderr handler with timestamped format
├── parser.py         # keyword extraction: regex + stopwords + frequency
├── scanner.py        # recursive walk with ignore-dirs filter
└── storage.py        # SQLite schema, upsert, inverted-index search
```

### How the search works

1. **Index time**: each file is tokenized (regex word matcher) → stopwords filtered → counted → top N stored in `keywords` table with foreign key to `files`.
2. **Query time**: `WHERE keyword LIKE ?` uses the `idx_keywords_keyword` B-tree index → JOIN back to `files` → `GROUP BY` file with `SUM(frequency)` as relevance score.

This is the minimal viable structure that powers larger search systems (BM25, vector DBs, etc.) — it can be upgraded by replacing the keyword column with embeddings and the LIKE with vector distance.

## Development

```bash
pip install -e ".[dev]"

pytest                              # run tests
pytest --cov=devnotes               # with coverage report
pytest -v                           # verbose test names
ruff check src/ tests/              # lint
```

CI runs on every push: Python 3.10-3.13 × Ubuntu/Windows = 8 combinations.

## License

MIT
