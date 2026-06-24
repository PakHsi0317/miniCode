import logging
from pathlib import Path

logger = logging.getLogger(__name__)

EXTENSIONS = {".py", ".md", ".txt"}
IGNORE_DIRS = {
    ".git", "__pycache__", ".venv", "venv",
    "node_modules", ".pytest_cache", ".devnotes",
    ".ruff_cache", "dist", "build",
}


def scan(
    root: Path,
    extensions: set[str] | None = None,
    ignore_dirs: set[str] | None = None,
) -> list[Path]:
    """Walk root recursively, return files matching extensions and not under any ignore dir."""
    extensions = extensions if extensions is not None else EXTENSIONS
    ignore_dirs = ignore_dirs if ignore_dirs is not None else IGNORE_DIRS

    logger.debug(
        "scan start: root=%s extensions=%s ignore_dirs=%s",
        root, extensions, ignore_dirs,
    )

    results: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in extensions:
            continue
        if any(part in ignore_dirs for part in p.parts):
            continue
        results.append(p)

    logger.info("scan complete: %d files matched under %s", len(results), root)
    return results
