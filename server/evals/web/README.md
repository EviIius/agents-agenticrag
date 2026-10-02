# Web evaluation

`cases.yaml` is JSON syntax (valid YAML 1.2), so the harness needs no extra dependency.
It contains 25 generic cases plus Jake's comprehensive NBA Finals-losses regression.

- `make eval-web-record CASE=nba-2021`: record actual provider responses/raw public pages.
- `make eval-web`: replay web fixtures with real local Ollama planner/answer calls.
- `make eval-web LIVE=1`: live web with real local inference.
- `RANKING=hybrid`: include the configured embedding model for the ranking comparison.
- `--replay-corpus`: freeze a recorded turn's public result batches while the planner runs normally.
- `--replay-plans`: also freeze recorded plans for an isolated ranking comparison. Decision scores then describe the recording, not a new planner run.
- `--planner-trial`, `--answer-trial`, `--table-trial`: experiments confined to the evaluator process. Reports record exact prompts/schema/hashes and table variant. No production agent or extra model call is added.

Answer sampling stays at native defaults. `--temperature` sets an explicit isolated test-chat value only when Jake requests that comparison; it is omitted by default and never changes app/model preferences. Reports record `chat_params`. Utility calls use only SPEC parameters. An optional
`--search-key-db` opens the new app database read-only and copies its key into the temporary
evaluation database. Never put the key on the command line or in an artifact.

Raw pages use lossless gzip where available; the loader also accepts original uncompressed bytes.
Errors are recorded, unseen queries are fixture misses, and replay/recording bypass production cache reuse.
The controlled injection fixture explicitly provides an attack; production never consults it.
Synthetic browser/model fixtures do not count as accuracy evidence.

Reports store raw and normalized answers, selected exact passages, provider/ranking provenance,
latencies and failures. Citation support is lexical overlap, not factual entailment. A full suite
uses E12 aggregate thresholds plus the individually required E13 examples. Live injection is
not applicable; the attack must be received and ignored in the separate controlled replay.

## Current evidence

See `docs/PHASE-2-REPORT.md` for the current evidence index and failed accuracy gates.
The keyword comparison `2026-10-02-155158` passes 22/25; functioning hybrid `155637` passes
21/25 and is slower. The earlier V6 recorded run `144854` passes 25/25, but repeated/live
failures prevent claiming consistent acceptance. DDG-only outages and discarded generic
trials remain historical evidence. Free provider order is Ollama → SearXNG → Exa → DDG.
