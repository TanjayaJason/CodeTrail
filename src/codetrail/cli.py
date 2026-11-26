from pathlib import Path
import typer
from .core import scan, markdown
from .support import render_json
app = typer.Typer(help='Find your route through a local Git repository.', add_completion=False)
@app.command()
def explore(path: Path, goal: str = 'Understand the architecture', ai: bool = False, json: bool = False):
    """Map tracked files. --ai sends selected metadata to the configured provider."""
    try:
        result = scan(path, goal, ai)
        typer.echo(render_json(result) if json else markdown(result))
    except (ValueError, OSError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1)
