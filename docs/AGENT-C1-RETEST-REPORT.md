# Native C1 citation reminder retest report

18 October 2026 · isolated `codex/native-agent-loop` · **failed and stopped**.

## Summary

The approved frozen v2 candidate fails the first original task after **one native
request**, taking **29.65 seconds**. It asks for the records instead of using the
available search tool, producing neither the required comparison nor citations.
No invented specification fact is observed, but that is insufficient for task
success. This candidate has **no demonstrated answer gain** and does not qualify.
The other eleven tasks remain unrun. Main and the live app are unchanged.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Exact reviewed generic v2 prompt on actual wire | Pass | `frozen.json`, `S1-H01/requests.json`, `summary.json` |
| Same daily 32K digest/runtime, default thinking and no sampling override | Pass | Admission and request; all non-message fields equal original N1 |
| New ledger; old N1/Hermes/PydanticAI ledgers preserved | Pass | `ledger-latest.json`, `preservation-final.json` |
| Original six questions/records/H04 mapping preserved | Pass | Frozen original files and source hashes |
| Original H01 facts and required references | **Fail** | Zero retrieved sources, tool calls or citations; manual review |
| No invented specification fact/forged reference | Observed on one answer | Does not excuse absent required facts and citations |
| Local citation coverage | **Not checked** | No sources retrieved; no gaps is not a citation pass |
| Twelve full manually reviewed passes | **Not achieved** | Zero passes / one attempted; eleven tasks unrun |
| First required failure durably stops | Pass | Post-stop task admission and request admission both refused offline |
| Resource and deadline bounds | Pass for sampled execution | 31 observations; metrics below |
| Product integration / N2 readiness | **Not qualified** | No merge, deployment or later-stage inference |

Artifacts are under `artifacts/agent-loop/c1/` unless specified otherwise.

## Actual answer and diagnosis

H01 asks for Cedar and Harbor storage and export formats, citing each original
specification. The required answer is Cedar 24 units/CSV and Harbor 36 units/JSON.
The fixed fixture tools offer those records through `web_search` and `read_page`.
They are identical to the original N1 fixtures; this is an oracle-fixture test,
not a real search-quality benchmark.

The candidate instead says it has no supplied records and asks the user to paste
the documents, supply URLs, or identify search terms. It invokes **no tool**.
There is correctly no local Library tool in this web-only task, but web search
and page reading were both available on the actual request. The missing retrieval
is a model tool-selection/task-completion failure, not a demonstrated missing
schema or network/tool-result failure. No tool ran, so tool-result correctness,
injection defense and retrieval quality cannot be evaluated here.

The reviewed reminder arrives byte-for-byte, with the original task, tool schemas,
32K context and other wire parameters. Prompt evaluation is 951 tokens; no
context limit, truncation, invalid tool call or transport error is observed.
Actual streamed answer text equals the persisted answer. No citations are stamped
onto it and there is no automatic retry or hidden helper call.

The original N1 H01 passed in 36.99 seconds with two calls. This candidate's
29.65-second failure with one call is **not a speed gain**: it did not do the work.
One result also does not establish that the reminder caused non-retrieval or that
another agent framework would fail identically. It does establish failure of
this predeclared candidate's qualification gate.

## Runtime observations and budgets

| Metric | Observed |
|---|---:|
| Native requests | **1 / 36**, then permanently stopped |
| Tool calls / retrieved source records | **0 / 0** |
| Total task time | **29.65 s** |
| Resource samples | **31** |
| Pretrial swap already in use | **3,861 MiB** |
| Maximum observed swap growth | **0 MiB** |
| Maximum Ollama-reported model allocation | **19,508,609,678 bytes** |
| Maximum sampled local health latency | **23.39 ms** |
| Runtime / context | Ollama **0.35.0** / **32,768** |

The digest remains `09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a`.
No model is downloaded, unloaded, replaced or made the default. The shared native
Capacity lease is released. These samples do not measure whole-host peak memory
or qualify simultaneous model decoding. No native cancellation trial is claimed.
Budget left over does not authorize another task or retry.

## Changed files

- `experiments/native_c1/`: isolated controller bindings and eight new tests,
  reusing frozen N1 execution/admission/counters/fixtures/deadline/manual review.
- `docs/AGENT-C1-RETEST-PLAN.md`, this report, roadmap README and authorization
  entries in AGENTS.md.
- Separate C1 requests, raw stream, ordered events, results, immutable manual
  review, resource samples, source freeze, preservation and audit records.

No application/server/web source, original prompt, dependency, migration,
production data or existing test is edited. Synthetic SQLite files are archived
privately with verified hashes, not committed.

## Deviations and retained preflight failures

The controller deliberately allows initial residency to be empty or contain only
the exact admitted daily profile, as the reviewed C1 plan permits. Nothing is
unloaded. The original N1 preparation's stricter empty-residency prerequisite is
not presented as a measured safety requirement or changed runtime behavior.

Preflight lint found a missing annotation for imports deliberately placed after
local path setup. A comment-only correction was made **before any native call**;
the old prepared source/manifest and AST-parity record are retained. The zero-call
C1 ledger was preserved unchanged. Final lint, formatting and all 76 offline
checks pass. The prompt candidate never changed.

## Test output and preservation

- **76 offline tests pass:** eight new C1 controls, 21 original N1 controls and
  47 citation-coverage tests. Existing tests are unchanged. Scripted transport
  verifies actual prompt injection, no sampling override, unchanged answer text,
  uncited-list stopping and restoration of scoped bindings after errors.
- Ruff lint and format checks pass for the C1 controller/tests. `git diff --check`
  and privacy audit pass; evidence is synthetic.
- Frozen executed C1 sources/inputs, all 196 original N1 files, the stopped N1
  four-call ledger and both earlier framework ledgers verify unchanged.
- All 548 accepted main source hashes, 114 installed server hashes and 425
  installed static hashes verify unchanged. Dependencies and original main
  commit `e7ffea2b` are intact; local and verified HTTPS health pass.
- Full app/browser suites are **not rerun** for isolated experiment code. The N0
  results (798 Python, 126 frontend, 719 browser passes with three existing skips)
  are historical evidence, not fresh C1 runs or a quality qualification.

Existing production Search/Library prompts, API/schema/data, motion, request
parameters, service identity, bind/port and Tailscale route remain unchanged.
Original N2 quality gates and 90/200-second timing targets are unchanged and unrun.

## Screenshots

None: no UI or product state changed. No real recording, Library content, photo,
filename, chat text or phone screenshot was used. Historical accessibility and
phone limitations are not retested or claimed passed.

## Decision and next steps

**End this candidate and retain the existing single-shot Search/Library product.**
Do not advance this loop to N2/N3 or start another prompt/framework campaign
automatically. A structural citation checker can warn about missing markers; it
cannot make the model retrieve evidence, complete the task or support its claims.

The useful product direction is explicit retrieval through the existing Search
and Library pipelines, with honest source/error presentation. Their retrieval is
controlled by the host, so the model cannot skip the lookup as it did here. That
does not make ordinary answers infallible; any further quality work should start
from a concrete failing production example and a measurable, bounded repair.

No further approval is needed to keep the current app running. This checkpoint
ends with the failed evidence preserved; no native continuation is pending.
