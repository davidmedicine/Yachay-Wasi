# Threat Model (PoC)

**Assets:** consent ledger, message contents, identifier hashes, device/SIM.

**Adversaries:** opportunistic thieves, curious admins, network eavesdroppers.

**Risks & Mitigations**
- SIM misuse → PIN on SIM; physical control; monthly audit.
- Metadata exposure → Hash + salt; keep plaintext off DB; rotate salt (with re-consent) if needed.
- Device seizure → Full-disk encryption; minimal retention; export only aggregates.
- Sensitive knowledge → Sacred/community/public classifier and human council veto (to be implemented in production).
