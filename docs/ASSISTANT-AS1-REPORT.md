# AS1 preparation report

4 November 2026 · `codex/assistant-as1` · native qualification remains open

## Summary

Prepared a fixed, locally signed Swift helper and strict one-shot transport for
the first real Mac preflight. Jake selected his conversation with himself.
The built helper exposes permission/open/role-structure operations only, with
no message text, screenshot or input API. Offline paths and synthetic process
tests pass. No native job has run; AS1 is not qualified by these tests.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Named bridge, app allowlist, permission identity and bounded native scope | Prepared for review | `ASSISTANT-AS1-PLAN.md`; exact Messages/Notes Info.plist metadata |
| Build without packages, downloads, app launch or permission prompt | Pass | `build-03.txt`, `build-manifest.json`, `signature.txt`; existing Swift toolchain |
| Compiled fixture redaction, caps and private-file validation | Pass | 16 checks in `swift-offline.txt`; no `--native-job` execution |
| Strict receipts, sealed build, durable eight-request budget, cancellation/deadline ownership | Pass with fake processes | `focused-final.txt`: 71 cases, including 35 new probe cases |
| Full application checks | Running | `make-check.txt` |
| Existing AS0 source and production preserved | Initial pass; final pending | 644/646 unchanged file inventories in `preservation-before.json` |
| Actual helper permission identity and real app opening/observation | **Not run** | Requires AS1-A's concrete live scope approval |
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
window could collect other conversations. The structure preflight will establish
the selected-pane boundary before a separately reviewed reader. It does not
establish a recipient or message identity. AS0's required capture geometry also
needs a genuine text-only representation before native observation integration;
do not invent screenshot dimensions to satisfy that contract.

## Runtime observations

Installed public metadata reports macOS 27.0 and bundle IDs
`com.apple.MobileSMS` / `com.apple.Notes` at their fixed system application paths.
Reading those Info.plist files did not open or inspect either app.
The existing compiler built and locally ad-hoc-signed the helper. Only manifest,
invented tree and private test-file validation paths were executed. No app/AX
session, desktop capture, permission prompt, Messages read/send or model call
occurred. No user data was used for fixtures.

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
- Full `make check` is running against the frozen five-file new-source inventory.
- No browser/UI wiring changed. AS0's retained 922 browser passes/four skips
  remain the unchanged baseline, not a new AS1 browser/native pass. Preparation
  is not a release or completed AS1 report; live qualification and release QA
  remain ahead.

## Screenshots

None: this stage deliberately collects no real screen or private app content.
The previous fake AS0 design screenshots remain unchanged.

## Open questions for Jake / native review gate

`ASSISTANT-FIRST-PLAN.md` AS1 requires agreement on the bridge, permission identity
and selected test conversation before execution. The concrete proposal is
**Aether Desktop Trial**, `dev.agenticrag.aether.desktop-trial`, exact sealed build
above, at most eight one-shot requests with no automatic retry. It checks access,
opens Messages/Notes and returns role structure only. Jake grants/revokes the
helper's Accessibility permission manually and selects his self-conversation and
a disposable Notes window. No text read, screenshot, typing, send, model call,
main merge or deployment is included. The full ordered scope and stop conditions
are in `ASSISTANT-AS1-PLAN.md`.
