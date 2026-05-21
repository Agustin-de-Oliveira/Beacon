"""
Terminal printing utilities for the Beacon CLI using the Rich library.
"""

from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green bold",
    "highlight": "magenta bold",
    "header": "blue bold",
})

console = Console(theme=custom_theme)

def print_success(message: str) -> None:
    console.print(f"[success]✔[/success] {message}")

def print_error(message: str) -> None:
    console.print(f"[error]✘ Error:[/error] {message}")

def print_warning(message: str) -> None:
    console.print(f"[warning]⚠ Warning:[/warning] {message}")

def print_info(message: str) -> None:
    console.print(f"[info]ℹ[/info] {message}")

def print_header(message: str) -> None:
    console.print(f"\n[header]=== {message} ===[/header]\n")
