# PE0 photo-reference preparation

Isolated candidate; not installed or imported by the production application.
No native execution is approved by these files. The accepted application and
all old trials remain unchanged. See `docs/PHOTO-EDITING-NEXT-CHECKPOINT.md`.

## Prepared components

- `contracts.py`: strict explicit generate/edit requests; fixed owned input
  names; original/working SHA-256 bindings; bounded actual PNG/JPEG decode,
  EXIF orientation, 2048-edge normalization and metadata stripping. An original
  is kept as `inputs/original`; the clean engine input is `inputs/reference.png`.
  This CPU preparation supports PNG/JPEG for the declared trial. HEIC in the
  future app integration still uses the existing Mac codec, not a new decoder.
- `worker.py`: isolated adaptation of the unchanged production worker. Generate
  retains its exact model arguments. Edit selects `Flux2KleinEdit` and passes one
  verified `image_paths` entry. Recheck references before and after execution;
  write PNG/metadata through partial files, fsync, then emit finished. No silent
  generation fallback, arbitrary path, new model, precision or sampling option.
- `controller.py`: reuse the application's `Engine`, `Capacity`, inherited lock,
  parent pipe and cancellation/reaping. PE0 requires the exact declared daily
  32K chat digest resident, retaining all generation limits. A health failure
  cancels through the same owned reaping path. A source-bound operator approval
  receipt is mandatory before `run_case`; offline preparation creates no native
  authorization receipt (unit tests use dummy receipts in temporary directories).
  Six fixed ordered reservations/results are append-only. A failed or incomplete
  attempt blocks the next, and no attempt can be repeated. Each call returns
  separately; each completed image needs a hash-bound visual review before
  the next invocation. A rejected review stops the trial. Human publication
  acceptance remains a separate gate.
- `trial.json`: six fixed prompts/seed/settings/expected changes: portrait,
  background edit, oriented non-square clothing edit, retained mug recolor,
  cancellation and one scheduled recovery. No text-model or keep-alive call.

The generated portrait's future hash cannot be frozen before it exists. Its
single retained output becomes the bound original for later edits; freeze each
input descriptor and request before starting its dependent invocation. The
non-square derivative is the declared crop/rotation/JPEG/EXIF transform, not a
second generation. The retained original mug hash is fixed now.

## Offline checks

Use the existing server pytest and installed image environment; install nothing:

```sh
. scripts/tool-env.sh
uv run --frozen --directory server python -m pytest ../image_worker/editing/tests -q
```

The image subprocess uses the already installed Pillow on CPU. The test driver
injects synthetic MLX/MFLUX modules, blocks actual native imports and network,
and never reads a model weight. It exercises the actual candidate worker and
production subprocess supervisor. Synthetic step events and fake memory numbers
verify protocol/control behavior only; they do not qualify image quality,
native resource use, latency, likeness or coexistence.

## Before approved native execution

Freeze the candidate's four source/plan hashes and exact installed environment;
copy its worker/contracts/plan into a private trial home, leaving the installed
product worker untouched. Use that home's `.python` and `config.json` selectors
for the existing interpreter and pinned snapshot. Preserve a separate job root
per case with a fresh output directory. Bind the operator receipt to these exact
hashes only after explicit user approval. The receipt documents authorization;
writing a receipt cannot supply human authorization by itself.

Use the production `data/native.lock` through `Capacity`; do not substitute an
independent lock during a native trial. No configured embedding release is needed
or performed by this candidate. Other/absent/expired chat residency is a stop;
do not refresh it with another call. The existing one-second admission/swap guard
and the added <=2-second health probe are read-only resource checks, not UI polling.
The controller runs in the existing server interpreter with `server/` on its
source path; its child uses the image interpreter selected by `.python`. It does
not start another application listener. Final residency/swap checks run after
reaping and before lease release, including expected cancellation; health is
also checked after completed or cancelled work.

Protocol success does not mean a correct edit. Review target changes, likeness,
pose, non-target detail and output framing side by side, retaining failures.
Human quality acceptance precedes PE1. No integration, download, live deployment,
mask/brush editing or guaranteed unchanged pixels is included.
