"""
Orchestrates the parsed specification data through the generator pipelines.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from beacon.config import Settings, load_settings
from beacon.parser.spec_parser import parse_spec_file
from beacon.generator import generate_adr, generate_codebase
from beacon.utils import print_success, print_info, print_header

class BeaconCore:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or load_settings()
        
    def process_spec(self, spec_path: Path, ai: bool = False) -> Dict[str, Path]:
        print_header(f"Beacon Processing Spec: {spec_path.name}")
        
        spec = parse_spec_file(spec_path)
        generated_artifacts: Dict[str, Path] = {}
        
        if spec.adr:
            print_info(f"ADR specification found: '{spec.adr.title}'")
            adr_path = generate_adr(
                spec=spec,
                output_dir=self.settings.output_dir,
                custom_templates_dir=self.settings.templates_dir
            )
            print_success(f"ADR successfully generated at: [highlight]{adr_path.resolve()}[/highlight]")
            generated_artifacts["adr"] = adr_path
        else:
            print_info("No ADR specification defined in the input file.")
            
        if spec.modules:
            print_info(f"Target modules identified: {', '.join(spec.modules)}")
            codebase_files = generate_codebase(
                spec=spec,
                output_dir=self.settings.output_dir,
                custom_templates_dir=self.settings.templates_dir,
                ai=ai
            )
            for file_path in codebase_files:
                print_success(f"Scaffolded file: [highlight]{file_path.resolve()}[/highlight]")
            
        return generated_artifacts
