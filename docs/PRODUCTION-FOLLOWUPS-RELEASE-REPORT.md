# Production follow-ups release — 18 October 2026

## Summary

Jake accepted the completed checkpoint and asked to continue to release.
PR #5 is merged as `b41ec3550bb83ab92c0710d39295dae0f27d92dd` and the two
repairs are live: manual titles survive the first text send and Workflows home
no longer advertises its disabled Search block. The service became healthy in
2.148 seconds. Exact installed hashes, private fallback, copied-data rehearsals
and installed HTTPS UI checks pass. Jake confirmed the physical iPhone title,
Workflows Canvas/Outline and workflow-run checks on 19 October.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Review/release authorization | Accepted | Jake's “Continue” after the completed report and proposed release; AGENTS.md |
| Exact tested source | Pass | All 551 frozen source/test/config hashes match |
| Reproduced build | Pass | All 425 hashes match; 254,973 initial gzip bytes / unchanged 256,000-byte budget |
| Full regression gates | Pass, exact-source reuse | 726 Python / 126 frontend / 110 contrast pairs; 721 browser passes, three existing skips, zero failures |
| Private full fallback | Pass | App/data/plist snapshot and consistent SQLite backup |
| Copied-data startup and row preservation | Pass | Candidate and previous schema-13 startup; all 55 table projections unchanged; child sockets disabled |
| Merge and publication | Pass | PR #5 merged; all 551 frozen hashes match merged main; healthy in 2.148 s |
| Installed source and data | Pass | 114 server / 425 static hashes; schema 13, integrity/foreign-key checks; all 55 pre-existing table projections preserved before bootstrap |
| Service, route and controls | Pass | Exact plist, one worker, 127.0.0.1:8787, unchanged Tailscale route, environments and transcription/image-worker controls |
| Installed HTTPS UI | Pass, synthetic API fixtures | Desktop Chromium and iPhone-profile WebKit; composer, Tools, attachments and corrected Workflows home; no page errors, overflow or native requests |
| Physical phone | User-confirmed pass, 19 October | Title stays; Workflows Canvas/Outline opens; workflow runs. `artifacts/production-followups/phone-check-20261019.json` |

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

The previous service PID was 65114; the new PID is 15411. Restart to healthy
was 2.148 seconds, including publication while stopped. Local and normally
certificate-verified Tailscale HTTPS health, workflow definitions/templates and
image-status checks pass. The installed HTML and service-worker entry hashes
match the tested build; production `/design` remains disabled (404).

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
- Installed verification: 114 server and 425 current-build static hashes;
  unchanged plist, route, protected environments and worker controls; SQLite
  integrity and foreign-key checks pass. Old hashed assets remain for open clients.
- Actual installed HTTPS UI: Chromium 1440 and WebKit/iPhone 13 profile 390 pass
  the prepared observer with 39/38 intercepted synthetic API requests, zero
  page errors and zero native requests. Service workers are blocked for API
  interception; no additional complete PWA suite or physical-phone pass is claimed.
- Final privacy and source/document whitespace checks pass. All stopped native
  experiment ledgers and their retained branch remain unchanged.

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

The requested physical phone check is closed by Jake's 19 October confirmation.
Preserve the historical VoiceOver limitation without adding it to the requested
work list.

Photo-reference editing is the next separate proposal in
`PHOTO-EDITING-NEXT-CHECKPOINT.md`. Its native trial has not run and requires
approval of its concrete bounded scope. Failed agent experiments stay closed.

## Physical phone closeout — 19 October 2026

Jake reported that the chosen title stays in the requested first-send/reload
check. He also confirmed Workflows opens in both Canvas and Outline views and
that running the workflow works. These are user-reported physical iPhone
results, distinct from Codex's synthetic browser observations above.

Close the production follow-ups release review. No new application change,
deployment, automated suite invocation or native trial accompanies this record.
No phone timing, specific workflow image/citation result or VoiceOver pass is
inferred. The frozen publication evidence remains unchanged; the confirmation
is retained separately in `artifacts/production-followups/phone-check-20261019.json`.
