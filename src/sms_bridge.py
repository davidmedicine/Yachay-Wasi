import time
from pathlib import Path

from .config import load_config
from .utils import normalize_msisdn, hash_identifier
from .db import enqueue_message, log_action, update_message_state
from .consent import check_consent, set_consent
from .queue import send_sms_via_gammu

WELCOME = {
    "es": "Gracias. Tu consentimiento está registrado. Responde REVOKE para retirarlo en cualquier momento.",
    "en": "Thanks. Your consent is recorded. Reply REVOKE to withdraw at any time.",
}

HELP = {
    "es": "Comandos: CONSENT YES/NO, REVOKE, HELP.",
    "en": "Commands: CONSENT YES/NO, REVOKE, HELP.",
}

REVOKED = {
    "es": "Se ha revocado tu consentimiento. No procesaremos más mensajes.",
    "en": "Your consent has been revoked. We will no longer process messages.",
}

BLOCKED = {
    "es": "No hay consentimiento. Envía CONSENT YES para participar o HELP para ayuda.",
    "en": "No consent on file. Send CONSENT YES to participate or HELP for help.",
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
            elif line.strip() and not any(line.startswith(prefix) for prefix in ("From:", "To:", "IMSI:", "SMSC:", "Sent:", "Text:")):
                text_lines.append(line.strip())
    body = " ".join(text_lines).strip()
    return sender, body


def main():
    cfg = load_config()
    inbox = Path(cfg["paths"]["inbox_dir"])
    poll_interval = 2

    print(f"[bridge] polling inbox: {inbox}")
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
                log_action(message_id, "inbound", "parsed", notes=body[:120])

                lower = body.lower().strip()
                reply = None
                if lower.startswith("consent"):
                    if "yes" in lower or "si" in lower or "sí" in lower or "grant" in lower:
                        set_consent(msisdn, "granted")
                        reply = WELCOME["es"]
                    elif "no" in lower or "deny" in lower:
                        set_consent(msisdn, "denied")
                        reply = BLOCKED["es"]
                elif lower.startswith("revoke"):
                    set_consent(msisdn, "revoked")
                    reply = REVOKED["es"]
                elif lower.startswith("help"):
                    reply = HELP["es"]
                else:
                    status = check_consent(msisdn)
                    if status != "granted":
                        reply = BLOCKED["es"]
                    else:
                        reply = "Recibido. Gracias por tu mensaje."

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
