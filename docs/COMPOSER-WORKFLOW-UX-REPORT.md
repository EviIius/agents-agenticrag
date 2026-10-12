# Composer and workflow builder report — 12 October 2026

## Summary

The Workflows tab above chat opens a visual builder for the two approved fixed
workflows. Connected steps select their actual settings; desktop uses a side
inspector and phones bring the inspector into view below the canvas. Image
creation is available from the message box, with progress, cancellation, saved
results and the existing cancellable save/share dialog. Seeds are automatic;
optional advanced controls support exact repeats. The static update is published with private static/database fallback and verified
local and Tailscale HTTPS health. The installed server was not restarted.

Jake reported the earlier Images feature works on his iPhone. This is overall
acceptance, not separate generation/save/cancel checklist evidence for this new UI.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Workflows tab above chat and visual steps/settings | Pass automated | `composer-workflows.spec.ts`: selected node, keyboard operation, 320/390/1440 px reflow, both themes/engines |
| Image creation from the message box | Pass automated | Composer fake generation reaches a saved image without a chat request |
| Automatic seeds, image count and optional repeat controls | Pass automated | Workflow count creates three resolved seeds with empty text sampling overrides; original explicit-seed version/save checks retained |
| Uncertain acceptance creates no duplicate | Pass automated | First response dropped after actual fake acceptance; image/workflow retry bodies including seeds and request key are identical |
| Chat drafts and same-chat return | Pass automated | Chat text survives image mode and Workflows navigation; saved-chat tab returns to its original ID |
| Cancellation and save/share controls | Pass automated | Cancellation reaches terminal state in composer; original image/workflow save dialogs and cancellation remain |
| Existing send rollback and streaming behavior | Pass focused | 46 composer/chat checks, including rejected send, new drafts, chat switch, reduced motion and exports |
| Repository gates | Pass | 532 Python, 39 frontend, API/types/contrast/motion/privacy; `make-check-final.log` |
| Full browser regression | Pass | `make-e2e.log`: 493 pass, three existing skips, 41.6 minutes. Two final markup corrections have separate final focused evidence |
| Initial bundle | Pass | 243,871 gzip bytes, existing 256,000 byte gate; lazy image/workflow code |
| Production source/prompt/runtime preservation | Pass before publication | 97 tracked server files match installed accepted `27dfaa3a`; no production inference |
| Static publication and fallback | Pass | `publication-20261012T174326858516Z.json`: private rollback, server parity, original label/route, local/verified HTTPS health 200, no restart |
| Actual deployed controls | Pass observed by Codex | `live-ui.json`: top tab, five nodes, three counts, 44 × 44 image action, both seeds hidden, composer return; zero work accepted, no private capture |
| New physical phone interface | Pending user review | Browser WebKit checks do not establish a physical phone pass |

## Changed files

- Web: SectionTabs, Composer, ImagesPage/ImagesWorkspace, WorkflowCanvas and
  WorkflowsPage, live/fixture shell navigation, sidebar entries, seed helper,
  token-based canvas dots and Images design preview.
- Tests: composer/workflow browser scenarios and existing Images/Workflows paths
  updated to use selected-step configuration and advanced controls.
- Server test only: split one pre-existing overlong synthetic string into
  parentheses; its resulting bytes and all production modules remain unchanged.
- Docs: bounded plan, workflow instructions, authorization/acceptance record.
- Tooling: static-only publisher with current server baseline and explicit gates.

## Deviations from SPEC.md

User-requested composer image action, top navigation and workflow canvas supersede
standalone sidebar/form layout. The canvas executes the two already-approved
fixed templates. Models stay explicitly visible/changeable; no arbitrary agent,
connector, branch, loop, schedule or extra model call is added. Image seeds are
host-generated worker inputs, not LLM sampling parameters. Existing prompts and
source-review requirements remain unchanged.

## Runtime observations

No new native inference was run. Existing image engine, server, model weights,
Ollama and service/route remain unchanged. The earlier workflow demonstrations'
quotation-context and timestamp failures remain in `PRODUCT-DELIVERY-REPORT.md`;
meeting packs are still drafts requiring original-source review.

## Test output

- `make-check.log`: failed on an existing overlong synthetic server-test string.
- `make-check-retry.log`: Python/tests/API/contrast passed; formatting failed while
  Composer was still being edited. Both failed outputs are retained.
- `make-check-final.log`: 532 Python / 39 frontend checks pass.
- `browser-first.log`: 22 Images/Workflows checks pass.
- `composer-first.log`: first six composer/builder checks pass.
- `composer-and-chat.log`: final eight new checks plus 38 chat checks pass.
- `make-e2e.log`: 493 passed, three existing skips.
- Final corrections: the image action gets a minimum 44 px width; its decorative
  wrapper uses a data slot. The final test counts the actual chat-create/message
  endpoints and scans the embedded panel. `composer-release.log`: eight pass in
  both engines. `frontend-release.log`: 39 pass plus types/lint/formatting; final
  build and budget pass. The full browser run precedes those two markup changes.
- Installed seed implementation was reviewed read-only: MFLUX forwards the integer
  to MLX’s key function. No image/model load or inference was executed.
- `regenerated-test-evidence.json`: 1,067 fresh synthetic outputs retained; 1,027
  historical tracked files restored. All 19,485 earlier evidence/eval files and
  59 historical manifests remain unchanged.
- Static publication preserves all 97 tracked installed server files, settings,
  data, original service identity and normally verified HTTPS route. Old hashed
  assets remain available, and rollback includes prior static assets and an
  online SQLite backup. No dependency, weights, interpreter or default change.

## Screenshots

Synthetic fixtures only, under `artifacts/composer-workflows/browser/`:
`builder/model-1440-dark-chromium-fake.png`, corresponding 320/390 px and WebKit
captures; Images/Workflow state/export captures; composer cancellation captures.
Codex inspected the desktop builder, phone layout and composer captures. No real
recordings, filenames, transcripts, Library text or physical phone images were
copied into evidence.

## Open questions for Jake

Review the new top tab/canvas and image composer on your phone after publication.
Further configurable step types remain a separate concrete workflow scope.
The source release is `306b656`; the local main/tag closeout retains this build
and all evidence. No general factual reliability or physical phone pass is claimed.
