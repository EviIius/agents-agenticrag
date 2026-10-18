# PydanticAI P0 (isolated, not application code)

Scope, criteria and native schedule: `docs/PYDANTIC-P0-PLAN.md`.
The installed minimal package and complete transitive hashes are in `uv.lock`;
its environment is private under the P0 QA directory. No application import,
route, model default, dependency lock or deployment uses this code.

## Entry points and retained attempts

- `runtime_probe.py` / `worker.py`: original scripted attempt. Retained failed
  usage-logging API call, zero native requests. Never rerun or overwrite.
- `runtime_probe_result_v2.py` / `worker_result_v2.py`: identical framework
  candidate with corrected result logging. All three scripted processes passed.
- `native.py`: prepared original controller, retained with the first source freeze.
- `native_result_v2.py`: first successful native candidate task. Retained intact.
- `native_counter_v3.py`: active native controller. Same candidate/settings/
  schedule; future ledger task keys are namespaced so they cannot collide with
  old stopped Hermes reference keys. All four old calls remain counted.
- `direct_worker.py`: one direct oracle-evidence reference per scheduled task.
- `policy.py`: narrow Python audit controls; not an operating-system sandbox.
- `test_policy.py`: eight audit/context controls. Original protocol's eighteen
  controls and fixture tools are reused unchanged from `experiments/hermes_h0/`.

The controller runs **one** task, then requires an evidence-backed manual claim
review. Do not automate passing these reviews. A failed candidate stops the new
ledger. Reference quality failures remain failed comparisons under the plan's
predeclared rule. Every actual upstream request is counted by the host.

The two instrumentation fixes preserve original files, raw failures and hashes.
They neither retry a native answer nor tune the model/prompt/tools. After this
checkpoint, stop for review; no implied application integration or Hermes restart.
