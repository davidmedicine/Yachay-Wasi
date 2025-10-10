import json
import time

import meshtastic
from meshtastic.serial_interface import SerialInterface

MSG = {"type": "consent_checked", "body": "hola"}


if __name__ == "__main__":
    iface = SerialInterface()
    iface.sendText(json.dumps(MSG))
    time.sleep(2)
    iface.close()
