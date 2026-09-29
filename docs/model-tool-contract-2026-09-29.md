# Local model tool contract: Qwen and GPT-OSS (29 Sep 2026)

These are short capability probes, not answer-quality or agent-success scores. The probe
source is `scripts/probe_model_tools.py`; raw local responses were saved under `.data/`.
Each task was repeated twice at temperature zero. The tasks ask for calculation, local
search, no tool, a follow-up after an untrusted tool result, and (for JSON actions) a
finish action with a host-verified quote. No tool was actually executed by the probe.

| Runtime and model | Native tool turns | JSON Schema actions | JSON object actions |
| --- | ---: | ---: | ---: |
| Ollama Qwen3 30B-A3B Instruct Q4 | 8/8 | 6/6 | 6/6 |
| Ollama GPT-OSS 20B | 8/8 | 0/6 | 0/4 on the simpler action set |
| LM Studio Qwen3 30B-A3B Instruct Q4 | 6/8 | 6/6 | API rejects this format |
| LM Studio GPT-OSS 20B MXFP4 | 8/8 | 6/6 | API rejects this format |

**What the failures mean.** Ollama's GPT-OSS returned empty final text in the JSON-action
probes; native tool turns worked. LM Studio's OpenAI-compatible endpoint rejected
`response_format.type=json_object` with HTTP 400, while `json_schema` worked. Qwen on LM
Studio made correct tool calls but repeated an instruction embedded in a synthetic tool
result in both trials, even with a system instruction to treat tool results as untrusted.
Qwen on Ollama and GPT-OSS on both runtimes passed that same two-trial follow-up. This is
one adversarial probe, not a general prompt-injection rate.

The LM Studio GPT-OSS run used LM Studio's own GGUF package. LM Studio's current runtime
could not load the GGUF blob imported from Ollama (`unknown model architecture: gptoss`).
The two GPT-OSS files may differ in quantization or metadata, so elapsed times here are not
an apples-to-apples runtime benchmark. A transient LM Studio compute error occurred when
Ollama's 32K-context Qwen and LM Studio's GPT-OSS were both loaded; unloading and reloading
the models resolved it. Run one large model at a time on this 64 GB Mac.

**Workbench check.** The installed Qwen workbench variant was separately run on an isolated
sample corpus through Direct, Fixed, Agentic, and Supervisor with `json_schema` mode. Fixed
and Supervisor passed their source gates on the first attempt. Agentic first exhausted its
steps because the model repeated an identical citation ID. The host now collapses identical
IDs before verifying the citation and quote; a rerun produced a cited Agentic answer in
8.8 seconds. This is one smoke case, not evidence that Agentic beats Fixed.

**Decision for now.** Keep Fixed and the current Qwen model as the default. Use JSON Schema
for this Qwen workbench variant. Keep native tool calling behind a future provider-interface
change and a broader tool contract. Do not promote GPT-OSS to the agent route or enable a
connector based on these probes. The larger document evaluation in
`docs/evaluation-v3-preparation.md` must decide quality and routing.

Runtime references: [LM Studio local server](https://lmstudio.ai/docs/developer/core/server),
[Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility).
