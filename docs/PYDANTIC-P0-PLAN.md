# P0: isolated PydanticAI feasibility and performance trial

18 October 2026. Jake asked whether to implement all the proposed frameworks,
then said: **“We can start with Pydantic and test going forward.”**

Use one agent framework. Aether already owns its UI, stored chats, workflows and
native scheduler. PydanticAI is the next integration candidate; Hermes remains
stopped, and Qwen-Agent/LangGraph are not installed by this checkpoint.

## Scope and dependency

- `pydantic-ai-slim[openai]==2.57.0`, stable release published 16 October. This
  is PydanticAI with only the provider support needed for local Ollama, not the
  default bundle of cloud/UI/MCP/Logfire extras. Freeze all transitive versions
  and package hashes with uv before importing it. The mandatory `pydantic-graph`
  dependency is PydanticAI's internal engine, not a LangGraph installation.
- Separate Python 3.14.7 environment below the private QA root, new isolated
  branch `codex/pydantic-ai-trial`. App/Hermes/transcription/image environments,
  Ollama 0.35.0, service identity, ports, route and live code stay unchanged.
- Reuse `qwen3.8:27b-hermes-h0-64k` and its existing weights, context 65,536 and
  runtime sampling/thinking defaults. No new profile, download, default switch
  or second model; this isolates the framework change.
- Reuse the frozen six synthetic H0 cases, source records, four tools, 12,000
  source-character allowance and generic system text. No real files or accounts.

Sources: [minimal install](https://pydantic.dev/docs/ai/overview/install/#slim-install),
[local Ollama](https://pydantic.dev/docs/ai/models/ollama/),
[agent budgets](https://pydantic.dev/docs/ai/core-concepts/agent/#usage-limits).
Live docs can move; installed package/lock/source hashes are the execution record.

## Host and offline gates

1. Inspect the pinned installed interfaces and request construction before
   freezing the worker. Tool functions use typed, validated arguments. No hosted
   models, fallback, memory, MCP, shell, subagents, learning, telemetry export or
   background inference. No added output schema requiring another model turn.
2. Route every model request through the existing host admission boundary. Keep
   original sampling checks and permit only `options.num_ctx: 65536` as the
   context extension. Inspect real payloads; reject unexpected framework values.
   Framework request-limit counters omit some transport/fallback retries; the
   host must count actual upstream requests, including failed requests.
3. Scripted loopback inference must prove a two-request calculator/tool-result
   loop, streamed content/events, per-run state separation, actual cancellation
   with response closure and owned-process reaping, and released capacity. Accept
   both TCP EOF and reset as connection closure and retain raw diagnostics.
4. Keep exact tool allowlisting, fixture-only tool dispatch, argument validation,
   the existing Python audit controls and an explicitly clean process environment.
   They are qualification controls, not a general operating-system sandbox.
5. Freeze worker/controller/config, corpus and criteria before the real-process
   scripted checks. First genuine structural failure stops inference; retain
   setup or instrumentation failures without turning them into model results.

## Native schedule and shared budget

The previous Hermes/reference ledgers remain stopped at four actual calls. P0
gets a new linked ledger starting at **four**, preserving the **42-call aggregate
ceiling**, three calls per agent task and 180 seconds per task. No budget reset.

- First: PydanticAI H01 smoke, then the direct H01 reference.
- Then alternate agent-first / reference-first for H02–H06. All six task inputs,
  expected facts, citations, injection and missing-information requirements stay
  unchanged. The first cold task is labeled, not used as a matched warm timing.
- If all candidate tasks pass: three additional warm H01 pairs, alternating the
  arm order. Each uses the same model, context, tools, records and generic prompt.
- Maximum new calls: six agent cases × three + six direct answers + three warm
  pairs × four = **36**. Aggregate maximum **40/42**; two calls remain unused.
  Actual use may be less; no extra retries, calibration or second candidate.

P0 is a **new trial**, not a restart or regrade of Hermes H0. A direct reference's
quality failures are retained as comparison outcomes; they do not stop a new
Pydantic candidate. Candidate unsupported claims, protocol/permission failures,
resource failures and time/budget violations stop P0 immediately. No reference
failure is relabeled a pass. This distinction is declared before new inference.

The direct arm receives the full identical corpus up front, an oracle-evidence
reference. The agent retrieves it through fixture tools, which return all sources
of the requested kind. This does not evaluate production Search, real ranking,
live website coverage, actual user Library data or an answer-gain versus Search.

## Measurement and acceptance

- All six candidate tasks correct and supported, citations resolve to retained
  records, no unauthorized execution. Dedicated hostile-note and unsupported-owner
  cases must pass. All three warm H01 repeats must also pass without prompt tuning.
- Collect actual model/tool counts, prompt characters and reported input/output
  tokens, total task duration, first streamed content and final-answer timing.
  Preserve interim versus final content distinctions. Review extra claims manually,
  not just required-fact regexes. No model-based judge calls.
- Same shared native lock, at most 512 MiB sampled swap growth, at most 48 GiB
  reported model allocation, correct 65,536 context and live app health guard.
  No automatic ejection. Samples are not whole-host/GPU instrumented peaks.
- Report warm H01 pairs individually and with median/range; no invented statistical
  confidence or favorable-run selection. This small trial can show feasibility
  and overhead; it cannot establish general factual reliability.
- The old Hermes cold task is descriptive only, not a fair speed benchmark.
  A framework decision requires correct bounded execution and an identified
  efficiency benefit; no automatic speed or answer-quality gain is assumed.

Stop with the SPEC H4 report after P0. No production integration, app deployment,
prompt/default changes, other framework/model or Research restart follows.
