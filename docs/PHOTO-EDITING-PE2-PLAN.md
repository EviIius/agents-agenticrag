# PE2 — selected-area editing and compositing

21 October 2026. Jake authorized implementation and a test of the supplied
original with the hat/gloves request. Use an isolated branch; review quality
before production publication. Existing PE0/PE1 native ledgers remain closed.

## Contract

- A brush selection in the existing photo composer; Undo, Clear, brush size,
  Apply/Cancel. No vision helper, automatic face detector or new package.
- Normalized bounded strokes travel with the admitted image request and are
  durable in its existing manifest/database JSON. No schema migration.
- The normalized reference (longest edge ≤2048) is the compositing baseline.
  Its dimensions/aspect ratio are retained. Full camera original stays private.
- Use the existing FLUX.2 klein 4B edit pipeline and unchanged 1024-square native
  inference parameters. Crop context around the selection, fit without distortion
  on the inference canvas, then map its generated pixels back to the source.
- Feather only inside the hard selection. Outside the selection every decoded
  output/export pixel must equal the prepared reference. This protects pixels;
  it does not promise good generated content or alignment inside the selection.
- Retain the raw native PNG separately from the composite and sanitized export;
  include it in storage, backup/restore, hash binding and cleanup.
- An independent CPU-only checker verifies composite provenance and unchanged
  pixels before successful promotion. Preserve cancellation/reaping/ownership,
  replay/retry, old requests, ordinary generation/text payloads and all budgets.
- Every new state is available in /design. Use existing tokens/primitives and
  lazy loading; initial JavaScript stays below 256,000 gzip bytes.

## Checks and native scope

1. Real CPU synthetic mask/composite/corruption/edge tests; API durability,
   ownership, idempotency, retry and backup tests; Chromium/WebKit brush checks.
2. Freeze executed source. Maximum **two native jobs**: one synthetic selected
   edit, then the separately supplied private original with the requested hat
   and gloves. One fixed seed per case; no hidden prompt rewriting, regeneration,
   extra model/helper call, preload or downloading. Stop on protocol/resource/
   preservation failure. A private quality failure is reported, not retried.
3. Use the existing shared Capacity/native lock, empty-slot or exact qualified
   32K admission, 24 GiB MLX / 1 GiB cache / 512 MiB swap-growth / 60 s native
   generation/decode and 2 s health limits. Check residency; never load or unload
   chat models as part of this trial. Keep production application unchanged.
4. Inspect the real private result and expose a private review page. Public
   evidence contains synthetic images and sanitized metrics only. Assess the
   hat and each glove separately, face/expression/background pixel preservation,
   boundary seams and original aspect ratio. No likeness claim from text alone.

If local FLUX content is inadequate, retain that failure and research stronger
mask-aware candidates. Another model/dependency/download/native trial requires a
named reviewed scope; the request to consider stronger models is not an install.

Stop with the H4 implementation/quality report before merge/publication.
