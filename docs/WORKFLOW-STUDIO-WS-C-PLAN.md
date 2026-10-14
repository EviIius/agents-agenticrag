# Workflow Studio WS-C implementation

Jake accepted WS-B and asked to continue on 12 October 2026, retaining Claude's
prototype UI and making it functional. WS-C stops for review before WS-D, main
merge or live publication.

- Match all provided references and the interactive prototype: neutral cards,
  category tiles, dotted canvas, compact controls, 264 px Blocks panel, 360 px
  Inspector and phone Outline/bottom sheet.
- Approved dependency: exact pin `@xyflow/react` 12.12.0, published 24 September,
  newest stable 12.x at least two weeks old. Import base.css only; retain MIT
  notice and attribution; editor/library load only on Studio routes.
- Seven executable kinds use WS-B generated contracts; later kinds stay visible
  but unavailable with the checkpoint explanation. Never simulate execution.
- Preserve layout-independent ID ordering, immutable snapshots, model/default
  inheritance and frozen template prompts.
- Real definition cards; template copies become editable definitions; remove
  fixed builder. Basic Start-input submission and durable results/approval/
  cancel/retry/export preserve today's template functionality. On-canvas live
  execution, test/reuse, versions and Pick favorites remain WS-D.
- Pure graph editing; shared browser/server validation fixtures. No native model
  inference or changed chat/search/Library/transcription/image prompts.
- Image creation/results inside the conversation remains DEFERRED-FIXES.md work.
- Synthetic tests/evidence only. Videos outside Git. Preserve historical evidence,
  references, main and installed hashes. No invented physical phone/VoiceOver pass.

Verify focused graph/store tests, both browser engines, phone Outline, visual
comparison, both themes, axe and reduced motion, then make check/build/bundle
and one complete make e2e. Record existing selector/navigation changes without
removing behavioral assertions.
