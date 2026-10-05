# Phase 5 report

## Checkpoint 5A — presets, save clarity and model display names

### Summary

Presets copy a saved prompt and explicit sampling values into a chat. They can
be created, edited, reordered, deleted, and selected as the default for new chats.
Chat controls now validate inline, retain unsaved drafts by chat and model, and
show an explicit Saved result. Context length has a separate Apply action.
Model rename uses a dialog; renamed picker rows retain searchable runtime IDs.
5B and 5C have not started. This is the required 5A review stop.

Source commits: `074d674`, `f713414` on `codex/phase-5-everyday-chat`.

### Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| P5-AC1: preset sampling precedence | Pass | `test_presets.py`: exact captures without defaults; explicit keys override saved model defaults, omitted keys inherit them |
| P5-AC2: existing chats keep copied values | Pass | Unit byte comparison after preset edit/delete; `phase5a.spec.ts` existing-chat copy assertions |
| P5-AC3: validation, dirty/saved state, separate context | Pass | `phase5a.spec.ts`, `parameters.spec.ts`, `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| P5-AC4: display name and runtime ID | Pass | Rename, search, empty-name reset in `phase5a.spec.ts` |
| P5-AC11: checkpoint QA gates | Automated pass; review pending | Gates below |
| P5-AC12: web answers unchanged | Frozen pipeline | No changes under search, runs, providers or model-facing prompts; prompt and request guards pass |
| Documents, folders, automatic backups | Future checkpoints | 5B and 5C are intentionally not started |

### Changed files

- Server: additive preset schemas and `/api/presets` CRUD; migration
  `005_presets.sql`; default preset setting; optional `preset_id` on chat creation;
  copied prompt/parameters inserted when creating a chat.
- Web: `SamplingFields`, `PresetEditor`, `PresetsPane`, `ModelRename`, retained
  `control-drafts`; `LiveChatSettings`, `LiveAppShell`, `useSend`, Settings,
  command palette, picker, API types and error copy.
- Design: production components at `/design?everyday`; synthetic state captures.
- QA: new preset unit/browser tests and design axe checks; contrast coverage;
  privacy audit includes Phase 5; private-copy rollback rehearsal script.
- Docs: authorization and preset precedence recorded in AGENTS/SPEC/phase plan,
  this report, and `artifacts/phase-5/5a/` evidence.

### Deviations and clarifications

Jake answered “Do what you think is best” to the plan's contradiction between
exact preset-only sampling and preserving the existing model-default pipeline.
Presets override only their explicit keys; other keys inherit saved model defaults
and otherwise use runtime defaults. Empty presets add no sampling values of their
own. Presets never store reasoning or context. The provider/run pipeline is unchanged.
The controls explain this inheritance. The clarification is recorded in AGENTS,
SPEC and the phase plan, and tested against runtime request captures.

The phase plan said there was no display-name control, but the current app had
an input that saved on blur. This checkpoint replaces it with explicit Rename
and Cancel actions. Picker search already matched runtime IDs; that is retained.

Axe checks exposed background controls that were aria-hidden but focusable while
a Radix Select was open. Background branches are now inert until dismissal,
restored before focus returns. The desktop picker also gained its missing name.
The selected model's metadata now uses existing `text-2` over `brand-soft`;
`text-3` measured 4.48:1 there in WebKit. No palette token or threshold changed.

Visual review found the duplicate-name save alert below the editor scroll fold.
The stronger viewport assertion failed before the fix (`error-viewport-before.txt`).
Save errors now sit outside the scroll body, above the fixed footer. All eight
state variants passed the strengthened assertion and axe (`error-viewport-after.txt`).
The first full browser run passed 351 tests, but it preceded this visual fix;
`e2e-before-error-fix.txt` is retained separately. Final acceptance uses the new
complete invocation against `f713414`, not the earlier run or targeted results.

### Runtime observations

No provider, search engine or transcription engine implementation changed.
All new inference tests use the existing fake runtime and synthetic input.
No new packages or model calls were added. Installed service remains independent
of Codex's account usage limit.

### Test output

- `make check`: **217 Python tests**, **36 frontend unit tests**, **60 contrast
  pairs**; lint/types, additive API, motion, privacy and prompt guards pass.
- Coverage: providers **85.8%**, runs **89.2%**, search **88.9%**, transcribe **90.7%**.
- Build: passes (`build.txt`). The existing large-chunk notice remains; the
  measured initial gzip payload meets its budget.
- Existing skips, unchanged: WebKit real-time timeout gate (run in Chromium),
  foundation all-size screenshot capture (Chromium), and offline service-worker
  navigation (Playwright WebKit offline reload reports an internal navigation
  error; physical Safari verification remains separate).
- `make e2e`: **351 passed, three existing skips, 27.2 minutes**, in one complete
  invocation against `f713414` (`e2e.txt`).
- Preliminary targeted runs found the issues above and new-test selector/readiness
  errors. No failed run is counted as acceptance, and no existing assertion was
  loosened. Full-run acceptance requires one green invocation on frozen source.

### Budgets

| Measure | Phase 4A baseline | Previous deployed phone fix | 5A |
|---|---|---|---|
| Initial JS gzip | 224,491 B | 229,667 B | 233,783 B (+4,116 B) |
| Budget | 256,000 B | 256,000 B | Pass; increase below 8 KiB |
| Streaming p95 frame | 1.3 ms Chromium / 2 ms WebKit | See phone-fix regenerated metrics | 3.3 ms Chromium / 3.0 ms WebKit |
| First-token overhead | ≤82 ms | See phone-fix regenerated metrics | 67.95 ms Chromium / 61.05 ms WebKit |
| 300-message scroll | Existing performance suite | Pass | Pass; median scroll frames 16.7 / 17 ms |

Final timing JSON is retained under `regenerated/phase-1/` and
`regenerated/phase-3/`; historical phase artifacts were restored after testing.
Preset management and editor are lazy loaded. The existing timing thresholds
are unchanged. `bundle.json` records static-import gzip measurement.

### Gates

| Gate | Status | Evidence |
|---|---|---|
| G-1 check/coverage | Pass | `check.txt` |
| G-2 one complete browser run | Pass | `e2e.txt` |
| G-3 no weakened tests | Pass | Ledger below |
| G-4 performance | Pass | `bundle.json`; full performance tests |
| G-5 axe/contrast/keyboard | Pass | 60 token pairs; `design-axe-*.json`; existing keyboard suite |
| G-6 additive API | Pass | `check_api_additive.py`, `check.txt` |
| G-7 row preservation | Pass | `test_phase4_guards.py` migration fixture row hashes |
| G-8 prompt freeze | Pass | `test_prompt_hashes.py` |
| G-9 web eval when pipeline changes | Not triggered | No search/runs/providers changes; frozen source checked |
| G-10 ordinary payload unchanged | Pass | `test_phase4_guards.py` golden capture; existing exact-parameter captures |
| G-11 privacy | Pass | `privacy-audit.json`; invented fixtures only |
| G-12 deployment invariants | Pass | `test_deployment.py`, `pwa.spec.ts`; deployment metadata |
| G-13 reduced motion | Pass | `motion.spec.ts`, `phone-motion.spec.ts` |
| G-14 production design states | Pass | 19 states, two widths, two themes, two engines |
| G-15 rollback rehearsal | Pass | `rollback.json`, 3.18 seconds; procedure below |
| G-16 Jake phone check | Not checked for 5A | Review pending; earlier motion confirmation is in the separate phone report |

### Test-diff ledger

| Existing file/test | What changed | Why | Behavior still asserted? |
|---|---|---|---|
| `server/tests/test_foundation.py` migration idempotence | Schema version 4 → 5 | New additive migration | Yes; WAL, foreign keys, privacy and idempotence assertions retained |
| `web/tests/parameters.spec.ts` parameter integration | Click context Apply before Save | Context now has its own action | Yes; exact runtime options and system prompt retained |
| `web/tests/load-selection.spec.ts` context/load | Use separate Apply, first apply 16K then 32K; locate card through Rename button | Context action moved and display-name input became a dialog | Yes; selection, loading, context ceiling and request captures retained |
| `web/tests/ui-regressions.spec.ts` context validation | Assert restored value is valid, pristine Save disabled, changed context Apply enabled | Approved dirty-only saving and separate context action | Yes; invalid Save blocking and all layout checks retained; more validity assertions added |

No existing test was deleted, skipped, had its timeout raised, or had a runtime
or performance assertion loosened. New tests cover pristine default application
without an extra client patch, deferred chat loading, and draft isolation across
chats/models as well as the requested workflows.

### Core unchanged

All refer to the final single `e2e.txt` run, supplemented by `check.txt` unit guards:

| Core | Evidence |
|---|---|
| C1 send/stream/stats | `chat.spec.ts` |
| C2 stop/partial | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 reopen/reconnect | `chat.spec.ts`, `web.spec.ts` |
| C4 long answer/idle | `chat.spec.ts` |
| C5 message/chat actions and exports | `actions.spec.ts` |
| C6 model operations/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 explicit sampling | `parameters.spec.ts`, `test_chat.py`, `test_presets.py` |
| C8 search/citations/retry | `web.spec.ts`, search unit guards |
| C9 audio/transcript/download/retention | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts` |
| C10 phone layout/composer/drawers | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 palette/PWA/update | `polish.spec.ts`, `pwa.spec.ts` |
| C12 legacy read-only import | `test_legacy_import.py` |
| C13 deployment | `test_deployment.py`, deployment metadata |
| C14 untrusted input | `foundation.spec.ts`, SSRF unit tests |
| C15 performance | `performance.spec.ts`, chat frame and overhead tests |
| C16 axe/keyboard | `foundation.spec.ts`, `review.spec.ts`, `phase3-accessibility.spec.ts`, `phase5a-design.spec.ts` |

### Migrations and rollback

`005_presets.sql` creates one new table; pre-existing tables and rows are unchanged.
The synthetic Phase 3 fixture upgrade asserts identical old-column row hashes.

Rehearsal command: `. scripts/tool-env.sh; uv run --directory server python
../scripts/rehearse_presets_rollback.py --previous 4b312e2`.
The script copied the data folder privately, used SQLite online backup, started
current source with schema 5, added an invented preset, restored the original copy
without stale WAL/SHM, then started previous source with its installed static
build and schema 4. Health and app shell returned 200 in both versions, all old
row hashes matched, elapsed 3.18 s. The private copy was removed and production
was not modified. Output contains metadata only. Deployment took a fresh online backup before installing 5A.
`deployment-invariants.json` verifies health 200 locally and over Tailscale, schema
5, unchanged service arguments/label/Tailscale configuration, production `/design`
404, byte-identical installed static assets, and the new preset/bootstrap fields.
Backup count increased from six to seven. TLS was verified using the existing
certifi CA bundle and independently with system curl; no TLS verification was disabled.

### Evals

No prompt, provider, run or search implementation changed, so QA G-9's conditional
eval is not triggered. Prompt hashes and ordinary payload capture remain identical.
The full suite retains deterministic fake web-answer/citation assertions.
No live model eval or new model call was performed for this checkpoint.

### Screenshots

`artifacts/phase-5/5a/`: 152 synthetic state screenshots (19 states × 2 widths × 2 themes
× 2 engines), plus eight focused `context-visible-*-fake.png` captures. Names end in `-fake.png`. States: controls pristine, invalid, dirty,
saved, loading/error; context invalid/apply; preset select/list/default/editor/
collision/delete/empty/error/loading; model rename and renamed picker.
Per-variant `design-axe-*.json` records zero serious/critical requirements.
`context-visible-fake.json` verifies the input is in view and axe finds no
serious/critical violations in the focused group at both widths/themes/engines.
All final captures were visually reviewed through contact sheets, with individual
mobile editor/error and context inspection (`visual-review.json`). One additional
before-fix screenshot is retained as failure evidence, bringing the PNG total to 161.
No physical-phone screenshot or real content is saved.

### Known limitations carried forward

VoiceOver was user-reported failed and remains deferred; this report does not
claim it passed. The earlier iOS keyboard problem recovered after restart; its
cause is unproven. Dirty control drafts survive panel closing/navigation in the
current session, not a page reload. Preset reorder uses sequential additive PATCH
requests; a connection failure can leave partial order, reported inline.

### Open questions for Jake

5A is the next review. On the installed phone app, try a preset, save controls,
close/reopen with unsaved changes, apply context separately, and rename a model.
The normal phone checklist in QA §7 still applies. 5B (documents) waits for review.
