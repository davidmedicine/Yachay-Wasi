import subprocess

from .config import load_config


def send_sms_via_gammu(number: str, text: str) -> bool:
    """
    Send SMS immediately using gammu-smsd-inject.
    """
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
