# I1 native verification declaration

Candidate: separate `image_worker/product/` source, pinned existing MFLUX 0.22.0,
original model revision, private I0 environment. No package or weight download.
Live installed code remains unchanged until all release gates are assessed.

The native run has no automatic retries and retains failures. Freeze the worker,
queue/resource boundary, API/models, shared native-admission code and harness in
`artifacts/images-i1/native/source-manifest.json` before executing.

Ordered native checks:

1. Ordinary daily 32K Qwen READY answer, no sampling values/default changes.
2. Cancel after the actual worker reports loading, before MLX imports/initialization.
3. Cancel after one actual denoising callback and GPU synchronization.
4. One original synthetic photograph, seed 42, durable PNG and metadata.
5. Same synthetic prompt, seed 1337, as an additional full generation version.
   Queue one ordinary READY answer during denoising; it must wait for worker
   reaping, then run without overlapping native image work.
6. Verify original SHA remains intact, two outputs/one version and real file sizes;
   back up outputs; ordinary READY answer after the image jobs.

All images use 1024², four steps, guidance 1, eligible-layer 8-bit quantization,
1 GiB unused-allocation cache. This is not a total/live/host memory cap. Native
steps have a 60-second generation/decode bound, a 300-second worker bound, host
swap growth at most 512 MiB and cancellation/reaping at most ten seconds. No hidden
unload/load/keep-alive refresh, fallback prompt/settings/seed or inferred capability.
Loaded residency is checked by reported digest/context/allocation before and during
images. Empty residency or the exact previously qualified daily profile is admitted;
other combinations fail with an explicit action, without evicting them.

Unit/process tests cover restart reconciliation, parent death and inherited native
resource-lock ownership, corrupt/missing outputs, low disk, deduplication, API
validation, SSE replay, restore and backup retention. Browser tests cover production
Images, all synthetic states at 390/1440 in both themes and both engines, cancelled
PNG/JSON selection, version preservation and storage deletion. They do not constitute
physical iPhone checks or reference-editing qualification.

Run full `make check`, a single complete `make e2e`, additive API/database/prompt/
payload checks, rollback on a synthetic copy, bundle measurement and unchanged
ordinary Search replay after scheduling-boundary changes. Keep original evidence
bytes and retain current-run outputs separately. Failed gates keep I1 open.
