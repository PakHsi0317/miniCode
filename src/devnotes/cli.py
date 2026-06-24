import logging
from pathlib import Path
from typing import Optional

import typer

from devnotes.config import load_config
from devnotes.logging_setup import setup_logging
from devnotes.parser import parse
from devnotes.scanner import scan
from devnotes.storage import (
    connect,
    count_files,
    count_keywords,
    search_files,
    upsert_file,
)

logger = logging.getLogger(__name__)

app = typer.Typer(help="Local developer notes indexer.", no_args_is_help=True)


def _bootstrap(config_path: Optional[Path], verbose: bool) -> dict:
    """Load config and set up logging. Returns the effective config dict."""
    config = load_config(config_path)
    level = "DEBUG" if verbose else config["logging"]["level"]
    setup_logging(level)
    logger.debug("config loaded: %s", config)
    return config


@app.command()
def index(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Directory to scan.",
    ),
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to config.yaml (defaults to ./config.yaml)."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show debug logs."
    ),
) -> None:
    """Scan a directory, extract keywords, and persist to SQLite."""
    config = _bootstrap(config_path, verbose)

    extensions = set(config["scan"]["extensions"])
    ignore_dirs = set(config["scan"]["ignore_dirs"])
    max_keywords = config["keywords"]["max_per_file"]
    db_path = Path(config["storage"]["db_path"])

    files = scan(path, extensions=extensions, ignore_dirs=ignore_dirs)
    conn = connect(db_path)
    try:
        for f in files:
            info = parse(f, max_keywords=max_keywords)
            upsert_file(conn, f, info["line_count"], info["keywords"])
        conn.commit()
        total_files = count_files(conn)
        total_keywords = count_keywords(conn)
    finally:
        conn.close()

    typer.echo(f"Indexed {len(files)} files from {path}")
    typer.echo(f"Total in index: {total_files} files, {total_keywords} keywords")


@app.command()
def search(
    query: str,
    limit: int = typer.Option(10, "--limit", "-n", help="Max results."),
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to config.yaml."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show debug logs."
    ),
) -> None:
    """Search indexed files by keyword content."""
    config = _bootstrap(config_path, verbose)
    db_path = Path(config["storage"]["db_path"])

    conn = connect(db_path)
    try:
        results = search_files(conn, query)
    finally:
        conn.close()

    if not results:
        typer.echo(f"No matches for: {query}")
        raise typer.Exit(code=1)

    for row in results[:limit]:
        typer.echo(
            f"[score={row['score']:>4}  matched={row['matched_keywords']}]  "
            f"{row['path']}  ({row['line_count']} lines)"
        )

    shown = min(limit, len(results))
    typer.echo(f"\n{shown}/{len(results)} match(es) shown.")


if __name__ == "__main__":
    app()
