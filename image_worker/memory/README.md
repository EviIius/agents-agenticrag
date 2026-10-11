# Frozen resource trial I1-0

This checkpoint reuses the existing I0 environment and model snapshot. It does
not alter I0 source or implement production job execution. Scope/stops are in
`docs/IMAGE-MEMORY-PLAN.md`; preserve every failed/successful stage separately.

`worker.py` is an isolated copy of the frozen I0 worker plus the declared free
cache setting, setting verification, per-image residency checks and latency
guards. It adds no component eviction, low-RAM callbacks, cache clears, prompt
changes, precision fallback, sampling or keep-alive override.

`run.py` enforces the frozen stage order and keeps source/requests/outputs under
the private `~/.local/share/workbench/image-worker/i1-0` directory. The interpreter
is the existing `image-worker/i0/venv`; model weights are not copied. It adapts the
unchanged I0 sampler within its own trial process, restoring it after supervision.
The supervisor still drains callback events and waits for the owned process to
exit and be reaped before recording completion or permitting the next stage.

Resource safety termination is distinct from the two intentional cancellations.
A safety signal is retained in the stage summary, cannot qualify as a success,
and ends this candidate. The OS swap measurement includes other host activity;
the guard is an operational stop, not a causal attribution to the image model.

The cache API's setting is not a hard bound on reported cache/live/host counters.
Keep those actual counters and limitations in the report. A four-image passing
trial does not qualify all models, contexts or simultaneous token decoding.

Guard tests use synthetic measurements and an owned fake worker. They complement
native cancellation/recovery rather than substituting for it.
