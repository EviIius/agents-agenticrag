# Messages store bridge preparation

9 November 2026 · isolated `codex/assistant-as1b` · draft PR #17

## Summary

Jake approved the named isolated read-only bridge after the AX metadata closeout.
Aether Messages Reader is built/signed separately with system Swift/SQLite.
Invented-database checks cover native identities, source changes and read-only WAL.
The private setup window is open; manual selection and Full Disk Access are pending.
No real Messages store access, model request, send, merge or deployment is claimed.

## Done-when checklist

| Item | Result and evidence |
| --- | --- |
| Named separate helper, no package/framework download | Pass: build-07 manifest, installed Apple frameworks/system SQLite only |
| Exact private address setup without reading Messages | Implemented: setup writes only its private 0600 selection; no database call in that entry point |
| Fixed database path, no caller SQL/path/recipient | Pass: operation models, native entry points, source/symbol checks |
| Literal direct-thread/native message identity binding | Pass on invented data only; real schema/identity unqualified |
| Eight rows / per-message and total UTF-8 caps | Pass on invented data; unsupported newest rows refuse, never silently skipped |
| Read-only and WAL freshness | Pass on invented WAL database, including unchanged main/WAL bytes during the reader operation |
| Duplicate/group/edited/deleted/unsupported data | Explicit refusals pass; no attributed-blob decoder or fuzzy recipient search |
| Cancellation and changed source | Offline checks pass; no actual native cancellation timing qualification |
| Real three-request trial | **Not started**; required manual setup/grant confirmation remains pending |
| Production app | Unchanged; new bridge is not registered or available to a model |

## Changed files

- `MessagesStore.swift`: fixed read-only SQLite queries, schema/type and native
  identity checks, size/progress/transaction bounds, authorizer, WAL-aware fresh
  reads and refusal of unsupported records. Received text remains literal.
- `MessagesStoreTrial.swift`: separate bundle identity, private self-address UI,
  exact job/selection validation and read-only entry points. No Accessibility,
  Automation, network, screen-capture, model or send API.
- `MessagesStoreFixtures.swift`: compiled only into a separate unprivileged
  invented-database checker; test data/DDL are absent from the named helper binary.
- `mac_messages_store.py`: strict unqualified private contracts, nonce/PID/build
  checking and three-reservation owned-process transport. Not imported by main.
- Builder/check/operator scripts, 47 Python tests and sanitized source/build
  evidence under `artifacts/assistant-messages-store-20261109/`.

## Deviations from SPEC.md

The separately approved store bridge replaces the stopped selected AX path for
this isolated trial. It does not install an agent framework or restart Research.
The exact self-address and Full Disk Access must be supplied manually by Jake;
neither an old Accessibility grant nor elapsed time is evidence of those facts.
No broad-parent permission grant, private model use or sending is authorized.

## Runtime observations

The native helper has a different bundle identity from Aether Desktop Trial.
Build-07's private code/source manifest is frozen. The setup entry point only
accepts an exact country-coded number or email, saves it outside Git and clears
the field. It does not inspect the Messages store or modify other apps.

The planned resolve operation accepts exactly one direct chat matching that
literal address and native service/participant set; no/group/duplicate matches
refuse. Read operations rebind that native target and collect at most eight
native GUID/direction/date/text records. A second short transaction must match
the first fully. No incoming row is an explicit null, not an outgoing-as-incoming
substitution. These are implementation contracts, not evidence of this Mac's data.

Plain stored text only is supported in this trial. Missing/NULL/oversized text,
attachment markers/rows, nonordinary event types, edit/summary/recoverable records
and unknown schema/type combinations refuse. Rich attributed-body decoding is
not implemented or silently approximated. An unsupported newest row cannot be
filtered away to make an older message appear latest.

SQLite uses READONLY/NOFOLLOW/PRIVATECACHE, verified readonly main, query-only,
trusted-schema off, an authorizer and parameterized fixed queries. Extension
enabling is absent from Apple's SDK; no enabling call exists, and the authorizer
also denies SQL load_extension. SQLite may coordinate through existing WAL/SHM;
do not extrapolate the invented main/WAL byte check to zero sidecar effects on
the real store. No immutable snapshot or main-file-only copy is used.

Preparation retained compiler corrections and failed offline builds. The first
compiled database check refused a temporary path: a separate all-synthetic
diagnostic showed SQLITE_OPEN_NOFOLLOW returning CANTOPEN_SYMLINK for Foundation's
temporary-directory alias, while POSIX realpath opened successfully. Fixture
paths are canonicalized with realpath; the native fixed-path/no-follow policy
was not relaxed. No protected Messages path was tested to diagnose this.
The new task-owned QA parent was tightened to 0700 before any private selection;
the builder now refuses nonprivate parents. Older preparation snapshots remain.

## Test output

- **47 new Python tests pass**, plus lint/format/strict types for the new module
  and tests. Cases cover source/target/ordering/size/protocol/forgery, three-call
  exhaustion, exact build file sets, refusal privacy and process cleanup.
- **33 compiled invented-database cases pass**, including fresh WAL-backed rows,
  main/WAL bytes unchanged during read, eight-row/combined text limits, recipient
  ambiguity, edits/deletions, unsupported latest text, missing schema, cancellation
  and deadline before open. No real store, model call or permission was used.
- Named helper manifest/symbol audit passes; four forbidden command-line modes
  refuse. There is no AX/AppleScript/network/system-launch symbol or fixture DDL
  in the named binary.
- Full `make check` passes: **1,089 Python / 156 frontend / 969 contrast pairs**,
  lint/format/strict types, API/motion/privacy checks and production build/glass.
  Assistant coverage **1,785/1,951 = 91.5%**. All 32,665 historical artifact hashes
  verify preserved; fresh coverage is retained separately. No frontend change or new browser
  state was added; no new physical-phone or native reliability claim is made.

## Screenshots

None. The private address/setup window and actual Messages data are not captured.
Existing synthetic app-opening UI evidence is retained separately.

## Required manual setup and next steps

The exact app is in the task's private `assistant-messages-store-20261109/build-07`
folder. Jake must enter his own exact address in its local setup window, save,
close it and manually add/enable **only Aether Messages Reader** under Full Disk
Access. Do not grant Codex/Terminal/Python/the server access. A broad-parent
requirement stops the scope. The assistant must receive confirmation before the
first native operation; private selection-file existence alone is not consent.

Then run the already-approved three-phase operator: resolve → read → manual
revocation and fresh refusal, stopping on first unexpected failure. Keep raw
records outside Git/tools/model context and publish counts/statuses only. Freeze
unused requests after a failure; no retries in this ledger. Future draft/model
integration, exact sends, main merge and live deployment are separate work.
