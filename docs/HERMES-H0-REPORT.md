# Hermes H0 — stopped at the structural tool gate

## Summary

Jake confirmed the image and repair phone checklist, closing the prerequisite.
The approved Hermes v0.22.2 core environment is installed privately: 67 locked
packages, separate from Aether, transcription and the image worker. The real
Hermes library imports and its constructor returns, but the first structural
probe stops before conversation/inference because its effective tool schemas
do not equal the four approved host adapters. No 64K profile or model call follows.

This is a configuration/interface failure, not a model-quality result or proof
that Hermes cannot integrate. The pinned source documents a direct-tool setting
that addresses this mismatch. A prospective next check is prepared separately;
it has not run. H1/product integration is not qualified.

## Done-when checklist

| Item | Result | Evidence |
| --- | --- | --- |
| Phone prerequisite | User-confirmed pass | `artifacts/image-memory-recovery/phone-check.json`; exact selection “Both image paths and phone checks pass” |
| Pinned source and dependency lock | Pass | Original v0.22.2 commit `d923a5eb487a17c0a68801bba9ef0f56c81040a8`; nine original critical hashes and clean tracked source verified |
| Install approved core closure in isolation | Pass | `artifacts/hermes/h0/install.txt`, `installed-environment.json`: 67 packages; no optional extras |
| Existing host controls | Pass | 18 tests, `host-controls-execution.txt`; fake requests and disposable host subprocess only |
| Import actual Hermes library | Pass | `runtime-structural-1/worker-events.jsonl`: import completes at 1.77 s |
| Construct actual Hermes agent | Returns | Initialized event at 2.55 s; explicit iteration/time/toolset/context/memory controls |
| Exact effective tool allowlist | **Fail; stop** | Expected calculator/library_search/read_page/web_search; actual tool_call/tool_describe/tool_search/web_search |
| Host containment | Enforced in this probe; broader qualification incomplete | Disallowed Python file/process operations blocked, owned worker reaped; no external network access or inference |
| Chat request fields, streaming and tool execution | Not exercised | No POST to the scripted model endpoint; downstream raw assertions are false because the conversation never starts |
| 64K profile and native smoke | Not run | No create/load/model request; durable native ledger stopped at **0/42** |
| Six-case comparisons and factual/citation review | Not run | Original cases/targets remain unchanged; no quality or latency claim |
| Current Aether preservation | Pass | 548 frozen source hashes, 114 installed server files, 425 static hashes and installed environment/transcription hashes verify; local/HTTPS health pass |
| Hermes production wiring / photo editing | Not authorized here | Main/live application source remains the accepted image handoff release |

## Changed files

- Main: phone acceptance record and docs only, committed separately as `e7ffea2b`.
- Isolated `codex/hermes-h0`: merges accepted main, preserving the existing H0
  source, cases, host controls and original preparation reports.
- `experiments/hermes_h0/worker.py`: real pinned `AIAgent`, supported fixture
  registry/toolset adapters and callback hooks, private HERMES_HOME, explicit
  context/memory/iteration/time settings and host Python audit controls.
- `runtime_probe.py`: scripted loopback-only model endpoint, exact wire guard,
  owned process/deadline handling, retained raw events and fail-before-native gate.
- This report, prospective retry plan, AGENTS status and new H0 evidence.
- No Aether server/web/schema, app dependencies, prompts, sampling or defaults
  change. Hermes source is not patched.

## Deviations from SPEC.md

The previously approved named isolated framework/dependency/profile trial is the
only exception. H0 requires first-failure stopping; the native smoke and larger
comparison are not executed after the structural failure. No Research restart,
new agent UI or photo-reference integration occurs.

The core-only library route avoids the separately unapproved gateway/aiohttp
extra, as documented in the preparation. A package installation is not product
integration and does not justify changing the live environment.

## Runtime observations and diagnosis

The pinned default `tools.tool_search.enabled: auto` activates progressive tool
disclosure whenever deferred tools exist. It replaces selected custom schemas
with `tool_search`, `tool_describe` and `tool_call`; `web_search` remains direct.
Consequently `enabled_toolsets=["h0_fixture"]` alone does not guarantee the
expected model-facing schema names. The host rejects that mismatch before
`run_conversation` starts.

Official pinned documentation and implementation:

- [Tool search configuration](https://github.com/NousResearch/hermes-agent/blob/d923a5eb487a17c0a68801bba9ef0f56c81040a8/website/docs/user-guide/features/tool-search.md)
- [Tool schema assembly](https://github.com/NousResearch/hermes-agent/blob/d923a5eb487a17c0a68801bba9ef0f56c81040a8/model_tools.py)
- [Activation and off switch](https://github.com/NousResearch/hermes-agent/blob/d923a5eb487a17c0a68801bba9ef0f56c81040a8/tools/tool_search.py)

Read-only inspection identifies `tools.tool_search.enabled: "off"` as the
supported remedy: keep all four authorized schemas direct rather than allowing
the discovery bridge. This setting is prepared, unexecuted, in the retry plan.
It does not require a new dependency, new tool permission or upstream patch.

The Python audit layer also blocked startup file/process attempts. Their exact
targets were deliberately not captured; do not describe them as model-issued
shell commands, credential access or proven malicious behavior. No model request
had occurred. Audit hooks here are qualification controls, not a general OS
sandbox. Additional platform containment/diagnostic tests remain before native.

The raw probe's `no_denied_process_file_or_network_access` assertion is stricter
than the original requirement of no unauthorized execution. A denied attempt is
not an executed operation. This diagnostic issue does not rescue H0: the separate
exact-allowlist gate genuinely fails. Preserve the raw assertion and classify
it separately before any future trial; do not silently broaden permissions or
relabel untested callback/cancellation behavior as passed.

Only one fake metadata request (`GET /api/v1/models`) reaches the loopback fixture.
There is no chat-completion request, real Ollama request, fallback inference,
tool execution, 64K profile creation, context/default change or image generation.
The worker exits with code 1 and is reaped; total probe time is 3.068 s.

## Storage

`~/.local/share/workbench/qa/hermes-h0-20261017/hermes-env` contains
114,129,324 logical bytes (about 109 MiB). `du` reports 122,812 KiB (about
120 MiB); this is not an estimate of exclusive APFS physical usage. The source
checkout including Git/generated package metadata is 304,815,659 logical bytes.
No model weights are downloaded or duplicated. Inventory and measurements are
in `installed-environment.json`.

The tagged project's installed distribution metadata says `0.0.0`; source
identity is established by the exact approved release commit and lock hashes,
not that placeholder package version.

## Test output and preservation

- Eighteen existing host-control tests pass in 0.020 s; no native inference.
- Experimental Ruff lint/format pass after retained formatting findings.
- One real-process structural probe: **failed, stopped, no retry**.
- Native usage: **0 of 42**, durable stopped ledger retained. No 64K profile.
- Retain the exact executed worker/controller/protocol/case hashes in
  `structural-source.json`; raw HTTP, events, stdout/stderr and result are in
  `runtime-structural-1/`. Original preparation evidence is unchanged.
- Aether's unchanged 548 source files, 114 installed server files and 425 static
  hashes verify. Its app environment and transcription hashes also match the
  accepted release. No new app full-suite run is needed or claimed for this
  isolated host-only experiment; accepted release evidence remains 721 Python,
  126 frontend and 14 targeted browser checks.
- No real user recording/document/photo name or content is used in this trial.

## Screenshots

None. This is an isolated host/process check; there is no product UI change.

## Next review

The H0 first-failure boundary requires a stop here. Review
`HERMES-H0-RETRY-PLAN.md`: one configuration/containment check using fake
inference only, with no extra dependencies, weights or real calls. Native work
stays stopped until that corrected gate and its diagnostic criteria are reviewed.
The original 42-call ceiling, six cases, factual/citation targets and separate
H1/product review remain intact.
