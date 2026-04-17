Yachay-Wasi — Community-Governed Offline AI Messenger (SMS)

Research Preview (v0.1)

Yachay-Wasi is an SMS-based knowledge and alerts system designed as offline-first for rural contexts where internet access is unreliable. It runs locally (for example, on a Raspberry Pi) and can optionally provide AI-assisted responses using a local LLM, always with community consent and governance.

This repository is part of Qori Labs (Public Interest Technology Lab): we build “Sovereign Layers” where connectivity, cognition (local AI), and governance are designed for local control.

What it does
Knowledge queries by SMS (offline)

Examples:

PRECIO papa → local reference prices (from a knowledge base curated by custodians)
CLIMA → local agronomic advice (not a weather forecast)
HISTORIA pachamama → approved cultural stories (if enabled)
Community alerts (SMS broadcast)

Topics may include:

SALUD, COMUNIDAD, PRECIO (configurable)
Optional local AI responses (only if enabled and authorized)
Runs a small local model through llama.cpp (no cloud)
Keeps responses short (SMS-friendly)
Governance and consent (core requirement)

Yachay-Wasi is designed to operate under local authority.

Separate consent layers:

Service consent (SMS system)
AI consent (local inference features)

STOP revokes subscriptions (and can be extended to revoke AI access as well).

Governance is enforceable locally through custodial tools and offline control.

Privacy by design (offline-first)
No cloud by default
No external telemetry required
Storage can be configured to minimize data retention
Phone identifiers can be hashed; offline identity mapping may remain in the hands of local custodians
How it works (architecture)
Gammu SMSD writes incoming SMS messages to a local spool
sms_bridge parses messages, applies consent rules, and routes requests
The local knowledge base provides approved reference content (CSV/YAML files)
If AI is enabled and authorized, the bridge calls the local LLM to generate a short response
Replies are sent back by SMS
Everything runs on the local device
Requirements
Raspberry Pi 4 (4GB recommended; 2GB minimum)
GSM modem compatible with Gammu
Linux, Python 3, SQLite, Gammu/SMSD
llama.cpp + a small quantized model (for example, TinyLlama q4) if AI mode is used
Quick start (high level)
Setup

Copy config.toml.example to config.toml and define:

paths (SQLite, inbox directory)
phonebook mapping location (optional)
AI settings (disabled by default)
Initialize
python3 -m src.cli init-db
Set service consent (example)
yachay-wasi consent --status granted --reason "Assembly YYYY-MM-DD"
Optional: enable AI only after separate consent
yachay-wasi ai-consent --status granted --reason "AI Record YYYY-MM-DD"
yachay-wasi ai --enable
Run
python3 -m src.sms_bridge
Safety notes
Use public, permitted, or synthetic datasets for demonstrations
Avoid sensitive personal content
Health-related messages should be educational and refer users to local health workers
This is a research prototype; validate locally before field use
License

MIT. (Community stewardship remains a governance norm even when the code is open.)

If you want, I can also turn this into a cleaner README-style version for GitHub.
