# Yachay Wasi

Yachay Wasi: A community-owned information service for rural Peru. Delivers health, price, and community alerts via SMS, voice, and paper—without internet.

Features
- People subscribe via SMS: SALUD, PRECIO, COMUNIDAD
- STOP revokes all subscriptions (with a confirmation)
- Stewards broadcast alerts to topics via CLI
- Privacy by design: DB stores salted hashes, not phone numbers
- Offline-first: runs on Raspberry Pi + GSM modem (Gammu), zero cloud dependency

Principles
- Consent is opt-in, revocable, auditable
- Community consent (FPIC) precedes individual participation
- Data minimization: short TTLs; steward phonebook stays off-DB
- Stewardship and local control

Quick start
1) Copy config.toml.example to config.toml and edit for your deployment.
2) Initialize DB:
   python3 -m src.cli init-db
3) Record community consent:
   yachay-wasi community-consent --status granted --reason "Asamblea 2025-10-25"
4) Run SMS bridge (or use systemd):
   python3 -m src.sms_bridge
5) Broadcast (example):
   yachay-wasi broadcast --topic salud --text "Dra. Elena llega mañana, 8 a.m."

Docs: see docs/subscription-flows.md and docs/steward-guide.md.
# Yachay-Wasi
