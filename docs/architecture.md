# Workbench architecture

**Browser → FastAPI on 127.0.0.1:8787 → local Ollama / transcription subprocess.**
Tailscale Serve supplies HTTPS without changing the loopback bind. Vite builds React,
TypeScript and shadcn primitives into `server/app/static`. Theme/spacing/color tokens are
shared; `/design` exposes synthetic component states only in development.

SQLite in Workbench's private data folder stores settings, message branches, source
metadata, attachments and transcript outputs. Numbered transactional migrations evolve
this database. The legacy importer opens its source read-only and creates idempotent,
linear imported chains in the new database. Original legacy data remains independent.

Provider adapters report runtime capabilities and operational context limits; the app
never infers them from model names. Omitted sampling preferences stay omitted. Runs are
server tasks independent of a browser request, with durable message snapshots. SSE logs
support reconnect/replay; the browser batches token deltas with requestAnimationFrame.
Finished rows are memoized and use content-visibility to limit long-history layout work.

Search uses one planner call, configured free provider fallbacks, bounded page reads and
keyword/hybrid ranking before the answer call. Sources are persisted with the message.
Private recording chats block search by default. Transcription uses one queued external
process at a time; uploaded files stream to private disk and temporary engine results
are stored in SQLite. Successful audio is released by default; opting in retains it for
retranscription. Bulk clearing removes inactive audio without deleting outputs or chats.

Public engine source lives under `transcribe/`; ignored weights/config/glossary are
installed inside the deployed app. No real recording, transcript or personal engine
configuration is part of source control. Host/origin checks, CSP and optional Tailscale
owner checks protect the HTTP boundary. Transcript text is untrusted plain text in the
UI and delimited model context, never host instructions.

The PWA worker caches public shell/hashed assets, excluding every API response and all
private content. Offline use provides a connection error, not offline inference. Updates
wait for a Reload action. Deployment preserves the launchd identity and Tailscale route,
backs up SQLite and keeps old installed data for rollback. Automated gates use isolated
fake runtimes and synthetic audio; physical iPhone installation/VoiceOver remains a
separate acceptance check. T2 cleanup and future Part F agents are outside Phase 3.
