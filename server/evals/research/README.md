# Research gate 8-0

This is an evaluation checkpoint. It adds no Research toggle, tool loop, product
prompt, dependency, migration or deployment. Jake authorized starting the gate
on 6 October 2026 and waived the two-week/17 October calendar hold **for this
checkpoint only**. Product implementation and §9 targets still require review.

## Inputs and selection

`cases.yaml` contains JSON, which is also valid YAML, matching the existing web
evaluator's format without adding a parser package. The 15 questions were
written before running the baseline. They cover database and filesystem
semantics, Python environments, Git, browser APIs, HTTP, accessibility standards,
space missions, national parks, World Heritage entries and founding documents.
Each joins separate requested parts backed by at least two primary references.
The reference URLs and human-readable expected facts are in each case.

The set uses stable public facts instead of personal files, recordings or
current news. It deliberately favors documentation and historical comparisons;
15 cases are a screening set, not representative evidence for every research
task. Search can already plan several queries in one batch, so multi-part does
not imply that an agent is necessary. Whether Research improves on that batch
remains to be measured after the gate.

The case assertions are frozen before baseline inference in
`artifacts/phase-8/gate/frozen-inputs.json`. Dates accept standard spelling and
abbreviations; rover dates are requested in UTC. Regex presence is a screening
metric, not proof of correct subject association or supported claims. Manual
review must distinguish facts, omission, contradiction, and source support.
Do not lower assertions or select a favorable rerun after seeing answers.

`record_references.py` captures authoritative reference HTML with hashes,
timestamps, redirects and extracted text. Initial mistyped or insufficient
overview URLs were corrected during preparation; draft and failed retrieval
logs are retained. UNESCO returns 403 to the local fetcher; its two entries were
verified through browser retrieval and explicitly marked as such in
`references/browser-verification.json`. That note is not a fabricated HTML
fixture. The actual Search recording retains fetched pages and fetch failures.

Reference pages remain attributed to their publishers by URL and title. Raw
snapshots preserve publisher notices. These are evaluation fixtures; they are
never ingested into the user's Library or consulted by production Search.

## Native protocol probe

`probe_tools.py` uses the runtime's reported `tools` and chat-completion
capabilities. It does not infer capabilities from model names. An embedding-only
model reporting `tools` is excluded from chat calls. Hidden chat models are still
probed because the gate asks for every installed eligible model; picker
preferences stay unchanged. The daily model is the saved default, corroborated
by Jake's recent Library check.

There are 40 independent synthetic requests per model: 15 searches, 15 reads
and 10 finishes. All five freshness values are exercised. Tools are supplied
using Ollama's native API; tools are **not executed**. See the official
[chat API](https://docs.ollama.com/api/chat) and
[tool-calling protocol](https://docs.ollama.com/capabilities/tool-calling).
No sampling or reasoning override is introduced. Runtime-reported context and
the user's saved defaults are retained. Each request has a 120-second bound.

Success requires completion, no transport/runtime error, at least one native
call, known tool names and schema-valid arguments for every emitted call.
Missing calls count as failures, including `finish` prompts, even though the
future product spec permits a no-call loop step to finish. No prose parsing,
repair or retry is used. Calling the requested tool is also reported separately.
≥38/40 passes the 95% gate. The prompt distribution is declared, and results
include a per-tool breakdown so a weak `finish` cannot be hidden by an aggregate.

Raw `.ndjson` and request JSON are under `provider-fixtures/{ordinal}`; the
report maps ordinals to model IDs. `test_gate.py` checks malformed calls,
schema boundaries, object/string argument forms and frozen case structure.

## Search baseline and release checks

`run_search_gate.py` imports the **unchanged** existing web evaluator. It uses
its temporary ASGI database and actual Search planner/answer path. Only the
report destination and case/fixture selection change. No prompt, ranking,
format, sampling or pipeline trial is enabled. Runs are serialized with the
native probes to avoid measuring simultaneous model loads as Search latency.

From the repository root:

```sh
. scripts/tool-env.sh
uv run --directory server pytest evals/research/test_gate.py -q
uv run --directory server python evals/research/probe_tools.py
uv run --directory server python evals/research/record_references.py
uv run --directory server python evals/research/run_search_gate.py release-live --search-key-db "$HOME/.local/share/workbench/data/workbench.db"
uv run --directory server python evals/research/run_search_gate.py baseline-record --search-key-db "$HOME/.local/share/workbench/data/workbench.db"
uv run --directory server python evals/research/run_search_gate.py baseline-replay
```

The credential option reads only `web.ollama_api_key`, read-only, and never
writes its value to evidence. Omit it for offline replay. The release-live mode
is equivalent to `make eval-web LIVE=1 MODEL=qwen3:30b-a3b-workbench-32k` with
the saved search credential and isolated report destination. It runs the
unchanged 25 release cases; it is distinct from the 15-case Research baseline.
The daily 32K variant is an explicit model selection, not a capability rule.

Recording saves provider search JSON, raw pages and each run's sources, answer
and timing. Replay uses the frozen search corpus with a real planner and answer
model; search results remain independent of new query wording, as documented by
the existing evaluator. Web content is frozen, model outputs are not guaranteed
deterministic. Keep the live baseline and replay separately labeled.

The same 15 questions and recorded corpus must be used in any later Research
comparison. Expanding adaptive-query fixtures or changing the corpus requires
a new labeled baseline, not silent substitution. The ≥80% facts and ≥15-point
gain proposal is not a result of this checkpoint, and native protocol success
does not establish agent accuracy, injection resistance or latency budgets.

## Review stop

Summarize G1–G5 in `docs/PHASE-8-REPORT.md`. Retain failures and missing gates.
Do not implement 8A or deploy a Research feature until Jake reviews the gate and
approves the separate product specification and targets.
