"""
Integration and unit tests for the Beacon CLI commands and file generation.
"""

from pathlib import Path
from typer.testing import CliRunner
from beacon.cli import app
from beacon import __version__

runner = CliRunner()

def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Beacon CLI" in result.stdout
    assert __version__ in result.stdout

def test_generate_non_existent_file():
    result = runner.invoke(app, ["generate", "non_existent.beacon"])
    assert result.exit_code == 1
    assert "Error:" in result.stdout

def test_generate_valid_file(tmp_path):
    spec_content = """---
project_name: "TestProject"
adr:
  title: "Use SQLite for Testing"
  status: "Accepted"
  date: "2026-05-24"
---

# Use SQLite for Testing

## Context
We need a lightweight database for local unit tests.

## Decision
We decide to use SQLite in-memory database.

## Consequences
Fast tests, easy setup.
"""
    spec_file = tmp_path / "test_spec.beacon"
    spec_file.write_text(spec_content, encoding="utf-8")
    
    out_dir = tmp_path / "output"
    
    result = runner.invoke(app, ["generate", str(spec_file), "-o", str(out_dir)])
    assert result.exit_code == 0
    assert "ADR successfully generated" in result.stdout
    
    expected_adr = out_dir / "adr_use_sqlite_for_testing.md"
    assert expected_adr.exists()
    
    adr_content = expected_adr.read_text(encoding="utf-8")
    assert "ADR: Use SQLite for Testing" in adr_content
    assert "**Status:** Accepted" in adr_content
    assert "We decide to use SQLite in-memory database." in adr_content

def test_generate_codebase_scaffolding(tmp_path):
    spec_content = """---
project_name: "AuthBillingProject"
adr:
  title: "Add Service Modules"
  status: "Accepted"
  date: "2026-05-24"
modules:
  - "auth"
  - "billing"
---

# Add Service Modules

## Context
Standard modules.

## Decision
Create auth and billing modules.

## Consequences
Clean layout.
"""
    spec_file = tmp_path / "test_modules.beacon"
    spec_file.write_text(spec_content, encoding="utf-8")
    
    out_dir = tmp_path / "output"
    
    result = runner.invoke(app, ["generate", str(spec_file), "-o", str(out_dir)])
    assert result.exit_code == 0
    assert "Scaffolded file" in result.stdout
    
    # Check that directory structures exist
    assert (out_dir / "src" / "auth" / "__init__.py").exists()
    assert (out_dir / "src" / "auth" / "service.py").exists()
    assert (out_dir / "src" / "billing" / "__init__.py").exists()
    assert (out_dir / "src" / "billing" / "service.py").exists()
    assert (out_dir / "tests" / "__init__.py").exists()
    assert (out_dir / "tests" / "test_auth.py").exists()
    assert (out_dir / "tests" / "test_billing.py").exists()
    
    # Check generated files contents
    auth_service_content = (out_dir / "src" / "auth" / "service.py").read_text(encoding="utf-8")
    assert "class AuthService:" in auth_service_content
    assert "Service handler for the auth module." in auth_service_content
    
    auth_test_content = (out_dir / "tests" / "test_auth.py").read_text(encoding="utf-8")
    assert "from auth.service import AuthService" in auth_test_content
    assert "def test_auth_service_initialization():" in auth_test_content

