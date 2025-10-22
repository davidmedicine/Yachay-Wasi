import os
import toml

_CFG = None


def load_config(path: str = None) -> dict:
    """
    Load configuration. Defaults to env YACHAY_WASI_CONFIG or ./config.toml.
    """
    global _CFG
    if _CFG is not None:
        return _CFG
    path = path or os.environ.get("YACHAY_WASI_CONFIG", "config.toml")
    with open(path, "r", encoding="utf-8") as f:
        _CFG = toml.load(f)
    return _CFG
