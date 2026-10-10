# Independent context-warning release — 10 October 2026

Jake authorized proceeding after the remaining-work list included publishing
verified fixes. Release only the existing frontend correction, independently of
the failed native evidence experiment. The answer contract is not integrated.

## Scope

- State the input allowance, reserved output and safety margin accurately.
- Honor explicit chat output limits before the user's saved model defaults.
- Keep the existing server reserve rule, prompts and provider payloads intact.
- Keep the recording warning readable across the chip's full width on a phone.
- Use the existing `/design` examples and existing browser assertions.

The six runtime/design source changes relative to stable `f87db46` are
`LiveAppShell.tsx`, `AudioChip.tsx`, `Composer.tsx`, `DocumentChip.tsx`,
`TranscriptionPreview.tsx`, and `lib/context-budget.ts`. Test changes are separate.

## Required evidence

Full `make check`, full Chromium/WebKit `make e2e`, focused attachment/output-limit
checks, a successful build within the existing 250 KB initial JavaScript budget,
synthetic screenshots, and unchanged stable installed server source. Any required
failure keeps publication pending; retain every failed test run separately.

## Publication

`scripts/publish_context_ui.py` defaults to a read-only verification. Applying
requires passing gates and the frozen release manifest. Back up the existing
static files and database privately, stage assets, retain old hashed assets, then
atomically publish index and service worker last. Verify local and Tailscale
health and frontend hashes with normal TLS verification. Keep launchd, routing,
runtime, installed server code and saved settings intact; do not restart the app.
On failure, restore static files automatically. Rollback does not restore the
database or replace newer chats/outputs. Record the private fallback location in
the publication receipt, never private data contents.

No physical iPhone pass is claimed from WebKit tests. Stop for checkpoint review
with actual publication or failure evidence. Image installation and Research
remain outside this release.

## Actual closeout

Published at 18:29:53 UTC on 10 October. Full checks passed (458 Python and 39
frontend), followed by one complete Chromium/WebKit run (463 passed, three
existing documented skips) after correcting the retained WebKit test scrolling
failure. Initial JavaScript is 240,843 gzip bytes, +317 from stable polish.
Local and normal-TLS Tailscale health return 200; the published index/service
worker hashes match the frozen build, all 81 server files match `f87db46`, service
identity and route are unchanged, and production `/design` returns 404.
The runtime was not restarted and no saved settings were edited. Private old
static files and a consistent database backup are recorded in
`artifacts/reliability/evidence-v14/context-warning/publication-20261010T182952757758Z.json`.
See `EVIDENCE-OBJECT-REPORT.md` for all gates, the failed native trial and test ledger.
