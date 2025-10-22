import time
from pathlib import Path

from .config import load_config
from .utils import normalize_msisdn, hash_identifier
from .db import (
    enqueue_message,
    log_action,
    update_message_state,
    get_or_create_subscription,
    revoke_all_subscriptions,
    add_consent_event,
    latest_community_consent,
)
from .queue import send_sms_via_gammu

CONFIRM_TPL = "Gracias. Recibirás alertas de [{TOPIC_UP}]. Tu código es {CODE}. Di STOP para salir."
ALREADY_TPL = "Ya estás suscrito a [{TOPIC_UP}]. Tu código es {CODE}. Di STOP para salir."
STOP_GENERIC = "Has salido. Gracias por usar Yachay Wasi."
STOP_LIST_TPL = "Has salido de {TOPICS}. Gracias por usar Yachay Wasi."
NO_COMMUNITY_CONSENT = "El servicio está inactivo hasta el consentimiento de la comunidad. Consulta con la persona encargada."

TOPIC_KEYWORDS = {
    "salud": "SALUD",
    "precio": "PRECIO",
    "comunidad": "COMUNIDAD",
}


def parse_sms_file(path: Path):
    sender = None
    text_lines = []
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if line.startswith("From: "):
                sender = line.split(":", 1)[1].strip()
            elif line.startswith("Text: "):
                text_lines.append(line.split(":", 1)[1].strip())
            elif line.strip() and not any(
                line.startswith(prefix)
                for prefix in ("From:", "To:", "IMSI:", "SMSC:", "Sent:", "Text:")
            ):
                text_lines.append(line.strip())
    body = " ".join(text_lines).strip()
    return sender, body


def _join_es_topics(topics):
    # Convert to uppercase labels and join with commas and 'y'
    labels = [TOPIC_KEYWORDS.get(t, t).upper() for t in topics]
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + " y " + labels[-1]


def main():
    cfg = load_config()
    inbox = Path(cfg["paths"]["inbox_dir"])
    poll_interval = 2

    print(f"[yachay-wasi] polling inbox: {inbox}")
    inbox.mkdir(parents=True, exist_ok=True)

    seen = set()
    while True:
        for sms_path in inbox.glob("*.txt"):
            if sms_path in seen:
                continue
            try:
                sender, body = parse_sms_file(sms_path)
                if not sender or not body:
                    seen.add(sms_path)
                    continue
                try:
                    msisdn = normalize_msisdn(sender)
                except Exception:
                    seen.add(sms_path)
                    continue

                sender_hash = hash_identifier(msisdn)
                message_id = enqueue_message("in", "sms", sender_hash, None, body, cfg["policy"]["default_ttl"])
                log_action(message_id, "inbound", "parsed", notes=body[:160])

                lower = body.lower().strip()
                reply = None

                if lower in TOPIC_KEYWORDS:
                    # Check community consent gate
                    cc = latest_community_consent()
                    if cc != "granted":
                        reply = NO_COMMUNITY_CONSENT
                    else:
                        topic = lower
                        created, code = get_or_create_subscription(sender_hash, topic)
                        if created:
                            reply = CONFIRM_TPL.format(TOPIC_UP=TOPIC_KEYWORDS[topic], CODE=code)
                        else:
                            reply = ALREADY_TPL.format(TOPIC_UP=TOPIC_KEYWORDS[topic], CODE=code)

                elif lower == "stop":
                    topics = revoke_all_subscriptions(sender_hash)
                    if topics:
                        add_consent_event(sender_hash, "revoked")
                        reply_topics = _join_es_topics(sorted(set(topics)))
                        reply = STOP_LIST_TPL.format(TOPICS=reply_topics)
                    else:
                        reply = STOP_GENERIC

                else:
                    # Ignore everything else (no chat echo)
                    reply = None

                if reply:
                    ok = send_sms_via_gammu(msisdn, reply)
                    update_message_state(message_id, "delivered" if ok else "error")
                    log_action(message_id, "reply", "ok" if ok else "error", notes=reply)
                else:
                    update_message_state(message_id, "blocked")
                    log_action(message_id, "blocked", "no_reply")
            finally:
                try:
                    sms_path.unlink()
                except Exception:
                    pass
                seen.add(sms_path)
        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
