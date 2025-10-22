# Ética: FPIC + Privacidad + Gobernanza Comunitaria

Principios
- FPIC (Consentimiento Libre, Previo e Informado) comunitario antes de operar.
- Participación individual por suscripción (SALUD, PRECIO, COMUNIDAD) y revocación (STOP).
- Mínimos datos: ningún MSISDN en la BD (solo hash salado), TTL de mensajes, sin analítica remota.
- Steward local: control de phonebook.csv (fuera de la BD, cifrado).
- No vigilancia: sin rastreo, sin nubes, sin scraping.

Procedimiento
- Asamblea comunitaria -> registrar en CLI:
  yachay-wasi community-consent --status granted --reason "Acta/fecha"
- Las personas se suscriben enviando SALUD/PRECIO/COMUNIDAD. Si no hay FPIC, el sistema no acepta suscripción.
- Revocación individual con STOP (se registra evento de revocación).

Cumplimiento
- Alineado a CARE Principles y UNESCO AI Ethics (2021).
- FPIC documentado y auditable (registro CLI y acta).
