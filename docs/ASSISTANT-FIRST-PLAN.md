# Assistant first: chat → Mac actions → Apple Messages reply

30 October 2026 · proposed implementation scope, not execution approval

## The goal Jake actually wants

Give Aether a task in normal language, and have it use the Mac to carry it out:

- “Search for this and tell me what you find.”
- “Open Notes.”
- “Read the latest message in this conversation and draft a reply.”
- Review the recipient and draft, then tap **Send**, **Edit**, or **Cancel**.

Jake selected **Apple Messages: iMessage and forwarded texts** as the first
messaging app. This takes priority over the earlier folder-workflow proposal.
The initial interface is the existing chat. Push-to-talk follows a working typed
version, so speech recognition is not a prerequisite for testing the actions.

Success is an observable task completed on this Mac, not a model claiming it
opened an app, read a thread or sent a message.

## First useful version

1. A local model proposes a small typed action using Aether's native Ollama path.
   Host code checks the action, target, arguments and budgets.
2. A narrow Mac bridge opens one allowed app or reads one selected conversation.
   Use a tested structured interface where available. A general vision-driven
   clicking loop is a later fallback, not a prerequisite for app launching.
3. Aether shows real progress and the result in the chat. A reply draft includes
   the selected conversation and latest incoming message used to prepare it.
4. Sending is a separate host operation after approval of that exact recipient
   and text. Text received from a contact cannot grant tool permissions.
5. The same task flow later accepts a phone voice transcript. Typed text and
   voice use the same checks, history, Stop and approval UI.

No new agent framework, multi-model planner or large vision-model download is
selected by this plan. A new model is justified only by a measured task failure
and its own concrete trial, not by assuming more parameters solve integration.

## Source-only Messages preflight: what is known

The installed public `Messages.sdef` was read without launching Messages,
querying chats, capturing the screen, granting permissions or sending anything.
It exposes participants, accounts, chats, file transfers and a `send` command.
Its chat class exposes identity/name/account and participants; it does **not**
expose message-history contents. Therefore scripting support for sending is not
evidence that a simple AppleScript can read the latest incoming message.

The dictionary SHA-256 is
`a9db9b015709c8c8e92a8bdccf08984635d5c3545f670bcd0e5a3a10bd5f9e4e`.
This is metadata inspection, not a successful app-integration test.

The first integration gate is **reliably reading and identifying one selected
conversation**. Prefer a bounded Accessibility/automation bridge if the transcript
and sender can be read unambiguously. If that cannot be qualified, present a
specific alternative bridge and its permissions for review. Do not silently
read `chat.db`, ask for Full Disk Access, install a third-party Messages server,
or use screenshots/model guesses as proof of recipient identity.

Apple documents that control of other apps needs user-granted
[Automation permission](https://support.apple.com/en-nz/guide/mac-help/mchl108e1718/mac).
Its [scripting guide](https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/HowMacScriptingWorks.html)
explains that an application's dictionary defines its scriptable objects and
operations. Further Accessibility/Screen Recording grants depend on the chosen
bridge; the existing launchd process having a GUI session does not establish them.

Forwarded SMS/MMS/RCS must already be available in Messages on the Mac. Apple
documents the account and forwarding setup in
[Set up Messages on Mac](https://support.apple.com/en-asia/guide/messages/-ichte16154fb/mac).
Do not change Apple Account, forwarding or read-receipt settings automatically.
Selecting/opening a thread can change its read state; the permission preview
must explain that before the first live read.

## Host operations and boundaries

| Operation | First contract | Evidence returned |
| --- | --- | --- |
| Search public information | Reuse existing search/fetch/source handling; keep private Messages text out of web queries | Actual source IDs/URLs and retrieval outcome. References do not by themselves prove factual support. |
| Open an app | A configured allowlist maps an app ID to its verified bundle; the model supplies an ID, never a shell command or executable path | Launch outcome plus an observed running-app identity; explain failures instead of asserting success. |
| Read conversation | User-selected direct conversation, stable thread/participant identity, at most eight recent text messages initially | Bounded text with sender/order and a latest-message revision/hash. No inbox-wide background ingestion, attachments or group ambiguity in version one. |
| Prepare reply | Native local generation uses that bounded text as untrusted context; preserve current model/settings behavior | Proposed text plus provenance to the selected thread/message. It is a draft until reviewed. |
| Send approved reply | Server-only commit endpoint consumes a persisted one-time approval tied to run, thread, exact recipient, message revision and exact edited reply | Submitted, failed or outcome unknown. Do not claim Delivered unless independently established. |

No model-executable AppleScript, JavaScript, Python or shell text. A host-authored
bridge may use a fixed script/program and validated arguments. Its process identity
must survive deployment/rollback and the user must be able to revoke app access.

The send operation is unavailable to the model during the initial read/draft
trial. Later, a displayed approval expires if the recipient, draft or incoming
message changes. Approval is consumed once. An uncertain outcome never triggers
an automatic resend; reconcile it before offering any retry. Choosing a duplicate
contact name requires a user choice, not a best guess.

## Milestones and stop points

### AS0 — offline task contracts and chat review states

Proposed next implementation milestone; no new packages or native calls.

- One default-off assistant capability in the existing chat; no new tab.
- Strict Pydantic operation contracts and an injectable fake bridge. Reuse
  existing capacity, SSE/rAF and durable attempt patterns; no second provider.
- Design states for task progress, requested conversation choice, reply preview,
  Send/Edit/Cancel, denied/missing permission, source unavailable and outcome
  unknown. Product copy contains meaningful names, not internal tool IDs.
- Persist approval identity and cancellation intent; propose additive schema
  before applying it. Disabling the capability rejects execution server-side.
- Show before/after tests that ordinary chat/search/image requests stay unchanged.

Required fake tests: duplicate recipient names; no transcript; hostile message
instructions; stale incoming message; changed draft; wrong-thread binding;
double tap; reconnect/restart; revoked permission; cancel during a queued action;
uncertain send outcome. Fake sends never contact Messages.

Report the implemented demo and tests, then stop for review. Passing fake tests
does not qualify a real Messages integration or native model behavior.

### AS1 — qualify a narrow Mac bridge

Separate native/permission scope after AS0 review. Initially **no model inference
and no sends**. Use fixed host-authored operations to:

1. Open one allowlisted app and verify its running identity.
2. Read up to eight text messages from one user-designated test conversation.
3. Bind the exact direct-thread recipient and latest incoming message.
4. Test missing/revoked permission and a changed selected thread; refuse ambiguous
   reads. Confirm cancellation and that unrelated apps/conversations are untouched.

Agree the concrete bridge, permission identity, selected app and test thread
before running. Keep real conversation contents, handles and screenshots out of
Git/logs/eval fixtures; review outputs privately. No Full Disk Access or driver
installation is bundled into AS1. If another bridge is necessary, stop with that
specific choice and its scope, rather than growing this trial silently.

### AS2 — three bounded real assistant tasks

Separate approval for a maximum **12 actual native model requests total**, using
the existing installed daily 32K profile and native adapter. No warm-up/helper
call, additional model, download, sampling override or automatic retry.

Ordered tasks, stopping on the first correctness/permission/protocol/resource
failure:

1. “Open [the AS1 allowlisted app].” Maximum two model requests.
2. Find Apple's public Text Message Forwarding instructions and summarize the
   actual setup requirements. Maximum four requests; no private text in queries.
3. Read the selected AS1 test conversation and prepare a requested reply.
   Maximum six requests; **no send operation** exposed or executed.

Each task has at most four action steps and a 180-second hard deadline. Every
model request counts, including invalid output; no next task after a failure.
Do not weaken existing image/residency guards or infer capability from model names.

Success requires observed app state, useful source-supported search results and
a relevant reply to the correct latest message. Record wall time, queue wait,
model calls, memory/swap and whether the user would actually use the result.
Correct JSON alone is insufficient. Repeatability and a held-out task follow
only after reviewing this small feasibility result.

### AS3 — one explicitly approved send and phone use

Separate sending scope, after the draft/read result is accepted. Start with one
user-designated test conversation and one exact message approved in Aether.
Verify the target binding, one-time commit, duplicate/reconnect handling and
observable outcome. No auto-replies, incoming-message watcher or bulk messaging.

Verify on the phone: request → real progress → correct draft → Edit/Send/Cancel →
correct outcome. Then scope push-to-talk and optional speech output separately,
reusing the same task pipeline. General desktop actions/VM autonomy and unattended
reply policies are later projects, not prerequisites for this useful first version.

## Relationship to the existing plan and rules

This is a narrower route to Jake's clarified goal. The original harness proposal,
audit, stopped agent trials, folder automation and pending Part B review remain
preserved. Research is not restarted. AS0–AS3 are proposed reviewable scopes;
this document does not grant their model calls, Messages access or sends.

The current step is ready-to-review planning. AGENTS.md requires approval of the
new task/model-call and permission scope before feature code or live actions.
