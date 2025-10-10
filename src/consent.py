from typing import Optional

from .db import add_consent_event, latest_consent, upsert_participant
from .utils import hash_identifier, normalize_msisdn

CONSENT_OK = {"yes", "si", "sí", "grant", "accept"}
CONSENT_NO = {"no", "deny"}


def ensure_participant(msisdn: str) -> str:
    msisdn = normalize_msisdn(msisdn)
    hashed = hash_identifier(msisdn)
    upsert_participant(hashed)
    return hashed


def set_consent(msisdn: str, status: str, actor: str = "individual", reason: str = None):
    hashed = ensure_participant(msisdn)
    add_consent_event(hashed, status=status, actor=actor, reason=reason)
    return hashed


def check_consent(msisdn: str) -> Optional[str]:
    msisdn = normalize_msisdn(msisdn)
    hashed = hash_identifier(msisdn)
    return latest_consent(hashed)
