# Deferred polish report — 7–8 October 2026

## Summary

Research is shelved at Jake’s request; its failed experiments and original gates
remain preserved on main and checkpoint `7737046`. This production polish starts
from accepted 7B (`d74067e`), with no Research module or new model calls deployed.
Recording menus now account for safe areas and visible viewport height. The picker
has capability filters, explicit selection and visible load/eject actions.
VoiceOver is excluded from current work; historical failure reports are retained.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Research stopped and history preserved | Pass | `RESEARCH-SHELVED.md`, existing main merge `a55041f`; no running Research eval process |
| VoiceOver removed from current backlog | Pass | `DEFERRED-FIXES.md`, AGENTS/SPEC amendment and QA G-5; no pass invented |
| Recording menu safe edges and scrolling | Pass | `deferred-polish.spec.ts`: portrait 390×844, landscape 844×390, keyboard-sized 390×360, light/dark, first/last access and dismissal |
| Explain missing motion | Diagnosed | Installed preference is `always`; it intentionally disables motion. Appearance now explains effective status and how to follow the device preference. No saved preference was changed. |
| Phone sidebar entrance/exit and reduced modes | Pass | New sidebar event checks; existing phone/overlay/conversation suites |
| Preserve desktop performance fallback | Pass by source review | Prior `PHASE-4-REPORT.md`: width animation exceeded WebKit’s 18 ms gate (25 ms). Width snap retained; labels and phone sheets retain CSS motion. |
| Picker clarity and genuine capabilities | Pass | All/Loaded/Images/Reasoning/Tools; explicit Selected text distinct from residency; selected/loaded rows first; IDs remain searchable; load/context tests preserved |
| Types, lint, units, contrast, frozen contracts | Pass | 298 Python tests, 36 web unit tests, 74 contrast pairs; API/prompt/row/payload guards |
| Full browser regression | Pass: 457 passed, 3 existing skips | Final run uses fake app on test-only 18787; installed app stays on 127.0.0.1:8787 |
| Production update and fallback | Pass | `deployment.json`: frontend-only publication, local/Tailscale health, unchanged 84 public runtime files, service identity and route; private static/database fallback preserved |
| Physical iPhone observations | Not claimed | Synthetic Chromium/WebKit evidence is not a physical phone test. Prior Jake acceptance remains historical. |

## Changed files

- **Web:** safe-area padding and menu height/scrolling; picker filters, explicit
  selection, selected/loaded ordering and always-visible residency actions;
  a scrollable phone picker with sticky search and a compact close button when
  keyboard-sized space would otherwise collapse its model list; Appearance
  effective-motion text; the full cleanup menu in `/design`.
- **Tests/tooling:** new `deferred-polish.spec.ts`; a test-only fake app port shared
  by Playwright, the opt-in Vite test proxy, direct test API/PWA URLs and fake-server
  RSS measurements. Production/development defaults remain 8787.
- **Server:** browser-fixture docstring only. No app, migration, prompt, provider,
  search, Library or engine changes.
- **Docs:** shelved Research status, revised backlog/QA and this H4 report.

## Deviations from SPEC.md

The latest user amendment excludes VoiceOver from current work. Existing ordinary
labels, focus and keyboard behavior remain intact. No accessibility pass is inferred.

The fake browser app uses test-only 18787 so it cannot replace or write to the live
8787 service. Vite uses it only when Playwright supplies `WORKBENCH_E2E=1`.
Production bind, port, launchd label and Tailscale route are unchanged. This changes
where browser tests run, not the application’s deployment configuration.

## Runtime observations

No new models, downloads, runtime upgrades, dependencies, prompts or actual model
inference were used for this polish. Tool/image/reasoning filters depend on the
existing runtime metadata, never tag-name guesses or claimed Research qualification.

The installed motion preference is Always. That explains disabled motion without
establishing the state of every earlier phone session. No physical-device repair
or VoiceOver result is claimed.

The initial diagnostic harness used 8787 and was interrupted after test defects
were identified. Its restoration check initially saw a detached fake server;
process inspection established this, the owned fake processes were stopped, and
the actual installed launchd listener was confirmed with HTTP 200 locally and over
Tailscale. The final harness isolates test traffic and needs no service pause.
See `service-during-tests.json`; live data was never used as test data.

## Test output

Final `make check` passes: 298 Python tests, 36 web unit tests, types, lint,
formatting, 74 contrast pairs and frozen contract/privacy/motion guards. The
targeted polish suite passes all 26 Chromium/WebKit checks. The final complete
`make e2e` run passes: **457 passed, 3 existing skips (38.1 minutes)**. The skips
remain the WebKit long-answer case, foundation screenshot case and offline PWA
navigation case; they are not counted as passes. See `verification.json` and
`e2e.txt`. Initial compressed JavaScript is 240,526 bytes
against the 256,000-byte budget, a 707-byte increase from accepted 7B against the
8,192-byte growth limit. See `bundle.json`.

The initial diagnostic failures were new test
mistakes: a focused tooltip consumes the first Escape before the sidebar, and
cmdk’s search control is a combobox rather than a textbox. The sidebar animation
check now uses the actual close button. A subsequent whole-suite run was stopped
before completion when a separate synthetic short-screen check showed the picker
list collapsing to zero height. The compact layout was corrected and the suite
restarted; `browser-before-short-picker-fix.txt` retains 205 passed, one
interrupted transcription wait and 250 not run. It is an incomplete run, not
acceptance evidence. Text logs normalize trailing whitespace only. Existing assertions, thresholds, timeouts
and skips are unchanged. Retain `diagnostic-browser.txt` as an unsuccessful run.

## Publication and fallback

The frontend from source checkpoint `85477f5` was published on 8 October 2026.
New assets were staged first, old hashed assets retained for existing clients,
and the index/service worker published last. The server was not restarted.
All 84 checked public server/shared files still match accepted `d74067e`;
production `/design` returns 404. Local and Tailscale `/api/health` return
HTTP 200 with `ok: true`; listener, launchd identity and Tailscale route match.

The first attempt rolled back after framework Python rejected the Tailscale
certificate chain. The restored service-worker hash was verified; the retry
used macOS curl with certificate verification enabled and passed. No certificate
verification was bypassed. See `publication-first-attempt.json`.

The private fallback is:
`~/.local/share/workbench/data/backups/polish-static-20261008T045106Z/`.
It contains the previous static files and a consistent SQLite backup, with no
audio copied. To undo only this frontend publication, restore its `static/`
into `~/.local/share/workbench/app/server/app/static/` using `rsync -a --delete`.
Do not restore the database for a frontend rollback; that could replace newer
chat/output data.

Live desktop checks confirmed the filters, explicit Selected label, Loaded
filter toggle and effective-motion explanation. The saved Always preference
was not changed. Targeted DOM checks avoided private content; owned tabs were
closed. See `live-browser.json`. No physical iPhone pass is claimed.

## Test-diff ledger

| Existing file | Change | Why | Behavior still asserted? |
|---|---|---|---|
| `performance.spec.ts` | Synthetic seeding host only | Isolated fake app | Yes; 300 messages, render/scroll budgets unchanged |
| `conversation-motion.spec.ts` | Synthetic seeding host only | Isolated fake app | Yes; original motion/export/performance assertions unchanged |
| `handoff.spec.ts` | Synthetic seeding host only | Isolated fake app | Yes; handoff assertions unchanged |
| `refinement.spec.ts` | Synthetic seeding host only | Isolated fake app | Yes; refinement assertions unchanged |
| `library.spec.ts` | RSS listener port only | Measure the fake process rather than production | Yes; upload sizes, sampling and memory threshold unchanged |
| `documents.spec.ts` | RSS listener port only | Same isolation | Yes; upload sizes, sampling and memory threshold unchanged |
| `pwa.spec.ts` | Built-app origin only | PWA checks against isolated fake data | Yes; installation, caches, update and offline assertions unchanged |

## Screenshots

Synthetic screenshots live under `artifacts/deferred-polish/`:

- `recording-menu-{390x844,844x390,390x360}-{light,dark}-{chromium,webkit}-fake.png`
- `motion-{normal,always,system}-390-{chromium,webkit}-fake.png`
- `picker-{390,1440}-{chromium,webkit}-fake.png`
- `picker-short-{320,390}x360-{chromium,webkit}-fake.png`

The recording menu at 390×360, the compact picker at 320×360, the phone picker
and Always-motion status were visually reviewed using synthetic WebKit images.
No real recording/document name, transcript or user screenshot is retained.

## Open questions for Jake / next steps

1. Reload the updated Home Screen app when its update prompt appears. If you want
   animations, choose **Appearance → Reduce motion → Follow system**; iOS may
   still reduce motion according to its own setting. Confirm the recording menu
   scrolls to its first and last actions on the physical phone.
2. Use the stable chat, Web search, transcription and Library features and report
   concrete failures. Keep Research shelved rather than advancing to 8B.
3. When desired, separately approve one named candidate from
   `MODEL-OPTIONS-AND-PICKER.md` for matched everyday chat/search/Library testing.
   Keep the current model as a fallback and do not download the entire shortlist.

## Saved checkpoint

Source implementation: `85477f5` on `codex/deferred-polish`. The final source,
reports and evidence are preserved by local tag
`atelier-7b-polish-2026-10-08`. Main remains at the existing Research-history
merge; this polish has not been merged or pushed.
