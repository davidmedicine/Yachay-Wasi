
# Yachay-Wasi — Community-Governed Offline AI Messenger (SMS)  
**Research Preview (v0.1)**

Yachay-Wasi is an **offline-first** SMS knowledge and alerts system designed for rural contexts where internet access is unreliable. It runs locally (e.g., Raspberry Pi) and can optionally provide AI-assisted replies using a **local LLM**—with consent and community governance.

This repo is part of **Qori Labs** (Public Interest Technology Lab): we build “Sovereign Layers” where connectivity, cognition (local AI), and governance are designed for **local control**.

---

## What it does

### 1) SMS knowledge requests (offline)
Examples:
- `PRECIO papa` → local reference prices (from a steward-curated KB)
- `CLIMA` → local agronomic tips (not a weather forecast)
- `HISTORIA pachamama` → approved cultural stories (if enabled)

### 2) Community alerts (SMS broadcast)
Topics can include:
- `SALUD`, `COMUNIDAD`, `PRECIO` (configurable)

### 3) Optional local AI replies (only if enabled + authorized)
- Runs a small local model via `llama.cpp` (no cloud)
- Keeps responses short (SMS-friendly)

---

## Governance & consent (core requirement)

Yachay-Wasi is designed to operate under local authority:

- **Separate consents:**  
  - Service consent (SMS system)  
  - AI consent (local inference features)
- `STOP` revokes subscriptions (and can be extended to revoke AI access).
- Governance is enforceable locally (steward tools + offline control).

---

## Privacy by design (offline-first)

- No cloud by default.
- No external telemetry required.
- Storage can be configured to minimize retention.
- Phone identifiers can be hashed; offline mapping can be steward-held.

---

## How it works (architecture)

1) **Gammu SMSD** writes inbound SMS to a local spool.
2) `sms_bridge` parses messages, enforces consent rules, routes requests.
3) The **local KB** provides approved reference content (CSV/YAML files).
4) If AI is enabled + authorized, the bridge calls the local LLM to generate a short response.
5) Replies are returned via SMS.

Everything runs on the local device.

---

## Requirements

- Raspberry Pi 4 (4GB recommended; 2GB minimum)
- GSM modem compatible with Gammu
- Linux, Python 3, SQLite, Gammu/SMSD
- `llama.cpp` + a small quantized model (e.g., TinyLlama q4) if using AI mode

---

## Quick start (high-level)

### Configure
Copy `config.toml.example` → `config.toml` and set:
- paths (sqlite, inbox dir)
- phonebook mapping location (optional)
- AI settings (default off)

### Initialize
```bash
python3 -m src.cli init-db
Set consent (example)
bash
Copy code
yachay-wasi consent --status granted --reason "Asamblea YYYY-MM-DD"
(Optional) Enable AI only after separate consent
bash
Copy code
yachay-wasi ai-consent --status granted --reason "Acta AI YYYY-MM-DD"
yachay-wasi ai --enable
Run
bash
Copy code
python3 -m src.sms_bridge
Safety notes
Use public/permitted or synthetic datasets for demos.

Avoid sensitive personal content.

Health messaging should be educational and defer to local health workers.

This is a research prototype; validate locally before field use.

License
MIT. (Community stewardship is a governance norm even when code is open.)
