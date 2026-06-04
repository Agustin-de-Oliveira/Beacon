"""
Beacon CLI entry point. Defines commands for checking version and generating artifacts.
"""

import datetime
from pathlib import Path
from typing import Optional
import typer
import yaml
import questionary
from beacon import __version__
from beacon.config import load_settings
from beacon.core import BeaconCore
from beacon.utils import console, print_error, print_success, print_info

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
    ai: bool = typer.Option(
        False,
        "--ai",
        help="Enable AI-driven code and test generation using Groq (requires GROQ_API_KEY)."
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
        core.process_spec(file, ai=ai)
    except Exception as e:
        print_error(f"An error occurred while generating artifacts: {e}")
        raise typer.Exit(code=1)

def slugify(text: str) -> str:
    slug = text.lower().strip().replace(" ", "_")
    return "".join(c for c in slug if c.isalnum() or c == "_")

def ask_or_exit(prompt_obj):
    res = prompt_obj.ask()
    if res is None:
        console.print("[warning]\nInitialization cancelled.[/warning]")
        raise typer.Exit(code=0)
    return res

@app.command("init")
def init(
    output_path: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Path or directory where the generated .beacon file will be saved."
    )
):
    """
    Initialize a new semi-structured Beacon specification file (.beacon) interactively.
    """
    console.print("[header]=== Beacon Specification Initializer ===[/header]\n")
    
    project_name = ask_or_exit(
        questionary.text("Project Name:", default="MyBeaconProject")
    )
    
    modules_raw = ask_or_exit(
        questionary.text("Modules to create (comma-separated):", default="")
    )
    modules_list = [m.strip() for m in modules_raw.split(",") if m.strip()]
    
    has_adr = ask_or_exit(
        questionary.confirm("Create initial Architecture Decision Record (ADR)?", default=True)
    )
    
    adr_title = ""
    adr_status = ""
    adr_context = ""
    adr_decision = ""
    adr_consequences = ""
    
    if has_adr:
        adr_title = ask_or_exit(
            questionary.text("ADR Title:", default="Use PostgreSQL for Core Data Storage")
        )
        adr_status = ask_or_exit(
            questionary.select(
                "ADR Status:",
                choices=["Proposed", "Accepted", "Deprecated", "Superseded"],
                default="Accepted"
            )
        )
        adr_context = ask_or_exit(
            questionary.text("ADR Context:", default="We need a database to store our records.")
        )
        adr_decision = ask_or_exit(
            questionary.text("ADR Decision:", default="We decide to use PostgreSQL.")
        )
        adr_consequences = ask_or_exit(
            questionary.text("ADR Consequences:", default="ACID compliance, ease of migrations.")
        )

    slug = slugify(adr_title) if (has_adr and adr_title) else slugify(project_name)
    if not slug:
        slug = "specification"
        
    filename = f"{slug}.beacon"
    
    if output_path:
        if output_path.is_dir() or (not output_path.exists() and not output_path.suffix):
            target_file = output_path / filename
        else:
            target_file = output_path
    else:
        target_file = Path("specs") / filename
        
    frontmatter = {
        "project_name": project_name,
    }
    if modules_list:
        frontmatter["modules"] = modules_list
        
    if has_adr:
        frontmatter["adr"] = {
            "title": adr_title,
            "status": adr_status,
            "date": datetime.date.today().isoformat()
        }
        
    frontmatter_yaml = yaml.dump(frontmatter, sort_keys=False, default_flow_style=False).strip()
    
    spec_content = f"---\n{frontmatter_yaml}\n---\n"
    if has_adr:
        spec_content += f"\n# {adr_title}\n"
        if adr_context:
            spec_content += f"\n## Context\n{adr_context}\n"
        if adr_decision:
            spec_content += f"\n## Decision\n{adr_decision}\n"
        if adr_consequences:
            spec_content += f"\n## Consequences\n{adr_consequences}\n"
            
    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(spec_content, encoding="utf-8")
        print_success(f"Successfully generated specification file at: [highlight]{target_file.resolve()}[/highlight]")
    except Exception as e:
        print_error(f"Failed to write specification file: {e}")
        raise typer.Exit(code=1)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        from beacon.utils import print_banner
        print_banner()
        console.print("[header]Beacon CLI[/header] - Automatic code, test, and ADR generator.\n")
        console.print("[info]Usage:[/info]")
        console.print("  [success]beacon generate <spec-file>[/success]  Generate ADRs, code, and tests")
        console.print("  [success]beacon init[/success]                  Initialize a new specification file")
        console.print("  [success]beacon version[/success]               Print CLI version")
        console.print("  [success]beacon --help[/success]                Show detailed help instructions\n")

if __name__ == "__main__":
    app()
