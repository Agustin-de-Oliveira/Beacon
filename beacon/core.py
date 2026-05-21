"""
Orchestrates the parsed specification data through the generator pipelines.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from beacon.config import Settings, load_settings
from beacon.parser.spec_parser import parse_spec_file
from beacon.generator.adr import generate_adr
from beacon.utils import print_success, print_info, print_header

class BeaconCore:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or load_settings()
        
    def process_spec(self, spec_path: Path) -> Dict[str, Path]:
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
            
        return generated_artifacts
