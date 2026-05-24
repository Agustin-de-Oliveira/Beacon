"""
Beacon CLI entry point. Defines commands for checking version and generating artifacts.
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

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        from beacon.utils import print_banner
        print_banner()
        console.print("[header]Beacon CLI[/header] - Automatic code, test, and ADR generator.\n")
        console.print("[info]Usage:[/info]")
        console.print("  [success]beacon generate <spec-file>[/success]  Generate ADRs, code, and tests")
        console.print("  [success]beacon version[/success]               Print CLI version")
        console.print("  [success]beacon --help[/success]                Show detailed help instructions\n")

if __name__ == "__main__":
    app()
