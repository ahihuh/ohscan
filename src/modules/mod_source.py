"""
Module de source. Ces modules :
- prennent le nom de domaine en paramètre (str)
- retournent une liste de sous-nom de domaine (list)
Pour lancer un programme externe, la fonction `_run_ext_tool` peut être utilisé.
Les modules générateur de sources doivent être ajouté ici, puis déclarer dans `MODS_SOURCE`,
à la fin de ce fichier.
"""
from .utils import _run_ext_tool, require_config_key
from .consts import *


def _mod__subfinder(domain : str) -> list:
    return _run_ext_tool(
        [f"{GO_PATH}subfinder","-silent","-nc","-d",
        domain])

def _mod_wayback(domain : str) -> list:
    return _run_ext_tool(
        [f"{GO_PATH}waybackurls"], 
        domain)

def _mod_puredns(domain : str) -> list: 
    return _run_ext_tool(
        [f"{GO_PATH}puredns","-q","bruteforce",f"{THIS_PATH}/assets/subdomains-top1million-5000.txt",domain])

@require_config_key('SHODAN_API_KEY')
def _mod_shosubgo(domain : str) -> list: 
    return _run_ext_tool([f"{GO_PATH}shosubgo","-d",domain,"-s",CONFIG["SHODAN_API_KEY"]])

MODS_SOURCE = [
    {"name":"subfinder","f":_mod__subfinder},
    {"name":"wayback","f":_mod_wayback},
    {"name":"puredns","f":_mod_puredns},
    {"name":"shosubgo","f":_mod_shosubgo},
]