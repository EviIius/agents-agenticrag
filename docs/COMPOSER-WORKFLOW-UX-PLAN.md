# Composer and visual workflow correction

Jake reports Images works on his iPhone, but the separate sidebar entry and seed
configuration are cumbersome. He requests a Workflows tab above chat and a visual
step canvas with selected-step settings, using the supplied screenshot as layout
inspiration. This supersedes the earlier standalone form layout.

## Bounded implementation

- Chat / Workflows navigation above the conversation, returning to the same chat.
- Create image in the message box. Describe the image and generate directly with
  the existing worker; saved results, progress, cancellation and saving remain
  available there. The separate gallery route remains available for saved outputs.
- Automatic image seeds. Optional advanced controls support exact repeats. Resolve
  seeds once before acceptance and reuse them after an uncertain response; retain
  the resolved values in existing job/workflow metadata.
- Visual builder for the two approved templates: select a step to configure its
  inputs, model, review or image count. Show real connected execution steps, with
  input settings beside the canvas on desktop and below it on phones.
- Start / saved runs remain actual existing durable workflows. No arbitrary
  agents, branches, loops, connectors or extra calls are implied by the canvas.
- Carry the user's explicitly selected chat model into the builder, show it in
  the model step and allow a change. Preserve saved sampling defaults and review.
- Preserve unsent chat text across a trip to Workflows. Keep separate image text
  from chat text; do not submit a chat message when creating an image.

## Evidence and release

No server/schema/prompt/engine/package changes or new native inference are needed.
Verify both browser engines, narrow reflow, keyboard step selection, automatic /
explicit seeds, request retry identity, draft preservation, existing exports,
review pauses, recovery and cancellation against the fake runtime. Retain
synthetic screenshots and the current bundle budget. Run repository checks and
browser regression gates; publish static assets with a private fallback and
unchanged server hashes. Report H4 evidence; actual phone review is separate.
