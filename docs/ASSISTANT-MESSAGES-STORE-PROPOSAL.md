# Messages read-only store bridge: concrete next scope

9 November 2026 · proposal, not authorization to open the Messages database

## Decision

Stop probing the current AX text/container path. The real metadata trial found
13 elements in 0.282 s, but outer groups have no IDs and four inner groups share
one ID. Recipient/thread and per-message identity remain unqualified. This is an
integration gap, not evidence that the daily local model cannot do the task.

Use a separately named **Aether Messages Reader** helper
(`dev.agenticrag.aether.messages-reader`) to read one explicitly chosen direct
conversation from the Mac's Messages store. Keep it below the existing desktop
task/observation interface; do not build another agent or new tab. App opening
continues using the already-qualified primitive.

No new package, framework, model or runtime is proposed. Build with installed
Swift, Foundation and Apple's system SQLite library. Do not install imsg,
BlueBubbles, a server, private-framework hook or inbox watcher.

## Why this bridge, and its limits

The installed public Messages scripting dictionary exposes chats/participants,
but not message history. Public imsg source independently demonstrates reading
message history from the local store in read-only mode. That establishes a
feasible approach, **not** this Mac's actual schema or helper qualification.
Apple does not promise a stable public Messages database schema. Validate every
required table/column/type and refuse unsupported variants; never silently guess.

Use native stored chat GUID, handle/address, message GUID, direction and order.
Do not substitute UI indices, generated IDs, display names or body hashes for
these identities. A content digest may later detect changed source text, with
the actual native identity retained separately; private digests stay private.

## Permission boundary

This changes the bridge and needs Jake's explicit approval under
`docs/ASSISTANT-FIRST-PLAN.md` (source-only preflight and AS1) and the stopped
reader's semantic gate. No production Messages store has been opened or copied.

Reading the live store normally needs **Full Disk Access**. This OS permission
is broad; the application's one-conversation policy does not make the OS grant
conversation-specific. Give it only to the exact named helper for this trial,
never Codex, Terminal, Python, the live server or a general agent. Jake must grant
it manually, then revoke it before the refusal check. If macOS requires a broad
parent-process grant as well, stop rather than grant that parent access.

The helper has no Accessibility, Automation, screen-capture, send, shell/script,
network or model operation. Freeze its executable and code-signing identity
before access; exact-build ad-hoc qualification is trial-only, not an established
upgrade/deployment identity. Production signing/rollback needs its own review.

## Offline preparation before any access

- Strict operation/receipt models and a minimal helper with a fixed store path;
  no caller/model-supplied SQL or file path, no model-selected recipient.
- Test against **invented** SQLite databases only: wrong thread, duplicate
  handle/name, group chat, ambiguous service, missing/duplicate GUID, unknown
  direction, malformed/changed schema, unsupported text, deleted/edited records,
  reordered/recent messages, budget expiry, revocation and cancellation.
- Open with `SQLITE_OPEN_READONLY`; verify `sqlite3_db_readonly`, disable extension
  loading, apply query-only/trusted-schema/authorizer/size/time limits, bound
  statements and use parameters. No attach, database modification, checkpoints,
  migration, backup/export or attachment opening.
- Respect live WAL state. Do not use `immutable=1` on a changing database or copy
  only its main file and claim the result is current. SQLite can require WAL/SHM
  coordination even for a logical read; qualify that behavior, do not promise
  zero sidecar effects merely from the read-only flag. Refuse if safe access or
  freshness cannot be established.
- Text-only feasibility first: bound accepted UTF-8 text to 4,000 bytes/message,
  16,000 total and eight messages. Do not regex-extract attributed/archived blobs,
  treat NULL text as an empty message, or silently skip a newer unsupported row
  and call an older one "latest." Explicitly refuse unsupported message formats.
- No private data in stdout, logs, Git, exceptions, fixtures or model context.
  Keep private mode-0600 receipts in a mode-0700 directory, short read transactions
  and no background ingestion. Public evidence contains counts/statuses only.

## Proposed native trial after approval and offline checks

A new fixed ledger, **at most three one-shot helper requests total**, stopping on
the first unexpected failure. Existing native/model ledgers stay sealed.

1. **Resolve one exact self handle.** Jake enters his own exact Messages address
   in the helper's private local setup UI, not this chat. Inspect the minimum
   schema and resolve at most two direct-chat candidates for that literal handle.
   No body/history or other recipients are returned. Ambiguity stops for an
   explicit choice; no fuzzy contact matching or broad chat enumeration.
2. **Read that exact chosen chat.** Bound the query to its verified native GUID
   and participant set, returning at most eight recent text messages, native
   message IDs, stored sender/direction and timestamps. Recheck identity and
   freshness in a separate short read before accepting a candidate. A self-thread
   need not contain an incoming message; report that without pretending an
   outgoing row is incoming. Read only; do not mark messages read.
3. **Revoke and refuse.** After Jake manually revokes only this helper's Full Disk
   Access, a fresh helper must refuse without returning any private record. Any
   unexpected permission attribution or access after revocation stops the trial.

Host deadline 15 s/helper 12 s, SQLite busy limit 250 ms plus progress deadline.
No retries, observer/watch loop, private screenshots, app inputs, sends, inference
or main merge/deployment. Inspect no private row until the precise grant and
self-address setup are confirmed. Keep the live app and all existing files intact.

## What follows a successful read

Report actual schema/identity/text/freshness behavior before enabling model use.
Then separately scope a bounded local-model draft trial through the existing
native Ollama adapter and task UI. Private source text stays untrusted, is never
sent to public search, and a draft cannot authorize sending. A later send needs
approval of the exact recipient and final text. This proposal approves no send.

If the permission is unacceptable, a useful lower-access fallback is user-pasted
text → local reply draft → manual send. Label its source as user-provided; do not
describe that fallback as automatic Messages reading or verified reply targeting.

## Primary sources checked

- [Apple: Updates to Full Disk Access](https://developer.apple.com/news/?id=p6zjojqw)
  explains its broad scope and need for explicit user action.
- [imsg source](https://github.com/openclaw/imsg/blob/main/Sources/IMsgCore/MessageStore.swift)
  and [permission guide](https://imsg.sh/quickstart.html) provide independent
  implementation evidence; no dependency or source was installed/copied.
- [SQLite opening flags](https://sqlite.org/c3ref/open.html) and
  [WAL behavior](https://sqlite.org/wal.html) define the storage constraints.
- The installed `Messages.sdef` remains the public scripting-surface evidence
  from `docs/ASSISTANT-FIRST-PLAN.md`; no scripting query ran.
