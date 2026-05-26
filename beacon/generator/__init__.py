"""
Exposes ADR and artifact generation functions for the generator package.
"""

from beacon.generator.adr import generate_adr
from beacon.generator.code import generate_codebase

__all__ = ["generate_adr", "generate_codebase"]
