import subprocess

from .config import load_config
from .db import enqueue_message, update_message_state, log_action
from .utils import hash_identifier, normalize_msisdn


def send_sms_via_gammu(number: str, text: str) -> bool:
    cfg = load_config()
    inject = cfg["sms"]["inject_bin"]
    try:
        res = subprocess.run(
            [inject, "TEXT", number, "-text", text],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return res.returncode == 0
    except Exception:
        return False


def enqueue_outbound_sms(sender_label: str, to_msisdn: str, body: str, ttl: int) -> int:
    to_msisdn = normalize_msisdn(to_msisdn)
    recipient_hash = hash_identifier(to_msisdn)
    sender_hash = hash_identifier(sender_label)
    return enqueue_message(
        direction="out",
        transport="sms",
        sender_hash=sender_hash,
        recipient_hash=recipient_hash,
        body=body,
        ttl_seconds=ttl,
        meta=None,
    )


def process_outbox_once():
    from .db import get_conn

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, recipient_hash, body, ttl_seconds, datetime(created_at) FROM messages
        WHERE direction='out' AND transport='sms' AND state='queued'
        ORDER BY id ASC
        """
    )
    rows = cur.fetchall()
    for mid, recipient_hash, body, ttl, created in rows:
        log_action(mid, "attempt_send", "start", notes=f"ttl={ttl}")
        update_message_state(mid, "error")
        log_action(mid, "attempt_send", "error", notes="No plaintext available for hash-only recipient")
