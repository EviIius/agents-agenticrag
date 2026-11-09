# Local-model app opening: first observable computer-use result

8 November 2026 · isolated `codex/assistant-as1b`, no live integration

Jake directed Codex to continue until local-AI computer use is possible and to
handle permission setup directly. The exact new reader entry was added and
enabled through Settings. Its corrected read returned `stale_window`; no
candidate was returned. This establishes that permission was no longer refused,
but does not identify which layout/stability check failed or prove that no
transient attributes were copied. The original two-request ledger and corrected
one-request stopped ledger stay intact. The helper was switched off afterwards;
no further read or refusal request follows that failed batch.

Do not make basic app opening depend on qualifying private Messages semantics.
Implement and qualify that already-planned operation separately. This narrows the
first AS2 task; it does not waive the recipient/latest-message gate for replies.

## Frozen native scope

- Native Ollama adapter, installed daily `qwen3.8:27b-atelier-eval-32k`, runtime
  metadata and saved parameters. No name-based capability inference or sampling
  overrides; model-default thinking unless a saved setting exists. Same 32K.
- At most **two** actual model requests total in one durable private ledger:
  “Bring Notes to the front.”, then “Open Messages.” Each makes one JSON intent
  request, followed by at most one fixed host-authored app-open operation.
- Strict Pydantic decision: open one allowlisted app ID, or refuse. No model
  scripts, arbitrary paths, URLs, input, screenshots, reading or sending.
- Fixed Apple app paths/IDs, verified before opening, after NSWorkspace completion
  and against the actual foreground process. Model JSON is never proof of success.
- Each complete task has a 180-second deadline; native opening has an eight-second
  host deadline and a shorter independent watchdog. Cancellation reaps the owned
  helper. No automatic retries; first unexpected failure ends the two-task batch.
- Share Aether's existing `native.lock` capacity gate for inference. Capture memory,
  swap, queue/model wall time and actual request parameters. No warm-up, unload,
  download, new package, service change, database write, default change or deployment.
- Preserve AS1-B's ten frozen source files and existing ledgers. Use new source,
  tests and an isolated executable that does not request any macOS permission.
  Notes/Messages are the previously approved app allowlist; opening Messages may
  mark the already selected thread read, as the original pilot disclosed.

Offline gates cover invalid/extra tool arguments, wrong target/foreground receipt,
unavailable/oversized/invalid output, and cancellation. Freeze prompt/source/build
hashes before the first actual request. Record observed results without describing
this narrow proof as general clicking, text editing, read/reply or live chat support.

After this proof, repair selected-window discovery using a fresh role-only
diagnostic rather than weakening identity checks or feeding private candidates to
a model. Messages reply integration remains blocked on exact identity/direction.
