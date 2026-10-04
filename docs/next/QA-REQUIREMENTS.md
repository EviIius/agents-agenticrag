# QA requirements for Phases 4 to 8

**For:** Codex · **Applies to:** every checkpoint in `docs/next/` · **Extends:** `docs/SPEC.md` §H2–H4

One principle: **the core is frozen.** Chat, web search and transcription work today and Jake uses them. Every phase after 3 is additive. A checkpoint is not done if existing behavior regresses. Explicitly approved changes, such as Phase 4 C1 send timing and Phase 5 presets, need their own assertions and a documented exception to the baseline.

---

## 1. The core, and what guards it

These flows must behave exactly as they do at commit `66a8c6b`. Each is already covered; the right-hand column is what must keep passing.

| # | Core flow | Guarded by |
|---|---|---|
| C1 | Send, stream, complete, stats | `chat.spec.ts` "live chat …" |
| C2 | Stop keeps the partial answer and closes the runtime connection | `chat.spec.ts` "Stop persists partial text…"; `phase3-accessibility.spec.ts` "Escape stops a send…" |
| C3 | Close the tab mid-answer, reopen, and the stream resumes exactly | `chat.spec.ts` "close tab and reopen…"; `web.spec.ts` "a late streaming chat snapshot cannot erase…" |
| C4 | Long answers and idle timeouts keep partial text | `chat.spec.ts` "long answer completes beyond 90 seconds…" |
| C5 | Regenerate, edit, branch navigation, rename, pin, export, delete | `actions.spec.ts` |
| C6 | Load, eject and select a model; context length | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 | Only the parameters the user set reach the runtime | `parameters.spec.ts`; `test_chat.py` request captures |
| C8 | Web answer with citations, card, Sources; skip; failure and retry | `web.spec.ts`; `test_search.py`, `test_web_evidence.py`, `test_web_grading.py`; `make eval-web` |
| C9 | Recording: upload, transcribe, review, download, ask; web guard; audio retention and clearing | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts`; `test_transcription.py` |
| C10 | Phone layout, safe areas, keyboard, drawers | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 | Command palette, shortcuts, PWA shell, update prompt, no API caching | `polish.spec.ts`, `pwa.spec.ts` |
| C12 | Legacy import is read-only and idempotent | `test_legacy_import.py` |
| C13 | Deployment keeps `127.0.0.1:8787`, the launchd label and the Tailscale route | `test_deployment.py` |
| C14 | Untrusted content cannot inject HTML, scripts or remote images | `foundation.spec.ts` "untrusted Markdown…"; SSRF tests in `test_search.py` |
| C15 | Performance budgets | `performance.spec.ts`; the two frame and first-token tests in `chat.spec.ts` |
| C16 | Accessibility on every screen, both themes | `foundation.spec.ts`, `review.spec.ts`, `phase3-accessibility.spec.ts` |

## 2. Baseline

Phase 3 reported these figures. Re-measure them in Phase 4 step 4A.1 and treat the re-measured values as the baseline; if they differ from this table, say so.

| Measure | Phase 3 report |
|---|---|
| `make check`: Python tests | 207 |
| `make check`: frontend unit tests | 36 |
| Contrast pairs | 56 |
| Coverage: providers / runs / search / transcribe | 85.8% / 89.2% / 88.9% / 90.7% |
| Vendored engine tests | 44 |
| `make e2e` | 221 runnable cases, 3 documented skips |
| Initial JS, gzip | 224,491 bytes (budget 256,000) |
| Streaming frame time at 100 tok/s | p95 1.3 ms Chromium, 2 ms WebKit |
| First-token overhead | ≤ 82 ms |
| Web eval, offline replay | Phase 2 closeout reports |

One thing to correct going forward: Phase 3 closed without a single fully green E2E run (220 passed and 1 failed in the full run; the failure was fixed and re-run on its own). That was reported honestly, and it is not good enough as a habit. See G-2.

## 3. Gates

Every gate applies at every checkpoint unless it says otherwise. Each needs evidence in the report: a test name, a command's output file, or an artifact path.

| ID | Gate | How it is checked |
|---|---|---|
| G-1 | **`make check` is green.** Test counts are at or above baseline. Line coverage ≥ 80% for `providers`, `runs`, `search`, `transcribe` and every new server package (`documents`, `library`, and Research's module as they appear; add them to `TARGETS` in `scripts/check_coverage.py`). | `check.txt` |
| G-2 | **`make e2e` is green in one complete run**, Chromium and WebKit. Not assembled from partial runs. A test that fails and then passes on a rerun is flaky: fix it, or list it for Jake; do not ignore it. | `e2e.txt` from a single invocation |
| G-3 | **No test was weakened.** Any edit to an existing test is in the ledger (§4). | `test-diff-ledger.md` |
| G-4 | **Performance budgets** (§G10) re-measured: initial JS ≤ 250 KiB gzip and no more than 8 KiB above the previous phase unless the report justifies it (new Settings sections and sheets are lazy-loaded); streaming ≤ 8 ms per frame at 100 tokens per second with only the streaming row rendering; 300-message scroll; first-token overhead ≤ 150 ms. | `bundle.json`, performance JSON |
| G-5 | **Accessibility.** Axe: zero serious or critical findings on every screen and every new state, both themes, at 390 and 1440, after `settle()`. Contrast script passes and covers new text-bearing tokens. The keyboard walkthrough spec passes. VoiceOver remains a recorded limitation; nothing may make it worse. | axe output, `check.txt` |
| G-6 | **The API only grows.** `scripts/check_api_additive.py` compares the current OpenAPI document with `artifacts/baseline/openapi-phase3.json` (save it in 4A.1): no removed path, method or field; no changed type; no new required request field. Response enums may gain values. | script output |
| G-7 | **The database only grows.** Migrations are numbered, transactional and forward-only. No `DROP`, no rename, and no rebuild of `chats`, `messages`, `attachments`, `transcripts`, `message_sources` or `web_reads` without Jake's approval. A migration test upgrades a synthetic Phase 3 database (`server/tests/fixtures/db/phase3.db`, generated by a committed script: chats with branches, a web answer with sources, a recording with a transcript, an imported legacy chat, settings) and asserts row hashes projected onto every pre-existing column are unchanged; added columns are verified separately. | test name |
| G-8 | **Prompts are frozen.** `server/tests/test_prompt_hashes.py` holds the SHA-256 of every model-facing prompt: planner, web answer, title, transcript clean-up, and later library and research. Changing a prompt means changing its hash in the same commit that links the before-and-after eval report. | test name |
| G-9 | **Web answers are unchanged.** Whenever anything under `server/app/search`, `runs` or `providers` changes: `make eval-web` offline replay is equal or better on every aggregate, and no case flips from pass to fail. | eval report |
| G-10 | **Runtime payloads are unchanged** for an ordinary chat: a golden request capture (default chat, no parameters set) matches byte for byte after explicit normalization of nondeterministic identifiers and timestamps only; parameter presence and values are never normalized. Unset sampling parameters are absent. No `tools` key unless Research is on. | test name |
| G-11 | **Privacy.** No real recording, transcript, glossary entry, library text or their filenames in Git, logs, fixtures, screenshots, videos or reports. A script (`scripts/privacy_audit.py`; turn the Phase 3 audit into one if it is not already) scans the diff and `artifacts/` for media files, known private marker strings and anything shaped like a key. Screenshots use synthetic data and say "fake" in the name. The scanner is a guard, not proof of screenshot privacy; capture only isolated synthetic fixtures and review images before committing. | `privacy-audit.json` |
| G-12 | **Deployment invariants.** Bind `127.0.0.1:8787`, one worker, the existing launchd label, the existing Tailscale route, `/design` returns 404 in production, the service worker never caches `/api`, deployment takes a database backup first. | `test_deployment.py`, `pwa.spec.ts` |
| G-13 | **Reduced motion** (from Phase 4 on): both triggers remove every animation and transition. | `motion.spec.ts` |
| G-14 | **`/design` shows every new state, built from production components.** | screenshot list |
| G-15 | **Rollback rehearsed** (checkpoints that add a migration): on a copy of the data folder, deploy the new build, then restore the pre-deploy backup with the previous commit, and confirm the app starts with the old data. Record the commands and the time taken. | report section |
| G-16 | **Jake's phone check** (§7) at each stop marked for review. | Jake's words, quoted |

## 4. The test-diff ledger

A table in every report, one row per edit to an existing test file:

| File and test | What changed | Why | Behavior still asserted? |
|---|---|---|---|

Allowed: a selector or label changed because the spec changed it (for example "Save & submit" became "Send"); a `settle()` call added; a test extended with more assertions.

Not allowed without stopping to ask: deleting a test; removing or loosening an assertion; raising a timeout or a performance threshold; adding a skip; replacing a real interaction with a mocked one.

## 5. Tooling to add (Phase 4A unless noted)

| Tool | Purpose |
|---|---|
| `web/tests/helpers.ts` `settle(page)` | Wait for finite animations before axe and screenshots. |
| `scripts/check_motion.py` | No dead animation classes, no `transition-all`, keyframes only in `motion.css`. In `make check`. |
| `scripts/check_api_additive.py` + `artifacts/baseline/openapi-phase3.json` | G-6. In `make check`. |
| `server/tests/fixtures/db/phase3.db` + generator script | G-7. |
| `server/tests/test_prompt_hashes.py` | G-8. |
| Golden request capture | G-10. |
| `scripts/privacy_audit.py` | G-11. In `make check`. |
| `make eval-library` (Phase 7), `make eval-research` (Phase 8) | Feature evals. |

These tools change no product behavior. Add them before the first feature commit of the phase that needs them.

## 6. How to test motion

Stills cannot show it, and a green test cannot say whether it feels right.

- **Automated:** `motion.spec.ts` asserts that animations exist, end, do not replay, do not shift layout and disappear under reduced motion (Phase 4 §8.1).
- **Performance:** the existing frame-time tests run with motion on, thresholds unchanged.
- **Recordings:** eight short Playwright videos with synthetic data, kept out of Git (Phase 4 §8.3).
- **By hand:** Jake's phone check after 4B and 4D. Feel is his call.

## 7. Jake's phone check (about five minutes)

Installed app, over Tailscale. Codex prepares the preview and lists anything phase-specific to add.

1. Open from the home screen. It loads and the composer is ready.
2. Send a short message. The bubble appears at once, the answer streams, the stats line appears.
3. Send a long request and press Stop. The partial answer stays.
4. Switch models from the picker. The top bar shows the new one.
5. Turn on Search and ask something current. Tap a citation; the card opens and closes.
6. Open a chat that has a recording, or add a short one. Ask about it.
7. Open the sidebar, search, open an older chat.
8. Open and close Settings. Change the theme.
9. Tap the composer. The keyboard opens and the composer stays above it.
10. Settings › Appearance › Reduce motion › Always. Nothing animates. Set it back.

Record Jake's answer in the report in his own words. "Not checked" is an acceptable entry; an invented result is not.

## 8. Report additions

Use the §H4 template. Add these sections:

- **Gates:** the §3 table with a status and evidence for each row.
- **Test-diff ledger** (§4).
- **Budgets:** baseline, previous phase, now.
- **Core unchanged:** one line per C1–C16 naming the passing test run.
- **Migrations and rollback:** files added, fixture migration result, rehearsal notes (G-15).
- **Evals:** which ran, links to reports, any case that changed outcome.
- **Known limitations carried forward:** VoiceOver; the iOS keyboard focus issue seen on 3 October (recovered after a restart, cause unproven); anything new.

## 9. Stop and ask Jake when

- A gate cannot be met.
- A core test would need a behavioral change to pass.
- A dependency seems necessary that the phase document does not already approve.
- A real runtime, the transcription engine or SQLite behaves differently from the spec.
- A migration would need to rebuild or drop an existing table.
- A prompt edit seems necessary.
- An eval target is missed.
- Anything would touch the port, the bind address, the launchd label, the Tailscale configuration or legacy data.
- Real private content is needed to reproduce a problem.

Stopping with a clear question is a good outcome. A workaround that hides the problem is not.
