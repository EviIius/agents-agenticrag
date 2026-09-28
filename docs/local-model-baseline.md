# Local model baseline — 27 September 2026

This is a **smoke comparison**, not a quality ranking. It used one frozen question from
`examples/sample-eval.jsonl`: why the sheet-pan nachos source adds wet toppings after baking.
All three installed chat models ran against the same local source collection and embedding model.
Direct answers are ungrounded and cannot validate source citation quality.
Run data was written to `/tmp/agenticrag-model-comparison-v2.jsonl` on this Mac mini.

| Model | Direct | Fixed | Agentic | Supervisor |
| --- | ---: | ---: | ---: | ---: |
| Gemma 4 12B MLX | 4.8s · answered | 3.8s · answered | 40.9s · answered | 70.2s · answered |
| GPT-OSS 20B | 6.7s · answered | 4.9s · answered | 61.9s · answered | 45.5s · abstained |
| Qwen3 30B A3B | 5.6s · answered | 3.4s · answered | 23.1s · abstained | 68.6s · answered |

The Fixed path was quickest for this simple sourced question. Agentic and Supervisor added
substantial latency and sometimes abstained after evidence review. These observations justify
keeping Fixed as the default for straightforward source questions. Run the full three-case sample
set and a larger frozen dataset before choosing a model or mode for general use.

Reproduce with `agenticrag compare examples/sample-eval.jsonl --model MODEL` repeated for each
installed chat model, plus `--include-agent --include-supervisor`. The comparison command does
not change the live workbench's selected model.
