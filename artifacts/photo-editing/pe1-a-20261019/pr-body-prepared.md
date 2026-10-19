## PE1-A — durable photo-reference backend (isolated)

Implements section A of `docs/PHOTO-EDITING-PE1-PLAN.md`. Composer integration is PE1-B; actual product-worker qualification remains PE1-C. Keep this PR draft. No merge or deployment at A.

### Implementation

- Additive schema 14, chat-owned opaque reference uploads/previews, explicit from-output copies, atomic job pins and retry/recovery.
- Preserve raw originals before HEIC conversion; CPU normalization uses the installed image interpreter. Originals stay private. Export PNGs strip metadata while retaining native output/provenance.
- Separate input/export/measurement storage accounting, confirmed inactive-input clearing, and version-2 reference-aware backups that include queued/failed/cancelled jobs. Old image companions remain readable.
- New product edit adapter supplies actual reference pixels and independently validates hashes. The original generation worker and legacy generation request canonicalization are unchanged.
- Availability updates advance holder timestamps and emit SSE. Queued edits preserve the bounded storage-sample budget until capacity is acquired.
- Web changes are generated API types and fixture defaults only; no new visible control yet.

### Evidence

- `make check`: 745 Python tests, 126 frontend tests; lint/types/coverage/API growth/motion/privacy/110 contrast pairs pass.
- 19 focused photo-reference cases; 14 additional CPU/fake-worker controls, with no native model calls.
- Browser result: complete invocation 720 passed / one frozen-clock fixture failure / three existing skips; corrected case then passed both Chromium and WebKit, 2/2. The full failure and trace are retained, not relabeled green.
- Main/live preservation: 563 candidate source hashes, 551 main source hashes, 114 installed server files, 425 static files, eleven PE0 sources and 73 evidence files verify; local/verified HTTPS health pass. All 1,631 historical overwritten artifacts are restored after archiving the fresh run.

H4: `docs/PHOTO-EDITING-PE1-A-REPORT.md`.
QA analysis: `docs/PHOTO-EDITING-PE1-A-QA.md`.
Evidence: `artifacts/photo-editing/pe1-a-20261019/`.

### Boundaries

PE0's eleven executed source files, all 73 evidence files and exactly six native invocations remain intact. No seventh call, dependency/weight/runtime/prompt/sampling/default change, automatic chat eviction or agent/Research restart. CPU HEIC preservation uses a conversion double; actual HEIC-to-edit and product GPU quality/resource qualification remain later gates. Empty chat residency is not yet qualified for edits and needs explicit review at C.

PE0 report/comparisons remain in `docs/PHOTO-EDITING-PE0-TRIAL-REPORT.md` and `artifacts/photo-editing/native-20261019/review.html`. The requested edits are visible, with the documented lighting/texture/framing drift; no guaranteed likeness or exact preservation claim.
