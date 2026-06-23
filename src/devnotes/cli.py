from pathlib import Path

import typer

from devnotes.parser import parse
from devnotes.scanner import scan
from devnotes.storage import (
    connect,
    count_files,
    count_keywords,
    search_files,
    upsert_file,
)

app = typer.Typer(help="Local developer notes indexer.", no_args_is_help=True)


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
) -> None:
    """Scan a directory, extract keywords, and persist to SQLite."""
    files = scan(path)
    conn = connect()
    try:
        for f in files:
            info = parse(f)
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
) -> None:
    """Search indexed files by keyword content."""
    conn = connect()
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
