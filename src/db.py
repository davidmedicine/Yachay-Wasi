import sqlite3
from pathlib import Path
from typing import Optional

from .config import load_config

SCHEMA = r"""
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY,
    msisdn_hash TEXT UNIQUE NOT NULL,
    label TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consent_events (
    id INTEGER PRIMARY KEY,
    participant_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('granted','denied','revoked')) NOT NULL,
    actor TEXT,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(participant_id) REFERENCES participants(id) ON DELETE CASCADE
);

CREATE VIEW IF NOT EXISTS v_consent_latest AS
SELECT p.id AS participant_id,
       p.msisdn_hash,
       (SELECT status FROM consent_events ce
         WHERE ce.participant_id = p.id
         ORDER BY ce.created_at DESC, ce.id DESC LIMIT 1) AS latest_status
FROM participants p;

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


def latest_consent(msisdn_hash: str) -> Optional[str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT latest_status FROM v_consent_latest WHERE msisdn_hash= ?",
        (msisdn_hash,),
    )
    row = cur.fetchone()
    return row[0] if row and row[0] else None


def add_consent_event(msisdn_hash: str, status: str, actor: str = None, reason: str = None) -> None:
    pid = upsert_participant(msisdn_hash)
    conn = get_conn()
    with conn:
        conn.execute(
            "INSERT INTO consent_events(participant_id,status,actor,reason) VALUES(?,?,?,?)",
            (pid, status, actor, reason),
        )


def enqueue_message(
    direction: str,
    transport: str,
    sender_hash: str,
    recipient_hash: str,
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
    conn = get_conn()
    with conn:
        conn.execute("DELETE FROM participants WHERE msisdn_hash=?", (msisdn_hash,))
