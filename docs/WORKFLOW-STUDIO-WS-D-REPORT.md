# Workflow Studio WS-D report

## Summary

Claude's Studio layout now runs real saved graphs: live canvas/timeline states,
streamed text, actual image steps, approvals, favorites and retry controls.
Verified reuse, isolated block tests, named versions and immutable run history
are implemented on `codex/workflow-studio`. Source is frozen at `a9a77bdd`.
One complete final browser invocation passes 555 checks with three existing skips.
Main and the installed app remain unchanged. Stop for WS-D review before CI-A.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| WS-AC18: live states/text and Follow yielding to manual pan/zoom | Passed | `workflow-studio-running.spec.ts`; synthetic videos |
| WS-AC19: approve, edit, reject; phone sheets | Passed | Same suite, including another run with the same review block |
| WS-AC20: retry block, optional clean-up skip, restart reconciliation | Passed | Existing engine/cleanup guards; new full application lifecycle browser test |
| WS-AC21: verified Run from here; changed settings refuse | Passed | `test_workflow_run_modes.py`; browser reuse/versions case |
| WS-AC22: one block, explicit samples or saved upstream, hidden tests | Passed | Run modes tests; browser reload and Output tab case |
| WS-AC23: disconnect/reconnect without polling | Passed | Live snapshot/cursor tests; browser reconnect case |
| WS-AC24: immutable run view, results/exports, legacy adapter | Passed | Favorites/run snapshot case; unchanged original workflow/shell tests |
| Favorites | Passed | Strict image/text selection, limits and idempotent decision tests |
| Named versions/restore/undo | Passed | Browser versions case; immutable snapshot/storage guards |
| Paged/filterable all-runs; paused count beyond 50 | Passed | `test_workflow_live_snapshots.py`; production history component |
| Palette/paused notification identities | Passed | Two identically named workflows navigate to the selected actual run |
| Final complete regression | Passed, 56.3 minutes | `artifacts/workflow-studio/ws-d/e2e-final.log` |

## Changed files

- Server: additive migration 012, Pick contracts, run/test/reuse acceptance,
  per-block provenance guards, original-source rebinding, hidden test retention,
  cumulative live snapshots and ordered SSE replay, paged/filtered history and
  aggregate paused counts. Existing native performers are retained.
- Web: Run panel, server-driven canvas/Outline states, Follow/manual pause,
  approvals/favorites/retry, verified block-run inputs, Output tab, versions,
  read-only run view, result rendering/save/share, history, palette and notifier.
  The timeline keeps Claude's flat appearance; completed outputs open on selection.
- Motion: CSS sweep, connection pulse, completion badge and pause decoration;
  only the explicitly approved `stroke-dashoffset` guard extension.
- Guards/tests: strict disjoint discriminator extension, populated v11 migration,
  reuse/input/media/source identity, live snapshots and browser run controls.
- Docs: authorization, plan, test-diff ledger, chat-image review and unchanged
  supplied chat-image documents/prototype/reference copies.

## Deviations and implementation decisions

- Reuse checks resolved model/default/connection settings, identical Start inputs
  and source/media identity in addition to the proposed block config hash.
  Only typed transcript pointers are rebound; literal strings are never rewritten.
- Disabled blocks do not resolve a model. Enabling/changing them changes their
  guard; the existing recording template works with no model on disabled clean-up.
- Tests accept explicit text/number/boolean samples. File/transcript/image inputs
  require actual saved sources. Expiry removes test rows and preserves Gallery files.
- The Run panel reports actual streamed character counts; it does not invent
  token counts. Cumulative text/progress and attempt IDs recover after reconnect.
- Connection motion is CSS-only. Both reduced-motion triggers stop loops; dimming
  applies to decorations rather than reducing text contrast.
- API union extension is accepted only with required matching discriminator consts,
  unique local references and preserved prior alternatives. Negative guards reject
  overlap, missing const/required keys and removals; no existing request is relaxed.
- Legacy phone controls stay inline, with a saved Outline disclosure. This retains
  existing navigation. Graph runs use the specified sheet with an explicit Close.
- One paused notification is updated to the latest transition. The sidebar and
  palette retain all paused runs; hidden overlapping Open actions are avoided.
- Workflow Markdown retains live copy-failure feedback without nested status roles;
  ordinary chat's copy behavior stays at its existing default.

## Runtime observations and retained failures

All new execution evidence uses fake Ollama/image/transcription runtimes and
synthetic inputs. No native inference or semantic-quality qualification is claimed.
No prompt, sampling/default, runtime/model or dependency change occurs.

The browser restart test closes and recreates the complete app lifecycle against
the same synthetic database, preserving completed outputs and reconciling unfinished
work. It is an in-process lifecycle test, not a physical launchd/process restart.
Its restart window retains closed-store/aborted-request diagnostics. Occasional
development ResizeObserver/module-loading warnings are not claimed absent.

The first complete invocation was intentionally interrupted after 17 passes for
the flat timeline correction. The next complete invocation fails eight checks:
545 passes, three existing skips, 57.7 minutes. Original tests expose nested
status regions, disabled clean-up model resolution, phone navigation blocked by
the legacy sheet, and overlapping paused toasts. The failed source, logs/traces
and fresh synthetic captures are retained under `attempts/e2e-second-failed/`.
The first focused repair pass retains ten passes/two failures: Vaul non-modal
semantics did not restore navigation, and a new fixture reused its name across
both projects. Inline legacy controls and an isolated repeated fixture name fix
those cases. The subsequent unchanged acceptance subset passes all 12 checks.

Earlier development failures and the lost fourth-attempt trace are recorded in
`WORKFLOW-STUDIO-WS-D-TEST-LEDGER.md`. No failed invocation is combined with focused
passes and reported as a complete run.

## Test output and QA gates

| Gate | Status / evidence |
| --- | --- |
| G-1 | Passed: 646 Python / 94 frontend; workflows 89.2% coverage, all monitored packages above 80%; `check-final-source.log` |
| G-2 | Passed: one complete invocation, 555 passes / three existing skips in 56.3 minutes; `e2e-final.log` |
| G-3 | Original browser tests/assertions/skips/retries/timeouts unchanged; ledger lists existing server fixture/schema edits |
| G-4 | Passed: initial JS 242,270 gzip bytes, +612 from WS-C; render p95 3.4 / 3 ms, first-token overhead 80.73 / 64.60 ms; `bundle-final-source.json`, `performance-final.json` |
| G-5 | 112 new-state axe checks pass: 14 states × two themes × two sizes × two browsers; 110 contrast pairs; existing keyboard gates retained |
| G-6 | Phase 3 and complete WS-C API comparison pass; `rollback-api.json` errors `[]`; strict discriminator negative tests |
| G-7 | `test_workflow_modes_migration.py` preserves populated v11 old columns/rows and verifies defaults, integrity/FKs |
| G-8 | Frozen prompt and exact legacy-template request guards retained; no prompt edit |
| G-9 | Not triggered: 34 core server modules under runs/providers/search/transcribe remain byte-identical |
| G-10 | Ordinary-chat golden payload and all six legacy-template parity cases retained |
| G-11 | Synthetic capture discipline; final scanner has zero findings; 24,444 historical evidence/eval/fixture blobs and 529 source/test/config files verified |
| G-12 | Installed app/main unchanged; local and normally verified HTTPS health pass; deployment/PWA invariants retained |
| G-13 | Both system and saved Always remove activity loops/transitions; first-party motion guard retained |
| G-14 | Production run states, favorites, block tests, versions, reuse/sample forms and saved-run view on `/design` |
| G-15 | Copied synthetic-data rollback passes in 1.599 seconds; previous schema 11 starts with exact restored backup |
| G-16 | Not checked on a physical phone. Automated WebKit viewport checks are not Jake's acceptance or a VoiceOver pass |

### Budgets

| Measure | WS-C | WS-D |
| --- | --- | --- |
| Initial JS gzip | 241,658 bytes | 242,270 bytes (+612); budget 256,000 |
| Studio own lazy file | 77,306 bytes | 17,278 bytes after shared splitting |
| Additional lazy static imports, excluding initial JS | 91,078 bytes | 363,941 bytes, including existing shared Markdown 284,399 bytes |
| Streaming render p95 | 2.7 / 3 ms | 3.4 / 3 ms; only the streaming row renders |
| First-token overhead | 85.57 / 66.31 ms | 80.73 / 64.60 ms |
| 300-message scroll p95 | 16.7 / 21 ms | 16.7 / 21 ms |

The Studio file's smaller size reflects splitting, not a smaller total route.
Shared Markdown is newly used for workflow outputs; its code remains lazy.

### Core unchanged

Every guard below passes in the complete final check/browser invocation.

| Core | Guard |
| --- | --- |
| C1 send/stream/stats | `chat.spec.ts` |
| C2 stop/partial/connection close | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 reconnect/history | `chat.spec.ts`, `web.spec.ts` |
| C4 long answer/idle timeout | `chat.spec.ts` |
| C5 regenerate/edit/branch/chat actions | `actions.spec.ts` |
| C6 model load/eject/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 only user sampling values | `parameters.spec.ts`, `test_chat.py` |
| C8 Web sources/skip/failure | `web.spec.ts`, search/evidence/grading tests; unchanged server source |
| C9 recording/output/storage | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts` |
| C10 phone/composer/safe areas | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 palette/PWA/no API caching | `polish.spec.ts`, `pwa.spec.ts` |
| C12 read-only legacy import | `test_legacy_import.py` |
| C13 deployment identities | `test_deployment.py` |
| C14 untrusted content/SSRF | `foundation.spec.ts`, `test_search.py` |
| C15 performance | `performance.spec.ts`, chat frame/first-token tests |
| C16 keyboard/labels/axe | `foundation.spec.ts`, `review.spec.ts`, `phase3-accessibility.spec.ts` |

### Migrations, rollback and evals

Migration `012_workflow_run_modes.sql` adds run mode/parent/expiry, step provenance
columns and indexes. Existing core tables are not rebuilt or dropped. The populated
v11 fixture compares all old-column row hashes, checks defaults, FKs and integrity.

`rollback_rehearsal.py` creates a copied synthetic v11 folder and SQLite backup,
starts the candidate lifecycle at schema 12, checks health/legacy rows/a blank graph,
restores the whole copied backup, and starts archived WS-C source at schema 11.
Backup/restored SHA-256 are identical; API comparisons have zero errors. Command
list and elapsed time are retained in `rollback-api.json`; no live data is used.

No new native or semantic eval is run. Ordinary Search/Library prompts, retrieval
and provider/runtime bodies are unchanged. Frozen prompt hashes, ordinary golden
captures and six legacy-template parity cases remain mandatory. No Research restart.

## Screenshots and preservation

Synthetic captures are under `artifacts/workflow-studio/ws-d/browser/`, including
live text, reused output, phone review, favorites, failure/interruption/completion,
skipped/reused states, block tests, versions, sample/reuse forms and saved-run view.
The state matrix covers 390/1440, light/dark, Chromium/WebKit, with zero serious
or critical axe findings. Representative desktop and phone captures were visually
reviewed by Codex against the supplied reference; this is not Jake's phone check.

320 final/available-at-closeout synthetic videos (64,913,679 bytes) are retained
outside Git, with additional earlier attempted-run recordings in separate manifests.
1,168 fresh regression outputs are archived separately; 1,128 historical outputs
are restored and 40 new fake settings captures relocated. Preservation verifies
24,444 historical evidence/eval/fixture blobs, 15 workflow reference files, all
17 supplied chat-image files, 529 frozen source/test/config files and installed
97 server / 410 current-release static files. Failed-run traces and source are
retained separately; `preservation-final.json` and the video manifests record proof.
The original workflow references and all new chat-image supplied files have frozen
hashes. Main stays at `dce4c49`; no final merge or installed publication occurs.

## Review and next checkpoint

Stop for WS-D review. The isolated fake preview is the review surface; native
engine qualification is not inferred from these tests. Phone acceptance remains
not checked. Historical iOS keyboard recovery after restart has an unproven cause;
VoiceOver's old failure remains outside the current work list.

Claude's chat-image plan is preserved and reviewed in
`CHAT-IMAGES-IMPLEMENTATION-REVIEW.md`. Next is CI-A's Playful/Plain waiting line
and live reasoning ticker, then CI-B's saved image turns and CI-C's viewer,
iteration and exports, with each checkpoint report/review stop. Image turns are
not implemented here. Main merge/live publication still need Jake's final okay.
