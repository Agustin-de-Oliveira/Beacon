"""
Generates Architecture Decision Records (ADR) using Jinja2 templates.
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, ChoiceLoader
from beacon.parser.models import BeaconSpec

def get_template_env(custom_templates_dir: Path | None = None) -> Environment:
    loaders = []
    
    if custom_templates_dir and custom_templates_dir.exists():
        loaders.append(FileSystemLoader(str(custom_templates_dir)))
        
    pkg_templates_dir = Path(__file__).parent.parent / "templates"
    if pkg_templates_dir.exists():
        loaders.append(FileSystemLoader(str(pkg_templates_dir)))
        
    return Environment(
        loader=ChoiceLoader(loaders),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True
    )

def generate_adr(spec: BeaconSpec, output_dir: Path, custom_templates_dir: Path | None = None) -> Path:
    if not spec.adr:
        raise ValueError("No ADR specification provided in the specification file.")
        
    env = get_template_env(custom_templates_dir)
    template = env.get_template("adr.md.jinja2")
    
    rendered = template.render(adr=spec.adr, project_name=spec.project_name)
    
    title_slug = spec.adr.title.lower().strip().replace(" ", "_")
    title_slug = "".join(c for c in title_slug if c.isalnum() or c == "_")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"adr_{title_slug}.md"
    output_file.write_text(rendered, encoding="utf-8")
    
    return output_file
