# Current Qwen3.8 image admission repair — proposed native check

14 October 2026. Prepared after Jake's physical iPhone report; no native probe or
production change is authorized by this document itself.

## Diagnosis and narrow change

Both chat images and Brief to images use `Engine.admit()`. The installed guard
accepts only the original Qwen 32K profile digest from I1-0, no loaded chat model,
or one model with that exact digest/context/size. The current runtime reports
Qwen3.8's 32K profile at 19,508,609,678 bytes with digest
`09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a`.
It is smaller than the existing 21,827,095,100-byte ceiling but is rejected by
identity, not by memory measurement or a failed image worker. Engine status
reports the worker is installed; it does not establish resident-model admission.

Prepare only the current digest addition to the shared admission set, and make
the fixed-workflow model list use that same set. Keep exactly one resident model,
32,768 context, the original VRAM ceiling, swap-growth limit 512 MiB, 1 GiB MLX
cache policy, pinned FLUX worker/settings and all process/capacity ownership.
Unknown digests, other contexts, excess/invalid VRAM and multiple resident models
remain rejected. No model-name heuristic or implicit model load/unload follows.

## Prepared offline checks

Retain every old assertion; add exact-current-digest, arbitrary-alias, bad-context,
bad-size, unknown-digest, multiple-residency and picker/engine consistency tests.
Run those with existing image/workflow/native-capacity tests and lint/types.
Ordinary prompts, provider payloads, runtime, sampling and defaults are unchanged.

## Native check requiring approval

One synthetic 1024-square image, seed 42, four steps, same pinned installed worker,
revision/environment and original I1-0 mug/notebook prompt. No text-model probe,
warmup, keep-alive override, unload, new weight/dependency or retry. Use the existing
cross-process native lease; stop without generation if the current residency is
absent or changed. Maximum elapsed native check 120 s; worker's original <=60 s
generation, <=24 GiB allocation and 512 MiB swap-growth guards remain.

Record current profile/digest/context/resident bytes before/during/after, actual
worker progress/output/metadata, swap, application health <=2 s, and process exit/
reaping/capacity release. Require current profile resident throughout; expiry is a
failure, not a reason to reload. Stop on the first failure and retain its outputs.
Use only the synthetic prompt; never read or rerun Jake's real workflow/chat text.

## Conditional release

Only after the bounded native check and regression checks pass: promote the two
server-file changes, preserve current code/plist/database fallback, restart the
same service, verify live new-profile admission and both workflow/chat wiring
without another native generation. Ask Jake to retry his failed image attempts.
If the check fails, retain the current live guard and explain the result; do not
remove safety bounds or silently eject his model. This specific qualification
does not qualify every installed model, factual answers, Research or WS-E.
