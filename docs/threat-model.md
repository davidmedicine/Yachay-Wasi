# Threat Model

Assets
- subscriptions (hashes + topics + user_code)
- community_consent ledger (granted/revoked + reason)
- processing logs and message metadata
- steward phonebook.csv (msisdn_hash -> MSISDN) [critical PII asset]
- device/SIM/RPi

Adversaries
- Opportunistic thieves, curious admins, network eavesdroppers.

Risks & Mitigations
- Phonebook exposure -> Store on encrypted USB; never email; rotate quarterly; strict steward custody.
- SIM misuse -> PIN on SIM; physical control; monthly audit.
- Metadata exposure -> Hash+salt in DB; keep plaintext MSISDN only in steward phonebook; no cloud sync.
- Device seizure -> Full-disk encryption; minimal retention; export only aggregates; fast purge procedures.
