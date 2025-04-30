# Misc
import os, subprocess, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
# Style
from rich import print
from rich.progress import SpinnerColumn, TextColumn, Progress
from rich.markup import escape
from rich.console import Console
from rich.panel import Panel
# Render
from jinja2 import Environment, FileSystemLoader
# Intern
from modules.mod_processing import *
from modules.mod_source import *
from modules.consts import *


console = Console(force_terminal=True)

def __say_hello():
    console.print(Panel("""
[bold blue]
 ▄██████▄     ▄█    █▄       ▄████████  ▄████████    ▄████████ ███▄▄▄▄   
███    ███   ███    ███     ███    ███ ███    ███   ███    ███ ███▀▀▀██▄ 
███    ███   ███    ███     ███    █▀  ███    █▀    ███    ███ ███   ███ 
███    ███  ▄███▄▄▄▄███▄▄   ███        ███          ███    ███ ███   ███ 
███    ███ ▀▀███▀▀▀▀███▀  ▀███████████ ███        ▀███████████ ███   ███ 
███    ███   ███    ███            ███ ███    █▄    ███    ███ ███   ███ 
███    ███   ███    ███      ▄█    ███ ███    ███   ███    ███ ███   ███ 
 ▀██████▀    ███    █▀     ▄████████▀  ████████▀    ███    █▀   ▀█   █▀  
                                                                         
[/bold blue]Version 1.0
by [italic]@ohohoh[/italic]"""))

def _post_processing(data : list) -> list:
    """
    Supprime les données inutiles (chaine vide etc...)

    :param data:    liste de résultats (url/ndd)
    """
    return [item for item in data if item]

def _domain_extractor(data : list) -> list:
    """
    Extrait les noms de domaines des données

    :param data:    liste de résultats (url/ndd)
    """
    domain = []
    url_reg = r"^(https|http):\/\/([a-zA-Z0-9\.]+)(\/|:)"
    domain_reg = r"^([a-zA-Z0-9\.]+)\.([a-zA-Z0-9]+)$"
    for item in data:
        _ = re.match(url_reg,item)
        if _:
            domain.append(_.group(2))
            continue
        _ = re.match(domain_reg,item)
        if _:
            domain.append(_.group(0))
    domain = list(set(domain))
    return domain


######################################################################
#
#       Main
#
######################################################################

def get_from_source(domain : str) -> list:
    _ = []
    with Progress(
            SpinnerColumn(style="bold cyan",speed=0.8),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
            console=console
        ) as progress:
        tasks = {}
        for mod in MODS_SOURCE:
            task = progress.add_task(f"Module (source) [bold green]{mod['name']}[/bold green]", start=True)
            tasks[mod["name"]] = task

        with ThreadPoolExecutor() as executor:
            running_mod = []
            for mod in MODS_SOURCE:
                running_mod.append(executor.submit(mod["f"], domain))

            for mod in as_completed(running_mod):
                mod_result = mod.result() 
                task_name = MODS_SOURCE[running_mod.index(mod)]["name"]

                progress.update(
                    tasks[task_name],
                    description=f"✅ Module (source) [bold green]{task_name}[/bold green] complete.",
                    completed=100)
                _ = list(dict.fromkeys(_ + mod_result))
    return _

def post_processing(res : list) -> list:
    # -- Builtin processing
    raw_res = _post_processing(res)
    domains = _domain_extractor(raw_res)
    # -- Mod processing
    _ = {}
    with Progress(
            SpinnerColumn(style="bold cyan"),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
            console=console
        ) as progress:
        tasks = {}
        for mod in MODS_PROCESSING:
            task = progress.add_task(f"Module (post-processing) [bold green]{mod['name']}[/bold green]", start=True)
            tasks[mod["name"]] = task
            
        with ThreadPoolExecutor() as executor:
            running_mod = []
            for mod in MODS_PROCESSING:
                running_mod.append(
                    executor.submit(mod["f"], 
                    domains if "domain-only" in mod and mod["domain-only"] == 1 else raw_res
                ))

            for mod in as_completed(running_mod):
                mod_result = mod.result() 
                task_name = MODS_PROCESSING[running_mod.index(mod)]["name"] 
                progress.update(tasks[task_name], completed=1)
                progress.update(
                    tasks[task_name],
                    description=f"✅ Module (post-processing) [bold green]{task_name}[/bold green] complete.",
                    completed=100)
                _[task_name] = mod_result
    return _


def main():
    # - Start
    __say_hello()
    console.print(f"[bold green]![/bold green] {len(MODS_SOURCE)} source modules and {len(MODS_PROCESSING)} processing are loaded")
    
    # - Check argument
    if len(sys.argv) < 2:
        console.print("[bold red]![/bold red] Argument manquant")
        return
    arg = sys.argv[1]

    print("")

    # - Source gathering
    console.print(f"[bold cyan]![/bold cyan] Scanning [italic underline]{arg}[/italic underline]")
    # -- Mod executions
    source_res = get_from_source(arg)

    print("")

    # - Post processing
    console.print(f"[bold cyan]![/bold cyan] Post processing")
    post_res = post_processing(source_res)

    # - Result
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('assets/template.html')
    html_rendered = template.render(data=post_res, arg=arg)

    with open(f"{OUTPUT_PATH}{arg}.scan.html","w") as output:
        output.write(html_rendered)

    console.print("[bold green]![/bold green] Scanning complete.")

if __name__ == "__main__":
    main()