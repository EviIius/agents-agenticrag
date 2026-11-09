# Selected Messages metadata checkpoint

9 November 2026 · isolated `codex/assistant-as1b` · draft PR #17

## Summary

The bounded native metadata read and actual post-disable refusal both pass.
Thirteen elements/four text areas expose 494 accepted metadata bytes in 0.282 s.
Outer containers have no IDs; inner containers and text areas each share an ID.
Exact message/recipient/direction binding remains unqualified. Close this AX route.
No bodies, model call/use, input/send, database access, merge or deployment occurred.

## Done-when checklist

| Item | Result and evidence |
| --- | --- |
| Only fixed selected-pane/container metadata | Pass: `read.summary.json`, 13 elements, same sealed ancestry and shape checks |
| No linked body-reading implementation | Pass: compiled symbol audit, original body-reading definitions excluded before compilation |
| Python/Swift field/path/cap parity | Pass: 48 compiled checks and the shared invented mutation corpus |
| Native read, then genuine revocation refusal | Pass: 0.282 s read; fresh helper permission_required in 0.128 s after disable |
| No unknown capability names/private data published | Pass: seven fixed metadata fields; known presence booleans and counts only |
| Native message/recipient/direction binding | **Not qualified**: no outer IDs, repeated inner/area IDs; `identity-assessment.json` |
| No further AX fishing or model use | Pass: two-request ledger exhausted; helper off; specific alternative prepared |
| Regression checks | See Test output below |

## Changed files

- `tools/mac_desktop/SelectedMetadata.swift`: separate version-three metadata
  entry point. Fixed seven fields, byte/path/type caps, before/after selected
  structure/window/element/attribute equality; no body or input operation.
- `scripts/build_dynamic_reader.py`, `build_metadata_reader.py`: reuse unchanged
  selection/structure and bounded-attribute definitions from protocol two, while
  excluding its body-reading and native entry point at source level.
- `server/app/assistant/mac_metadata.py`: strict unqualified private models and
  sealed two-request owned-process transport; not registered in the application.
- `server/tests/test_mac_metadata.py`, `check_metadata_reader.py`: invented-data
  parity, boundaries, forgery, source isolation, cancellation and budget tests.
- `run_metadata_trial.py`, source/build manifest and sanitized evidence under
  `artifacts/assistant-metadata-20261109/`; raw attributes stay outside Git.
- This H4 report, the metadata plan and the concrete store-bridge proposal.

## Deviations from SPEC.md

Jake continued the local computer-use pilot and freshly confirmed the selected
self-conversation/empty composer ("youre good"). That direction and delegated
Settings setup cover the declared two-request metadata scope. No old ledger was
reopened. This does not authorize Full Disk Access, a store read or a local-model
draft. Jake subsequently approved the isolated read-only store trial; its new grant
and exact self-address setup remain required before database access.

No extra package/model, UI mode, migration, provider prompt, sampling override,
service/port/route change, main merge or live deployment belongs to this checkpoint.

## Runtime observations

The selected pane contains four outer groups, four inner groups and four text
areas. None of the outer groups has AXIdentifier; the four inner groups share
one identifier, and the four areas share another. No inspected identifier
contains a UUID. Descriptions exist, but the assessed attributes do not establish
an exact native thread/recipient/message/direction binding. Absence of explicit
direction words is a diagnostic, not proof that every possible accessibility
surface lacks that information. We do not call the four areas four messages.

All 13 elements advertise custom-content/linked-element/selection attributes,
and four areas advertise attributed-range support. Those booleans establish
availability only: no linked element, custom-content value or attributed body was
read, and they are not asserted to solve identity. Do not extend this stopped
scope by querying them or derive identity from paths, names, body text or hashes.

The helper's exact new build was added via delegated System Settings actions,
then disabled after the single successful read. A fresh second process actually
refused access and returned no target or snapshot. Other permission entries
were unchanged. Codex used no SDK inspection or screenshot of Messages.

Raw receipts remain mode-0600 in a private mode-0700 QA directory. The public
summary contains counts, standard roles and presence flags, not attribute values,
handles, private-text digests or user content. New model requests: **zero**.

Preparation failures were retained before any native request: the builder refused
a packaged boundary's 0644 mode; an identical private 0600 copy fixed that setup.
Compiled parity then caught Swift accepting a floating-point zero path; explicit
numeric-type checks fixed it. A subsequent symbol check found an unused body
function still linked from shared definitions; source-level exclusion fixed that.
Final build-04 passes all checks; older preparation builds remain private.

## Test output

- Focused Python: **101 passed**, comprising 60 new metadata tests and 41 existing
  snapshot tests. Lint/format/strict types for the added application/test modules pass.
- Compiled final build: **48 checks passed**, with zero native jobs/model calls.
  Cases include field/combined UTF-8 caps, numeric/boolean paths, unknown fields,
  wrong app/operation/version, stale metadata, no-body mode and forbidden symbols.
- Full `make check`: **1,042 Python / 156 frontend / 969 contrast pairs** pass,
  including lint/format/strict types, API/motion/privacy guards and the production
  build/glass check. Assistant coverage is **1,611/1,767 = 91.2%**. All 32,654
  historical artifact hashes verify preserved; fresh coverage is retained separately. No frontend changes or new browser states were introduced;
  no browser rerun or physical iPhone acceptance is claimed for this checkpoint.
- Native scope: exactly two one-shots, one metadata read and one permission refusal;
  no retry, body retrieval, model call, input or send. Both passed their declared gate.

## Screenshots

None required for a metadata-only change. No private app/snapshot screenshot was
captured. Existing app-opening chat/design screenshots remain historical evidence,
not a fresh Messages identity or iPhone pass.

## Review and next steps

`docs/ASSISTANT-MESSAGES-STORE-PROPOSAL.md` specifies a separate named helper,
installed system SQLite, exact user-selected self handle/native chat/message IDs,
text/row/time caps, WAL-aware read-only access and a three-request trial. It also
states that macOS Full Disk Access is broad even if helper policy is narrow.
No Messages database has been opened/copied and no new permission was granted.

Jake approved the isolated bridge trial after reviewing this scope. Prepare it
without real store access; he must still manually grant/revoke the new helper's
OS access and enter his selected self-address before the native requests. Private model use and sending remain
later scoped work. If he declines, use explicitly user-provided text for a manual
reply draft and do not claim automatic Messages reading. Keep already working
app opening intact on the isolated branch; the live app remains unchanged.
