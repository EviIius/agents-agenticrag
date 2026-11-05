# AS1 role-only preflight report

4–5 November 2026 · `codex/assistant-as1` · message reading and native chat integration remain open

## Summary

The original trial passed Messages and preserved Notes' modal-sheet refusal.
Both separately approved follow-up requests passed on the unchanged sealed build.
Messages/Notes returned 66/43 role-only nodes; revocation refused access with zero nodes.
Only this exact-build structure preflight is qualified; selected-text/chat integration remains open.
No text, screenshot, input, model call, merge or deployment occurred.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Named bridge, app allowlist, permission identity and bounded native scope | Approved; helper identity confirmed by Jake's supplied photo | `ASSISTANT-AS1-PLAN.md`; private photo kept outside repository |
| Build without packages, downloads, app launch or permission prompt | Pass | `build-03.txt`, `build-manifest.json`, `signature.txt`; existing Swift toolchain |
| Compiled fixture redaction, caps and private-file validation | Pass | 16 checks in `swift-offline.txt`; no `--native-job` execution |
| Strict receipts, sealed build, durable eight-request budget, cancellation/deadline ownership | Pass with fake processes | `focused-final.txt`: 71 cases, including 35 new probe cases |
| Full application checks | Pass | `make-check.txt`: 856 Python, 156 frontend, 969 contrast pairs |
| Existing source, history and production preserved | Pass after completed follow-up | `verification-after-followup.json`; five new / 644 AS0 / 646 installed files and 32,515 historical artifacts unchanged |
| Native permission check and access request | Expected initial refusal; recheck passes after manual grant | `native-progress.json`: three permission requests total |
| Real Messages opening | Pass | Fourth request verifies fixed installed application identity |
| Real Messages structure observation | Pass for role-only preflight | Fifth request: 66 nodes, no truncation, 0.161 s |
| Real Notes opening | Pass | Sixth request: expected application identity, 0.346 s |
| Original Notes structure observation | **Failed host acceptance; retained** | Seventh original request: `AXSheet` root, 11 nodes; `notes-refusal-analysis.json` |
| Follow-up Notes structure observation | Pass for role-only preflight | First AS1-A2 request: 43 nodes, no truncation, 0.121 s; `native-followup-progress.json` |
| Permission revocation refusal | Pass | Second AS1-A2 request: fresh helper refuses, zero target/nodes, 0.094 s |
| AS1-A2 follow-up | Two approved requests complete; no further native scope | Original eighth request remains unused; follow-up ledger exhausted |
| Selected conversation text, recipient and latest-message identity | **Not implemented/qualified** | AS1-B follows a reviewed structure map; no guessed parser |
| Native driver integrated with chat or model | **Not implemented/qualified** | Existing fake-only constructor remains unchanged |

## Changed files

- `tools/mac_desktop/Probe.swift`: fixed helper; separate manifest/fixture/file
  validation paths; native app opening and capped role-only Accessibility reader.
- `server/app/assistant/mac_probe.py`: strict requests/receipts, file/build checks,
  durable request budget, fixed Launch Services invocation and supervised Stop.
- `scripts/build_desktop_probe.py`, `scripts/check_desktop_probe.py`: isolated
  local build/signature verification and reproducible offline compiled checks.
- `server/tests/test_mac_probe.py`: 35 synthetic protocol, identity, privacy,
  budget, cancellation/deadline and source-boundary tests.
- Scope/report/AGENTS notes and `artifacts/assistant-as1-20261104/`.

## Deviations from SPEC.md

The recorded AS1 preparation amendment permits this isolated helper source and
offline build. No production API, UI, schema, prompt, provider, sampling, model
selection, package or service wiring changes. The helper is a preflight tool,
not a second agent or a qualified native `DesktopDriver`.

AS1-A uses role structure before text: inspecting every label in a Messages
window could collect other conversations. The structure preflight informs the
selected-pane design before a separately reviewed reader. It does not qualify
that boundary or establish a recipient or message identity. AS0's required capture geometry also
needs a genuine text-only representation before native observation integration;
do not invent screenshot dimensions to satisfy that contract.

## Runtime observations

Installed public metadata reports macOS 27.0 and bundle IDs
`com.apple.MobileSMS` / `com.apple.Notes` at their fixed system application paths.
Reading those Info.plist files did not open or inspect either app.
The existing compiler built and locally ad-hoc-signed the helper. Only manifest,
invented tree and private test-file validation paths were executed during the
offline checks. After the full regression check passed, seven one-shot native jobs
ran through Launch Services. The first checked trust without prompting; the
second requested permission. Both returned `permission_required`. Jake then
supplied a photo showing Aether Desktop Trial enabled under its own name. The
third request confirmed trust; the fourth opened and verified the expected
Messages application. They completed in 0.085 and 0.089 seconds respectively.
Jake then confirmed both test windows were ready. Messages structure returned
66 nodes without truncation in 0.161 seconds. Notes opening passed in 0.346
seconds, but its structure request failed host acceptance in 0.105 seconds.
The helper's saved response contained 11 nodes rooted at `AXSheet`, without
truncation. Offline validation reproduces the `Expected focused window` guard
failure: the host requires `AXWindow`. The sheet's purpose/content is unknown
because no text attributes were read. The refusal does not establish that Notes
cannot be supported; it does mean this trial did not qualify the second app.

No automatic retry, original eighth request, guard relaxation or source change
followed that refusal.
No message read/send, desktop capture or model call has occurred. Jake's
supplied photo was not copied into repo evidence. Raw role-only native receipts
remain private; committed evidence contains statuses, counts and a response hash.
No user data was used for fixtures.

On 5 November, Jake confirmed the ordinary Notes editor ready for the separately
approved AS1-A2 follow-up. Its first one-shot request accepted a normal window
with 43 nodes, without truncation, in 0.121 seconds. Jake then confirmed the
helper manually disabled. The second request, in a fresh helper process, returned
`permission_required`, no target and zero nodes in 0.094 seconds. No prompt or
re-enable followed. Both follow-up slots are consumed; no further native request
is authorized. The original refusal/ledger remain unchanged. No helper/core
rebuild, guard change, text read or other attribute collection occurred.

The exact build's manifest SHA-256 is
`2b42d2f56b37226e5b26ecb6009957422fd8faea9eaf7635744c715c2c99d4ef`;
the executable SHA-256 is
`ce63bce2d8431415ffcaa006ec2733e4a1171580a093b7af14dc3ef7950ff7c7`.
Ad-hoc signing identifies this exact build; permission survival after a rebuild
is not established. Native qualification must stop if System Settings attributes
the grant to Codex/Terminal/Python instead of Aether Desktop Trial.

## Test output

- **16 compiled offline checks pass**, including dropping synthetic text/title/
  identifier fields, masking custom role strings, depth/width/count limits,
  invalid JSON, oversized input, unknown operation, expired/future job, file
  permissions and symlink rejection.
- **71 focused Python cases pass**: 35 new probe tests plus AS0's 36 controller
  tests. Actual Mac-process cancellation remains a native qualification task;
  the synthetic tests prove transport control flow only.
- Focused lint, formatting and mypy pass. Initial formatting and test-double type
  errors are retained in the initial logs; no native trial failure is concealed.
- Offline replay of the saved Notes response reproduces the root-role refusal
  without a new native call; `notes-refusal-analysis.json` records the cause and
  response hash. The five frozen implementation files and exact sealed helper
  remain unchanged. This is a refused modal sheet, not evidence of a permission,
  timing or local-model failure.
- AS1-A2's operator passes **five synthetic checks** for its two-request cap,
  phase order, first-failure stopping, initial permission refusal and unexpected
  revocation success. All use fake transports and temporary files, with zero
  native calls. Its exact source is retained as `followup-operator.py`, SHA-256
  `4fc4f2f4785fa8fb11f6c31487921e64a44cc4d03f3371c10310b07018d22bae`.
  The frozen five-file core and sealed app remain unchanged. AS1-A2 has consumed
  both approved native requests. The offline report's zero-call/pending fields
  describe preparation time; `native-followup-progress.json` records the actual
  successful Notes and revocation checks. No new inference or broad regression
  run was needed: the frozen implementation and UI/API wiring are unchanged.
- Full `make check` passes against the frozen five-file new-source inventory:
  **856 Python / 156 frontend tests**, 969 contrast pairs, lint/types/format,
  API/additive contract, motion/privacy checks and production build/glass guard.
  Assistant line coverage is **835/920 (90.8%)**; native branches are not claimed
  as live-tested by this coverage.
- All **32,515 historical tracked artifacts** verify unchanged. The fresh
  synthetic coverage output was archived privately before restoring its retained
  predecessor; `historical-artifact-preservation.json` records the archive hash.
  All five new source files, 644 AS0 source files and 646 installed public files
  match their inventories. Main, AS0, the separate design branch, launchd plist
  and service PID 77443 are unchanged. The fresh after-follow-up inventory and
  seal check confirm preservation; local and normally verified HTTPS health
  checks both return 200. See `verification-after-followup.json`.
- No browser/UI wiring changed. AS0's retained 922 browser passes/four skips
  remain the unchanged baseline, not a new AS1 browser/native pass. Preparation
  is not a release or completed AS1 report; live qualification and release QA
  remain ahead.

## Screenshots

No desktop screenshots were captured. Jake's permission photo stays outside
repo evidence. The previous fake AS0 design screenshots remain unchanged.

## Open questions for Jake / next checkpoint

Jake approved **Aether Desktop Trial**, `dev.agenticrag.aether.desktop-trial`,
the exact sealed build above, and at most eight one-shot requests with no retry.
Seven have run, with the first failure preserved. The original scope has stopped;
do not use its remaining request as a retry. The separately approved AS1-A2
follow-up completed both requests and verified refusal after manual revocation.
The helper remains disabled; do not re-enable or issue another native request.

Jake authorized **AS1-A2** by saying “Continue” after the concrete proposal in
`ASSISTANT-AS1-PLAN.md`: one Notes structure request after Jake
selects the normal disposable-note editor, then one refusal check after he
manually disables the helper. Same sealed build, at most two new requests, no
retry/rebuild/extra open or permission prompt, and all existing privacy limits.
The original failed trial remains retained. Jake confirmed both manual setup
steps; both follow-up gates passed. No text read, screenshot, typing, send, model
call, main merge or deployment occurred. No additional OS setup is pending for
this scope.

Next is AS1-B: review a bounded selected-conversation reader and its text-only
observation contract before implementation/native text access. It must establish
the actual direct recipient and message identity from explicit app evidence,
limit collection to the selected self-thread (at most eight messages), and
refuse ambiguous panes, groups or missing identity. A self-thread with no incoming
message must report that state explicitly. No sidebar-wide text dump or Messages
database access. Native chat integration and AS2 model tasks remain later gates;
these successful role-only probes do not prove model-driven computer use.
