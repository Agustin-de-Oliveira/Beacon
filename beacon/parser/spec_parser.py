"""
Parser logic to extract YAML frontmatter and Markdown headings from specification files.
"""

import re
from pathlib import Path
from typing import Dict, Any
import yaml
from beacon.parser.models import BeaconSpec, ADRSpec

def parse_markdown_sections(content: str) -> Dict[str, str]:
    sections = {}
    heading_pattern = re.compile(
        r'^(?:#|##)\s+(Context|Decision|Consequences)\b', 
        re.IGNORECASE | re.MULTILINE
    )
    
    matches = list(heading_pattern.finditer(content))
    for i, match in enumerate(matches):
        section_name = match.group(1).lower()
        start_idx = match.end()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(content)
        
        section_content = content[start_idx:end_idx].strip()
        sections[section_name] = section_content
        
    return sections

def parse_spec_file(file_path: Path) -> BeaconSpec:
    if not file_path.exists():
        raise FileNotFoundError(f"Specification file not found at: {file_path}")
        
    content = file_path.read_text(encoding="utf-8")
    
    yaml_data: Dict[str, Any] = {}
    markdown_body = content
    
    frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    match = frontmatter_pattern.match(content)
    if match:
        frontmatter_text = match.group(1)
        yaml_data = yaml.safe_load(frontmatter_text) or {}
        markdown_body = content[match.end():]
    else:
        try:
            yaml_data = yaml.safe_load(content) or {}
            if not isinstance(yaml_data, dict) or not any(k in yaml_data for k in ["project_name", "adr", "modules"]):
                yaml_data = {}
        except yaml.YAMLError:
            pass
            
    md_sections = parse_markdown_sections(markdown_body)
    
    if "adr" not in yaml_data:
        yaml_data["adr"] = {}
        
    if isinstance(yaml_data["adr"], dict):
        for section in ["context", "decision", "consequences"]:
            if section in md_sections and not yaml_data["adr"].get(section):
                yaml_data["adr"][section] = md_sections[section]
                
        if "title" not in yaml_data["adr"]:
            h1_match = re.search(r'^#\s+(?!Context|Decision|Consequences)(.+)$', markdown_body, re.MULTILINE | re.IGNORECASE)
            if h1_match:
                yaml_data["adr"]["title"] = h1_match.group(1).strip()
            else:
                yaml_data["adr"]["title"] = file_path.stem.replace("_", " ").title()

    if isinstance(yaml_data.get("adr"), dict):
        non_empty_values = {k: v for k, v in yaml_data["adr"].items() if v}
        if not non_empty_values and not md_sections:
            yaml_data["adr"] = None
            
    return BeaconSpec.model_validate(yaml_data)
