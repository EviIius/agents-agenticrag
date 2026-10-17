# Hermes H0 preparation — execution prerequisite pending

17 October 2026. This is a preparation report, not a completed Hermes feasibility
result. Jake approved the pinned isolated trial and then answered **“I haven’t
checked yet”** to its phone prerequisite. No acceptance, installation, native
output or quality pass is inferred from that approval.

## Summary

Preparation is saved on `codex/hermes-h0`, based on live main `713b3a4d`.
The exact Hermes v0.22.2 source and locked core dependency closure are verified.
Eighteen standalone host controls pass; six synthetic tasks/expected facts are
retained. The current live Aether source, assets and health are verified unchanged.
Hermes installation, 64K profile and native comparison await the phone result.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Approved source pin | Prepared | Official checkout `d923a5eb487a17c0a68801bba9ef0f56c81040a8`; clean Git tree, critical source/lock hashes |
| Core dependency inventory | Dry-run only | Frozen upstream uv.lock: would install 67 packages, download 51; no optional extras; environment does not exist |
| Host request/budget/tool controls | 18 passing unit tests | `host-controls-final.txt`; tests use fake request bodies and temporary ledgers |
| Inputs and grading intent | Prepared, unexecuted | Six tasks in `experiments/hermes_h0/cases.json`; expected facts, support/refusal cases and comparison limits explicit |
| Real Hermes initialization/stream/permission checks | Not run | Needs the approved isolated installation after phone acceptance |
| Separate 64K profile | Not created | No runtime profile, default or weights change |
| Native comparison/quality/resource results | Not run | Zero model calls; the 42-call budget is unspent |
| Live application preservation | Verified | 560 frozen source/test/config hashes, 114 installed server files, 425 static hashes; local/HTTPS health and PID 60537 |
| Physical phone acceptance | Pending | Actual user reply: “I haven’t checked yet” |

## Changed files

- `experiments/hermes_h0/protocol.py`: experimental host-only admission controls.
  Durable global/per-task counters include retries; rejected requests do not
  reach inference. Persist a stop state, enforce time/cancel checks, reject
  unselected sampling/fallback models/tools, constrain fixture IDs and arithmetic,
  bound returned source text, terminate/reap only owned child process groups.
- `test_protocol.py`: 18 fake-request/host tests, including concurrent admission,
  persistent stop, malformed/forced tools, exact sampling, timeout/cancel and a
  real disposable sleeping subprocess. This subprocess does no model work.
- `cases.json`: fixed synthetic corpus and six tasks. Direct-answer comparison
  is an oracle-evidence reference supplied the full same corpus; do not call it
  the production Search baseline or use it to claim answer gain over the app.
- `README.md`: exact pending stages and source-review constraints.
- Docs/AGENTS/evidence: scope approval, this report, package dry-run and manifests
  under `artifacts/hermes/h0/`. No `server/app`, web, API, schema or product
  dependencies change.

Private preparation root:
`~/.local/share/workbench/qa/hermes-h0-20261017/`. The source checkout, including
Git data, is **304,709,006 logical bytes**. Physical disk usage and future package
environment size have not been measured; there is no weight download.

## Deviations from SPEC.md

The user explicitly authorized the named isolated agent/dependency/profile trial;
none of that extends to production integration or Research. This preparation
observes its phone condition rather than claiming release acceptance.

Source review found that the pinned gateway API imports **aiohttp**, absent from
the approved 67-package core closure. Adding an optional dependency was not
silently approved. The documented Python `AIAgent` library offers callbacks and
explicit tool/iteration/time controls: assess that supported interface in a
supervised process for H0, with a later host SSE bridge. A full gateway/API-server
path needs its dependency decision. This is an inspected transport constraint,
not a failed native protocol trial or a new inference candidate.

## Runtime observations

No Hermes package import, process, inference or model creation was attempted.
The dependency command uses `uv sync --frozen --no-dev --dry-run` with an explicit
future private environment; it creates no venv. The pinned source includes an
unlimited default iteration setting, provider/model request heuristics and
optional background behavior. These make real wire/permission checks necessary;
host unit tests alone do not qualify the framework.

Main/live remains the accepted repair release. Model defaults, image admission,
service/plist/Tailscale and existing interpreters are unchanged. No photo edit,
Research experiment, image generation or external communication is performed.

## Test output

- First host control set: **16 passed**, zero native calls.
- Added malformed schema/forced-tool negative controls: final **18 passed**.
- Initial Ruff check retained one import-order finding. The import-only correction
  is applied; final formatting and lint pass. Test criteria are unchanged.
- All **560** frozen application/test/config files match the release; **114**
  installed server files and **425** installed static hashes verify. Local and
  normally verified HTTPS health pass; service PID remains **60537**.
- No new application full-suite invocation is claimed. The exact unchanged app
  retains release evidence: 686 Python, 126 frontend, 110 contrast pairs and one
  complete browser run with 711 passed / three unchanged skips. The new experimental
  controls are tested separately and do not constitute a Hermes runtime pass.

## Screenshots

None needed for this host-only preparation. No real filename, recording,
transcript, document or photo is included in logs, inputs or captures.

## Open questions and next action

Only the existing phone prerequisite is pending: Tools shows Model default,
typing/sending works, and Workflows opens. Jake need not reapprove the named
Hermes scope or its 42-call ceiling after confirming those results.

Then install the locked core environment and validate the real supervised Hermes
process against fake inference before freezing a native smoke. Preserve actual
sampling/defaults, metadata qualification, native Capacity, callback streaming,
allowed tools, cancel/reap behavior and the absolute call/time limits. Stop at the
first required gate failure and report it; do not run a full comparison merely to
spend the approved budget. H1/product wiring remains a later review checkpoint.
