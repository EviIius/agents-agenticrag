# 5B test-diff ledger

| Existing file / test | Change | Reason | Assertions retained |
|---|---|---|---|
| `server/tests/test_foundation.py` / `test_migration_is_idempotent_and_private` | Expected current `user_version` changes from 5 to 6 | Authorized additive `006_attachment_meta.sql` migration | Same exact version assertion on both starts; idempotence and private-file checks retained |

All document unit/browser/design tests are new. No existing test was deleted,
skipped, loosened, given a higher timeout, or had a performance threshold raised.
The initial new browser tests had a selector mistake; the corrected tests click
the actual model option. Additional menu axe coverage found hidden focusable
background content; the attachment menu now uses native inert background handling
matching the existing Select pattern. Final acceptance requires the complete E2E
run, not a combination of these focused runs.
