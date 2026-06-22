# devnotes

Local developer notes indexer. Scans a directory for `.py` / `.md` / `.txt` files
and (eventually) lets you search across them from the command line.

## Status

Day 1: walking skeleton. `index` scans and prints; `search` is a stub.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
```

## Usage

```bash
devnotes index .
devnotes search "hello"
```
