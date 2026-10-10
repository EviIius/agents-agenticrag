# Isolated image trial I0

This is trial tooling, not Atelier's image feature or durable job queue. The
installed application remains unchanged. Scope and review gate:
`docs/IMAGE-TRIAL-PLAN.md`; results: `docs/IMAGE-TRIAL-REPORT.md`.

Public source, exact dependency lock and synthetic trial settings live here.
The approved environment is private at
`~/.local/share/workbench/image-worker/i0/venv`, with Python 3.13.15 managed under
`~/.local/share/workbench/image-worker/python`. Model weights are shared under
`~/.local/share/workbench/models/image/huggingface`, outside Git and ordinary
deployment/backup copies. Server and transcription environments are untouched.

`download_model.py` pins the model revision and downloads only inference files,
omitting the duplicate root checkpoint. `worker.py` loads the local snapshot
offline, emits JSON-line stage/actual-step events, validates PNG output and saves
metadata. `control.py` owns the subprocess session, termination/reaping, timeout
and independent output checks. `run_trial.py` enforces the frozen stage order and
refuses to overwrite evidence. Its worker source, requests and outputs are all
outside Documents; synthetic outputs are copied into evidence after execution.

Re-running a recorded stage requires a separately preserved trial directory and
manifest; do not delete or overwrite previous outcomes. The first initialization
inspection failure and exact old source remain under `attempt-1/`. The correction
preserves MLX Module objects as leaves when counting quantized layers. It changes
no model, prompt, seed, precision, steps or package.

The standalone control tests run with the existing server's pytest, without
installing image packages into the server:

```sh
. scripts/tool-env.sh
uv run --directory server python -m pytest ../image_worker/test_control.py -q
```

Operational limits:

- Only declared synthetic prompts may be used by this runner. It is not a user
  input or authorization boundary for a production image API.
- A completed JSON event alone is insufficient; the runner checks expected jobs,
  complete image bytes, dimensions, metadata and hashes after the process exits.
- Progress is pushed from callbacks; one-second RSS/swap/health sampling measures
  the trial, rather than polling a job endpoint for UI progress.
- Reaping the owned process is required before handing off capacity. This proves
  its address space is gone, not that host-wide GPU caches/swap immediately vanish.
- CLI restart, OS file caches and actual model-instance reuse are distinct.
- No explicit Ollama unload is sent. Its usual keep-alive expiration still applies.
- The first successful image increased host swap. Bound image cache/residency and
  measure it with the intended loaded chat model before production integration.

No image UI, new app listener, Research or workflow agent is implemented here.
