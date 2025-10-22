import sqlite3
import random
from pathlib import Path
from typing import Optional, Tuple, List

from .config import load_config

SCHEMA = r"""
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY,
    msisdn_hash TEXT UNIQUE NOT NULL,
    label TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Individual consent audit (minimal): currently used for revocation events.
CREATE TABLE IF NOT EXISTS consent_events (
    id INTEGER PRIMARY KEY,
    participant_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('revoked')) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(participant_id) REFERENCES participants(id) ON DELETE CASCADE
);

-- Community-level consent (FPIC): steward sets granted/revoked with a reason.
CREATE TABLE IF NOT EXISTS community_consent (
    id INTEGER PRIMARY KEY,
    status TEXT CHECK(status IN ('granted','revoked')) NOT NULL,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Topic subscriptions; user_code is unique 4-digit code for revocation/audit cards.
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY,
    participant_id INTEGER NOT NULL,
    topic TEXT CHECK(topic IN ('salud','precio','comunidad')) NOT NULL,
    user_code TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(participant_id) REFERENCES participants(id) ON DELETE CASCADE,
    UNIQUE(participant_id, topic)
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    direction TEXT CHECK(direction IN ('in','out')) NOT NULL,
    transport TEXT CHECK(transport IN ('sms','bt','dtn','lora')) NOT NULL,
    sender_hash TEXT,
    recipient_hash TEXT,
    body TEXT,
    ttl_seconds INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivered_at DATETIME,
    state TEXT CHECK(state IN ('queued','delivered','error','blocked')) NOT NULL DEFAULT 'queued',
    meta TEXT
);

CREATE TABLE IF NOT EXISTS processing_log (
    id INTEGER PRIMARY KEY,
    message_id INTEGER,
    action TEXT,
    status TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(message_id) REFERENCES messages(id) ON DELETE SET NULL
);
"""

_conn: Optional[sqlite3.Connection] = None


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        cfg = load_config()
        db_path = Path(cfg["paths"]["sqlite_path"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(db_path))
        _conn.execute("PRAGMA journal_mode=WAL;")
    return _conn


def init_db():
    conn = get_conn()
    with conn:
        conn.executescript(SCHEMA)


def upsert_participant(msisdn_hash: str, label: str = None) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM participants WHERE msisdn_hash=?", (msisdn_hash,))
    row = cur.fetchone()
    if row:
        pid = row[0]
    else:
        cur.execute("INSERT INTO participants(msisdn_hash,label) VALUES(?,?)", (msisdn_hash, label))
        pid = cur.lastrowid
    conn.commit()
    return pid


def add_consent_event(msisdn_hash: str, status: str) -> None:
    """
    Record an individual consent event (currently only 'revoked' on STOP).
    """
    pid = upsert_participant(msisdn_hash)
    conn = get_conn()
    with conn:
        conn.execute("INSERT INTO consent_events(participant_id,status) VALUES(?,?)", (pid, status))


def latest_community_consent() -> Optional[str]:
    """
    Returns 'granted' | 'revoked' | None if never set.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT status FROM community_consent ORDER BY created_at DESC, id DESC LIMIT 1"
    )
    row = cur.fetchone()
    return row[0] if row and row[0] else None


def set_community_consent(status: str, reason: Optional[str] = None) -> int:
    conn = get_conn()
    with conn:
        cur = conn.execute(
            "INSERT INTO community_consent(status,reason) VALUES(?,?)",
            (status, reason),
        )
        return cur.lastrowid


def _generate_unique_user_code(cur: sqlite3.Cursor) -> str:
    """
    Generate a globally-unique 4-digit user_code (1000-9999).
    Phase 1: 4 digits (simple). Future: 6 digits or alphanumeric.
    """
    while True:
        code = f"{random.randint(1000, 9999)}"
        cur.execute("SELECT 1 FROM subscriptions WHERE user_code=?", (code,))
        if cur.fetchone() is None:
            return code


def get_or_create_subscription(msisdn_hash: str, topic: str) -> Tuple[bool, str]:
    """
    Ensure a subscription exists for (participant, topic).
    Returns (created, user_code).
    """
    conn = get_conn()
    cur = conn.cursor()
    pid = upsert_participant(msisdn_hash)
    cur.execute(
        "SELECT user_code FROM subscriptions WHERE participant_id=? AND topic=?",
        (pid, topic),
    )
    row = cur.fetchone()
    if row:
        return False, row[0]
    user_code = _generate_unique_user_code(cur)
    with conn:
        cur.execute(
            "INSERT INTO subscriptions(participant_id,topic,user_code) VALUES(?,?,?)",
            (pid, topic, user_code),
        )
    return True, user_code


def revoke_all_subscriptions(msisdn_hash: str) -> List[str]:
    """
    Remove all subscriptions for a participant.
    Returns list of topic names that were removed.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM participants WHERE msisdn_hash=?", (msisdn_hash,))
    row = cur.fetchone()
    if not row:
        return []
    pid = row[0]
    cur.execute("SELECT topic FROM subscriptions WHERE participant_id=?", (pid,))
    topics = [r[0] for r in cur.fetchall()]
    with conn:
        cur.execute("DELETE FROM subscriptions WHERE participant_id=?", (pid,))
    return topics


def get_subscriber_hashes_by_topic(topic: str) -> List[str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.msisdn_hash
        FROM subscriptions s
        JOIN participants p ON p.id = s.participant_id
        WHERE s.topic=?
        ORDER BY p.id ASC
        """,
        (topic,),
    )
    return [r[0] for r in cur.fetchall()]


def enqueue_message(
    direction: str,
    transport: str,
    sender_hash: Optional[str],
    recipient_hash: Optional[str],
    body: str,
    ttl_seconds: int,
    state: str = "queued",
    meta: str = None,
) -> int:
    conn = get_conn()
    with conn:
        cur = conn.execute(
            "INSERT INTO messages(direction,transport,sender_hash,recipient_hash,body,ttl_seconds,state,meta) VALUES(?,?,?,?,?,?,?,?)",
            (direction, transport, sender_hash, recipient_hash, body, ttl_seconds, state, meta),
        )
        return cur.lastrowid


def update_message_state(msg_id: int, state: str):
    conn = get_conn()
    with conn:
        conn.execute(
            "UPDATE messages SET state=?, delivered_at=(CASE WHEN ?='delivered' THEN CURRENT_TIMESTAMP ELSE delivered_at END) WHERE id=?",
            (state, state, msg_id),
        )


def log_action(message_id: int, action: str, status: str, notes: str = None):
    conn = get_conn()
    with conn:
        conn.execute(
            "INSERT INTO processing_log(message_id,action,status,notes) VALUES(?,?,?,?)",
            (message_id, action, status, notes),
        )


def purge_participant_personal(msisdn_hash: str):
    """
    Remove participant and cascade to subscriptions & consent ledger.
    (Use with community governance approval.)
    """
    conn = get_conn()
    with conn:
        conn.execute("DELETE FROM participants WHERE msisdn_hash=?", (msisdn_hash,))
