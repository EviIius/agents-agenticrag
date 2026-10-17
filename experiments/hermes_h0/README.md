# Isolated Hermes H0 preparation

This directory is not imported by Aether. No app/server dependency is added.

The user approved Hermes v0.22.2 core dependencies, a separate 64K profile reusing
installed Qwen3.8 weights, and the bounded trial. The approval question put the
phone check first. Jake subsequently answered **“I haven’t checked yet.”** Source
and harness preparation is permitted; installation/profile creation/native calls
remain pending that result. Do not manufacture a phone acceptance file.

## Prepared

- Official source pin: `d923a5eb487a17c0a68801bba9ef0f56c81040a8`.
- Source checkout, package-resolution dry-run and future isolated environment:
  `~/.local/share/workbench/qa/hermes-h0-20261017/`.
- Frozen upstream `uv.lock`; dry-run resolves 67 packages with no optional extras.
- `protocol.py`: durable shared call ceiling and stop state, per-task limit,
  time/cancel checks, exact request/sampling checks, four fixture-only tool kinds,
  source budget, bounded calculator and owned-child termination/reaping.
- `cases.json`: six synthetic tasks and explicit expected facts. Direct answers
  get the same full corpus; this is an oracle-evidence reference, not an execution
  of Aether's production Search pipeline. No answer-gain claim may conflate them.
- `test_protocol.py`: host controls using fake requests, no Hermes import or
  native inference.

Run host controls from the repository root:

```sh
. scripts/tool-env.sh
uv run --directory server python -m unittest discover -s ../experiments/hermes_h0 -p 'test_*.py' -v
```

## Source-review findings to resolve before a native smoke

The pinned API server imports `aiohttp`, which is absent from the approved locked
core dependency closure. Do not silently add messaging/other extras. The supported
Python `AIAgent` library provides explicit toolsets, stream/event callbacks,
iteration and time limits. Use it in a supervised isolated process for H0 if its
real structural tests pass; Aether can translate process events to SSE in a later
integration. Gateway API transport would require a separate dependency decision.
This is a source finding, not an executed Hermes import/protocol failure.

The source defaults `max_iterations` to unlimited and can add model/profile
request parameters. Always set the approved limit; capture actual requests and
reject injected sampling, unknown models/tools and uncounted auxiliary requests.
Do not modify the pinned Hermes source or silently normalize away failures.

## Next after the phone result

1. Record the actual phone result and verify the pinned source/environment roots.
2. Install the frozen core closure only in the approved private environment;
   inventory installed versions/storage before executing Hermes.
3. Prove the real isolated Hermes process obeys permissions, exact payloads,
   streaming/reconnect, tool allowlist, deadlines and cancellation with fake
   inference. Current host tests alone do not establish those Hermes properties.
4. Freeze the final worker/controller/prompt/case hashes, then create the approved
   64K profile without extra sampling values or new weights. Preserve the default.
5. Run one smoke. Protocol/permission/support/resource failure stops native work;
   no retry or larger stage. If it passes, use the original bounded schedule:
   six direct answers plus six Hermes tasks twice, at most three calls per task,
   at most 42 model calls in total, 180 seconds per task. Include retries and
   auxiliary calls. Cancellation and host Capacity must gate actual native work.
6. Manual claim/citation review and H4 feasibility report before H1 integration.

No Hermes execution, native result or quality/latency qualification exists yet.
Research, reference-photo editing and production agent wiring remain out of scope.
