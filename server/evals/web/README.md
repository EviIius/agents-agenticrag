# Web evaluation

`cases.yaml` uses JSON syntax, a subset of YAML 1.2, so the harness needs no additional dependency.
The 25 cases include SPEC Appendix E and the reported comprehensive NBA losses regression.
Review case expectations before accepting the phase.

Run `make eval-web-record CASE=nba-2021` to record live search JSON and raw public page bytes.
Run `make eval-web` to use recorded web fixtures with a real Ollama model, or `make eval-web LIVE=1` for live web.
`RANKING=hybrid` enables the configured embedding model for the A/B run; keyword is the baseline.
All model sampling remains at defaults for answers; planner and title use only their specified parameters.

Recording captures errors too. Offline search replays the recorded query results for that turn; unseen
queries are reported as fixture misses, rather than silently querying the internet. Each report records
queries, source passages, answers, request status, token timings, failures, and the heuristic's limits.
Synthetic browser fixtures are separate and do not count as real model evaluations.

## Current evidence

The current DDG-only full recording is `reports/2026-10-01-173016-…-live-keyword` and
`fixtures/2026-10-01-ddg-only/`; it failed acceptance (only 3 successful web turns out of 24).
Older recordings may include Brave scraping under a DuckDuckGo label and older loose metrics.
They are historical, not provider-specific reliability evidence. Production now selects only the
DuckDuckGo backend for that provider. The generic task/scope trial remains unpromoted.
Freshness expectations are checked by the current harness; earlier runs did not store them.
