# Corrected-mask pair — isolated evaluation only

Approved scope: `docs/PHOTO-EDITING-PE4-COMPARISON-PLAN.md` and the corresponding
23 October AGENTS amendment. One FLUX invocation, then one Qwen invocation;
no extra images, retries, helper models, downloads, integration or publication.

`prepare.py --root <new-private-root>` copies the existing private reference/task
and corrected selection, verifies CPU context and face exclusion, hashes the
already installed checkpoints, then freezes source/inputs and records the
operator's current explicit approval. **Run it only after that approval.** The
receipt records authorization; generating a receipt is not authorization.
It cannot be used to reopen an older budget. Never replace a prior root/ledger.

Run one case at a time through the repository `run.py` using the server Python:
`run.py flux --root <private-root>`, inspect the actual result, write its bound
private quality review, then `run.py qwen --root <private-root>` if technical
gates permit. Do not execute the private copy of `run.py`: its repository import
root is intentionally anchored to the checked repository launcher.

The controller verifies frozen hashes, actual step counts, model/settings/output
binding, CPU compositing, health/swap/latency/MLX bounds and owned reaping under
the existing shared lease. Failed/cancelled native launches consume their slot.
A technical failure blocks the second engine. An output-bound FLUX visual review
may record failure without blocking Qwen, as explicitly approved for this pair.

Both workers use the existing MFLUX 0.22.0 environment, native progress and a
parent-death pipe. FLUX derives from the existing product edit worker, adding
network refusal, the same 24 GiB allocation guideline, an initialized event and
settings/helper-count metadata. Its one image call/recipe is unchanged. Qwen
uses the PE3 worker unchanged except formatting and its filename, alongside the
new CPU paint/erase module. No product or installed worker is replaced.

CPU tests exercise actual subprocesses and Pillow while replacing all native
model modules. The controller fixture also verifies that a FLUX visual failure
can be compared, a stale review cannot continue, and slots cannot be retried.
Keep private media, exact prompt, masks and output metadata outside Git.
