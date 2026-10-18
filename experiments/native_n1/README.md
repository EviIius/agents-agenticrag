# Native N1 experiment

The approved trial is **stopped at four calls** on S1-H02's per-bullet citation
failure. Do not delete/reset its private ledger, retry tasks or run the remaining
schedule. See `docs/AGENT-LOOP-N1-REPORT.md` and the retained artifacts.

Before execution the controller supported `prepare`, one `run --task S1-H01`,
and `review --task ... --review-file ...`. Each next task required a passing
manual review. Native admission is experiment-only and does not alter the app's
production model-qualification guard.

Offline verification, from the repo root with the existing tool environment:

```sh
uv run --frozen --directory server pytest -c pyproject.toml -q ../experiments/native_n1/test_trial.py
```

No new packages, real user data, web fetch or embeddings are used. The four
native requests use the existing native adapter and shared Capacity lock.
