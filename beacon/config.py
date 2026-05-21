"""
Configuration model and helper functions to load settings for the Beacon project.
"""

import json
from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field

class Settings(BaseModel):
    templates_dir: Path = Field(default=Path("templates"))
    output_dir: Path = Field(default=Path("specs_output"))

def load_settings(config_path: Optional[Path] = None) -> Settings:
    if not config_path:
        for filename in ["beacon.yaml", "beacon.yml", "beacon.json"]:
            path = Path(filename)
            if path.exists():
                config_path = path
                break
                
    if config_path and config_path.exists():
        try:
            content = config_path.read_text(encoding="utf-8")
            if config_path.suffix in (".yaml", ".yml"):
                data = yaml.safe_load(content) or {}
            else:
                data = json.loads(content) or {}
            return Settings.model_validate(data)
        except Exception:
            pass
            
    return Settings()
