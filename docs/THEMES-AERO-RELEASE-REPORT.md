# Eight-theme release report — 24 October 2026

## Summary

Jake clarified that Claude UI review follows integration. PR #11 merged as
`326acbaabbf113c1d341c79f6be4496b4bd61cc4`, incorporating the seven-theme history
from #10. All eight themes, including Aero, are now live in Aether. The paired
server/web update preserves the reference-aware backend, worker and current data.
Claude can review the integrated UI; physical iPhone acceptance is still pending.

## Done-when checklist

| Item | Status | Evidence under `artifacts/themes/release-20261024/` |
|---|---|---|
| Release authorization and guarded main merge | Pass | AGENTS amendment; exact expected head `6764f9c0`, merge `326acbaa` |
| Merged payload equals qualified product source | Pass | 677 hashes in `release-source.json`, `verification.json` |
| Release build within existing budget | Pass | 252,235/256,000 gzip JS bytes; 476 static hashes |
| User work idle; no task cancelled | Pass | `dry-run.json`, `preflight.json`; all six background counts zero, chat list empty and native lock free |
| Fresh private production bundle | Pass | 2,200 files, manifest reverified; raw data stays private |
| Exact installed server/static/shared and unchanged worker | Pass | 602 installed files, four worker files; `publication.json` |
| Rows and retained inputs preserved | Pass | 1,806 rows across 57 tables and 126 non-DB files, compared while stopped |
| Schema, integrity and foreign keys | Pass | Schema remains 14; integrity/FKs pass after restart |
| Service, route and protected runtime/configuration | Pass | Original plist/route hashes and runtime/selector checks; same bind/port/label |
| Local and normally verified HTTPS | Pass | Health, editing capability, exact index/SW/theme-init/icon/manifest hashes |
| Actual installed assets in Chromium/WebKit | Pass with synthetic API | `installed-ui.json`; all eight choices, reload, scene, typing, Tools and Workflows |
| Real iPhone / icon / GPU feel | Pending | Requested from Jake; browser device profile is not a physical phone |
| Claude UI evaluation | Next | After integration, as requested |

## Changed files

- Product payload: the already tested eight-theme source from PR #11. The only
  backend source change is `server/app/db/settings.py`, which accepts the theme
  preferences. The compiled UI and palette assets ship with it. Dependencies,
  migrations, image worker, prompts and sampling behavior are unchanged.
- Operational code: `publish_themes.py` reuses the exercised PE1 helpers and
  private bundle preparer; `verify_release.py` performs read-only checks.
- Browser observer: `installed-ui.mjs` loads real HTTPS assets while intercepting
  every API request with invented settings/models/data. Preference saves in that
  observer are synthetic; it does not mutate real preferences or send a prompt.
- Docs: release authorization/plan, this H4 report and current review entry point.

## Deviations and release boundaries

The prior local-only stop is superseded by Jake's clarification. Claude UI review
is after integration. The 778 Python /151 frontend /969 token-pair and complete
892-browser-pass gates remain the tested qualification; no original assertion,
threshold, timeout or skip changed for this release. The four skips are historical.

Generic `make deploy` remains blocked for schema 14/photo-reference payloads.
Publication follows `PHOTO-EDITING-RELEASE-RUNBOOK.md`, with the existing
reference-aware backend/worker and private current-data protection. No interpreter,
dependency resolution, worker reinstall, model download/load/unload, inference or
unattended workflow was needed. No legacy data was modified.

## Runtime observations

The service was idle before shutdown. Publication used the existing
`dev.agenticrag.workbench` plist byte-for-byte, on `127.0.0.1:8787`, with the
unchanged Tailscale route. Observed downtime was **4.127 seconds**. Ollama remains
**0.35.0**. The image worker still reports generation and editing availability.

The fresh production recovery bundle is private at
`~/.local/share/workbench/releases/themes-20261024/bundle`. Its manifest verifies
2,200 files. It contains real application data and must stay outside Git. The
original code workspace remains on `8f38ef7b`; the supplied documents/patch and
qualified seven-theme branch `c7758120` remain unchanged. The original source,
failed trials and earlier evidence have not been replaced or regraded.

## Test output

- Reused qualified source: **778 Python /151 frontend**, **969 token pairs**,
  lint/types/coverage/API/motion/privacy pass. Only release docs/controller and
  evidence were added after qualification; all 677 inventoried files match.
- Complete pre-release browser invocation: **892 passed, four existing skips,
  zero failures** in Chromium/WebKit (1.4 h). No need to repeat it for docs alone.
- Build: **252,235 gzip bytes**, below 256,000; exact 476-file static manifest.
- Actual installed HTTPS observer: **two engines pass**, zero page errors or
  failed loaded assets. All eight palettes can be selected through Settings;
  Aero reloads, nine bubbles/scene appear, typing and Send availability work,
  Tools offers Model default, normal/reduced motion works, and Workflows opens.
- The observer made **zero real API mutations and zero model calls**. Service
  workers are blocked in its own browser contexts to guarantee interception.
  This is not physical PWA/keyboard/share/icon/GPU acceptance or a real chat send.
- Post-publication read-only verification: installed app/source/worker/bundle,
  schema/FKs, preferences shape, original inputs and service/route all pass.

The new publisher's dry run passed before merge. The pre-commit whitespace gate
first found trailing whitespace in Vite's build log. Its raw bytes and hashes
are preserved privately; only log formatting was normalized before committing.
No publication or product retry was caused by that formatting correction.

## Screenshots

Four installed-asset captures use invented data only:
`appearance-1440-chromium-synthetic.png`,
`appearance-390-webkit-synthetic.png`,
`new-chat-1440-chromium-synthetic.png`, and
`new-chat-390-webkit-synthetic.png`. Codex inspected the phone-profile Aero
new-chat capture and found no clipped composer or horizontal overflow. No real
photo, transcript, recording or filename appears in these captures.

## Fallback

Keep the current schema-aware backend, image worker, selectors and **current
user data**. If UI rollback is needed, quiesce the same service and restore only
the verified previous static UI from `bundle/compatibility-app/server/app/static`.
Preserve the failed UI for diagnosis, restart the same label and recheck health.
Do not restore the pre-release database over newer messages or use a pre-PE1
backend that could treat an edit as plain generation. The private snapshot is
recovery evidence, not an automatic data rollback.

## Next review

Open the integrated theme lab at
<https://jakes-mac-mini.tailc4d343.ts.net/design?themes> or use Settings → Appearance
in normal Aether. Reload/update the Home Screen app first. Claude's design review
can now evaluate the integrated UI.

Jake has been asked to check Aero, typing/sending, Workflows and smoothness on the
real iPhone. That answer is pending. If Aero stutters, the reviewed fallback order
is sidebar blur first, then fewer bubbles. Saved icon behavior is unverified.
Historical VoiceOver limitations remain unresolved and excluded from this work.
Recording-folder NS0 remains a separate proposal, with no watcher or native run
started by this theme release.
