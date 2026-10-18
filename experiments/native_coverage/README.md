# Offline citation coverage prototype

No model calls, production hook or modification of the stopped N1 controller.
`check.py` detects obvious structural citation gaps; `warn_copy` demonstrates a
notice on a copy of a completed native message. It never verifies claim support
or repairs content. The generic `candidate.py` prompt is unexecuted.

From the root using the existing environment:

```sh
uv run --frozen --directory server pytest -c pyproject.toml -q ../experiments/native_coverage/test_check.py
uv run --frozen --directory server python ../experiments/native_coverage/replay.py
```

The C1 native retest is proposed in `docs/AGENT-CITATION-COVERAGE-PLAN.md` and
requires review after the stopped N1 trial. Do not reset the old ledger.
