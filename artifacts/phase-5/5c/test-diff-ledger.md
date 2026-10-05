# 5C test-diff ledger

| Existing test | Change | Reason | Assertions retained |
|---|---|---|---|
| `server/tests/test_foundation.py` / migration idempotence and private database | Exact schema version 6 → 7 | Authorized additive folder migration | Exact version on both starts; all privacy/idempotence checks retained |
| `server/tests/test_documents.py` / `test_phase5a_rows_and_meta_nullable_survive_migration` | Exact current schema version 6 → 7 | Test runs all current migrations | Exact version, NULL old metadata and every old column/row projection retained |

All other folder/backup tests are new. No existing browser test, timeout,
performance threshold or skip changed. The additive-API guard now compares
parameters by name/location, permitting optional additions while still rejecting
removal, changed schema/location, required additions and duplicates; new guard
regressions cover these cases. Existing API guard tests are unchanged.

The initial new migration test incorrectly treated the Phase 3 fixture as schema
3 (it is schema 4) and passed the snapshot tuple rather than its columns; these
new-test mistakes were fixed. The initial design run found dark destructive-button
contrast failures. Removing its old translucent fill fixed the implementation;
axe assertions were retained. Screenshots scroll synthetic components into view
so the phone evidence includes their controls.
