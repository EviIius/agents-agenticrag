# Local model evaluation baseline — 28 September 2026

This is an early engineering check, not a model ranking. The isolated
`evaluation-v1.jsonl` set has eight questions from a small frozen sample corpus:
six answerable source questions and two cases that should abstain. Each
model/mode pair ran once on the same Apple M5 Pro Mac with 64 GiB unified memory,
using local Ollama and the same Qwen3 0.6B embedding model for Fixed RAG.
The paired Direct and Fixed run tested five model configurations. The installed
app shows this report on Models; it is labeled **Early check**.

| Model | Direct completed / avg | Fixed completed / avg | Fixed answer checks | Fixed no-evidence checks | Fixed citation IDs resolve | Loaded model sample |
| --- | --- | --- | --- | --- | --- | --- |
| Gemma 4 12B MLX | 8/8 · 0.7 s | 8/8 · 2.9 s | 6/6 | 1/2 | 100% | 15.93 GB |
| GPT OSS 20B | 6/8 · 4.6 s | 7/8 · 5.8 s | 5/6 | 1/2 | 100% | 13.67 GB |
| Llama 3.3 70B, 16K | 8/8 · 7.1 s | 8/8 · 22.4 s | 6/6 | 2/2 | 100% | 47.52 GB |
| Qwen3 30B A3B | 8/8 · 1.2 s | 8/8 · 2.1 s | 5/6 | 2/2 | 100% | 45 GB |
| Qwen3 30B A3B, 32K context | 8/8 · 0.5 s | 8/8 · 1.9 s | 5/6 | 2/2 | 100% | 21.83 GB |

Direct has no source retrieval, so its answer check on this source-based set is
not a useful quality measure and is omitted from the Models screen. The averages
exclude failed runs. The citation metric only checks that an ID refers to returned
evidence; it does not check whether the evidence supports the claim. The loaded
model value is sampled after a completed call and is not peak system memory.

The 32K Qwen variant reuses the original model weights and leaves substantially
more room for the workbench's bounded source packs and saved chat history than
the 16K variant; the longest allowed history has not been stress-tested. Its sampled
loaded footprint was less than half that of the original large-context setting,
with the same Fixed checks on this small set. The live chat selection was moved
to the 32K variant; the original remains installed for much longer contexts.

The local web-research path was measured separately on a 26-year World Series
question. The 70B run took 92.0 s: 1.4 s for search/page reading and 90.6 s for
one model request (2,141 input tokens, 404 output tokens). A Qwen 32K run took
19.8 s total but incorrectly swapped several winners and losers and treated the
completed 2025 result as speculative. A revised prompt on a fixed search snapshot
still made factual errors. These web runs had different answer lengths and search
snapshots, so they show a quality failure and a latency opportunity, not a
controlled ranking. Add a frozen web-evidence set and claim-level support checks
before using a fast model automatically for long factual lists.

GPT OSS produced two Direct failures and one Fixed failure. One Direct failure
returned an unrequested tool call rather than final text. The local adapter now
adds an explicit final-text instruction on its one bounded retry. That affected
case completed in a follow-up run, but the original paired baseline remains
unchanged so the reported numbers are comparable. The other failures still need
diagnosis. A one-question Gemma smoke run completed in all four modes: Direct
2.0 s, Fixed 4.4 s, Agentic 11.6 s, Supervisor 19.3 s. That case only verifies
the mode paths; it does not establish an Agentic or Supervisor quality gain.

## Decision for now

Keep Fixed as the everyday sourced mode. Offer 70B as a slower manual choice for
complex or uncertain work; its simple source-check results do not justify making
it the default. Keep Qwen and Gemma available for faster responses. Avoid an
automatic quality-based router until the case set includes web research,
multi-step synthesis, claim-level citation checks, repeated runs, and failures
under each mode. The [next-phase plan](next-phase-plan.md) includes the measured
web-run breakdown and the next source-verification checks.
