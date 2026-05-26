"""
Generates codebase scaffolding (directories, module stubs, and tests) using Jinja2 templates.
"""

from pathlib import Path
from typing import List
from beacon.parser.models import BeaconSpec
from beacon.generator.adr import get_template_env

def generate_codebase(spec: BeaconSpec, output_dir: Path, custom_templates_dir: Path | None = None) -> List[Path]:
    """
    Generates directory structures, Python source files, and unit test suites
    based on the modules defined in the specification.
    
    Returns a list of Path objects for all created files.
    """
    generated_files: List[Path] = []
    
    if not spec.modules:
        return generated_files
        
    # Initialize Jinja2 environment
    env = get_template_env(custom_templates_dir)
    module_template = env.get_template("module.py.jinja2")
    test_template = env.get_template("test_module.py.jinja2")
    
    # Establish base directories
    src_dir = output_dir / "src"
    tests_dir = output_dir / "tests"
    
    src_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure tests package init exists
    test_init = tests_dir / "__init__.py"
    if not test_init.exists():
        test_init.write_text("# Automated tests for Beacon scaffolding.\n", encoding="utf-8")
        generated_files.append(test_init)
        
    for module in spec.modules:
        # Standardize module name to be a valid Python module identifier (lowercase, underscore)
        module_name = "".join(c if c.isalnum() or c == "_" else "_" for c in module.lower().strip())
        
        # Create module directory structure
        mod_dir = src_dir / module_name
        mod_dir.mkdir(parents=True, exist_ok=True)
        
        # Write __init__.py inside module package
        mod_init = mod_dir / "__init__.py"
        if not mod_init.exists():
            mod_init.write_text(f'"""{module_name.capitalize()} module stub."""\n', encoding="utf-8")
            generated_files.append(mod_init)
            
        # Render and write service.py
        rendered_module = module_template.render(
            module_name=module_name,
            project_name=spec.project_name
        )
        service_file = mod_dir / "service.py"
        service_file.write_text(rendered_module, encoding="utf-8")
        generated_files.append(service_file)
        
        # Render and write test_<module>.py
        rendered_test = test_template.render(
            module_name=module_name,
            project_name=spec.project_name
        )
        test_file = tests_dir / f"test_{module_name}.py"
        test_file.write_text(rendered_test, encoding="utf-8")
        generated_files.append(test_file)
        
    return generated_files
