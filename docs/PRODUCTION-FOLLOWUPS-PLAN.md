# Production follow-ups — title ownership and workflow wording

18 October 2026. Jake asked to continue after the failed native C1 report.
Close that candidate; fix the two specific remaining source findings from the
reviewed QA roadmap. Isolated branch `codex/production-followups` starts from
accepted main `e7ffea2b`, with none of the dormant native-loop implementation.
Native evidence remains on `codex/native-agent-loop` at `376205a3`.

## Scope and acceptance

1. Preserve a user-set title on the first text send, including a concurrent
   rename while request preparation is pending. Check title ownership inside the
   existing acceptance transaction, rather than trusting a stale preflight read.
   Preserve default fallback titles for untitled chats. Verify completed/reloaded
   detail, full-text title search and export; no extra title/model call.
2. Remove the unavailable Search capability from Workflows home wording. Keep
   the existing disabled Search block, theme, layout and other capabilities.
3. Update the current deferred status so historical pending entries do not imply
   current failures or authorize another agent campaign.

## QA and boundaries

- Retain the four original synthetic title failures and passing fallback control
  before the fix. Add tests instead of weakening existing assertions.
- Use fake runtime/API tests, including the concurrent preflight rename and both
  auto-title settings; run the actual browser rename/send/reload on Chromium and
  iPhone-profile WebKit. Capture only synthetic evidence.
- Run `make check`, one complete `make e2e`, build/bundle and privacy guards on
  frozen source; retain failures and fresh outputs separately from old evidence.
- Existing prompts, model calls, parameters, Search/Library, transcription,
  image/workflow engines, API/schema, dependencies and runtime stay unchanged.
  G9 inference is not triggered: no search/runs/providers source changes.
- No native inference, framework experiment, model download, routing, new block,
  photo editing, main merge, installed-app modification or deployment. Preserve
  working production and service/Tailscale invariants; stop with the H4 report
  and a reviewable draft PR before release.

These changes do not qualify factual answers or enable native agent tools.
