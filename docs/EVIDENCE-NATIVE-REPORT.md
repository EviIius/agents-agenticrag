# Native evidence checkpoint report — 10 October 2026

## Summary

Authenticated host annotations now have separate quotation accounting, with
source labels, headings and definitions still charged. The one predeclared native
smoke failed and stopped automatically. Version-matched upstream source explains
the positional-schema incompatibility; a named-field remedy is prepared and
host-tested, **not executed natively or qualified**. Local image model research
is documented; the installed production application remains unchanged.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Preserve original inputs and executed source | Pass | 7,296 original hashes; 194 frozen source hashes; `manifest.json` |
| Exempt only authenticated generated context | Pass in host tests | `test_evidence_native.py`; `host-replay.json` |
| Retain original fields, heading, definitions and limits | Pass in host tests | Original field tests plus spoofed-prefix/heading/definition tests |
| Stop on the first native protocol failure | Pass | One grounded stream, failed child exit, raw trace and `smoke-review.json` |
| Native enforcement of prospective v12 positional schema | **Fail** | Required identity column missing in all four selections; duplicate IDs |
| Full Web/Library, semantic and performance qualification | **Not run / not passed** | No remainder, Library, candidate or retries after failed smoke |
| Prepare compatible schema remedy | Host tests only | `evidence_object_v14.py`, eight tests, prospective manifest |
| Regression checks | Pass | 452 Python / 39 frontend; `make-check.log` |
| Image model Mac feasibility research | Complete as research | `IMAGE-MODEL-OPTIONS.md`, primary source links and metadata |
| Production stability | Pass | 81 installed application files match stable `f87db46`; health responds |

## Changed files

- Server evaluation tooling: `evidence_contract_v13.py`, `contract_stream_v13.py`,
  `run_contract_v13.py`, copied isolated `trials/evidence-v13/` modules.
- Tests: `test_evidence_native.py` verifies provenance, budget retention, row
  identity and stop-before-next-call behavior. `test_evidence_object.py` verifies
  the prospective remedy without inference.
- Prospective tooling: `evidence_object_v14.py` uses evidence IDs as object keys
  and original column positions as true-valued property keys, with identity/scope
  keys required. It has no executable pilot driver or production wiring.
- Documentation: scoped native plan, this H4 report, image shortlist and AGENTS
  authorization/closeout records. Evidence lives in
  `artifacts/reliability/evidence-v13/`.

## Deviations from SPEC.md

This remains an explicitly authorized isolated answer-contract experiment.
The native failure ends the checkpoint as declared. Preparing a replacement
schema adds zero inference; it does not retry, reinterpret or repair the failed
response. Production prompts, sampling, runtime, dependencies, data, endpoints
and default remain unchanged. Research is shelved.

No new product UI or screenshots and no browser suite rerun: only isolated
evaluation tooling and research documents changed. Earlier browser outcomes
remain as previously recorded; this checkpoint does not claim a new full browser
release pass. The new image pipeline is a proposal requiring separately named
model/runtime approval, not an added feature.

## Runtime observations

### Native smoke: a schema compatibility failure

The original `nba-2021` case ran on `qwen3:30b-a3b-workbench-32k` with original
recorded sources and the existing planner/answer path. The answer returned JSON
and a normal stop after **5.33 seconds**. All four selected objects used columns
`[1,2]`, omitting the identity in column zero. Both row IDs were repeated. The
host rejected the response before emitting factual text, wrote the raw trace and
terminated the child automatically. The driver exited with failure.

The trace contains one grounded answer stream and two outer planner/answer
streams. The existing harness also warms the model; these stream counts are not
a count of every HTTP call. No new full Web report, remaining-case trial, Library
trial, candidate call or repeat followed. This is not an accuracy score or a
successful answer latency result.

The schema used `prefixItems` for mandatory positions and `items` for optional
positions. Ollama 0.35.0 pins llama.cpp `b11081`; that version's schema builder
chooses `items` when both keywords are present. It therefore restricts columns
to the optional enum and loses the mandatory prefix. Our schema design was
incompatible with that implementation. Its grammar documentation also excludes
`uniqueItems`, so reference uniqueness remains a host responsibility.
[Pinned runtime source](https://github.com/ollama/ollama/blob/v0.35.0/LLAMA_CPP_VERSION),
[array schema builder](https://github.com/ggml-org/llama.cpp/blob/b11081/common/json-schema.cpp),
[grammar limitations](https://github.com/ggml-org/llama.cpp/blob/b11081/grammars/README.md).

This explains the observed failure using version-matched upstream code; the
installed helper binary was not rebuilt or disassembled. The failure does not
establish that Qwen cannot answer the question. It establishes that this native
contract did not constrain the response as intended.

### Host-only replay

Replay all 16 completed v11 selections without changing their IDs or column
choices. One rejection becomes rendered evidence: the 23-row complete-list case
previously exceeded the prose limit because of generated host metadata. The
remaining 14 rejected and one unsupported selections stay failed/unsupported.
Original outputs and sources remain intact. This is an accounting diagnosis,
**not new inference, semantic qualification or a revised model accuracy score**.

Authentication requires the host boolean flag, complete known annotation prefix
and source-bound reference column. Page text alone cannot opt out of quotation
limits. Source definitions, projected header names and source headings remain
charged; generated summaries cannot be selected as factual units. Full display
context and original snapshots remain available. This provenance check is not a
proof that the source itself is true or that the selected fields answer the task.

### Prepared next remedy

The named-object schema uses required properties and literal booleans instead of
positional array prefixes. It also avoids relying on native `uniqueItems` or
large per-row `anyOf` branches. Host parsing still rejects duplicate/unknown
keys, missing identity/scope, ambiguous units, invalid booleans and over-budget
excerpts. No automatic insertion of missing fields or permissive normalization
repairs a failed selection. Its native compatibility, relevance, completeness,
coverage labels and latency **remain unmeasured**.

### Image research

The inspected machine has M5 Pro / 64 GB unified memory / 16 GPU cores, macOS
27.0 and about 1.6 TiB available storage. FLUX.2 klein 4B through Draw Things is
the recommended first local trial; compare Z-Image-Turbo next. Larger Qwen and
klein models and SDXL are documented with primary sources, license differences,
implementation caveats and a proposed measured trial. Hardware fit is an
inference, not a benchmark. No image model, runtime, package or app was installed,
downloaded, launched or integrated.

## Test output

- Preflight v13 evidence/stream/field/schema tests: **28 passed**.
- Prospective object/native/schema focused tests: **20 passed**; eight are new
  prospective object tests. No model call occurs in these tests.
- Initial lint found overlong lines; formatting repaired them before execution.
  The prospective preformat lint output is retained. Final eval-file lint passes.
- Initial system-Python HTTPS source lookup failed certificate verification;
  curl succeeded with normal TLS verification. No insecure TLS bypass was used.
- Coverage backup initially referenced a nonexistent `server/coverage.json`;
  the original tracked `artifacts/coverage.json` was recovered from unchanged HEAD
  and retained. New coverage is stored separately and the original restored.
- Final full `make check`: **452 Python tests and 39 frontend tests pass**; lint,
  formatting, types (111 files), required coverage, 74 contrast pairs, API types,
  additive/motion guards and privacy audit pass. The earlier v13-only check also
  passed (444 Python / 39 frontend), retained separately. No new `make e2e` or
  live web qualification run; no claim of release readiness.

## Screenshots

None newly captured. No product UI changed; evidence is public/synthetic and no
real recording/document filename or text appears in new fixtures or captures.

## Open questions for Jake / next scope

No blocker requires a runtime upgrade. The next refinement should freeze and
natively verify the prepared named-field contract, using the original first
case and immediate stopping before a gated original-corpus run. Retrieval gaps,
per-fact support, completeness, ordinary-chat grounding and buffered latency
still require evaluation before product integration.

For images, the concrete proposal is a Draw Things / FLUX.2 klein 4B local trial
with fixed synthetic inputs and memory/speed/cancellation measurements. A named
runtime/model installation and any later Atelier integration need separate
approval. This checkpoint stops for review under AGENTS.md and SPEC §H4.
