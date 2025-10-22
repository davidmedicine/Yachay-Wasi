import csv
from pathlib import Path
from typing import Dict, Iterable

from .config import load_config
from .utils import normalize_msisdn


def load_phonebook_map() -> Dict[str, str]:
    """
    Load steward-managed CSV mapping msisdn_hash -> msisdn.
    Headers: msisdn_hash,msisdn
    Returns empty dict if file missing or malformed.
    """
    cfg = load_config()
    path = Path(cfg.get("phonebook", {}).get("mapping_csv", ""))
    if not path or not path.exists():
        return {}
    mapping: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return {}
        cols = {k.lower(): k for k in reader.fieldnames}
        h_hash = cols.get("msisdn_hash")
        h_msisdn = cols.get("msisdn")
        if not (h_hash and h_msisdn):
            return {}
        for row in reader:
            h = (row.get(h_hash) or "").strip()
            m = (row.get(h_msisdn) or "").strip()
            if not h or not m:
                continue
            try:
                mapping[h] = normalize_msisdn(m)
            except Exception:
                continue
    return mapping


def resolve_msisdns(hashes: Iterable[str]) -> Dict[str, str]:
    """
    Given msisdn_hashes, return mapping of hash -> msisdn for those present in phonebook.
    """
    book = load_phonebook_map()
    return {h: book[h] for h in hashes if h in book}
