# Library evaluation

All documents, people, organizations and questions here are invented. The harness
creates an isolated temporary database and uploads only this committed corpus.
It never opens Workbench's production data or the user's Library. It uses the
existing Ollama embedding and answer adapters; no model judge or extra planner
call is added. Temporary files are removed when the application closes.

From the repository root:

```sh
make eval-library
RETRIEVAL_ONLY=1 make eval-library
RETRIEVAL_ONLY=1 FAKE_EMBEDDING=1 make eval-library
```

The default full run uses `qwen3-embedding:0.6b` and
`qwen3:30b-a3b-workbench-32k` at loopback Ollama. Use the harness's `--url`,
`--embedding` and `--model` arguments for another approved local selection.
Fake embedding runs are development checks and do not establish J7 accuracy or
real-dimensional latency. `cases.yaml` uses JSON syntax, which is valid YAML,
so the existing standard library suffices.

The first full run is the baseline for the exact version-one Library prompt.
Reports include prompt, source, corpus and case hashes, raw synthetic answers,
selected passages and automatic grades. A prompt edit requires a before/after
comparison and approval under QA §9.

Automatic grading checks exact declared facts, inline numeric citations and
support in cited passages. It cannot judge all paraphrases or extra claims.
Review every synthetic answer before reporting citation or abstention success.
Page retrieval checks the actual selected passage ranges, not the file's overall
minimum/maximum page span. The committed unit tests reject wrong values, invalid
citations and missing pages within that span.

The latency benchmark adds a separate invented collection of 20,000 passages,
with deterministic vectors at the selected model's measured dimension. Fifty
queries exercise the production candidate, fusion and selection code, excluding
query embedding. This measures a synthetic workload rather than every possible
collection distribution. First-token timing retains Workbench's existing
provider statistic, which includes the first text or reasoning delta.

`generate_corpus.py` rebuilds the public synthetic corpus from the committed
manifest using the existing PDF fixture writer and standard-library Word ZIP
writer. Regeneration may change PDF serialization hashes; keep the corpus fixed
through comparisons and preserve each report's hash manifest.
