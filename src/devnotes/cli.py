from pathlib import Path

import typer

from devnotes.scanner import scan
from devnotes.storage import connect, count_files, search_files, upsert_file

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
    """Scan a directory and persist results to SQLite."""
    files = scan(path)
    conn = connect()
    try:
        for f in files:
            upsert_file(conn, f)
        conn.commit()
        total = count_files(conn)
    finally:
        conn.close()
    typer.echo(f"Indexed {len(files)} files from {path}")
    typer.echo(f"Total files in index: {total}")


@app.command()
def search(query: str) -> None:
    """Search indexed files by filename."""
    conn = connect()
    try:
        results = search_files(conn, query)
    finally:
        conn.close()

    if not results:
        typer.echo(f"No matches for: {query}")
        raise typer.Exit(code=1)

    for row in results:
        typer.echo(row["path"])
    typer.echo(f"\n{len(results)} match(es).")


if __name__ == "__main__":
    app()
