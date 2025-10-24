GitHub README (reescrito)
Yachay Wasi: Community-Governed Offline AI Messenger (SMS)

Yachay Wasi is a community-owned, offline-first AI messenger for rural Peru. It delivers on-demand knowledge and community alerts via simple SMS—no internet, no apps, no surveillance.
What it does

On-demand Q&A (offline LLM on Raspberry Pi):
CLIMA  → local agronomic tips (from community calendar; not a forecast)
PRECIO  → fair market reference prices (from local KB)
HISTORIA pachamama → approved cultural stories

Dual language:
Responds in Spanish or Quechua (auto or via keyword ES/QU)
Alerts still supported:
Topics: SALUD, PRECIO, COMUNIDAD
Consent-first:

FPIC required; separate FPIC to activate AI
STOP revokes all subscriptions
Privacy by design:

DB stores salted hashes, not phone numbers
Phonebook (hash→MSISDN) stays offline, steward-held
No cloud, no data extraction
How it works (architecture)
Gammu SMSD writes incoming SMS to a local spool; sms_bridge.py parses, enforces FPIC, routes queries.
If AI is enabled and authorized, sms_bridge calls the local LLM (llama.cpp) to generate a short reply (<160 chars).
Knowledge base (KB) is local and steward-curated: prices.csv, calendario.yml, historias.yml.
All inference happens on the Raspberry Pi. No internet needed.
Requirements
Raspberry Pi 4 (4 GB recommended; 2 GB minimum), GSM modem compatible with Gammu
Linux, Python 3, SQLite3, Gammu/SMSD
llama.cpp and a small quantized chat model (e.g., TinyLlama-1.1B-Chat q4)
Quick start
Configure
Copy config.toml.example to config.toml and set:
[core] salt, sqlite_path, inbox_dir
[phonebook] mapping_csv (USB, encrypted)
[ai] enabled=false (default), model_path, mode=server or on-demand
Initialize
python3 -m src.cli init-db
yachay-wasi community-consent --status granted --reason "Asamblea 2025-10-25"
(Optional) Enable AI after FPIC for AI
yachay-wasi ai-consent --status granted --reason "Acta AI 2025-11-10"
yachay-wasi ai --enable
Test locally: yachay-wasi ai --ask "PRECIO papa" --lang ES
Run services
SMS bridge: python3 -m src.sms_bridge
Or via systemd: yachay-wasi.service
For LLM server mode: yachay-wasi-llm.service (llama.cpp server with your model)
Examples (SMS)
“PRECIO papa” → short price guidance from KB
“CLIMA papa QU” → short agronomic tip in Quechua
“HISTORIA pachamama ES” → brief approved story
“SALUD” / “COMUNIDAD” → subscribe to alerts
“STOP” → revoke all
Steward CLI highlights
yachay-wasi broadcast --topic salud --text "Dra. Elena llega mañana, 8 a.m."
yachay-wasi kb import --file kb/precios.csv
yachay-wasi ai --status | --enable | --disable
yachay-wasi ai-consent --status granted|revoked --reason "Acta…"
yachay-wasi status
Safety, consent, and ethics
Separate FPICs: service FPIC and AI FPIC
No personal data to the model; queries aren’t kept beyond TTL
Only public/communal knowledge; no sacred content
Health content is educational; always refer to local health workers
Performance tips
Use server mode to keep the model loaded (faster replies)
Keep responses under 160 chars (configured in [ai].max_chars)
Start with TinyLlama q4; test temperature 0.6–0.8 and max_tokens ~80
Roadmap
Better Quechua support (community-approved datasets)
Optional IVR for low-literacy users
Co-designed response templates with elders and farmers
Docs
docs/subscription-flows.md
docs/steward-guide.md
docs/ai-setup.md (llama.cpp, models, prompts, KB)
License
MIT. Community stewardship required by norm and practice, even if code is open.

