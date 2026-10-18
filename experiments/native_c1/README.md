# C1 native retest

Isolated bindings over the frozen N1 controller. See
`docs/AGENT-C1-RETEST-PLAN.md`. No app source changes. Each run requires its
predecessor's passing semantic review; any required failure permanently stops.
Never reset either ledger or rerun a task.

Use the existing server environment, from the repository root:

```sh
PYTHONPATH=. server/.venv/bin/python experiments/native_c1/controller.py prepare
PYTHONPATH=. server/.venv/bin/python experiments/native_c1/controller.py run --task S1-H01
PYTHONPATH=. server/.venv/bin/python experiments/native_c1/controller.py review --task S1-H01 --review-file /path/to/manual-review.json
```

These commands make native calls only for `run`. `prepare` only reads metadata
and host resources. Actual model prompts are synthetic; no production data opens.
