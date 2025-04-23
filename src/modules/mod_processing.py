"""
Module de post processing. Ces modules :
- prennent des données en paramètre (url, nom de domaine) (list)
- retournent une liste (list)
Pour lancer un programme externe, la fonction `_run_ext_tool` peut être utilisé.
Les modules de post processing doivent être ajouté ici, puis déclarer dans `MODS_PROCESSING`,
à la fin de ce fichier.
"""
from .utils import _run_ext_tool
from .consts import *
# httpx module
import re
# ping3 module
from ping3 import ping
import socket



def _httpx_parser(data : list) -> dict:
    res = []
    for line in data:
        httpx_regex = re.compile(
            r"(?P<url>\S+)\s+\[(?P<status>[0-9,]+)\](?:\s+\[(?P<title>[^\]]*)\])?(?:\s+\[(?P<technos>[^\]]*)\])?"
        )
        match = httpx_regex.match(line)
        if match:
            d = match.groupdict()
            technos = ",".join([tech.strip() for tech in d["technos"].split(",")] if d["technos"] else [])
            res.append({
                "url": d["url"],
                "status": int(d["status"]),
                "title": d["title"] if d["title"] else "",
                "technos": technos
            })
    return res

def _mod_httpx(data : list) -> list:
    with open(TMP_FILE_PATH,"w") as _:
        _.write("\n".join(data))
    _ = _run_ext_tool(
        [f"{GO_PATH}httpx","-silent","-nc","-l",TMP_FILE_PATH,"-title","-status-code","-tech-detect"])
    return _httpx_parser(_)

def _mod_ping3(data : list, timeout=1) -> list:
    _ = []
    for line in data:
        try:
            delay = ping(line, timeout=timeout)
            if delay is not None:
                try:
                    ip = socket.gethostbyname(line)
                except socket.gaierror:
                    ip = "❌"
                _.append(
                    {
                        "domain":line,
                        "ip":ip
                    })
        except exceptions.PingError:
            pass
    return _

MODS_PROCESSING = [
    {"name":"httpx","f":_mod_httpx},
    {"name":"ping3","f":_mod_ping3},
]
