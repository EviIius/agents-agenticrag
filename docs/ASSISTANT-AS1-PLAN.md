# AS1: qualify a real Mac observation bridge

4 November 2026 · `codex/assistant-as1` · starts from AS0 `3e456010`

Jake continued after the AS0 report and selected **a conversation with himself**.
This accepts the technical AS0 checkpoint, without inventing a UI/phone review.
AS0's driver and model behavior remain scripted until separately qualified.

## Implementation choice

Prepare **Aether Desktop Trial**, a small fixed Swift program, built with the
installed Command Line Tools and Apple's AppKit/ApplicationServices frameworks.
There is no Cua/framework/package installation, runtime download or second agent.
Its trial bundle identifier is `dev.agenticrag.aether.desktop-trial`.

Use a version-frozen, locally ad-hoc-signed app bundle in the private QA directory,
launched through Launch Services for a reviewed trial. Do not grant Accessibility
to Python, Terminal or Codex as a substitute. The actual responsible permission
identity must be checked in System Settings; a bundle identifier alone does not
prove that identity. Apple's [designated-requirement documentation](https://developer.apple.com/documentation/technotes/tn3127-inside-code-signing-requirements)
explains that ad-hoc identity is tied to that exact code version. Rebuilding
invalidates this trial qualification; cross-version permission survival remains
future installation/release work. No certificate/keychain changes are needed.

The host controls two exact installed app paths and verifies their bundle IDs:

| Trial name | System application | Observed bundle ID |
| --- | --- | --- |
| Messages | `/System/Applications/Messages.app` | `com.apple.MobileSMS` |
| Notes | `/System/Applications/Notes.app` | `com.apple.Notes` |

Those IDs were read from public installed Info.plist files; neither app was
launched or inspected. Arbitrary PIDs, application paths, scripts and URLs are
not accepted as requests.

## Why a structure preflight comes first

Messages' current Accessibility tree is unqualified. Dumping all labels/values
from its window could collect other conversations from the sidebar. The first
native probe therefore returns **standard role names, numeric paths and child counts
only** for the focused window. It never requests titles, descriptions,
identifiers, text values, screenshots, contacts or Messages databases.

This stage does not identify a recipient or read a message. AS1 remains open
until a reviewed selected-conversation adapter can read at most eight text
messages and establish the direct recipient and latest incoming message. If
Accessibility cannot provide that evidence, refuse qualification and propose a
specific alternative; never guess from a display name or use Full Disk Access.

The preflight receipt is deliberately not an AS0 `DesktopObservation`: role
structure cannot establish recipient/message identity. AS0 also currently requires
capture geometry even for a text observation. Before native-driver integration,
allow a genuinely text-only observation without invented screenshot dimensions,
and reject coordinate actions without qualified capture metadata. Keep AS0's
fake-only constructor and native-action refusal until the actual observation
adapter is qualified. A structure digest is not a conversation identity.

## AS1-A approved native scope

Jake approved this bounded trial on 4 November after reviewing the sealed helper
and permission scope on draft PR #16. The full regression check passed before
the first request. Manual confirmation of the actual permission identity remains
required before app inspection; approval does not substitute for that observation.

At most **eight one-shot helper requests**, each with a 15-second host deadline
and shorter bounded Accessibility traversal. No automatic retry. Stop on an
unexpected target, permission identity, timeout, protocol/privacy failure or
unexplained result. A denied permission check is an expected negative control,
not authorization to bypass it.

1. Check the helper's Accessibility trust without prompting.
2. If needed, request access under the helper's own identity. Jake grants or
   denies it manually; no permission database or global reset is touched.
3. Recheck after the manual decision.
4. Open Messages using the fixed path; verify the returned running identity.
5. Inspect only the focused Messages window's structure. Jake selects his own
   test conversation first. Opening a thread may mark messages as read.
6. Open Notes using the same bridge and identity checks.
7. Inspect its focused window's structure, with a disposable test note selected.
8. After Jake revokes access, verify a fresh helper process refuses observation.

If access was already granted, unused requests are not spent on extra probes.
Cancellation is tested in the offline transport first and checked during the
approved trial where meaningful. Opening an app cannot be undone by Stop; an
uncertain open outcome is reported without automatic replay. No send, typing,
clicking, key presses, scrolling, screenshot or model request exists in this
helper. No private message/body/recipient is collected in AS1-A.

Apple documents [trust checks and optional prompting](https://developer.apple.com/documentation/applicationservices/1459186-axisprocesstrustedwithoptions),
[per-element messaging timeouts](https://developer.apple.com/documentation/applicationservices/1459345-axuielementsetmessagingtimeout),
and [asynchronous app opening](https://developer.apple.com/documentation/appkit/nsworkspace/openapplication(at:configuration:completionhandler:)).
These establish API contracts, not successful local qualification.

## Protocol and isolation

- No HTTP listener or background service. One private request/response directory
  per operation, mode 0700, with files mode 0600 and a single-use request ID.
- Strict operations: permission, request_access, open, structure. An app is
  required only for open/structure. Unknown fields/operations are rejected.
- Pin the built bundle manifest and executable hashes before a native request;
  a changed helper is refused. Reject symlinked job files and expired requests.
- The helper accesses apps only after an explicit native-job invocation. Its
  manifest, synthetic-fixture and private-file-validation paths never initialize
  the app/AX runtime.
- The response echoes request identity/operation/app. Validate size, role list,
  path depth and traversal caps. Never log raw native output/errors.
- Kill and reap the exact helper process on cancellation/deadline; keep the
  outcome unresolved when an open may have been dispatched. Never use broad
  application kill commands.
- Keep private native receipts outside Git. Public evidence contains source/build
  hashes, counts, statuses and invented fixtures only.

## Preparation evidence and review gate

Compile/sign the frozen helper without launching a native job. Run its manifest
and synthetic-tree paths and test malformed requests/responses, redaction, caps,
changed build, expired job, cancellation and timeout using fake subprocesses.
Keep AS0 source/evidence, ordinary provider paths, installed app and other
branches intact. No production wiring/schema/UI changes belong to preparation.

Report offline results separately from live results. AS1-A needs its concrete
bridge/permission approval before execution. AS1-B message reading, AS2 model
tasks, AS3 sending and any merge/deployment remain separate checkpoints.
