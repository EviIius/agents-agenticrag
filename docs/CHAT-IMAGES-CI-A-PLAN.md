# CI-A execution plan

13 October 2026 · base `104c6858` · isolated `codex/workflow-studio`

Keep Claude's waiting-line geometry, cobalt Atelier mark and reasoning ticker.
Known queue/loading/search stages take priority, the seeded 36-word sequence is
cosmetic, and the ticker is an excerpt of existing rAF-batched reasoning. Thinking
starts closed, expands on request and follows new text while the reader stays at
the bottom. First answer text closes it and retains the existing reasoning/stats.

Use one shared presentation clock for elapsed seconds and 2.4-second word changes;
stop it when no active indicator needs it. No network polling, extra model call
or server change. Persist Playful/Plain in the UI store and browser storage,
without writing stale preferences during hydration. The existing server whitelist
does not accept a status-word key. Keep this checkpoint web-only: store this one
UI preference in browser storage, while existing Mac-synced preferences retain
their unchanged payload. Cross-device word-preference sync belongs to server work.

The proposed 400 ms prediction before a future phase is impossible with today's
events. Real phases replace cosmetic text immediately; no token is delayed.
B6 explicitly calls for a 200 ms height collapse, which the existing guard allows;
use that existing property, with opacity/transform/dasharray for mark/word motion.
Both reduced-motion triggers stop all motion while labels continue to update.
Phase announcements retain ordinary semantics; no VoiceOver pass is claimed.

Add all states to `/design`, meaningful pure-state/seed/tail tests, actual fake
stream tests and original performance/keyboard/motion guards. Preserve failures,
source hashes, original artifacts and supplied design bytes. One complete final
check/browser invocation is required. No new dependency or native trial. Stop
with `CHAT-IMAGES-CI-A-REPORT.md`; CI-B/C and the bounded local-LLM workflow trial
follow their concrete scopes and review stops. No main merge/live publication.
