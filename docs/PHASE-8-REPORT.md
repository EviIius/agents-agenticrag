# Phase 8 report — checkpoint 8-0, review stop

## Summary

The isolated evaluation is complete; no Research product code is implemented.
Five of six eligible chat models pass the 40-prompt native protocol probe;
Jake's daily 32K Qwen passes 40/40. The fresh 25-case live Search evaluation
passes its automated targets with 7.23 s median first-answer-token latency.
The new 15-case multi-part baseline scores 9/15 on the frozen fact assertions,
both live and with recorded web replay. Manual review identifies genuine gaps,
wording-sensitive grading and a release-source discrepancy; the automated
scores are preserved. The live Atelier release remains unchanged and healthy.

## Done-when checklist — Phase 8 §1

| Item | Status | Evidence |
|---|---|---|
| G1 calendar/daily use | Explicitly waived for 8-0 only; two weeks of use **not** claimed | Jake: “Then go ahead and start”; AGENTS amendment |
| G1 fresh Search checks | Quantitative E12/E-AC9 targets met; manual caveat below | `artifacts/phase-8/gate/release-live/reports/2026-10-06-212915-qwen3-30b-a3b-workbench-32k-live-keyword.json` and `.md` |
| G2 15 multi-part cases/fixtures | Prepared, frozen, recorded and replayed | `server/evals/research/cases.yaml`, README; 91 compressed page recordings plus provider results/errors and 15 run recordings |
| G3 existing Search baseline | Measured; its shortcomings retained | Live and offline reports below; 9/15 frozen fact checks in each |
| G4 native tools ≥95% on a daily model | Pass: Qwen 40/40 | `tool-probe.json`, `tool-probe-summary.json`; all 240 request/stream pairs verified |
| G5 product spec/targets approval | **Pending** | This is the review stop; 8-0 authorization did not authorize an agent loop or UI |

G1's existing ranking comparison remains the documented Phase 2/7B evidence;
ranking code, prompts, dependencies and tests are unchanged. The fresh check
uses the current keyword default. This is not a new ranking A/B experiment or
an unqualified claim that every live answer is factually perfect.

## Changed files

- Evaluation only: `server/evals/research/README.md`, `cases.yaml`,
  `probe_cases.json`, `tools.json`, `probe_tools.py`, `inspect_probe.py`,
  `record_references.py`, `run_search_gate.py`, `test_gate.py`, `audit_evidence.py`.
- Evidence: `artifacts/phase-8/gate/`, including request streams, public web
  recordings, reference snapshots, failed preparation requests, reports and
  source/input hashes.
- Documentation: this report and AGENTS' narrowly scoped 8-0 authorization.
- Product server/web, existing tests, prompts, dependencies, database,
  deployment and transcription engine: no changes. The `make check` coverage
  output is preserved inside the gate folder; its shared tracked artifact was
  returned to its prior contents.

## Native runtime observations

Runtime metadata reports `tools` for six chat models and for one embedding-only
model. The latter is excluded using its lack of chat-completion capability,
not a name heuristic. Hidden chat models are still included in this installed
model probe; picker preferences are unchanged. Tool requests do not execute
searches or reads. There are no repairs, retries or parsed prose calls.

| Model | Valid / 40 | Search / 15 | Read / 15 | Finish / 10 | Gate |
|---|---:|---:|---:|---:|---|
| `qwen3:30b-a3b-workbench-32k` | 40 | 15 | 15 | 10 | Pass; daily model |
| `gemma4:12b-mlx` | 40 | 15 | 15 | 10 | Pass |
| `gpt-oss:20b` | 36 | 15 | 15 | 6 | **Miss: 90%** |
| `llama3.3:70b-workbench-16k` | 40 | 15 | 15 | 10 | Pass |
| `llama3.3:70b-instruct-q4_K_M` | 40 | 15 | 15 | 10 | Pass; hidden picker preference retained |
| `qwen3:30b-a3b-instruct-2507-q4_K_M` | 40 | 15 | 15 | 10 | Pass |

All 240 emitted calls use object arguments, a nested `function.index` and a
call ID. Each saved stream agrees with its report. GPT-OSS's four invalid
`finish` calls add arguments (`args`, an empty key, or `commentary`) to the
declared empty schema; they are rejected rather than coerced. Every prompt
called its requested tool, but schema validity remains the gate criterion.
The probe requires a native finish call, stricter than the future no-call
finish rule. All requests preserve reported context and saved defaults; no
sampling or reasoning override is added.

The daily Qwen's median native request is 0.44 s. This is protocol timing on
simple independent prompts, **not** Research-loop latency or proof of choosing
useful tools autonomously. Ollama reports version 0.35.0 at closeout. Model
digests were captured after the run, not before: do not claim the weights were
frozen throughout. Details are in `runtime-closeout.json`.

## Search measurements

All rows use real 32K Qwen and the existing planner/answer path in temporary
databases. No title, judge or Research loop call is added. The credential
option reads only the saved search key, read-only, without logging its value.

| Measurement | Existing 25-case live release set | 15-case live baseline | Same 15, recorded web |
|---|---:|---:|---:|
| Frozen required-fact case checks | 25/25 | 9/15 | 9/15 |
| Search decision accuracy | 100% | 100% | 100% |
| Rendered citation validity | 100% | 100% | 100% |
| Lexical citation support heuristic | 0.91349 | 0.94316 | 0.93998 |
| First answer token median | 7.23 s | 7.23 s | 4.79 s |
| First answer token p90 | 11.26 s | 16.37 s | 5.66 s |
| Searched turns with evidence | 22/22 | 15/15 | 15/15 |

Baseline reports:

- `artifacts/phase-8/gate/baseline-record/reports/2026-10-06-213208-qwen3-30b-a3b-workbench-32k-live-keyword.json` and `.md`.
- `artifacts/phase-8/gate/baseline-replay/reports/2026-10-06-213415-qwen3-30b-a3b-workbench-32k-offline-keyword.json` and `.md`.

Both baseline commands exit 1 because the unchanged web evaluator applies its
85% release threshold to the harder new set. These are retained baseline
quality failures, not a fixture or harness crash. This is not a failure on the
existing 25 release cases. Model outputs vary: the Linux case passes only on
replay and the HTTP transports case passes only live. The corpus and assertions
did not change. Replay makes no external provider search requests; its real
planner may phrase queries differently against the same frozen corpus.

Ollama Search returned 429 during the live checks. Existing cooldown/fallback
continued through local SearXNG. No provider, key, subscription or fallback
configuration was changed. The numerical live latency target still passes.

### Manual review and interpretation

`quality-review.json` retains the per-case observations. Key findings:

- HTTP comparison omits strong versus weak ETag matching; the replay also
  incorrectly restricts If-Match to methods other than GET/HEAD.
- WCAG comparison gives the numbers and levels but omits the essential-motion
  exception. Voyager supplies only the month, not the requested exact date.
- PostgreSQL's answer contradicts the Read Committed statement-snapshot rule.
- Recorded replay cannot establish HTTP/3's TLS version from the passages it
  selected, despite the reference document containing TLS 1.3. It abstains.
- Python correctly explains path dependence and recreation but misses the
  frozen wording regex. Linux's live wording also differs from the assertion;
  replay explicitly states that **all** open descriptors must close.
- The Cache answer adds an inaccurate implication about HTTP caching headers.
  Citation-number validity and lexical overlap do not prove semantic support.
- Requests naming primary references often receive third-party citations.

The fresh release set's Ollama answer calls a third-party `v0.40.0-rc6` entry
the latest release. The subsequent official API review returns `v0.40.0` as
latest and 404 for the RC release, while the retrieved GitHub page still shows
an RC tag. Preserve this as a source/version discrepancy, not proof of its
cause or an invented corrected score. Official API bodies and URLs are saved
under `release-live/official-release-*.json`. The existing quantitative
thresholds pass, but this case does not receive an unqualified manual pass.

Do not claim all 25 live answers are perfect or that 60% is a semantic truth
score. Keep the frozen baseline and these annotations together. Before
claiming a Research gain, adjudicate equivalent wording, subject association,
contradictions and claim support consistently for baseline and candidate.
Any grader correction needs a labeled deterministic regrade of both retained
answers; changing questions, expected facts or corpus needs a new baseline.

With the current 9/15 frozen baseline, the proposed ≥80% and ≥15-percentage-point
gain requires **at least 12/15** (three additional cases, a 20-point increase).
No Research answer was generated, so improvement is **not yet demonstrated**.
This clean multi-part corpus has no controlled attack: the web evaluator's
vacuous replay `injection_exercised=true` must not be presented as an injection
test. Attack, SSRF, cancellation, budget and ordinary-payload evidence belong
to 8A and later Research evaluation.

## Deviations from SPEC.md

- Calendar hold waived only for 8-0 by Jake; no two-week use claim. Product work
  before 17 October still needs its own explicit decision.
- Chat-ineligible embedding model omitted from a chat-tool probe even though
  its metadata reports `tools`.
- Existing Search evaluator reused with isolated output destinations and the
  saved search credential, equivalent to the specified fresh live command.
- Preparation fixes preserve their draft/failed retrieval evidence. UNESCO's
  locally blocked pages were browser-verified, labeled separately; no fabricated
  successful raw fetch was inserted.
- Complete browser/performance/image evidence is carried forward by exact
  source hashes for this evaluation-only checkpoint. It is not a fresh browser
  run or a new product release. A fresh complete run remains required for 8A.

## Test output and QA gates

Fresh `make check`: **298 Python tests**, **36 frontend tests**, **74 contrast
pairs**, lint/types/API-additive/prompt/privacy/motion guards pass. Coverage:
providers 86.5%, runs 89.4%, search 88.9%, transcribe 93.1%, documents 96.6%,
library 92.6%, backup 96.8%. New evaluation harness: **19 offline tests pass**;
evaluation scripts also pass Ruff formatting/lint. No app Research module exists
yet, so there is no new production coverage target.

| QA gate | Status / evidence |
|---|---|
| G-1 checks/coverage | Fresh pass: `check.txt`, `coverage.json`, `harness-tests.txt` |
| G-2 complete browser suite | Carried forward: 431 pass/3 existing skips in one 7B invocation; all 389 tested source hashes match; `regression-source-verification.json`. No fresh run claimed |
| G-3 test weakening | None; existing test files untouched |
| G-4 performance | Same production bytes/source; 7B bundle/frame/scroll evidence carried forward; new feature budgets not measured |
| G-5 accessibility | Same UI; existing evidence retained; VoiceOver unresolved/deferred |
| G-6 API additive | Fresh guard pass; API unchanged |
| G-7 data additive | Fresh synthetic migration tests pass; no new migration or production data write |
| G-8 frozen prompts | Fresh prompt hashes pass; product prompt bytes unchanged |
| G-9 web unchanged | No search/run/provider source edits; fresh live release checks and separate harder baseline retained |
| G-10 ordinary payload | Fresh golden capture tests pass; probe tools exist only in evaluation requests |
| G-11 privacy | Fresh scanner plus gate audit; public/synthetic evidence only; no user Library or recording read |
| G-12 deployment invariants | Fresh deployment/PWA unit guards, unchanged deployment source, health 200 on both routes; no deployment |
| G-13 reduced motion | Unchanged source and prior complete browser evidence; reported physical regression remains deferred |
| G-14 design states | No new product state; no new screenshot requirement |
| G-15 rollback | No migration/deployment; prior fallback unchanged |
| G-16 Jake phone check | Not requested or invented for evaluation-only work; 7B acceptance remains recorded |

### Test-diff ledger

No existing test was edited. New tests validate malformed native calls and
schema boundaries, 40/15-case structure and absence of Search trial/sampling
overrides. The validator gained a type guard for malformed tool names; all
saved streams were deterministically verified against the final validator
with no result changes and no new inference.

## Screenshots

None: no UI change or phone inspection. Existing synthetic 7B image evidence
is unchanged. Supplied private phone images and filenames are not copied here.

## Recommendations and open decisions for Jake

1. Use the tested daily 32K Qwen for the initial Research implementation. Keep
   native-only tools and the proposed budgets and quality thresholds. Do not
   silently enable an unqualified model merely because `tools` is reported;
   GPT-OSS's 90% result needs a clear eligibility decision. Qualification should
   be tied to observed model metadata rather than inferred from names.
2. Keep manual fact/support review beside the frozen automated baseline.
   Semantic gains must not consist only of matching different wording.
3. Review Phase 8's product spec and §9 targets, including controlled injection
   and budget tests, before authorizing 8A. Decide separately whether to waive
   the product calendar hold or begin after 17 October. This report ends 8-0;
   it does not deploy Research or close the whole Phase 8.

The recording-dropdown, physical motion and VoiceOver issues remain in
`docs/DEFERRED-FIXES.md` as requested. The installed 7B app and fallback remain
available; localhost and Tailscale health both return 200 at closeout.
