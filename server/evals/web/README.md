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
- `--evidence-format sectioned`: an isolated heading experiment that also changes ranking input. It cannot be combined with `--table-trial`; it is not a controlled answer-only comparison and is not used in production.

Answer sampling stays at native defaults. `--temperature` sets an explicit isolated test-chat value only when Jake requests that comparison; it is omitted by default and never changes app/model preferences. The harness creates the chat, PATCHes its explicit sampling value, and checks completion stats for the requested temperature. Reports record `chat_params`. Utility calls use only SPEC parameters. An optional
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

See `docs/PHASE-2-REPORT.md` for the current evidence index and outstanding gates.
Final production `2026-10-03-001904` passes 24/25 recorded-web cases, all aggregate targets and required examples. Fresh live NBA `001926` and 32K replay `001943` pass the complete list with a citation on each row. The release case still expects two distinct sources but gets one. Latest browser evidence has two deferred phone layout failures, so Phase 2 remains open.

The planner's nullable literal-word condition, conservative host selection and row citation references are production features within existing budgets. Experimental row-record/prompt/human-predicate trials are isolated and failed runs remain attached. The historical `numeric-selection` trial name uses the current production condition behavior now; exact recorded schema and code hashes distinguish earlier prototype reports. No old report is rewritten to match later grading or implementation.

Comprehensive-list grading now checks each Markdown list/table item for a citation and rejects a false full-population conclusion; `strict-list-citation-audit.json` rechecks saved answers separately. Lexical citation support still does not establish every claim.

Controlled frozen-plan comparison `222041` native passes 24/25 versus `222231` temperature 0.2 at 21/25. Keep native answer defaults. This is one run per setting, not statistical significance or a comparison on the final formatter. Keyword remains preferred over the earlier functioning hybrid comparison (`155158`/`155637`), which added latency without accuracy improvement. No final-formatter hybrid rerun is claimed. Free provider order is Ollama → SearXNG → Exa → DDG.
