# Production follow-ups release — 18 October 2026

## Summary

Jake accepted the completed checkpoint and asked to continue to release.
The two repairs preserve manual chat titles at the first text send and remove
the unavailable Search promise from Workflows home. The tested build reproduces
exactly. A full private fallback and both copied-data startup rehearsals pass.
Publication results will be recorded after merge and installed checks.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Review/release authorization | Accepted | Jake's “Continue” after the completed report and proposed release; AGENTS.md |
| Exact tested source | Pass | All 551 frozen source/test/config hashes match |
| Reproduced build | Pass | All 425 hashes match; 254,973 initial gzip bytes / unchanged 256,000-byte budget |
| Full regression gates | Pass, exact-source reuse | 726 Python / 126 frontend / 110 contrast pairs; 721 browser passes, three existing skips, zero failures |
| Private full fallback | Pass | App/data/plist snapshot and consistent SQLite backup |
| Copied-data startup and row preservation | Pass | Candidate and previous schema-13 startup; all 55 table projections unchanged; child sockets disabled |
| Merge and publication | Pending | Must match frozen source before publication |
| Installed source, service and live UI | Pending | Exact hashes, unchanged service/route/controls, HTTPS synthetic UI observer |
| Physical phone | Pending | No new phone acceptance or VoiceOver pass claimed |

Evidence: `artifacts/production-followups/release-20261018/`. The implementation,
original failures and completed suites remain in `PRODUCTION-FOLLOWUPS-REPORT.md`
and the parent artifact folder.

## Changed files

- **Application:** only the two already tested application files; no new
  application edits during release.
- **Release tooling:** adapt the prior image-memory-handoff controller to the
  current frozen manifests. Recheck source/build and controller identity before
  publication, and verify previous-app copied-data row preservation as well as
  candidate startup. Preserve the exact installed plist, environments and workers.
- **Observer:** fetch actual installed HTTPS assets while intercepting every
  API request with synthetic fixtures. Check composer, typing, Tools/Model default,
  long paste/undo, photo tray/viewer/removal, and corrected Workflows home wording.
- **Docs:** release authorization and this H4 report. No photo-edit implementation.

## Deviations from SPEC.md

Reuse completed full suites through exact source parity; reproduce and compare
the build separately. No extra full-suite invocation is claimed. Use the reviewed
full-fallback controller instead of the generic deploy command, which would
synchronize packages and touch transcription unnecessarily. Retain old hashed
assets for open clients. Same-schema rollback keeps accepted current data.

## Runtime observations

No native inference, model load/unload, new dependency, model/runtime update,
prompt/sampling/default change, schema migration or agent/Research restart.
Copied-data lifecycle runs have sockets disabled. The installed UI observer
uses synthetic intercepted API data and does not read or capture private chats,
recordings, photos, documents or filenames.

## Test output

- Completed `make check`: 726 Python / 126 frontend / 110 contrast pairs, all
  required coverage, lint, types, API, motion and privacy guards pass.
- Completed `make e2e`: 721 passed / three existing skips / zero failures in
  one complete invocation; no assertion, timeout or threshold weakened.
- Fresh `make build`: exact parity on 425 files; all 551 frozen source hashes
  still match. Existing Vite config-loader warning retained in raw output.
- Candidate and previous copied-data startup pass with no network access;
  all 55 pre-existing table projections preserved at unchanged schema 13.

## Screenshots

Reuse the checkpoint's retained synthetic desktop/phone captures, including
separate focused and full-suite title images. The installed HTTPS observer takes
no screenshot or video; its source, hashes and assertion results are retained.
Browser device profiles are not a physical-phone result.

## Rollback

Private full fallback:
`~/.local/share/workbench/qa/production-followups-release-20261019T023801Z`.
The UTC directory date is 19 October; this release began on 18 October locally.
The controller's rollback restores the previous app/plist and checks health,
keeping current live data on schema 13. Whole-data restoration is reserved for
a separately assessed recovery; it must not discard accepted messages or files.
Source fallback tag: `checkpoint/pre-production-followups-2026-10-18`.

## Open questions for Jake

After publication, reopen Aether and confirm Workflows opens and a title chosen
before the first message remains after sending and reloading. Preserve the
historical VoiceOver limitation without adding it to the requested work list.

Photo-reference editing is the next separate proposal in
`PHOTO-EDITING-NEXT-CHECKPOINT.md`. Its native trial has not run and requires
approval of its concrete bounded scope. Failed agent experiments stay closed.
