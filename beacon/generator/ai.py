"""
AI code and test generator using Groq's LLM API.
"""

import os
import re
from typing import Optional
from groq import Groq
from beacon.parser.models import BeaconSpec

DEFAULT_MODEL = "llama-3.3-70b-versatile"

def get_groq_client() -> Groq:
    """
    Initializes and returns the Groq client.
    Raises ValueError if GROQ_API_KEY is not set.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set it to use the AI-driven generator (e.g., export GROQ_API_KEY='your-key')."
        )
    return Groq(api_key=api_key)

def clean_code_block(content: str) -> str:
    """
    Cleans up any markdown code block formatting returned by the LLM.
    """
    match = re.search(r"```python\s*(.*?)\s*```", content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    match_any = re.search(r"```\s*(.*?)\s*```", content, re.DOTALL)
    if match_any:
        return match_any.group(1).strip()
        
    return content.strip()

def _build_context_prompt(spec: BeaconSpec) -> str:
    """
    Builds the context string from the parsed spec to pass to the LLM.
    """
    context_parts = [f"Project Name: {spec.project_name}"]
    if spec.adr:
        context_parts.append(
            f"Architecture Decision Record (ADR):\n"
            f"Title: {spec.adr.title}\n"
            f"Status: {spec.adr.status}\n"
            f"Context: {spec.adr.context}\n"
            f"Decision: {spec.adr.decision}\n"
            f"Consequences: {spec.adr.consequences}"
        )
    return "\n\n".join(context_parts)

def generate_code_with_ai(spec: BeaconSpec, module_name: str, model: str = DEFAULT_MODEL) -> str:
    """
    Generates functional Python code for service.py based on the module name and specification.
    """
    client = get_groq_client()
    context = _build_context_prompt(spec)
    
    system_prompt = (
        "You are an expert software developer writing production-grade Python code. "
        "Your task is to generate the contents of a service module file named `service.py`. "
        "You must return ONLY valid Python code. Do not include markdown formatting or explanations, "
        "except for python docstrings inside classes/methods. Do not wrap the output in ```python."
    )
    
    user_prompt = (
        f"Generate the full content of `service.py` for the module named '{module_name}'.\n\n"
        f"Here is the context of the project and architectural decisions:\n"
        f"{context}\n\n"
        f"Provide a class `{module_name.capitalize()}Service` containing realistic, functional methods, "
        f"properties, or stubs that align with the architectural decisions described above. "
        "Make sure to include appropriate imports and docstrings. Do not leave the implementation completely empty."
    )
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model=model,
        temperature=0.2,
    )
    
    raw_code = response.choices[0].message.content or ""
    return clean_code_block(raw_code)

def generate_test_with_ai(
    spec: BeaconSpec, 
    module_name: str, 
    implementation_code: str, 
    model: str = DEFAULT_MODEL
) -> str:
    """
    Generates pytest code for tests/test_<module_name>.py based on the module implementation code.
    """
    client = get_groq_client()
    context = _build_context_prompt(spec)
    
    system_prompt = (
        "You are an expert software developer writing production-grade unit and integration tests. "
        "Your task is to generate the contents of a test file named `test_{module_name}.py` using pytest. "
        "You must return ONLY valid Python test code. Do not include markdown formatting or explanations. "
        "Do not wrap the output in ```python."
    )
    
    user_prompt = (
        f"Generate the full content of a pytest file `test_{module_name}.py` for the '{module_name}' module.\n\n"
        f"Here is the context of the project:\n"
        f"{context}\n\n"
        f"Here is the implementation code of the service module (`service.py`) we are testing:\n"
        f"```python\n"
        f"{implementation_code}\n"
        f"```\n\n"
        f"Please write a comprehensive suite of unit tests using `pytest` to test all functionality in the implementation code. "
        f"Make sure to import `{module_name.capitalize()}Service` from `{module_name}.service`. "
        f"Use pytest fixtures, mocks, parameterization, and assertion checks as appropriate."
    )
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model=model,
        temperature=0.2,
    )
    
    raw_code = response.choices[0].message.content or ""
    return clean_code_block(raw_code)
