import hashlib
import re

from .config import load_config

PHONE_RE = re.compile(r"[+0-9]{6,15}")


def hash_identifier(raw: str) -> str:
    cfg = load_config()
    salt = cfg["core"]["salt"].encode("utf-8")
    return hashlib.sha256(salt + raw.encode("utf-8")).hexdigest()


def normalize_msisdn(msisdn: str) -> str:
    s = msisdn.strip().replace(" ", "")
    if not PHONE_RE.fullmatch(s):
        raise ValueError("Invalid MSISDN format")
    return s
