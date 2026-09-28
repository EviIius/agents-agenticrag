# Data contract changes for the v2 UI

The redesign is mostly front-end. A few elements need data the backend doesn't send yet. Every change here is **additive**: API version `/api/v1` stays, existing fields keep their meaning, and older saved chats still render (the UI falls back gracefully). **Rule:** if a field is missing, the UI hides the element. It never invents a value.

| ID | What the UI needs | Needed for | Priority |
|---|---|---|---|
| B1 | Time offset on every run event | Per-step durations (§3.4, §4.2) | Phase 3, required |
| B2 | Readable arguments on `tool_called` | "Searched library `query`", "Read source `file › section`" | Phase 3, required |
| B3 | Live run events over SSE | Live step timeline, live evidence, budget readout (§5) | Phase 3, required |
| B4 | `[n]` citation markers in answer text | Inline citation pills (§3.5) | Phase 3, required |
| B5 | Runtime reachability | Honest readiness dot, runtime pill, Models status (§1.1, §9) | Phase 1/2, required |
| B6 | Obligation texts in `plan_created` | Plan step detail | Optional |
| B7 | System memory in bootstrap | Memory meter "of 64 GB" (§9) | Optional |
| B8 | Supporting quote per citation | Sentence-level highlights like the mockup (§4.1) | Optional, stretch |
| B9 | Chat rename endpoint | Rename in breadcrumb or history (§6) | Optional |

---

## B1: `at_ms` on run events

**Change.** Add an optional field to `RunEvent` in `domain.py`:

```python
@dataclass(frozen=True)
class RunEvent:
    kind: EventKind
    detail: dict[str, Any] = field(default_factory=dict)
    at_ms: int | None = None   # milliseconds since the run started, set when the event is appended
```

Populate it wherever events are appended in `agent.py`, `workflows.py` and `supervisor.py`: use `_elapsed_ms(started)`, which already exists in `agent.py`. A small helper `events.append(_event(kind, detail, started))` keeps it tidy.

**Serialised:** `{"kind": "tool_called", "detail": {...}, "at_ms": 812}`. `RAGResult.to_dict()` already uses `asdict`, so this needs no further change.

**UI:** the step duration is `next.at_ms − this.at_ms`, and the last step runs to `elapsed_ms`. If any `at_ms` is null, hide all per-step times.

**Tests:** extend `test_agentic.py` / `test_workflows.py` to assert that `at_ms` is non-decreasing and ≤ `elapsed_ms`.

---

## B2: argument summaries on `tool_called`

**Change.** In `agent.py` where `tool_called` is appended, add a compact, display-safe summary:

```python
detail = {
  "action": action, "step": step, "success": True, "evidence_delta": result.evidence_delta,
  "summary": {"query": arguments.get("query", "")[:120]}                       # search
           | {"source_path": <logical_path of the looked-up source>, "section": <heading or None>}  # lookup
           | {"expression": arguments.get("expression", "")[:80]}             # calculate
}
```

Also add `"query"` to the initial `retrieval_completed` event (the host already knows `initial_query`).

**Safety:** these are the user's own question words and paths the user is authorised to see. They're truncated, and the UI renders them as text (never HTML).

**Tests:** assert that the summary keys exist for each action type.

---

## B3: live run events over the existing SSE stream

Today `/api/v1/ask-stream` emits `started`, one generic `progress` message, `token`, `completed`, `stopped` and `error`.

**Change.**

1. Workflows accept an optional `on_event: Callable[[RunEvent], None]`. Call it right after each `events.append(...)`. The host passes a callback that emits an SSE frame:

   ```
   data: {"type":"event","event":{"kind":"tool_called","detail":{...},"at_ms":812}}
   ```

2. Optional `evidence` frames when retained evidence grows, so the Evidence tab can fill live. Send the chunk ID, path and heading only, not the full text (the full text arrives in `completed`):

   ```
   data: {"type":"evidence","items":[{"chunk_id":"…","logical_path":"sheet-pan-nachos.md","heading":"Method"}]}
   ```

3. Extend `started` with limits so the budget meters are honest:

   ```
   data: {"type":"started","run_id":"…","limits":{"max_steps":8,"max_seconds":180}}
   ```

**Compatibility:** clients that ignore unknown `type` values keep working. The current `streamQuestion()` does, because it only matches known types. `completed` still carries the full `result` with all events.

**Tests:** in `test_server.py`, alongside the existing stream test (which asserts `"type":"started"` / `token` / `completed`), assert that at least one `"type":"event"` frame arrives for an agent run using the fake provider.

---

## B4: inline citation markers

**Change.** Update the answer instructions for Fixed (`workflows.py` system prompt), Agentic (the `finish` decision prompt in `agent.py`) and the Supervisor synthesis step:

> Place a marker `[n]` directly after each sentence or clause that uses evidence, where `n` is the 1-based position of that evidence's ID in your `citations` array. Use only markers for IDs you cite. Do not invent markers.

**Validation** (host side, after the existing citation validation; never fail the run for markers):

- Find `\[(\d+)\]` in `answer`.
- Remove markers where `n < 1` or `n > len(citations)`, and count them as `marker_repairs` in the `answer_validated` detail.
- If the answer has citations but no markers, leave it as is. The UI falls back to chips-only.

**Tests:** a fake-provider answer with markers [1], [2] and [7], where 2 citations are valid, keeps [1] and [2], strips [7], and reports `marker_repairs: 1`.

---

## B5: runtime reachability

**Change.** Add `GET /api/v1/runtime-status`:

```json
{
  "checked_at": "2026-09-28T12:00:00Z",
  "chat":      {"configured": true, "reachable": true,  "latency_ms": 38, "model_present": true,  "error": null},
  "embedding": {"configured": true, "reachable": false, "latency_ms": null, "model_present": null, "error": "Connection refused"}
}
```

- Implement it with the existing discovery and probe code in `runtimes.py` (list models on the configured base URL, 2 s timeout).
- `model_present` is whether the configured model ID is in that list.
- Cache for 15 s so polling is cheap.
- Loopback only, like everything else.

**UI:** poll on load, every 60 s while the page is visible, and right after any configure call. The readiness footer, runtime pill dot and Models status use it. Until this ships, the UI shows "Configured" with a hollow dot, never green.

**Tests:** fake runtime up → `reachable: true`; closed port → `reachable: false` with an error string.

---

## B6 (optional): obligation texts

Add `"obligations": [{"id":"o1","question":"…"}]` (each truncated to 140 characters) to the `plan_created` detail. The UI shows them as the Plan step's detail and in a tooltip on the chain label.

## B7 (optional): system memory

Add `"system": {"memory_gb": 64}` to `/api/v1/bootstrap`. On macOS use `sysctl hw.memsize`, on Linux `/proc/meminfo`, else null. The UI uses it as the denominator for the Loaded memory meter and header ("of 64 GB").

## B8 (optional, stretch): supporting quotes

Extend the answer schema with `"quotes": {"<chunk_id>": ["verbatim substring", …]}`. The host validates that each quote is an exact substring of that chunk's text and drops any that aren't. The UI then marks only those substrings, which gives the sentence-level highlight shown in the mockup. Without B8, the whole cited chunk is marked.

## B9 (optional): rename chat

`PATCH /api/v1/chats/{id}` with `{"title": "…"}` (1–120 chars, trimmed). Returns the chat. It uses the same cross-origin write checks as the other write endpoints.

---

## Static assets the server must serve (Phase 0)

`server.py` uses an allowlist (`UI_FILES`). Add:

```python
"/tokens.css": "tokens.css",
"/fonts/Geist-Variable.woff2": "fonts/Geist-Variable.woff2",
"/fonts/Geist-Variable-LatinExt.woff2": "fonts/Geist-Variable-LatinExt.woff2",
"/fonts/GeistMono-Variable.woff2": "fonts/GeistMono-Variable.woff2",
"/fonts/GeistMono-Variable-LatinExt.woff2": "fonts/GeistMono-Variable-LatinExt.woff2",
"/fonts/Newsreader-Variable.woff2": "fonts/Newsreader-Variable.woff2",
"/fonts/Newsreader-Variable-LatinExt.woff2": "fonts/Newsreader-Variable-LatinExt.woff2",
"/fonts/Newsreader-Variable-Italic.woff2": "fonts/Newsreader-Variable-Italic.woff2",
```

In `_asset()`:

- **Content type:** fonts must be sent as `font/woff2` with **no** `; charset=utf-8` suffix (today only `.png` skips the charset). `mimetypes` may not know `.woff2` on every platform, so map it explicitly.
- **Caching:** `Cache-Control: public, max-age=31536000, immutable` is safe for fonts. Keep `no-cache` for html, js and css.

The CSP `default-src 'self'` already covers self-hosted fonts, so no CSP change is needed. Don't add Google Fonts: CSP blocks it, and the app must work offline.

`pyproject.toml` package data: add `"ui/fonts/*.woff2", "ui/fonts/LICENSE-*"`. Add `"ui/tokens.css"`, or rely on the existing `"ui/*.css"` glob.
