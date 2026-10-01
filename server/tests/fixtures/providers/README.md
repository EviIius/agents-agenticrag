# Real provider recordings — 1 October 2026

These are unmodified HTTP response bodies from the Mac's Ollama (`127.0.0.1:11434`)
and LM Studio (`127.0.0.1:1234`). Each `.request.json` sidecar records the exact request,
HTTP status, content type, UTC timestamp, raw filename, and SHA-256 checksum.
The image input is a synthetic red PNG. No personal conversation or library content was sent.

The active rebuild uses Ollama only. LM Studio captures are retained as historical evidence, not an active provider or test requirement.

Run `make record-fixtures` from the repository root to refresh Ollama.
For a targeted capture, use the tool environment and run:

```sh
. scripts/tool-env.sh
uv run --directory server python ../scripts/record_provider_fixtures.py --only ollama
uv run --directory server python ../scripts/record_provider_fixtures.py --only vision
```

The recorder loads and unloads models for its probes. It uses the installed Qwen,
GPT-OSS and Gemma variants on Ollama, and runtime capability metadata to select
LM Studio models. It never loads the excluded standard Llama variant.
There are no sampling overrides except the explicit 20-token length-stop probes.
LM Studio load probes explicitly request a 16,384-token context.
Later captures also record first-byte and total elapsed times in milliseconds;
the initial captures predate that instrumentation and have no timing fields.

## Coverage

- Ollama: tags, show for all seven registered models, unloaded/loaded ps, plain text,
  native reasoning, Gemma image input, a 20-token length stop, unknown-model 404, unload.
- LM Studio: v1/v0/OpenAI model catalogs, plain text, native reasoning, a 20-token
  length stop, explicit load, loaded-instance contexts, and unload by `instance_id`.
- LM Studio invalid model ID with a loaded model: HTTP **200**, answering with a
  different model. See `lmstudio-unknown-loaded.request.json` and its raw `.sse`.
- LM Studio invalid model ID with no models loaded: HTTP **400**, asking to load a
  model. The raw error JSON is retained in `lmstudio-unknown.sse` because the suffix
  identifies the endpoint's expected protocol, not the actual error content type.
- LM Studio vision: unavailable. Neither installed chat model reports vision.

**The LM Studio routing discrepancy is historical; the user removed LM Studio from scope.**
The regression tests preserve the observed wire behavior; they do not assert that
this behavior is acceptable in the rebuilt application.
