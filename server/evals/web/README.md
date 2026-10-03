# Web evaluation

`cases.yaml` is JSON syntax (valid YAML 1.2), so the harness needs no extra dependency.
It contains 25 cases, including Jake's comprehensive NBA Finals-losses regression.

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
Final evaluation-closeout evidence is indexed below. The earlier `001904` / `001926` / `001943` numeric-selection checkpoints remain preserved, including their original assertions and failures. Latest browser evidence has two deferred phone layout failures, so the whole Phase 2 remains open.

The planner's nullable literal-word condition, conservative host selection and row citation references are production features within existing budgets. Experimental row-record/prompt/human-predicate trials are isolated and failed runs remain attached. The historical `numeric-selection` trial name uses the current production condition behavior now; exact recorded schema and code hashes distinguish earlier prototype reports. No old report is rewritten to match later grading or implementation.

Comprehensive-list grading now checks each Markdown list/table item for a citation and rejects a false full-population conclusion; `strict-list-citation-audit.json` rechecks saved answers separately. Lexical citation support still does not establish every claim.

Controlled frozen-plan comparison `222041` native passes 24/25 versus `222231` temperature 0.2 at 21/25. Keep native answer defaults. This is one run per setting, not statistical significance or a comparison on the final formatter. Keyword remains preferred over the earlier functioning hybrid comparison (`155158`/`155637`), which added latency without accuracy improvement. No final-formatter hybrid rerun is claimed. Free provider order is Ollama → SearXNG → Exa → DDG.

## Evaluation closeout

Release-source diversity alone is not an accuracy criterion: a single official release note can support the version and changes. The corrected case requires a cited version, cited change assertions and a cited official release URL. It does not automatically validate the current version against an independent oracle; final recorded/live answers are also reviewed. Original reports and case hashes remain unchanged.

Section context is preserved generically: consecutive headings before body text form one label; new heading boundaries prevent separate entries with identical subheadings from merging. The answer builder exposes each stored heading beside its passage, using escaped metadata. Report `chunker_sha256` identifies this evidence change alongside existing builder/planner/pipeline hashes. No topic-specific production prompt, sampling override or extra model call is added.

Jake requested the evaluation closeout before mobile work. No mobile layout changes or new browser layout acceptance claim belong to this closeout.

The first full closeout live run `011356` is a failure and remains recorded: later result tables/backgrounds displaced direct evidence, and a defined W/L table could not bind its expanded loss property. The final refinements keep explicit abbreviation definitions local to a heading/table, reassemble all selected rows with an identified long-prose projection, use scoped tables for a numeric-list answer, and prefer relevant leads/compact tables within the original caps. `ranker_sha256` records this ranking change. The broad-list assertion now also rejects describing series losses as individual-game losses.

The subsequent broad replay `012839` exposes two additional defects: row-reference binding was overwritten by later sanitization, and a short follow-up could answer its historical year despite the correct new search plan. Final code sanitizes before binding and sends planner queries as explicitly non-prescriptive retrieval context. Integration tests require numeric references in the persisted table and the exact answer input. The release grader also covers plural “Updates”/singular “Fix” change assertions; old case hashes/scores remain intact.

The general planner source-constraint prompt trial `015926` / `020252` is rejected: it regresses the complete-list condition despite improving release provenance. Production retains the previous evaluated planner prompt. Instead, host query handling preserves literal positively requested official/primary qualifiers, without adding queries, inferring publishers, overriding sampling or changing non-source requests. Final recorded `032410` passes 24/25 and all aggregate/mandatory gates, with release coverage passing; the personal-history refusal case remains a declared failure. Final live and sampled manual review are indexed in the phase report.

Full recorded `032410` passes all E12/E13 gates at 24/25; full live `032719` has 24/25, P50 5.96 s/P90 7.52 s and mandatory examples passing but fails official release provenance. Final affected case `032822` passes after avoiding publication-date filtering only for positively requested official/primary sources, with original page freshness retained. Full-suite observations are pre-filter-fix and are not rewritten or blended into 25/25. Manual review supports the listed version/changes; the mirror-derived publication date remains unverified. Evaluation closeout is ready for separate mobile review; whole Phase 2 still has two known layout failures.
