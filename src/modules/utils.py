"""
Fonctions récurrentes utilisées pour les modules de source et
de post processing.
"""
import subprocess
from rich import print

from .consts import *

def _run_ext_tool(cmd: list, input_text: str = None) -> list:
    _ = subprocess.run(
        cmd,
        input=input_text.encode() if input_text else None,
        stdout=subprocess.PIPE
    )
    return _.stdout.decode().splitlines()


def require_config_key(key):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if key in CONFIG and key != "":
                return func(*args, **kwargs)
            else:
                print(f"[bold yellow]![/bold yellow] '{key}' is not defined in the config. Skipping the module [bold green]{func.__name__}[/bold green]")
                return []
        return wrapper
    return decorator