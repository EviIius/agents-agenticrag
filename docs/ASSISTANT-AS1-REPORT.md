# AS1-A stopped preflight report

4 November 2026 · `codex/assistant-as1` · native qualification remains open

## Summary

Seven approved native requests ran after the full regression check passed.
Permission and both app openings passed; Messages returned 66 role-only nodes.
Notes exposed a modal `AXSheet`, refused by the host's normal-window guard.
The trial stopped at that first failure; revocation refusal is untested.
No text, screenshot, input or model call occurred; AS1 remains unqualified.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Named bridge, app allowlist, permission identity and bounded native scope | Approved; helper identity confirmed by Jake's supplied photo | `ASSISTANT-AS1-PLAN.md`; private photo kept outside repository |
| Build without packages, downloads, app launch or permission prompt | Pass | `build-03.txt`, `build-manifest.json`, `signature.txt`; existing Swift toolchain |
| Compiled fixture redaction, caps and private-file validation | Pass | 16 checks in `swift-offline.txt`; no `--native-job` execution |
| Strict receipts, sealed build, durable eight-request budget, cancellation/deadline ownership | Pass with fake processes | `focused-final.txt`: 71 cases, including 35 new probe cases |
| Full application checks | Pass | `make-check.txt`: 856 Python, 156 frontend, 969 contrast pairs |
| Existing source, history and production preserved | Pass after stopped trial | `verification-after-trial.json`; five new / 644 AS0 / 646 installed files and 32,515 historical artifacts unchanged |
| Native permission check and access request | Expected initial refusal; recheck passes after manual grant | `native-progress.json`: three permission requests total |
| Real Messages opening | Pass | Fourth request verifies fixed installed application identity |
| Real Messages structure observation | Pass for role-only preflight | Fifth request: 66 nodes, no truncation, 0.161 s |
| Real Notes opening | Pass | Sixth request: expected application identity, 0.346 s |
| Real Notes structure observation | **Failed host acceptance** | Seventh request: `AXSheet` root, 11 nodes; `notes-refusal-analysis.json` |
| Permission revocation refusal | **Not run** | First-failure stop; unused eighth request retained |
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

No native retry, eighth request, guard relaxation or source change followed.
No message read/send, desktop capture or model call has occurred. Jake's
supplied photo was not copied into repo evidence. Raw role-only native receipts
remain private; committed evidence contains statuses, counts and a response hash.
No user data was used for fixtures.

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
  and service PID 77443 are unchanged. Local and normally verified HTTPS health
  checks pass.
- No browser/UI wiring changed. AS0's retained 922 browser passes/four skips
  remain the unchanged baseline, not a new AS1 browser/native pass. Preparation
  is not a release or completed AS1 report; live qualification and release QA
  remain ahead.

## Screenshots

No desktop screenshots were captured. Jake's permission photo stays outside
repo evidence. The previous fake AS0 design screenshots remain unchanged.

## Open questions for Jake / proposed follow-up

Jake approved **Aether Desktop Trial**, `dev.agenticrag.aether.desktop-trial`,
the exact sealed build above, and at most eight one-shot requests with no retry.
Seven have run, with the first failure preserved. The original scope has stopped;
do not use its remaining request as a retry. The helper's permission has not been
revoked/checked by this trial yet. Jake may disable it manually at any time.

The concrete **AS1-A2** proposal in `ASSISTANT-AS1-PLAN.md` requires separate
approval under the first-failure rule: one Notes structure request after Jake
selects the normal disposable-note editor, then one refusal check after he
manually disables the helper. Same sealed build, at most two new requests, no
retry/rebuild/extra open or permission prompt, and all existing privacy limits.
The original failed trial remains retained. If the first request fails, stop
again. No text read, screenshot, typing, send, model call, main merge or deployment.

Even successful role-only probes leave the selected-message reader and native
chat integration open for AS1-B review; they do not establish recipient identity
or prove that a local model can reliably operate either app.
