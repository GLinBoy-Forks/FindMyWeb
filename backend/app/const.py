import os

from app.config import load_config

DEFAULT_CFG_PATH = "config.toml"
CFG_PATH = (
    os.environ["CONFIG_PATH"]
    if os.environ.get("CONFIG_PATH", None)
    else DEFAULT_CFG_PATH
)
MAINTENANCE_MODE = True if os.environ.get("MAINTENANCE", None) else False

CONFIG = load_config(CFG_PATH)

COLOR_REGEX_STR = r"^#(([0-9a-fA-F]{2}){3}|([0-9a-fA-F]){3})$"
