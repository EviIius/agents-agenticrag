# Approved everyday model comparison

See `docs/MODEL-COMPARISON-PLAN.md` for the frozen cases, smoke stop conditions,
three-pair order and approved targets. This evaluator does not implement Research.

`run_everyday.py` uses the existing app chat pipeline with a temporary database.
It disables automatic titles only in that database, requires the selected
model's reported 32K operational context and captures the actual answer payload.
Answer options must contain only the explicit context; sampling stays unset.
Each case is saved immediately, with first-delta and visible-text timing.
Accuracy and claim support require manual review; only E05's JSON format has an
automatic check. The isolated 600-second case timeout is an execution guard.

`run_comparison.py` runs the declared pairs sequentially. It checks every frozen
input hash and live inference/transcription activity before each suite. Web and
Library use the existing harnesses and unchanged grades. Web explicitly selects
the frozen `phase2-final-corpus`, retaining real planner decisions against common
recorded result batches; this is not a fresh live search test. Existing planner
sampling settings remain unchanged. The wrapper skips the harness's final model
unload to avoid ejecting a concurrent user. It records residency snapshots rather
than claiming peak memory and retains synthetic/public stream inputs and events.

Results are in `artifacts/model-comparison/pairs.json`; each entry points to its
suite report and log. JSONL streams preserve raw responses independently of a
suite's final benchmark/report writing. `--resume` skips completed reports, even
when their quality gates failed. Only explicitly documented setup-invalid
attempts are rerun; every such attempt remains in the index. Never retry a smoke
failure into a pass, overwrite reports or change cases to help a candidate.

The initial import-path failure and historical-fixture selection error are kept
as setup attempts. The interrupted Library attempt's persisted synthetic answers
and sources were recovered read-only; its missing raw pre-finalization stream
and retrieval benchmark are explicit limitations, not passing J7 evidence.

No actual recordings, Library documents or filenames are used. The Web harness
reads only the saved search credential through its existing read-only support;
the credential is never recorded in reports or model-stream payloads. No
production source, prompts, sampling preferences, default model or deployment is
changed by this comparison. A model download does not authorize promotion.
