# Ethics: Consent-First, Community-Governed

This PoC follows **CARE Principles** and **UNESCO AI Ethics (2021)**:

- **Consent & Revocation:** Individuals can grant, deny, or revoke at any time (SMS commands: `CONSENT YES`, `CONSENT NO`, `REVOKE`).
- **Local Control:** Identifiers are salted & hashed. Keep plaintext outside the DB whenever possible.
- **Data Minimization:** No unnecessary collection; short, human-readable logs; TTL for messages.
- **No Surveillance:** No background scraping, no location tracking, no remote analytics.
- **Multilayer Governance:** Add community (ayllu) approval steps before deployments.

Add your CLPI/FPIC procedures here (who, how, when), and include bilingual (ES/EN + Quechua) versions of consent texts.
