# Model options and picker proposal — 7 October 2026

Status: researched proposal, no model download, runtime upgrade, default switch,
new routing, Research qualification or UI deployment. The accepted 7B app remains
installed. Jake requested model research and clearer categorization while 8A
consistency work continues.

Jake's follow-up: document candidates and continue the existing 8A scope; do not
install Qwen 3.8 or another model now. Expand this list through research only.

## What to test first

The local machine reports Apple M5 Pro and 64 GiB unified memory. Published weight
sizes are download sizes, not measured resident memory: context cache, vision,
Ollama, macOS and transcription need additional room. These are candidate-fit
inferences, not speed or quality results on this Mac.

| Priority | Explicit Ollama candidate | Published size | Proposed purpose |
|---|---|---|---|
| 1 | `qwen3.8:27b-q4_K_M` | About 18 GB | First candidate for grounded answers and native tool reliability. Explicit quantized tag avoids the moving `latest` alias; record its full digest after installation. |
| 2 | `qwen3.6:35b` | About 23–24 GB | Alternative for coding and tool work. The publisher specifies 35B total / 3B active parameters; measure actual speed rather than equating active parameters with RAM. |
| 3 | `gemma4:26b` | About 16–19 GB | A second model family for comparison, with a mixture-of-experts architecture. Keep the existing Gemma 12B as the smaller installed option. |
| 4 | `qwen3.5:9b` | About 6.6–7.6 GB | Smaller candidate for quick everyday requests; accuracy and latency still require local tests. |

Sizes and listed capabilities come from the official
[Qwen 3.8 tags](https://ollama.com/library/qwen3.8/tags),
[Qwen 3.6 library](https://ollama.com/library/qwen3.6),
[Gemma 4 library](https://ollama.com/library/gemma4) and
[Qwen 3.5 library](https://ollama.com/library/qwen3.5).
The [Qwen 3.6 model card](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)
establishes its architecture. Ollama lists vision, tools and thinking for these
families; installed `/api/show` metadata must establish each exact variant's
capabilities before Atelier enables them.

Qwen 3.8 is a real release, including a local dense 27B vision-language model.
Its [official model card](https://huggingface.co/Qwen/Qwen3.8-27B) reports improved
agent execution and instruction following. Those publisher evaluations use other
harnesses and do not establish Atelier's citation/support or consistency gates.
Preserved thinking is also a compatibility question for our native adapter, not
permission to add private reasoning to visible activity or make extra calls.

Start with an explicitly approved 32K operational profile. A listed 256K maximum
is not the memory allocation or context we have tested. Increasing context uses
more memory, as [Ollama's context guide](https://docs.ollama.com/context-length)
explains. Do not silently apply publisher sampling recommendations or change
Ollama's global context setting.

## Additional families to compare later

| Candidate (explicit local tag) | Published download | Potential role / limit |
|---|---|---|
| `ministral-3:14b-instruct-2512-q4_K_M` | 9.1 GB | A smaller general-purpose, image-capable alternative with native tool support. Useful to compare everyday answers and responsiveness with the larger Qwen candidates; no local speed result yet. |
| `nemotron-3-nano:30b-a3b-q4_K_M` | 24 GB | A different reasoning/tool family for the evidence benchmark. NVIDIA describes a hybrid architecture with 30B total and 3.5B active parameters; its total weights still occupy memory. Text-only listing. |
| `devstral-small-2:24b-instruct-2512-q4_K_M` | 15 GB | A coding-focused, image/tool-capable candidate. Publisher software-engineering results do not prove reliable web claim support; lower priority for this Research task. |
| `ministral-3:8b-instruct-2512-q4_K_M` | 6.0 GB | A smaller image/tool alternative to the 14B, for a deliberate speed-versus-quality comparison. |
| `nemotron-3-nano:4b` | 2.8 GB | Small text reasoning/tool candidate. Keep distinct from the 30B; do not transfer architecture or quality claims between variants. |

The sizes are from official tag inventories:
[Ministral 3](https://ollama.com/library/ministral-3/tags),
[Nemotron 3 Nano](https://ollama.com/library/nemotron-3-nano/tags), and
[Devstral Small 2](https://ollama.com/library/devstral-small-2/tags).
The capability and intended-use descriptions come from their official
[Ministral](https://ollama.com/library/ministral-3),
[Nemotron](https://ollama.com/library/nemotron-3-nano), and
[Devstral](https://ollama.com/library/devstral-small-2) pages. These are proposed
test roles, not quality rankings or measured RAM/latency. The installed runtime
is Ollama 0.35.0; a listed minimum runtime version is not a compatibility test.
Every future candidate still needs the same native protocol, context, memory,
grounding and regression checks below.

Do not add a model just because its family is popular. In particular,
[DeepSeek V4.1 Flash](https://ollama.com/library/deepseek-v4.1-flash) currently
lists only a cloud tag, so it is outside this local shortlist. The older
[V4 Flash entry](https://ollama.com/library/deepseek-v4-flash) says it was retired
on 25 September 2026 and has no downloadable tags. A cloud alias would change
where prompts are processed and is not an equivalent local replacement.

Recommended eventual order: Qwen 3.8 27B first; then one different family
(Nemotron 30B for Research or Ministral 14B for smaller everyday use); then a
coding candidate if needed. Test one at a time with only one chat model resident
before comparing memory. Avoid downloading every candidate on this list.

## Qualification before recommendation

1. Get approval for the named weight download and test profile. The current 8A
   amendment excludes new models; research alone does not authorize installation.
2. Keep the old model/defaults and installed app. Record candidate digest, runtime
   version, actual capabilities, configured/loaded context and peak memory.
3. Run the unchanged 40 native-tool cases, with every failure retained. A protocol
   pass is not permission to label the model Research-ready.
4. Evaluate both single-shot Search and Research on the same 15 frozen questions,
   raw fixtures, candidate, approved settings and context. The old model's 10/15
   baseline cannot establish the new model's agent gain.
5. Freeze a candidate and run three full evaluations, retaining all results. Each
   must clear completeness, actual tool validity, citation support, unsupported
   output, injection and budget gates. No best-of retries or lower thresholds.
6. Run the ordinary regression gates before a proposed deployment/default switch.
   If the new model makes single-shot Search sufficiently good and Research adds
   less than the required gain, prefer the better fixed pipeline. Do not force 8B.

## Clearer picker, without automatic model routing

The current picker groups by connection, so a single Ollama connection produces
one long list. Long runtime tags occupy a line in every row, and context variants
look like different models. Proposed display organization:

| Picker element | Meaning / source of truth |
|---|---|
| Favorites | Stored user choices, with the selected model visible first. A suggested favorite is not a quality certification. |
| All chat models | Remaining runtime-reported chat-capable models. Preserve the explicit hidden Llama preference. |
| Images / Reasoning / Tools filters | Filters from exact runtime capability fields, with readable labels alongside icons. Tools does not mean Research-qualified. |
| Context profiles | Explicit stored grouping of variants, with separate selectable 16K / 32K entries. Do not merge or switch profiles based on name guessing. |
| Selected and Loaded labels | Separate chat selection and residency states, both visible; preserve current load/select behavior. |
| Runtime tag details | Show the friendly name and operational context first. Keep the exact tag searchable and available in row details or Manage models. |
| Research qualification | Only a digest/context/runtime-bound evaluated status after all applicable gates pass. Never derive it from the model name or a tool icon. |

Embeddings remain in Library configuration, not the chat picker. No category
automatically chooses a model, changes a chat, adds a mode or starts a model call.
Desktop and phone layouts, empty/loading/offline states, focus, nested load
controls, profile selection and safe scrolling need `/design` and regression
evidence before this proposal ships.

## Deferred work order

1. Recording dropdown safe-area clipping: highest priority for phone usability.
2. Sidebar/overlay motion regression: normal, system-reduced and Always-reduced
   checks using authored synthetic content.
3. Picker organization and readable capability labels: use this proposal after
   the current 8A review; model qualification remains separate.
4. VoiceOver: preserve the reported failure and deferred acceptance status until
   a physical accessibility review is scheduled. Do not mark it passed.

The authoritative bug list remains `docs/DEFERRED-FIXES.md`. No real phone capture,
recording, private filename or Library text was used for this proposal.
