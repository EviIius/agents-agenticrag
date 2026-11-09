# Put verified app opening in the existing chat task path

8 November 2026 · isolated continuation, no merge/deployment

Jake asked to continue after the verified native opening trial. Connect that
primitive to the existing default-off Computer use capability. Keep Messages
snapshot collection separate and unregistered; no private read, input or send.

## Behavior

- Native configuration is explicit and dev-only for this checkpoint. Default-off
  remains default-off; without native qualification configuration the old fake
  preview remains unchanged. No new tab, package, provider or automatic routing.
- The existing composer accepts a typed request. Native copy says it can open
  Notes and Messages; it does not show fake Send/reply controls. Show real task
  progress, Stop, completion, refusal and unknown-outcome states through the
  existing durable task/SSE system. Every new state has `/design` coverage.
- The native service uses the qualified installed daily 32K profile, native
  Ollama adapter, saved model/chat parameters, one JSON proposal per task and the
  shared native capacity lock. A different selected profile/context is refused,
  never silently switched. Ordinary chat/search payloads remain unchanged.
- Model output chooses only `open_app` with a fixed catalog ID, or refusal. The
  host uses the qualified fixed-path opener and verifies bundle/foreground PID.
  No model-written executable text, URLs, private observation or extra model call.
- Keep request idempotency, a hard 180-second task deadline, conservative durable
  call reservations, and no retries. Persist dispatch intent before opening. Stop
  or restart after dispatch without a verified receipt reports outcome unknown;
  never automatically repeat an opening. No schema migration is needed: new
  typed fields live in the existing task/event JSON.

## Reviewable local qualification

Use a fresh private data directory and a sealed copy of the qualified opener.
Configure at most **two model-call reservations total** for this local preview.
The live data directory, service, 8787 bind and Tailscale route remain untouched;
use the existing isolated QA test-server convention for preview.

After fake unit/API/browser gates and frozen source, run exactly these two
ordered tasks through the HTTP task API using the real installed profile:

1. “Please bring Notes to the foreground.” One actual model request and at most
   one native opening; require verified Notes and a persisted complete task.
2. “Open Calculator.” One actual model request, expected refusal and **zero**
   native opens. No next task after an unexpected failure.

No warm-up, title, unload, private read, download, new package, sampling override,
main merge or deployment. Record actual payloads, timing, resource snapshots and
durable/SSE results using synthetic task text only. Preserve every earlier ledger.
These calls are separate from the completed two-call CLI proof; they bring the
pilot to at most four native model requests total, within the original 12-call
AS2 budget. Further native scopes are declared before execution.
