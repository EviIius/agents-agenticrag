# Phase 8A report — isolated prototype, review stop

## Summary

8A adds an isolated, default-off Research backend and tests. The installed Atelier
app remains on accepted 7B; no Research UI or deployment was added. Native protocol
qualification passes, but autonomous research does not meet the approved quality
or host-validity targets. The phase remains open and cannot proceed to 8B.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Reviewed 8-0 before product work | Pass; narrow 8A authorization, calendar hold waived only for this prototype | AGENTS.md; prior commit `d74067e`; historical Phase 8 report |
| Daily model native tool qualification | 40/40; digest, context and runtime version equal before/after | `artifacts/phase-8/8a/qualification/`, `qualification.txt` |
| Native provider events and ordinary payload | Pass; all 240 original streams replayed; tools absent for ordinary requests | `test_recorded_native_streams_and_ordinary_payload` |
| Budgets, finish/no-call, cancellation, semaphore release | Pass in controlled tests; counters hold in both real-model evals | `test_research.py`; retained reports |
| Public URL allowlist and existing SSRF protection | Pass in controlled host tests; guessed URLs refused in actual runs | `test_user_allowlist_still_uses_existing_ssrf_guard`; adjudication |
| Persisted activity, evidence and final streamed answer | Backend tests pass; no Research UI claim | `test_research_sources_answer_is_separate_reload_and_sse` |
| Additive migration and rollback | Synthetic schema 8→9→8; pre-existing row hashes unchanged | `rollback.json`, `rollback-final.txt`; migration fixture tests |
| ≥80% facts and ≥15-point gain | **Miss**: 10/15 and 9/15; corrected baseline 10/15 requires 13/15 | `eval-initial/report.json`, `eval/report.json`, `baseline-regrade.json` |
| Citations / zero unsupported claims | **Miss**: uncited source-free memory answers and incorrect WCAG assertions | `quality-review.json` |
| ≥95% valid autonomous calls | **Miss**: schema 100%, host acceptance 91.35% and 85% | `tool-validity-adjudication.json` |
| Injection ignored | **Open/miss**: final answer and fetch guard hold in one case, but persisted note copied attack sentinel | `attack.json`, `attack-review.json` |
| Existing Search equal-or-better | **Miss**: 24/25 vs 25/25; `unanswerable` flips; lexical support lower | `web-regression/comparison.json` |
| Full ordinary browser regression | 431 passed / 3 existing skips in one complete invocation; see post-suite scope below | `e2e.txt`, `e2e-closeout.json` |
| UI / phone acceptance | Not introduced or claimed; 8B remains gated | No new controls or states |

Evidence paths below are relative to `artifacts/phase-8/8a/` unless stated otherwise.

## Changed files

- **Server:** optional native tool request/events in provider types and Ollama;
  Research loop/qualification, run snapshots, default-off configuration, additive
  request/response fields, chat mode guards and persisted message activity.
- **Database:** `009_research.sql` adds three columns; no destructive migration.
- **Tests:** new `test_research.py`, opt-in fake-runtime tool scripts and runtime
  metadata, Research prompt hash, three schema-version assertions advanced to 9.
- **Web:** generated API types and required-field updates in five synthetic design
  fixtures only. No toggle, activity renderer, new icon or product behavior.
- **Tooling:** `make eval-research`, isolated replay/probe/regrade/attack helpers,
  Research coverage threshold, Phase 8 privacy scan coverage.
- **Documentation/evidence:** AGENTS authorization, phase status, README, this
  report and retained synthetic/public fixtures and failed attempts.
- No dependency manifests, deployment scripts, launchd/Tailscale configuration,
  transcription engine or existing Search prompt/rank/pipeline files changed.

## Deviations from SPEC.md

Jake authorized 8A before the calendar hold elapsed, with a stop before 8B. This
is not evidence of two weeks of daily use. Research is disabled by default and
only enabled in isolated test configurations; qualifying just the daily model is
intentional for this prototype. Other installed models need fresh qualifications
before enabling them. Live Research evaluation remains separately gated; `LIVE=1`
currently exits with an explicit explanation instead of silently replaying.

Research skips automatic title generation so that eight loop calls plus one
answer stay within nine calls; ordinary chat titles retain their existing path.
The final answer uses the existing web answer prompt and citation finalizer. No
prompt refinement or hidden retry was applied to rescue the failed evals.

The two real-loop evals precede final host bookkeeping/source-sanitization
hardening. Their source hashes and original outputs are retained, with no claim
that final source has passed real-model quality qualification. Frozen per-case
web results are query-independent, matching the old replay convention; this does
not measure whether adaptive searches find better live pages.

## Runtime observations and evals

The fresh daily Qwen probe uses actual Ollama native tools and runtime-reported
metadata, with no sampling override. Qualification binds digest, 32768 context
and runtime 0.35.0; a runtime change is refused. Model metadata uses the existing
short-lived registry cache; instantaneous weight-change detection is not claimed.

The original 8-0 baseline remains 9/15 in its original reports. Deterministic
regrading accepts equivalent Python hardcoded-path wording, producing 10/15 in
both retained live/replay answers without new inference or changed facts/corpus.
All other requirements remain. Consequently ≥80% **and** ≥15 points now requires
13/15 (86.67%). Date omissions are not excused as formatting differences.

| Measure | Prototype first run | Prototype second run | Required |
|---|---:|---:|---:|
| Complete fact cases | 10/15 | 9/15 | ≥13/15 |
| Gain over regraded baseline | 0 points | −6.67 points | ≥15 points |
| Native schema validity | 104/104 | 100/100 | Insufficient alone |
| Calls accepted by host URL/schema policy | 95/104 (91.35%) | 85/100 (85%) | ≥95% |
| Off-allowlist requests, all refused | 9 | 15 | No successful forbidden fetch |
| Median total time | 14.94 s | 16.85 s | ≤90 s |
| P90 total time | 20.93 s | 19.76 s | ≤200 s |
| Maximum model calls | 9 | 9 | ≤9 |
| Counters beyond host limits | 0 | 0 | 0 |
| Citation coverage and support | Failed | Failed | 100% / zero unsupported cases |

The old `valid_tool_fraction=1.0` field measured only name/argument schema
validity. `tool-validity-adjudication.json` labels the distinction without
rewriting reports. Ordinary unreadable pages (17 and 11) were also incorrectly
included in the early invalid-call counter; they are availability failures.
Future harness output separates schema validity and host acceptance explicitly.
The initial command's zero exit meant screening completion, not target success;
the second exits 1 for failed targets. Neither is selected as a qualifying run.

Concrete failures: Animation from Interactions is misnumbered/misleveled or
confused with seizure/five-second controls; one UNESCO answer and one parks
answer state facts with zero supplied sources; HTTP omits strong/weak comparison;
Voyager omits the exact day. `quality-review.json` is a counterexample screening,
not an exhaustive semantic count or certification. Numeric citation validity and
regex fact matches cannot override these failures.

The controlled real-model attack has no successful off-allowlist fetch and no
sentinel in the final answer, but the loop puts `PWNED` into a persisted note.
The original answer-only assertion missed that contamination. The stricter
review and future harness include activity; do not call injection resistance a
pass. Only one controlled case was executed.

### Existing Search regression

The correct replay uses the accepted 7B base-Qwen/keyword configuration and
`server/evals/web/fixtures/phase2-final-corpus`, with no overrides. It scores
24/25 versus 25/25; `unanswerable` changes from pass to fail. Its answer says the
user's breakfast is not established but adds other people's breakfasts and
misses the frozen expected wording. Do not silently change the grader or
assert this proves a Research-caused regression. Search source/prompt hashes
are unchanged; real-model generation variance does not waive QA G-9.

Lexical support is 0.866334 vs 0.882382; median TTFT 4.298 vs 4.467 s; P90 5.363
vs 5.987 s. All release thresholds still pass, but equality/no-case-regression
fails. The specific 7B variance acceptance is not reused. No favorable rerun is
selected. An earlier wrong-fixture-root attempt scored 10/25 with empty replay
batches; that preparation error is retained under `release-replay/` and is not
presented as a product regression.

## Test output

Final `make check`: **333 Python tests, 36 frontend tests, 74 contrast pairs**;
Ruff, formatting, mypy, additive API, generated API types, motion and privacy
checks pass. Coverage: providers 87.2%, runs 89.8%, search 89.2%, transcription
93.1%, documents 96.6%, Library 92.6%, backups 96.8%, Research **90.4%**.
`check-post-suite.txt` and `coverage.json` retain the outputs. Research plus
prompt tests: 37 passed; existing gate harness: 19 passed. Build passes with
the existing lazy-chunk warning; no added dependency.

The complete browser invocation passes **431 tests with 3 existing skips** in
37.3 minutes, Chromium and WebKit. Source hashes were unchanged throughout that
run; `e2e-closeout.json` also proves service restoration. It is not assembled
from the interrupted run. Afterwards, exactly two frozen-suite files changed:
`research.py` and `test_research.py`, for availability classification, persistent
queries and cancelled/timed-out activity. The new tests and final `make check`
pass. `post-suite-source-delta.json` records this precisely. **A full E2E of the
final tree has not been repeated**; this checkpoint stays open and needs its
release gates repeated after any approved quality refinement. No final-tree
full-browser certification is claimed.

The post-suite hardening removes availability errors from the invalid-call
counter and preserves queries/URLs on failure, cancellation and timeout. Host
policy/schema/budget refusals remain invalid. Original failed real-model reports
are retained unchanged; they are not relabeled as passing after bookkeeping fixes.

Initial failures remain recorded: old schema-version expectations; an accidental
fake-runtime web-answer branch omission (restored); five design fixtures missing
the new required response field (type-only fixes); and a mypy test import issue
(fixed). The interrupted first browser attempt is retained separately, never
combined with the complete run or labeled a full pass.

## QA gates

| Gate | Status / evidence |
|---|---|
| G-1 checks/coverage | 333 Python / 36 frontend / 74 contrast pass; Research 90.4%; `check-post-suite.txt` |
| G-2 complete browser suite | Complete pre-bookkeeping run passes; **final-tree rerun outstanding**, as scoped above |
| G-3 no weakened tests | Ledger below; no skip, threshold or timeout changes |
| G-4 budgets | Initial JS 239813 bytes gzip vs 239797 at 7B (+16), below 256000 and +8192 limits; 300-message render p95 3.2 ms Chromium / 3 ms WebKit, max 5.3 / 3 ms; first-token overhead 58.39 / 58.77 ms; `regenerated-metrics/phase-1/` and `/phase-3/` |
| G-5 accessibility | Existing synthetic suite; no new UI; VoiceOver unresolved/deferred |
| G-6 additive API | `make check` additive guard pass |
| G-7 additive DB | Synthetic fixture row hashes; new columns separately checked |
| G-8 prompts frozen | Existing hashes unchanged; Research v1 added/frozen |
| G-9 Search equality | **Miss**, as above; review required |
| G-10 ordinary payload | Golden byte comparison, unset sampling absent; tools only opt-in |
| G-11 privacy | Scanner and supplemental public/stream audit pass; 280 native streams and 91 public page hashes verified; representative images reviewed; public/synthetic inputs only |
| G-12 deployment invariants | No deployment; Local/TLS health 200, `/design` 404, installed schema 8, Research off; 81 installed public code files match prior commit; `installed-closeout.json` |
| G-13 reduced motion | Existing complete suite; no new motion |
| G-14 design states | No Research UI yet; five fixtures have type-only updates |
| G-15 rollback | Synthetic old/new/restore health+shell 200, 8→9→8, unchanged row hashes, 4.64 s |
| G-16 physical phone check | Not checked for 8A; no invented result; live still 7B |

## Test-diff ledger

| File | Change | Reason | Previous behavior retained? |
|---|---|---|---|
| `test_documents.py` | Maximum migration version 8→9 | New additive migration | Yes, existing projected row hashes retained |
| `test_foundation.py` | Maximum migration version 8→9 | Same | Yes |
| `test_folders_backups.py` | Maximum migration version 8→9 | Same | Yes, backup/restore assertions retained |
| `test_prompt_hashes.py` | Adds frozen Research hash | New model-facing prompt | Yes, every previous hash unchanged |
| `fake_runtime.py` | Opt-in native scripts/metadata and version endpoint | Exercise Research separately | Yes, default tools off; existing web answer branch restored |
| `test_research.py` (new) | Backend assertions and original native replay | New feature | Additive tests; no old expectations replaced |

Privacy scanner adds Phase 8 to its existing scope; coverage checker adds the
new Research module at the same 80% floor. Eval helpers are new and do not loosen
existing release graders. No E2E test file is changed.

## Core unchanged

Browser entries refer to the one complete `e2e.txt` invocation on its recorded
source tree; Python entries refer to final `check-post-suite.txt`. Research-only
post-suite changes and failed G-9 prevent an unqualified final release claim.

| Core | Existing contract | Evidence |
|---|---|---|
| C1 | Send/stream/stats | chat.spec.ts |
| C2 | Stop persists partial output | chat.spec.ts; phase3-accessibility.spec.ts |
| C3 | Reattach and late snapshot | chat.spec.ts; web.spec.ts |
| C4 | Long answers/timeouts | chat.spec.ts |
| C5 | Message/chat actions | actions.spec.ts |
| C6 | Load/eject/selection/context | load-selection.spec.ts; ui-regressions.spec.ts |
| C7 | Set-only sampling | parameters.spec.ts; final test_chat.py |
| C8 | Search UI/failure/citations | web.spec.ts and Python checks pass; **real-model G-9 equality misses** |
| C9 | Transcription/download/retention | transcription.spec.ts; recording-download.spec.ts; audio-storage.spec.ts |
| C10 | Mobile layout/keyboard/drawers | mobile-layout.spec.ts; mobile-composer.spec.ts |
| C11 | PWA/palette/shortcuts | polish.spec.ts; pwa.spec.ts |
| C12 | Read-only legacy import | final test_legacy_import.py |
| C13 | Deployment invariants | final test_deployment.py; installed-closeout.json |
| C14 | Markdown/SSRF | foundation.spec.ts; final test_search.py/test_research.py |
| C15 | Performance | performance.spec.ts; chat.spec.ts; measured outputs above |
| C16 | Automated accessibility | foundation.spec.ts; review.spec.ts; phase3-accessibility.spec.ts; VoiceOver not passed |

## Migrations and rollback

`009_research.sql` adds chat `research_enabled` and message `research_json` /
`activity_json`. Existing rows are projected onto old columns for migration
hash checks. Rollback uses an archived `d74067e` app and a synthetic Phase 3
fixture upgraded through its old migrations, snapshots schema 8, starts new
schema 9, then restores the backup plus old code. Health and shell return 200
at every stage; old row hashes agree. It takes 4.636 s; temporary files removed.
The first two rehearsal attempts used a wrong static path, returned 404 for
shell, and are retained; the corrected full rehearsal passes. No production
data was read or migrated for this exercise.

## Screenshots

Fresh synthetic screenshots are archived under `regenerated-metrics/`. Four
representative views were visually inspected: `phase-1/chat-390-light-fake-runtime.png`,
`phase-2/citation-card-1440-dark-fake-web.png`,
`phase-t/mobile-save-1440-light-fake.png`, and
`phase-7/7b/states/fake-library-answer-searching-390-dark-webkit.png`.
These show existing product states; no Research UI is claimed. All capture data
comes from the isolated fake runtime. Copied older outputs lacking a synthetic
filename receive a `fake-` prefix; `synthetic-evidence-paths.json` retains their
mapping. No supplied real-phone images are used. The scanner is not proof of
visual privacy; representative review is not an exhaustive visual audit.

## Known limitations carried forward

VoiceOver remains reported failing and deferred. The earlier iOS keyboard issue
recovered after restart; its cause remains unproven. Sidebar/other motion
regression and the recording dropdown layout remain deferred at Jake's request.
No private recording names, text or phone screenshots are added to evidence.
Research also remains unavailable in the product, pending quality improvement.
Context estimates bound text history; exact native tool-envelope/image token
accounting is not claimed. The probe's success does not establish autonomous
planning quality.

## Open questions for Jake

Recommended next step: keep 7B deployed, agree an evidence-first Research
refinement (read coverage, explicit abstention, safe activity) and evaluate it
against the unchanged corpus and targets. Any prompt change needs an approved
before/after eval; none is made in this checkpoint. G-9's new variance also needs
review, not an inherited waiver. Do not begin 8B or publish this prototype.
