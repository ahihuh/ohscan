"""
Declare les constantes techniques du projet.
"""
import os
from dotenv import dotenv_values

TMP_FILE_PATH = "/tmp/.ohscan.temp"

GO_PATH = "/home/ohohoh/go/bin/" # Debug only, empty for Docker
THIS_PATH = os.path.abspath(os.path.dirname(__file__) + "/../")
OUTPUT_PATH = f"{THIS_PATH}/output/"
CONFIG_PATH = f"{THIS_PATH}/.env"
CONFIG = dotenv_values(CONFIG_PATH)