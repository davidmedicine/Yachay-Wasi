import sys
from pathlib import Path

from .sms_bridge import parse_sms_file
from .consent import set_consent, check_consent
from .queue import send_sms_via_gammu
from .utils import normalize_msisdn

ES_BLOCKED = "No hay consentimiento. Envía CONSENT YES para participar o HELP para ayuda."
ES_WELCOME = "Gracias. Tu consentimiento está registrado. Responde REVOKE para retirarlo."
ES_REVOKED = "Se ha revocado tu consentimiento. No procesaremos más mensajes."


def main():
    if len(sys.argv) < 2:
        sys.exit(0)
    path = Path(sys.argv[1])
    sender, body = parse_sms_file(path)
    if not sender:
        return
    try:
        msisdn = normalize_msisdn(sender)
    except Exception:
        return
    lower = (body or "").lower().strip()
    if lower.startswith("consent") and ("yes" in lower or "si" in lower or "sí" in lower or "grant" in lower):
        set_consent(msisdn, "granted")
        send_sms_via_gammu(msisdn, ES_WELCOME)
    elif lower.startswith("revoke"):
        set_consent(msisdn, "revoked")
        send_sms_via_gammu(msisdn, ES_REVOKED)
    else:
        status = check_consent(msisdn)
        if status != "granted":
            send_sms_via_gammu(msisdn, ES_BLOCKED)
        else:
            send_sms_via_gammu(msisdn, "Recibido. Gracias por tu mensaje.")


if __name__ == "__main__":
    main()
