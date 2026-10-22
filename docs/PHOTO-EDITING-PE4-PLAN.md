# PE4 — precise selection and coverage review

22 October 2026. Jake approved improving mask coverage after the PE3 result.
Continue on `codex/masked-photo-editing`, keeping draft PR #9 isolated.

## Scope

- Add Paint / Protect (erase) / Move tools, zoom and pan, a visible brush cursor,
  Undo/Redo and selected/protected preview modes in the existing lazy dialog.
- Preserve original image proportions, draft ownership, Cancel, keyboard access
  and mobile controls. Use existing primitives/tokens and no dependency.
- Ordered optional stroke operations: omitted operation remains legacy paint;
  `erase` removes selected pixels. Preserve omitted-field serialization and
  existing saved masks, replay identity, retries, backups and export proofs.
- Render a single mask layer so overlap does not become misleadingly darker.
  Display approximate selected coverage and refuse an effectively empty mask.
  Browser edge rasterization is a visual approximation; the CPU raster and final
  verifier remain authoritative. Do not call preview statistics semantic proof.
- Check the supplied original privately on CPU: cover the existing hair/hand
  areas that need replacement, plus space for additions, and protect the actual
  facial area instead of using a rectangle that also excludes necessary hair.
  Keep the original, selection, task and private review media outside Git.
- Synthetic real-CPU erase/order/legacy/preservation tests; durable API retry/
  backup tests; Chromium/WebKit paint/erase, zoom/pan, Undo/Redo, Cancel, empty
  selection and mobile theme/short-viewport checks. Expose all states in /design.

## Review boundary

No model/native generation, new download, prompt/step/precision change, Qwen
integration, routing, main merge or live publication. PE2 and PE3 ledgers stay
exhausted; freeze their executed worker/engine/evidence snapshots unchanged.
Use a separately copied CPU module for new private coverage checks. Do not alter
old selections or recompose old results as a new quality pass.

Stop with SPEC H4 evidence and a private mask-only comparison. A corrected mask
is not a generated-result improvement. Any subsequent generation comparison
needs its concrete bounded scope reviewed after coverage is inspectable.
