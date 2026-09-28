# Local 70B feasibility check — 28 September 2026

This is a hardware and compatibility smoke test, not a model quality ranking.
After the test, the live workbench was set to the tested 16K variant with
`json_object` structured output; its embedding model was unchanged.

## Machine and model

- Apple M5 Pro Mac with 64 GiB unified memory.
- Ollama 0.34.4; existing chat models: Gemma 4 12B MLX, GPT-OSS 20B, and Qwen3 30B A3B Q4_K_M.
- Added `llama3.3:70b-instruct-q4_K_M` (42 GB download). Created
  `llama3.3:70b-workbench-16k` from the same weights with `num_ctx 16384`.
  The variant adds only a small configuration layer, not another copy of the weights.
- The 16K variant loaded at 48 GB, **100% GPU**, with 16,384 context tokens.
  The Mac reported 23% system memory free during the 8K test; memory pressure
  under a full workload and concurrent phone use still needs measurement.

Ollama's OpenAI-compatible API does not accept a per-request context length, so a
derived model is needed to give the workbench a predictable context size.
See the [Llama 3.3 model tags](https://ollama.com/library/llama3.3/tags) and
[Ollama's context-size guidance](https://docs.ollama.com/api/openai-compatibility#setting-the-local-context-size).

## Measured runs

| Test | Result |
| --- | --- |
| Short direct prompt, Qwen3 30B A3B, 8K context | 1.42 s wall time; 24 output tokens; 95.7 output tokens/s |
| Same prompt, Llama 3.3 70B, 8K, cold | 12.43 s; 3.10 s load; 53 output tokens; 6.29 output tokens/s |
| Same prompt, Llama 3.3 70B, 8K, warm | 8.61 s; 53 output tokens; 6.28 output tokens/s |
| Same prompt, Llama 3.3 70B, 16K | 12.97 s, including 3.64 s load; 6.29 output tokens/s |
| Simple workbench JSON Schema contract | Passed in 3.58 s |
| Fixed RAG, nachos case, 8K with JSON Schema | Failed citation validation after 26.61 s: malformed chunk ID |
| Fixed RAG, same case, 8K with JSON object | Passed with one valid citation in 23.08 s |
| Fixed RAG, same case, 16K with JSON object | Passed with one valid citation in 23.93 s |

The Fixed runs used the live corpus database in read-only fashion and the same
Qwen3 0.6B embedding model. The initial attempt against the repository's demo
database contained no matching `research` evidence, so its abstention was not a
model result. The JSON Schema failure shows why a trivial structured-output check
is insufficient: the final citation contract must be tested on real evidence.

## Working recommendation

1. Keep Fixed as the everyday sourced mode and Qwen3 30B A3B as the fast local
   baseline while a representative evaluation set is built.
2. Offer Llama 3.3 70B as an optional quality candidate, selected as
   `llama3.3:70b-workbench-16k` with **JSON object** structured output. Do not
   assume a quality gain from parameter count; compare answers and citation
   support on paired cases.
3. Add runtime and structured-output settings to the experiment manifest so
   command-line results reflect the live workbench. Add bounded memory and cold/
   warm latency measurements. Run the full model/mode matrix serially on this Mac.
4. Build durable, reconnectable phone runs before relying on 70B Agentic or
   Supervisor work. At roughly 6 output tokens/s, several sequential model calls
   can easily turn a phone request into minutes. Keep one heavy local run active
   until measured concurrency headroom is established.

No Agentic or Supervisor 70B quality claim follows from this smoke test. Repeated
case runs, long-context behavior, sustained memory pressure, and phone reconnect
behavior are still open checks.
