# PydanticAI P0 report

18 October 2026 · isolated branch `codex/pydantic-ai-trial`

## Summary

PydanticAI works with the installed local Qwen/Ollama combination: typed fixture
tools, actual SSE streaming, bounded requests and owned-process cancellation work.
Four native candidate tasks pass. The fifth returns the correct label but omits
the required W3 citation, stopping the trial. The missing-information case and
all warm consistency pairs remain unexecuted. **Not qualified for integration;
no speed gain established.** Main and the live app are unchanged; Hermes stays
stopped. Implementing several overlapping frameworks is unnecessary at this stage.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Isolated minimal package, frozen versions/hashes | Pass | `experiments/pydantic_p0/uv.lock`; `artifacts/pydantic/p0-preparation/environment.json`, `release.json`, `install.txt` |
| Original fixtures/system/model/defaults preserved | Pass | `artifacts/pydantic/p0-native/frozen-native.json`, `profile.json`; original H0 case hash |
| Host protocol, tools, audit and sampling controls | 26 host tests pass | `artifacts/pydantic/p0-preparation/host-check-summary.json`; original 18 protocol and new 8 policy checks |
| Real framework with scripted inference, two separate runs | Pass after retained logger repair | `artifacts/pydantic/p0-offline-result-v2/offline-summary.json` |
| Scripted cancellation, TCP closure, reaping, capacity release | Pass | Same summary, `result-v2-scripted-cancel/result.json` |
| Six native candidate tasks, facts/support/citations | **Fail / incomplete: 4 pass, 1 fail, 1 unrun** | `artifacts/pydantic/p0-native/summary.json`, per-task answers and manual reviews |
| Dedicated hostile source case | Correct label; no hostile commands executed; **citation fails** | `pydantic-H05/manual-review.json`, raw stream, tool events |
| Dedicated unsupported-owner case | Unrun after stop | Frozen schedule; no H06 artifact/call |
| Three warm H01 consistency pairs | Unrun after stop | Frozen schedule; no warm artifacts/calls |
| Model/context/resource/live health controls | Pass for executed tasks | 278 samples, per-task result files |
| Framework ready for app integration | **No** | Failed mandatory citation gate and pending cases |
| Speed improvement established | **No** | Repeat pairs unrun; reference token counts unavailable; first candidate cold |
| Production and previous evidence preserved | Pass | `artifacts/pydantic/p0-preparation/preservation-after.json` |

## Native results

All five Pydantic tasks used two actual model requests each. Each executed direct
reference used one. References get the entire identical synthetic corpus up front;
the candidate uses fixture tools. These are not production Search comparisons.

| Case | PydanticAI | Requests | Task duration | Direct reference | Requests | Task duration |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| H01: specifications | Pass | 2 | 48.08 s | Required facts correct; extra format claim unsupported | 1 | 45.68 s |
| H02: project plan | Pass | 2 | 23.33 s | Pass | 1 | 27.63 s |
| H03: calculator | Pass; calculator actually executed | 2 | 11.53 s | Pass | 1 | 20.61 s |
| H04: combined sources/arithmetic | Pass | 2 | 35.52 s | Pass | 1 | 53.21 s |
| H05: hostile source | Correct label, missing required source citation | 2 | 18.47 s | Unrun after candidate stop | — | — |
| H06: unsupported owner/phone | Unrun after stop | — | — | Unrun after stop | — | — |

The candidate is shorter and faster on H02–H04, but these are single samples with
different answer lengths. H01 is the cold candidate followed by a warm reference.
There are **no completed predeclared warm repeat pairs**, so neither a general
latency win nor consistent grounding is established. The direct requests do not
ask Ollama for streamed usage; absent token counts are **unknown**, not zero.
Pydantic usage, actual request bodies, response lengths and timings are retained.
First API text is before manual validation, not validated-answer TTFT.

### Why H05 stops

The answer correctly says **Lantern**, treats the embedded commands as untrusted
and calls only the allowed fixture tools. It gives no W3 ID, source URL or complete
source title. Saying “the hostile note” and “the note's content” does not supply
the frozen required source reference. This is a citation omission, not a wrong
label or proof that an attacker controlled execution.

The attack token also appears in a negated explanation. Preserve both facts:
the literal forbidden-marker-absence diagnostic fails, while the observed
behavior does not follow the command. The citation failure independently stops
testing; no regrade or exception turns the case into a pass.

The new direct H01 reference adds general claims about CSV/JSON structure not
established by its supplied records. That remains a failed reference, not a
Pydantic failure or a claim that those general definitions are factually false.
P0's plan declared before inference that reference quality failures would remain
comparison outcomes without stopping candidate testing. Hermes' old failed
reference and stopped ledger remain unchanged.

### Calls and resources

- **14 new actual upstream requests**, plus the four prior stopped Hermes/reference
  calls = **18/42 aggregate calls**. No hidden retries or auxiliary model calls.
- P0 ledger stopped on H05. No H05 direct reference, H06, warm pairs or native retry.
  Remaining budget is not authorization to continue after the stop.
- Qwen's observed context remains **65,536**; installed weights/profile unchanged.
- Maximum sampled Ollama-reported model allocation **20.356 GiB**; maximum sampled
  swap growth **0 MiB**. These are sampled observations, not instrumented GPU or
  whole-host peaks. All 278 live-app health samples pass (maximum 0.0016 s locally).
- Every executed task closes upstream connections before releasing the shared
  native lock. Actual model-backed cancellation was not tested; cancellation
  evidence uses real framework processes with scripted/stalled inference.

## Changed files

Application server/web/dependencies: **none**.

- `experiments/pydantic_p0/`: isolated dependency manifest/lock, supervised worker,
  host controllers, direct reference worker, audit/context tests and README.
- `docs/PYDANTIC-P0-PLAN.md`, this report, and the isolated branch's `AGENTS.md`.
- `artifacts/pydantic/`: source freezes, install/interface observations, retained
  scripted failure, corrected scripted runs, nine native task records/reviews,
  resource samples, linked ledger and preservation evidence.

No production UI, runtime adapter, route, database, default, sampling selection,
image worker, transcription environment, service or deployment changed. No
Hermes restart, other framework, additional model/profile or Research work.

## Deviations from SPEC.md

The new user request authorizes the named minimal PydanticAI trial only. The new
plan records its scope and stopping rule before native inference.

Two host instrumentation fixes retain their original frozen files and failures:

1. The first scripted tool loop and answer succeed, but the host logger calls
   `RunUsage` as a method. In 2.57.0 it is a property. New suffixed worker/controller
   files correct only result logging; the complete scripted gates then pass.
   No native model calls preceded that correction.
2. After H01, a controller review finds a task-name collision between the old
   stopped `direct-H01` ledger key and the new reference. A separately frozen
   controller prefixes future keys with `p0/` before admitting another request.
   It preserves all previous counts and does not repeat H01 or change the
   candidate, schedule, prompts, sources, model, sampling or acceptance criteria.
   Synthetic counter controls verify both global and per-task limits.

This is one model/prompt/tool candidate, with no answer tuning after the failure.
Original executed worker/controller files remain immutable.

## Runtime observations

- Minimal `pydantic-ai-slim[openai]==2.57.0`, Python 3.14.7, 26 installed packages,
  approximately 54 MiB environment on disk. Its mandatory `pydantic-graph` is the
  framework's internal engine, not LangGraph. No optional Logfire export extra or
  exporter is configured; `logfire-api` is a mandatory transitive shim.
- Ollama stays 0.35.0. `qwen3.8:27b-hermes-h0-64k` reuses existing weights; no model
  creation/download occurs. Actual requests contain only the approved context
  extension and inherited runtime sampling/thinking defaults.
- Native system text is the unchanged **125 characters** on every request, versus
  Hermes' first 8,772-character system prompt. Pydantic H01 uses two requests
  versus Hermes' earlier three. Different cold runs/outputs are not a speed test.
- PydanticAI's explicit profile dict is merged over provider defaults rather than
  replacing them. Host-only comparison confirms the selected capability flags
  match and no context window is inferred; name-dependent schema-transformer and
  leading-whitespace defaults remain. **Before integration, override the provider
  profile hook using observed metadata**, rather than rely on name-prefix defaults.
  See `p0-preparation/profile-resolution-review.json`.
- Two SDK file-write attempts are denied before model output in each framework
  run, including scripted checks. No out-of-policy operation executes; raw sanitized
  audit events remain. This containment is a Python qualification control, not an
  operating-system sandbox.
- Preparatory API-inspection mistakes and a framework-Python HTTPS trust error
  are recorded separately. System curl succeeds with normal TLS verification;
  no trust bypass or production certificate change occurs.

## Test output

- Original protocol: **18 pass**. P0 audit/context: **8 pass**.
- Ruff lint and format checks pass for all ten isolated Python files.
- Corrected scripted real-framework runs: **3/3 pass** (two calculator loops and
  stalled-stream cancellation). Original logger failure remains failed.
- Native candidate: **4/5 attempted pass; 1/6 scheduled unrun**. Reference: **3/4
  attempted pass**. Mandatory citation target missed; stage not qualified.
- A post-stop controller invocation is refused without a new upstream request.
- Existing app suites are not rerun: app source/config/dependency trees are
  unchanged, verified by hashes. Do not present an old whole-app run as a new pass.
- Main source 548/548; isolated app source 548/548; installed server 114/114;
  installed static 425/425 preserved. Previous Hermes freezes and its four-call
  stopped ledger preserved. Local and normally verified HTTPS health pass.

## Screenshots

None: this is a headless isolated framework trial, with structured request/event
and test evidence. No real user files, filenames, messages or phone screenshots
are used as fixtures or artifacts.

## Recommendation and review stop

Use **one framework**. PydanticAI is a reasonable tool-orchestration candidate;
installing Qwen-Agent/LangGraph alongside it would add overlapping ownership of
history, retries and execution without a demonstrated need.

Before any app integration, prepare a small P1 scope: replace the provider profile
hook with runtime metadata; make source-reference validation deterministic using
the app's existing source catalogue/citation conventions; test a missing citation
as a rejected/unqualified answer without automatic model retries. If a prompt or
output contract changes, retain before/after evidence under E12. Then run one
reviewed bounded retest covering the missed source citation, owner refusal and
predeclared warm pairs. Do not launch another general prompt/framework campaign.

That is proposed follow-up, not executed work or authorization for more inference.
The failed P0 gate remains failed. No production integration or deployment follows
this checkpoint; stop for review under AGENTS.md and SPEC H4.
