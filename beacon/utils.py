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
    console.print(f"[success][+][/success] {message}")

def print_error(message: str) -> None:
    console.print(f"[error][x] Error:[/error] {message}")

def print_warning(message: str) -> None:
    console.print(f"[warning][!] Warning:[/warning] {message}")

def print_info(message: str) -> None:
    console.print(f"[info][i][/info] {message}")

def print_header(message: str) -> None:
    console.print(f"\n[header]=== {message} ===[/header]\n")

def print_banner() -> None:
    import sys
    try:
        if sys.stdout and sys.stdout.encoding:
            "╔═╗║╚╝█".encode(sys.stdout.encoding)
            
        logo = r"""[#fff]
██████╗ ███████╗ █████╗  ██████╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝██╔══██╗██╔════╝██╔═══██╗████╗  ██║
██████╔╝█████╗  ███████║██║     ██║   ██║██╔██╗ ██║
██╔══██╗██╔══╝  ██╔══██║██║     ██║   ██║██║╚██╗██║
██████╔╝███████╗██║  ██║╚██████╗╚██████╔╝██║ ╚████║
╚══════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
[/]"""

        console.print(logo)
    except (UnicodeEncodeError, AttributeError):
        box = r"""[#e07a5f]+--------------------------------------------------------------+[/]
[#e07a5f]|  * Welcome to the [bold]Beacon CLI[/bold] developer preview!                |[/]
[#e07a5f]+--------------------------------------------------------------+[/]"""

        logo = r"""[#e07a5f]
  ____  _____    _     ____ ___  _     
 | __ )| ____|  / \   / ___/ _ \| \ | |
 |  _ \|  _|   / _ \ | |  | | | |  \| |
 | |_) | |___ / ___ \| |__| |_| | |\  |
 |____/|_____/_/   \_\\____\___/|_| \_|
[/]"""
        console.print(box)
        console.print(logo)
