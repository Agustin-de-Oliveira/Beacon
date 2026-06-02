import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from typer.testing import CliRunner
from beacon.cli import app
from beacon.parser.models import BeaconSpec, ADRSpec
from beacon.generator.ai import get_groq_client, generate_code_with_ai, generate_test_with_ai, clean_code_block
from beacon.generator.code import generate_codebase

runner = CliRunner()

def test_clean_code_block():
    raw_md = "```python\ndef test():\n    pass\n```"
    assert clean_code_block(raw_md) == "def test():\n    pass"
    
    raw_md_any = "```\ndef test():\n    pass\n```"
    assert clean_code_block(raw_md_any) == "def test():\n    pass"
    
    no_block = "def test():\n    pass"
    assert clean_code_block(no_block) == "def test():\n    pass"

@patch.dict(os.environ, {}, clear=True)
def test_get_groq_client_missing_key():
    with pytest.raises(ValueError) as exc:
        get_groq_client()
    assert "GROQ_API_KEY environment variable is not set" in str(exc.value)

@patch.dict(os.environ, {"GROQ_API_KEY": "test-key-123"})
@patch("beacon.generator.ai.Groq")
def test_generate_code_with_ai(mock_groq_class):
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = "class MockService:\n    pass"
    mock_client.chat.completions.create.return_value = mock_completion
    
    spec = BeaconSpec(
        project_name="TestProject",
        adr=ADRSpec(
            title="Use AI",
            status="Accepted",
            context="Ctx",
            decision="Dec",
            consequences="Cons"
        ),
        modules=["auth"]
    )
    
    result = generate_code_with_ai(spec, "auth")
    assert result == "class MockService:\n    pass"
    mock_client.chat.completions.create.assert_called_once()

@patch.dict(os.environ, {"GROQ_API_KEY": "test-key-123"})
@patch("beacon.generator.ai.Groq")
def test_generate_test_with_ai(mock_groq_class):
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = "def test_mock():\n    pass"
    mock_client.chat.completions.create.return_value = mock_completion
    
    spec = BeaconSpec(
        project_name="TestProject",
        adr=ADRSpec(
            title="Use AI",
            status="Accepted",
            context="Ctx",
            decision="Dec",
            consequences="Cons"
        ),
        modules=["auth"]
    )
    
    result = generate_test_with_ai(spec, "auth", "class MockService:\n    pass")
    assert result == "def test_mock():\n    pass"
    mock_client.chat.completions.create.assert_called_once()

@patch.dict(os.environ, {"GROQ_API_KEY": "test-key-123"})
@patch("beacon.generator.code.generate_code_with_ai")
@patch("beacon.generator.code.generate_test_with_ai")
def test_generate_codebase_with_ai_enabled(mock_gen_test, mock_gen_code, tmp_path):
    mock_gen_code.return_value = "class MockService:\n    pass"
    mock_gen_test.return_value = "def test_mock():\n    pass"
    
    spec = BeaconSpec(
        project_name="TestProject",
        modules=["auth"]
    )
    
    files = generate_codebase(spec, tmp_path, ai=True)
    
    service_path = tmp_path / "src" / "auth" / "service.py"
    assert service_path.exists()
    assert service_path.read_text() == "class MockService:\n    pass"
    
    test_path = tmp_path / "tests" / "test_auth.py"
    assert test_path.exists()
    assert test_path.read_text() == "def test_mock():\n    pass"

@patch.dict(os.environ, {}, clear=True)
def test_generate_codebase_fallback_on_missing_key(tmp_path):
    spec = BeaconSpec(
        project_name="TestProject",
        modules=["auth"]
    )
    
    files = generate_codebase(spec, tmp_path, ai=True)
    
    service_path = tmp_path / "src" / "auth" / "service.py"
    assert service_path.exists()
    assert "class AuthService" in service_path.read_text()
