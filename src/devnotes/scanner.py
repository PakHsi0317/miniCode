from pathlib import Path

EXTENSIONS = {".py", ".md", ".txt"}
IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".pytest_cache",
    ".devnotes",
    ".ruff_cache",
    "dist",
    "build",
}


def scan(root: Path) -> list[Path]:
    """Walk root recursively, return all files matching EXTENSIONS,
    skipping any path that contains an IGNORE_DIRS component."""
    results: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in EXTENSIONS:
            continue
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        results.append(p)
    return results
