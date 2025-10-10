import os
import toml

_CFG = None


def load_config(path: str = None) -> dict:
    global _CFG
    if _CFG is not None:
        return _CFG
    path = path or os.environ.get("OFFLINE_AGENT_CONFIG", "config.toml")
    with open(path, "r", encoding="utf-8") as f:
        _CFG = toml.load(f)
    return _CFG
