# CI-B regression test ledger

Baseline `72619f46`; source `3825196a`. Jake explicitly approved replacing the
separate image composer/Gallery creation form with saved image chat turns. The
new UI preserves their retry, draft, save/share, cancellation and storage checks.
No timeout, performance target, assertion threshold or existing skip is relaxed.

| Existing file / assertion | Change | Reason and replacement coverage |
| --- | --- | --- |
| `composer-workflows.spec.ts`: image POST interception | `/images/jobs` becomes `/chats/*/images`; array seeds replace one seed | Approved durable chat-turn API; identical retry body/key and integer/range assertions retained |
| Same: prompt/create/save/back controls | New composer labels and actual image reply locator; Leave image mode replaces Message | Approved UI; seed remains hidden by default; save dialog, axe, focus, draft and workspace navigation assertions retained |
| Same: zero chat POSTs | Exactly one chat POST, with zero text-message POSTs in that counting scope | Images are explicitly saved chat turns; separate exact mixed-context/provider tests prove no image turn reaches the text runtime |
| Same: cancellation | New composer/card/status selectors; same cancellation, draft and saved-chat return assertions | Approved UI; stronger new API test verifies cancellation cannot stop a sibling turn's jobs |
| `images.spec.ts`: Gallery creation | New image navigates to chat composer; chat URL and durable reply assertions added | Approved Gallery library behavior; close/reopen, storage totals, save format, cancellation and removal/reload checks remain |
| Same: Use prompt for new version / seed input | Existing job API creates the lineage version; adds exact accepted parent/seed assertions | Gallery form is removed in CI-B; CI-C owns refinement UI. Old job lineage continues to be tested, and the new composer fixed-seed test covers UI validation/exact payload/two outputs |
| Four Python migration version assertions | Latest schema number increments 12→13 | Mechanical expectation; all existing row projection, integrity, privacy and idempotence assertions retained. New v12→v13 test compares every original column |

New tests in `test_chat_images.py`, `test_chat_images_migration.py`,
`image-state.test.ts` and `chat-images.spec.ts` cover atomic rollback, concurrent
idempotence, conflict, deleted-chat provenance, active text guard, branches,
context equality, literal output-limit payloads, automatic/fixed seeds, uncertain
acceptance, event snapshots, actual paused steps, real reveal events, output load
failure, scoped cancellation/removal and both reduced-motion triggers.

New-state axe checks audit 14 frame/step states × 2 themes × 2 widths × 2 engines.
Each state also renders counts 1/2/3. These are synthetic browser checks, not
native generation, factual accuracy or physical iPhone evidence.

Review fixes add explicit-versus-implicit parent identity tests and a browser
round trip between image and text user siblings. Image-user copy/branch controls
are preserved; their text-edit action is suppressed to avoid an unintended text
model request. No original assertion is removed.
