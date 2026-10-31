# Assistant first: typed requests → reusable computer use

30 October 2026 · proposed implementation scope, not execution approval

## The goal Jake actually wants

Give Aether a task in normal language, and have it use the Mac to carry it out:

- “Search for this and tell me what you find.”
- “Open Notes.”
- “Read the latest message in this conversation and draft a reply.”
- Review the recipient and draft, then tap **Send**, **Edit**, or **Cancel**.

Jake selected **Apple Messages: iMessage and forwarded texts** as the first
messaging app. This takes priority over the earlier folder-workflow proposal.
He further clarified that this is a **general computer-use assistant**, with
Messages as the pilot before trying other apps. The main input is typed text in
the existing chat. Voice is an optional input into that same execution path.
The goal includes observing interfaces, clicking, typing, navigating and checking
results across allowed apps; it is broader than a bespoke Messages integration.

Success is an observable task completed on this Mac, not a model claiming it
opened an app, read a thread or sent a message.

## First useful version

1. A shared desktop interface observes the allowed app/window: its identity,
   available Accessibility information and, when separately permitted, a bounded
   screenshot. Observation describes what is actually available to act on.
2. A local model proposes a typed action using Aether's native Ollama path.
   Host code binds the target and observed state, checks permissions and budgets,
   requests the required approval, and dispatches through the shared driver.
3. Observe again and verify the expected result before continuing. Use structured
   app operations where they are reliable; expose screen interaction through the
   same execution contract when it is needed. Messages-specific parsing is an
   adapter inside this layer, not a separate agent or a new flow for every app.
4. Aether shows real progress and the result in the chat. A reply draft includes
   the selected conversation and latest incoming message used to prepare it.
5. Sending is a separate host operation after approval of that exact recipient
   and text. Text received from a contact cannot grant tool permissions.
6. The same task flow later accepts a phone voice transcript. Typed text and
   voice use the same checks, history, Stop and approval UI.

No new agent framework, multi-model planner or large vision-model download is
selected by this plan. A new model is justified only by a measured task failure
and its own concrete trial, not by assuming more parameters solve integration.

## Reusable desktop contract

Build a common `DesktopDriver` interface with a fake implementation before choosing
or installing its native implementation. Cua Driver is an existing candidate in
the [harness audit](harness-notes.md); a dependency/permission review is still
required. A new vision model is not presumed necessary or sufficient.

| Shared operation | Contract |
| --- | --- |
| Open/focus app | Validated app identity from the current allowlist; no model-supplied executable path. |
| Observe | Target app/window identity, geometry/scale, observation revision, readable UI state and permitted screenshot reference. |
| Propose action | `click`, `type_text`, `key` or `scroll`, with an expected outcome and a binding to the observed target/state. Expand the set only when a task requires it. |
| Authorize | Host policy decides the operation's permission; approval records bind exact arguments/target/revision. Screen text and model labels cannot grant permission. |
| Act | The selected driver performs the validated action; no model-written executable scripts. |
| Verify | Read fresh structured state or a fresh observation and check the task's expected outcome. A model's “done” is not sufficient. |
| Stop | Cancel queued actions/approvals and end or acknowledge the active operation before reporting completion. |

Normalized coordinates, screenshot resize/crop offsets, display origins and
Retina scale are explicit observation metadata. Changing the window, scaling or
observed state invalidates an old target. Validate transforms offline before
native clicks. Keep driver replacement and future app adapters below the same
task/approval interface.

Screenshot observations require a runtime-reported vision-capable model and a
qualified image/tool request format. Text-only UI state can use a compatible
text model. Never drop an unsupported screenshot and pretend the model saw it;
refuse or request an explicitly qualified selection instead. Identify that
selection in the native trial scope before executing any model requests.

The Messages pilot narrows **permissions and test cases**, not the desktop
architecture. After it works, a second-app task must use the same driver and
controller; it should not require another assistant implementation or workflow.

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
| Observe/interact with an app | Shared driver targets an allowed app/window and a current observation; host checks each action's arguments, permissions and expected outcome | Fresh UI/screen state and a verified or failed outcome; no implied success from a tool acknowledgement. |
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

General desktop tools must not bypass the send gate: an Enter key or click on
Send can submit a message just as a scripted send can. The first read/draft
trial blocks those actions. If the host cannot establish whether an action
commits a send, it refuses it. The later send scope needs approval for the exact
operation regardless of which driver executes it.

## Milestones and stop points

### AS0 — offline task contracts and chat review states

Proposed next implementation milestone; no new packages or native calls.

- One default-off assistant capability in the existing chat; no new tab.
- Strict Pydantic operation contracts and an injectable fake `DesktopDriver`.
  Include observe/action/result/state-revision/coordinate contracts from the start.
  Test the controller against both a fake Messages window and a fake second app.
  Reuse
  existing capacity, SSE/rAF and durable attempt patterns; no second provider.
- Design states for task progress, requested conversation choice, reply preview,
  Send/Edit/Cancel, denied/missing permission, source unavailable and outcome
  unknown. Product copy contains meaningful names, not internal tool IDs.
- Persist approval identity and cancellation intent; propose additive schema
  before applying it. Disabling the capability rejects execution server-side.
- Show before/after tests that ordinary chat/search/image requests stay unchanged.

Required fake tests: 1×/2× coordinate transforms, cropped/resized observations,
wrong/stale window, shared controller working in two apps; duplicate recipient
names; no transcript; hostile message
instructions; stale incoming message; changed draft; wrong-thread binding;
double tap; reconnect/restart; revoked permission; cancel during a queued action;
uncertain send outcome. Fake sends never contact Messages.

Report the implemented demo and tests, then stop for review. Passing fake tests
does not qualify a real Messages integration or native model behavior.

### AS1 — qualify the shared driver on a narrow app scope

Separate native/permission scope after AS0 review. Initially **no model inference
and no sends**. Use the chosen driver/host-authored adapters to:

1. Open one allowlisted app and verify its running identity.
2. Read up to eight text messages from one user-designated test conversation.
3. Bind the exact direct-thread recipient and latest incoming message.
4. Test missing/revoked permission and a changed selected thread; refuse ambiguous
   reads. Confirm cancellation and that unrelated apps/conversations are untouched.
5. Demonstrate a read-only observation in a second allowed app using the same
   driver, target binding and cancellation mechanism. Verify screenshots and
   coordinate metadata only within the separately approved capture scope.

Agree the concrete bridge, permission identity, selected app and test thread
before running. Keep real conversation contents, handles and screenshots out of
Git/logs/eval fixtures; review outputs privately. No Full Disk Access or driver
installation is bundled into AS1. If another bridge is necessary, stop with that
specific choice and its scope, rather than growing this trial silently.

### AS2 — three bounded real assistant tasks

Separate approval for a maximum **12 actual native model requests total** through
the native adapter. AS1 must identify one exact installed profile suitable for
its observation format before that approval: the daily 32K profile for compatible
text observations, or a separately qualified vision/tool profile for screenshots.
There is no implicit model switch. No warm-up/helper call, extra profile, download,
sampling override or automatic retry.

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
reusing the same task pipeline. Typed commands remain fully available.

### AS4 — prove reuse in other apps

After the Messages pilot, extend the allowlist and task suite to Notes and a
browser using the same observe/act/verify controller. Examples: create a reviewed
note from user-supplied text, or navigate to a requested public page and retrieve
its information. Define the exact permissions, success checker, model-call limit
and held-out cases before native testing. Compare speed and task success, not
just whether the model can click once.

Only add app-specific structured adapters where they improve the existing
controller. Autonomous desktop sessions, a VM, unattended replies and a split
planner remain separately qualified extensions; general interactive computer-use
contracts are already part of AS0/AS1.

## Relationship to the existing plan and rules

This is an incremental route to Jake's clarified computer-use goal. Messages is
the first real task; it is not the final feature set. The original harness proposal,
audit, stopped agent trials, folder automation and pending Part B review remain
preserved. Research is not restarted. AS0–AS3 are proposed reviewable scopes;
this document does not grant their model calls, Messages access or sends.

The current step is ready-to-review planning. AGENTS.md requires approval of the
new task/model-call and permission scope before feature code or live actions.
