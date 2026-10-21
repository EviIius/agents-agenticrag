# PE1 release preparation and compatibility fallback

21 October 2026. **Prepared on the isolated branch; publication is not approved.**
Jake accepted the reported generative-edit quality and authorized the measured
guard, worker installer and copied-data rehearsal. The exhausted native test
allowance is not extended. Keep PR #6 in draft until release review.

## Prepared and rehearsed

- `scripts/install_image_worker.py` installs only `worker.py`, `edit_worker.py`,
  `reference_contract.py` and `reference_codec.py`. It preserves existing matching
  interpreter/model selector bytes, refuses an occupied native lease or a silent
  selector change, and restores prior named files on a simulated copy failure.
  It neither imports the image model nor downloads weights.
- `scripts/prepare_photo_release.py --prepare` builds a **new private bundle**.
  It has no publish operation. It requires explicit source/data/plist/output
  paths, unchanged dependency locks and a quiesced source; it checks the native
  lease, active image state and source consistency across the snapshot.
- Candidate and compatibility payloads share the new schema-aware backend and
  worker. Compatibility contains the previous compiled UI. The previous backend
  and worker are archived for evidence and are not valid fallback selections.
- A full private data snapshot includes non-image files as well as the SQLite
  online backup; previous backup directories and the lock/WAL/SHM files are not
  recursively copied. A separate paired DB/image/reference backup is restored
  and validated. All retained pins, including failed/cancelled/queued edits, are
  covered. The original plist is copied unchanged.
- Actual staged imports, schema 13→14 startup, a real CPU HEIC upload and
  reference-bound queued resume/retry pass on synthetic copies with network and
  GPU execution blocked. The compatible UI/backend switch keeps a chat and input
  added after the candidate boot. The paired backup restores its complete graph.

The private rehearsal bundle is under:
`~/.local/share/workbench/qa/photo-editing-pe1-integration-20261021/bundle`.
It contains **synthetic data**, not a production recovery snapshot. Never replace
live data with that rehearsal snapshot. A fresh production bundle is required at
an approved publication boundary.

## Fresh bundle command (only after publication approval and quiescence)

Use the installed app interpreter or the unchanged development environment.
Substitute the actual existing plist, and a new output directory outside the
source/app/data/worker directories. The command prepares only; it does not deploy.

```sh
server/.venv/bin/python scripts/prepare_photo_release.py --prepare \
  --output "$AETHER_RELEASE_BUNDLE" \
  --data "$AETHER_BASE/data" \
  --installed-app "$AETHER_BASE/app" \
  --installed-worker "$AETHER_BASE/image-worker/product" \
  --plist "$AETHER_EXISTING_PLIST"
server/.venv/bin/python scripts/prepare_photo_release.py --verify "$AETHER_RELEASE_BUNDLE"
```

The bundle includes `release.json`, `candidate-app/`, `compatibility-app/`,
`worker/`, `original.plist`, `data-snapshot/`, `paired-backup/`, and archival-only
previous source/worker directories. Verify every manifest hash before a future
publication. Original server/image interpreters, transcription configuration and
weights remain in place and are never resolved or upgraded by preparation.

## Future publication sequence to review

This is a concrete operation plan, **not authorization to execute it**.

1. Confirm the existing plist/bind/port/label and normally verified Tailscale route
   still match. Ensure no accepted user task is lost: finish or cancel/reap active
   work, then stop the existing launchd service. Preserve queued inputs/jobs. The
   image parent pipe and shared native lock prevent releasing the slot before an
   old child exits; require the lock to be available before any replacement.
2. With the app stopped, create the fresh bundle above. Keep the installed app,
   image/transcription interpreters, model paths and original plist available.
   The bundle's original data is disaster-recovery evidence, not a rollback that
   can later erase new messages.
3. Validate the candidate app and four-file worker payload hashes against the
   reviewed source. Install the worker using the existing selector values while
   quiesced. Publish only the candidate's `server/app` and `shared` trees; retain
   the installed `.venv`, transcription tree/configuration and all live data.
   Dependencies are unchanged; no `uv sync`, model load or inference is needed.
4. Keep the **existing plist byte-for-byte**, including its image-home selector.
   Restart that same label on 127.0.0.1:8787. Verify local and normally validated
   Tailscale HTTPS health, installed hashes and schema. Queued jobs are accepted
   user work: the new backend may resume them with their pinned references;
   do not mislabel that recovery as a new qualification test or silently turn an
   edit into generation. No added native validation call is authorized here.
5. Verify actual UI loading, normal typing/sending, Edit photo/reference viewing,
   exports and Workflows. Request the post-release physical iPhone check. Earlier
   phone checks do not cover this unreleased feature.

`make deploy` / the generic `deploy.py --apply` path now refuses a source tree
with migration 014 before touching the service. It lacks this combined worker/
reference/fallback contract and must not be used to bypass PE1 release review.

## Compatibility fallback

Quiesce/reap the same service, preserve the failed UI tree, and replace **only**
its static tree with the reviewed `compatibility-app/server/app/static` payload.
Keep the newly installed schema-aware backend, worker and **current data**. Keep
the original plist/port/label/Tailscale route. Restart the same service, verify
installed hashes/health and reload the UI. Edits remain image turns with output
access; the older UI does not expose the new editing/reference controls. Its
existing retry still reaches the reference-aware backend.

Do not copy `previous-app-archive` or `previous-worker-archive` into service, and
do not restore the pre-release DB over newer data. The old server can start on
schema 14 but retry an edit as plain generation. A backend startup failure cannot
be repaired by this UI fallback: stop the failed service, preserve current data
and prepare a schema-aware fix/recovery. Full old-backend rollback is unqualified.

## Gate before a release decision

Review the integration H4 report, final check/browser results, bundle hashes,
source/evidence preservation and the fallback's limited scope. Main merge and
publication still need Jake's final approval. No additional native call, automatic
model unloading, scheduler/watcher or agent implementation is part of preparation.
