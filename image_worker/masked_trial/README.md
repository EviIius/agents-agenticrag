# PE3 isolated Qwen mask trial

Scope: `docs/PHOTO-EDITING-PE3-QWEN-TRIAL-PLAN.md`. This directory does not install
Qwen into Aether's live engine, change the FLUX default or qualify simultaneous
residency. Both checkpoints can remain on disk. Use the existing image Python;
no dependency changes.

Closeout: `docs/PHOTO-EDITING-PE3-REPORT.md`. The two native invocations are
exhausted; private content quality failed. The approved installation does not
authorize another case, retry, altered selection or product integration.

- `preflight.py`: static installed-source inspection and actual CPU processor /
  context/compositor checks, with model/MLX imports and weight/network access
  blocked. The installed PIL processor imports the existing CPU torch package.
- `model-files.json` / `download.py`: exact pinned file allowlist and content-hash
  verification; excludes other checkpoints and writes a private download receipt.
- `trial.json`: frozen candidate-only settings and ordered two-image allowance.
- `worker.py`: explicit mask at every denoising step, disabled language-generating
  helpers, real step events, reference binding, independent final compositing and
  measured resource checks. Decoder stays unquantized as required by the engine.
- `control.py` / `run.py`: existing shared native lease, parent-death descriptor,
  empty-slot / health / swap guards, initialization/generation/wall deadlines,
  owned process-group reaping, append-only attempts and a separate synthetic
  visual gate before the private invocation.
- `fake_worker_driver.py` / `test_trial.py`: real CPU/process checks with image
  inference replaced; a finder rejects actual model imports in the double.

Sources and **both** input requests are frozen privately before the first launch.
The public tree never contains the user's original, its filename/task/mask or
real-image screenshots/traces. Keep protocol pass distinct from generated-content
quality. A failure ends the trial, even when another call remains in its cap.
Creating a new root or approval JSON is not permission to repeat the trial.

Offline checks (no model invocation):

```sh
server/.venv/bin/python -m pytest image_worker/masked_trial/test_trial.py -q
server/.venv/bin/ruff check image_worker/masked_trial
```

Native commands require the private, approved/frozen trial root and a complete
verified local checkpoint. Run one case at a time, inspect the synthetic result,
and retain all failures. No automatic retry, prompt rewriting, evaluator, other
model, download, chat load/unload or cloud fallback is provided.
