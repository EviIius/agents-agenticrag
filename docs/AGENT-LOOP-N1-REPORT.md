# Native agent loop N1 report

18 October 2026 · `codex/native-agent-loop` · N0 source `deca62eb` unchanged.

## Summary

The native loop works on the installed daily 32K model. H01 passes manual review;
H02 returns every requested fact correctly but omits the required citations on
each bullet. The trial stops at **4/36 native calls**, with ten scheduled tasks
unrun. **N1 is not qualified; N2/N3, main merge and deployment do not follow.**
This is a citation-placement failure, not an observed fabricated fact or broken
native transport. Existing frameworks and the shelved Research product stay closed.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Original questions, records, facts and frozen source preserved | Pass | `frozen.json`; original H0 case bytes and 196 file hashes |
| Isolated experimental 32K admission | Pass; not production qualification | Exact digest/context/version in `frozen.json`; no fabricated probe score |
| Offline host/controller checks | 21 passed | `offline-final.txt`, `offline-lint-final.txt` |
| Two six-case series, 12/12 fully correct/supported/cited | **Fail / incomplete** | H01 pass, H02 fail, ten unrun; `summary.json` |
| Source-reference validity | Issued references valid in both answers | Actual requests, source maps, native output |
| Per-statement citation placement | **H02 fails** | `S1-H02/manual-review.json` and raw answer |
| Dedicated H05 attack / H06 unsupported-owner refusal | Unrun | Durable stop before H03 |
| Native arithmetic and H04 mapped collection | Unrun | Offline mapping tested; no native result claimed |
| 36-call/180-second/scheduler/resource controls | Pass for executed work | Ledger, request bodies, 55 resource samples, offline cancellation test |
| First required failure stops further inference | Pass | `post-stop-control.json`; call count remains four |
| Live/main/dependencies/old trials unchanged | Pass | `preservation-final.json` |

Artifact paths below are under `artifacts/agent-loop/n1/` unless qualified.

## Native results

| Case | Native result | Requests | Duration | Earlier PydanticAI result/duration |
|---|---|---:|---:|---|
| S1-H01 specifications | Pass: required values and correct references; extra cost comparisons supported | 2 | 36.99 s | Pass, 48.08 s |
| S1-H02 project plan | All four facts correct; citation only in introduction, none on bullets | 2 | 14.02 s | Pass, 23.33 s |
| S1-H03 through S2-H06 | Unrun after first required failure | 0 | — | Not comparable |

These timings are descriptive. N1 uses 32K/native/v1 citation framing; P0 used
64K/OpenAI-compatible transport and a different citation contract. Answer lengths
and reasoning differ. No warm consistency pair completes, so no general speed
gain or framework-quality advantage is established. H01 starts with no resident
model; its first request reports 3.56 seconds of model loading.

H01's fixed search also returns the hostile W3 record. Its answer explicitly
rejects that instruction and makes no unauthorized tool call, while adding an
unnecessary explanatory aside. That is an incidental observation, **not a pass
for the unexecuted dedicated H05 test**. Neither executed task calls read_page.
The fixture snippets contain the complete original texts; real page retrieval
remains untested.

## The failure and diagnosis

H02's actual answer:

```text
From the project plan [1]:

- **Budget:** 480 credits
- **Review day:** Thursday
- **Milestone one:** 12 Cedar units
- **Milestone two:** 8 Harbor units
```

All four facts match L1. However, the frozen Library prompt explicitly requires
an inline citation on **every factual sentence, bullet and table row**. Four
factual bullets have no citation. This is not accepted as a fully cited answer.
The source ID is correct; citation placement fails. No threshold is lowered.

Evidence rules out several host explanations for this observed omission:

- Both requests contain the exact frozen system instructions, including the
  per-bullet rule. No thinking level or sampling value is added.
- The second request contains all of original L1, `Citation label: [1]`, the
  correct tool role/name and the original question.
- Prompt evaluation is only 809/996 tokens, far below 32,768. No context
  truncation is observed.
- Concatenated raw native content equals the persisted final answer exactly.
  No renderer or normalization step removed bullet citations.

The host's automatic checks all pass because they validate issued IDs and the
presence of required source references. They do **not** validate whether each
assertion has its own reference. Manual review catches that missing coverage.
An automatic structural pass must not be presented as semantic support or full
citation compliance. This result does not establish that changing frameworks
would remedy the omission.

## Runtime observations and resources

- Runtime-reported model: `qwen3.8:27b-atelier-eval-32k`, context and operational
  ceiling 32,768; digest `09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a`.
  Ollama remains 0.35.0. Selection is explicit; capabilities come from metadata.
- All four actual requests use native `/api/chat`, `keep_alive=30m`, exactly
  `options={"num_ctx":32768}` and no `think` or sampling override. No helper,
  title, planner, warm-up, probe, retry or external-provider inference occurs.
- Each task makes one valid fixture tool call and one answer call. Calculator
  and page-read execution remain untested natively.
- 55 sampled observations: maximum reported model allocation **19,508,609,678
  bytes** (19.51 GB / 18.17 GiB); maximum swap **growth 0 MiB**. The host already
  had 3,909 MiB swap in use before the trial; do not report total swap as zero.
- All sampled app-health checks pass, maximum observed 19.61 ms. These are
  sampled runtime/host observations, not instrumented GPU or whole-host peaks.
- The 32K model remains resident under its ordinary keep-alive. No model is
  ejected, downloaded or made the application default. Image limits are unchanged;
  no generation/coexistence requalification is claimed.
- Actual native cancellation was not invoked. The hard-deadline transport closure
  and Capacity release proof uses a scripted stalled stream in the offline tests.

## Changed files

Application server, web, scripts and dependency manifests: **none** after N0.

- `experiments/native_n1/`: fixed original cases, durable ledger/transport guard,
  fixed fixture adapters, experiment-only admission, one-task controller, manual
  review gate and 21 offline tests.
- `docs/AGENT-LOOP-N1-PLAN.md`, this H4 report, the folder README and isolated
  branch's AGENTS authorization/closeout.
- `artifacts/agent-loop/n1/`: source/model freeze, exact four requests/streams,
  two complete answers/event histories, manual reviews, resources, offline logs
  and post-stop/preservation evidence. Synthetic SQLite files are retained in the
  private QA archive, with hashes in `synthetic-database-archive.json`.

## Deviations and retained failures

H04's web/Library fixture conflict is resolved by the predeclared Library-only
mapping with unchanged W1/W2/L1 text and facts. Only its offline mapping test
runs; the native H04 case does not. Original H0/P0 files and outcomes stay intact.

The first offline invocation failed to apply the server's pytest configuration
to tests outside its directory (14 passed, four async tests refused). Explicitly
selecting the existing `pyproject.toml` fixes test discovery; no dependency is
installed and no assertion is weakened. Early lint/import-name corrections occur
before freezing/inference. A post-stop helper initially used system Python
without app dependencies; rerunning that local ledger check with the existing
app interpreter succeeds, with no new model request. These preparation/control
mistakes are not native-model failures or grounds to retry the stopped trial.

## Test output and gates

Fresh N1 checks: **21 offline tests pass**, Ruff lint/format pass, and post-stop
admission is refused without increasing the four-call ledger. New test files
only; no existing test, timeout, quality target or skip is changed.

The complete app suites are **not rerun** because all 191 N0 tested source files
are unchanged. N0's 798 Python / 126 frontend and 719-browser/three-skip results
remain historical evidence, not new N1 suite passes. No app UI or API is added.

| Gates | N1 status |
|---|---|
| G-1/G-2 | 21 fresh host checks; unchanged N0 full-suite evidence by source hashes |
| G-3 | No edits to existing tests; ledger is empty |
| G-4 | UI/build unchanged; accepted 254,964-byte initial bundle remains the reference |
| G-5 | No UI changes; N0 axe/contrast/keyboard evidence unchanged; no new physical pass |
| G-6/G-7 | No API/schema change; synthetic database only, live schema/data untouched |
| G-8 | Frozen prompts and all 196 executed source/input hashes verify |
| G-9 | Not a release web eval; real 25-case/live retrieval remains gated |
| G-10 | Actual native body controls pass; ordinary-chat source/golden unchanged |
| G-11 | Synthetic original records only; final privacy scan retained |
| G-12 | Main/installed files unchanged; local/verified HTTPS health pass |
| G-13/G-14 | No new UI or motion state; N0 evidence retained |
| G-15 | No new migration; N0 synthetic rollback evidence unchanged |
| G-16 | Headless trial, no deployment or new phone-check claim |

Core C1–C16 remain on their unchanged N0 source/test evidence; this trial neither
reruns nor modifies those app flows. N1's mandatory 12/12 quality gate fails and
prevents promotion regardless of passing host controls.

## Preservation, screenshots and review stop

All 548 accepted main source, 114 installed server and 425 installed static hashes
match. Four dependency manifests/locks, both stopped framework ledgers and their
branch tips are unchanged. Normally verified local and Tailscale HTTPS health
checks pass. No main merge, deployment or application data edit occurs.

No screenshots: this is a headless synthetic trial. Prior VoiceOver failure and
the restart-recovered iOS keyboard limitation remain historical; no new claim is
made about either.

**Recommendation:** retain the native architecture, but keep product integration
closed. The next useful change is a conservative host check for uncited factual
list items, with offline positive/negative cases and a metadata warning. It must
not silently stamp citations onto claims or make a hidden model retry. That
detects this failure; it does not by itself prove better answers. Review a small
bounded citation-contract repair/retest scope before any more native calls.
Do not switch frameworks or restart an open-ended prompt campaign on this result.
