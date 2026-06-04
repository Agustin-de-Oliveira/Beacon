import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from typer.testing import CliRunner
from beacon.cli import app

runner = CliRunner()

@patch("questionary.text")
@patch("questionary.confirm")
@patch("questionary.select")
def test_init_command_with_adr(mock_select, mock_confirm, mock_text, tmp_path):
    mock_text_prompt = MagicMock()
    mock_text.return_value = mock_text_prompt
    mock_text_prompt.ask.side_effect = [
        "MyProject",
        "auth, billing",
        "Use SQLite for Database",
        "We need a db.",
        "Use SQLite.",
        "Easy testing."
    ]
    
    mock_confirm_prompt = MagicMock()
    mock_confirm.return_value = mock_confirm_prompt
    mock_confirm_prompt.ask.return_value = True
    
    mock_select_prompt = MagicMock()
    mock_select.return_value = mock_select_prompt
    mock_select_prompt.ask.return_value = "Accepted"
    
    out_dir = tmp_path / "specs"
    
    result = runner.invoke(app, ["init", "-o", str(out_dir)])
    
    assert result.exit_code == 0
    assert "Successfully generated specification file at" in result.stdout
    
    expected_file = out_dir / "use_sqlite_for_database.beacon"
    assert expected_file.exists()
    
    content = expected_file.read_text(encoding="utf-8")
    assert "project_name: MyProject" in content
    assert "modules:" in content
    assert "- auth" in content
    assert "- billing" in content
    assert "status: Accepted" in content
    assert "# Use SQLite for Database" in content
    assert "## Context\nWe need a db." in content
    assert "## Decision\nUse SQLite." in content
    assert "## Consequences\nEasy testing." in content

@patch("questionary.text")
@patch("questionary.confirm")
def test_init_command_without_adr(mock_confirm, mock_text, tmp_path):
    mock_text_prompt = MagicMock()
    mock_text.return_value = mock_text_prompt
    mock_text_prompt.ask.side_effect = [
        "LightweightProject",
        "api, workers"
    ]
    
    mock_confirm_prompt = MagicMock()
    mock_confirm.return_value = mock_confirm_prompt
    mock_confirm_prompt.ask.return_value = False
    
    out_dir = tmp_path / "specs"
    
    result = runner.invoke(app, ["init", "-o", str(out_dir)])
    
    assert result.exit_code == 0
    
    expected_file = out_dir / "lightweightproject.beacon"
    assert expected_file.exists()
    
    content = expected_file.read_text(encoding="utf-8")
    assert "project_name: LightweightProject" in content
    assert "modules:" in content
    assert "- api" in content
    assert "- workers" in content
    assert "adr" not in content
    assert "#" not in content

@patch("questionary.text")
def test_init_command_cancelled(mock_text, tmp_path):
    mock_text_prompt = MagicMock()
    mock_text.return_value = mock_text_prompt
    mock_text_prompt.ask.return_value = None
    
    out_dir = tmp_path / "specs"
    
    result = runner.invoke(app, ["init", "-o", str(out_dir)])
    
    assert result.exit_code == 0
    assert "Initialization cancelled." in result.stdout
    
    assert not out_dir.exists() or len(list(out_dir.iterdir())) == 0

@patch("questionary.text")
@patch("questionary.confirm")
def test_init_command_non_existent_dir_heuristic(mock_confirm, mock_text, tmp_path):
    mock_text_prompt = MagicMock()
    mock_text.return_value = mock_text_prompt
    mock_text_prompt.ask.side_effect = [
        "LightweightProject",
        ""
    ]
    
    mock_confirm_prompt = MagicMock()
    mock_confirm.return_value = mock_confirm_prompt
    mock_confirm_prompt.ask.return_value = False
    
    out_dir = tmp_path / "new_non_existent_folder"
    
    result = runner.invoke(app, ["init", "-o", str(out_dir)])
    
    assert result.exit_code == 0
    
    expected_file = out_dir / "lightweightproject.beacon"
    assert expected_file.exists()

