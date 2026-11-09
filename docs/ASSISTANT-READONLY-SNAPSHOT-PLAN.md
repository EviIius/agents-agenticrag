# Read-only selected-pane snapshot

8 November 2026 · continuation on `codex/assistant-as1b`

Jake asked to go on after the verified app-opening checkpoint and confirmed the
self-conversation is open on his number with an empty composer. Permission setup
through Settings remains delegated to Codex. Main and the installed app stay intact.

## Correct the access contract

The capability trial established that both current text areas advertise bounded
character/range APIs and a modifiable AXValue. That flag is neither proof of an
editor nor permission for this helper to edit. Rejecting it blocked every area.

Prepare a separately versioned read-only snapshot contract/helper. Required
`value_settable: bool` records the observed API flag on each area. The snapshot
explicitly declares `access: read_only` and `qualification: unqualified`. There
are no AX write, click, key, scrolling, screenshot, send or scripting operations.
The helper reads the same fixed pane only; modifiability never grants authority
to the host, model or later input operations. Missing/nonboolean flags still fail.

Keep 1–8 leaf text areas discovered from the fixed pane, deny text fields or
unexpected ancestry/leaf shapes, 4,000 UTF-8 bytes per value / 16,000 total,
1,000-byte descriptions and 200-byte title/identifier/subrole/group metadata.
Require reported character counts and bounded AXStringForRange, with no AXValue
fallback. Retain 15-second host / 12-second helper / three-second AX budgets and
before/after window, shape, element, flag and value stability checks. Return only
an enum stage on failure, never a raw error or private attribute.

Old candidate contracts/builds and their rejection tests remain historical and
unchanged. The dynamic builder may accept a fixed source selection for the new
wrapper; its earlier source and native seal remain at `739443ed`. No new package,
provider prompt, sampling or production path changes belong to this reader repair.

## Bounded native scope

Freeze new source/build after invented-packet and compiled checks. Use a new
private `assistant-readonly-20261108/native` ledger capped at **two** one-shots:

1. Add the exact new helper via the delegated Settings flow, then collect one
   bounded snapshot of Jake's currently selected self-conversation.
2. Only after success, switch only that helper off and require a fresh permission
   refusal with no target/snapshot. Cleanup disables access even after a failure.

No retries or spending old unused slots. Stop on the first unexpected failure.
Raw values, metadata and private-text digests remain outside Git/tool output;
public summaries contain counts, statuses and metadata-presence flags only.
No model call or model use of these private candidates is authorized by this scope.

## Semantic gate and follow-through

Successful collection alone does not qualify messages. Assess whether actual
attributes establish a direct recipient, thread, message order/direction and
latest incoming identity. Never manufacture those from a display name, content,
path or digest. If unavailable, state the exact gap and prepare a specific bridge.
Do not expose a draft/send operation until its source/target contract is qualified.

App opening is already qualified separately. Continue its existing-chat integration
behind the default-off capability, preserving durable status/Stop and all ordinary
chat payloads. Its next model/native test scope is declared separately before calls;
do not consume further calls in the completed opening or reader ledgers.
