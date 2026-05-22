"""
Beacon CLI entrypoint. Defines commands for versioning and artifact generation.
"""

from pathlib import Path
from typing import Optional
import typer
from beacon import __version__
from beacon.config import load_settings
from beacon.core import BeaconCore
from beacon.utils import console, print_error

app = typer.Typer(
    name="beacon",
    help="Beacon: A CLI tool to automatically transform semi-structured specifications into ADRs, code, and tests.",
    add_completion=False,
)

@app.command("version")
def version():
    console.print(f"[header]Beacon CLI[/header] v[highlight]{__version__}[/highlight]")

@app.command("generate")
def generate(
    file: Path = typer.Argument(
        ..., 
        help="Path to the specification file (.md or .beacon) to parse."
    ),
    config_path: Optional[Path] = typer.Option(
        None, 
        "--config", 
        "-c", 
        help="Path to a custom configuration file (beacon.yaml/json)."
    ),
    output_dir: Optional[Path] = typer.Option(
        None, 
        "--output", 
        "-o", 
        help="Directory where generated artifacts will be saved."
    ),
    templates_dir: Optional[Path] = typer.Option(
        None, 
        "--templates", 
        "-t", 
        help="Directory to search for custom Jinja2 templates first."
    ),
):
    settings = load_settings(config_path)
    
    if output_dir:
        settings.output_dir = output_dir
    if templates_dir:
        settings.templates_dir = templates_dir
        
    if not file.exists():
        print_error(f"Specification file does not exist: {file}")
        raise typer.Exit(code=1)
        
    try:
        core = BeaconCore(settings)
        core.process_spec(file)
    except Exception as e:
        print_error(f"An error occurred while generating artifacts: {e}")
        raise typer.Exit(code=1)

@app.callback()
def main():
    pass

if __name__ == "__main__":
    app()
