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

common_web_ports = [
    # Standard web ports
    8080,   # Alternative HTTP / proxies
    8443,   # Alternative HTTPS
    8000,   # Dev servers / APIs
    8888,   # Dev tools / dashboards

    # Admin interfaces
    2082,   # cPanel (HTTP)
    2083,   # cPanel (HTTPS)
    2095,   # Webmail (HTTP)
    2096,   # Webmail (HTTPS)
    10000,  # Webmin
    5000,   # Flask / Kibana / other dev servers
    5601,   # Kibana

    # Dev tools / node apps
    3000,   # Node.js, React, etc.
    9000,   # Various apps (e.g., SonarQube)
    9001,   # Supervisord, alternate dashboards
    9443,   # Alternative HTTPS admin panels

    # Other
    631,    # CUPS (web printing interface)
    5985,   # WinRM (HTTP)
    5986,   # WinRM (HTTPS)
]


def _mod_httpx(data : list) -> list:
    with open(TMP_FILE_PATH,"w") as _:
        for line in data:
            _.write(f"{line}\n")
            for port in common_web_ports:
                _.write(f"{line}:{port}\n")
    _ = _run_ext_tool(
        [f"{GO_PATH}httpx","-silent","-nc","-l",TMP_FILE_PATH,"-title","-status-code","-tech-detect"])
    return _httpx_parser(_)

def _mod_ping3(data : list, timeout=1) -> list:
    _ = []
    for line in data:
        try:
            delay = ping(line, timeout=timeout)
            if delay:
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

def _mod_url_decomposer(data : list, _max=50) -> list:
    url_reg = r'(https|http):\/\/([a-zA-Z0-9.:-]+)\/([\wÀ-ÿ\/\-%.():]+)(\?[\wÀ-ÿ\/\-=%&():.,]+|)(#.+|)'
    _ = []
    for line in data:
        match = re.match(url_reg, line)
        if match:
            url_decomposed = {
                "protocol":match.group(1),
                "domain":match.group(2),
                "path":match.group(3),
                "query":match.group(4),
                "fragment":match.group(5)
            }
            # Limiter les resultats aux urls les plus pertinentes
            # Todo: Filtrer sur les extensions
            if url_decomposed["query"] != "" or url_decomposed["query"] != "" and len(_) < _max:
                _.append(url_decomposed)
    return _

MODS_PROCESSING = [
    {"name":"httpx","f":_mod_httpx,"domain-only":1},
    {"name":"ping3","f":_mod_ping3,"domain-only":1},
    #{"name":"urldecomposer","f":_mod_url_decomposer,"domain-only":0}
]
