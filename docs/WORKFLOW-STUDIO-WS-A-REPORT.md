# Workflow Studio WS-A report

12 October 2026 · baseline `dce4c49` · source `ee788832` · branch `codex/workflow-studio`

## Summary

Claude's reference documents, prototype and eleven screenshots were reviewed and
preserved. The redesign is sufficient for staged implementation, with the engine
corrections in `docs/WORKFLOW-STUDIO-REVIEW.md` required before WS-B.
WS-A replaces top tabs with persistent sidebar navigation, a shared application
shell, template cards, recent runs and a run detail view. The original fixed
builder and composer image action remain available. No live publication or merge.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| WS-AC1: no Chat / Workflows tabs | Pass | SectionTabs removed; source search; `workflow-studio-shell.spec.ts` |
| WS-AC2: sidebar rows, rail and phone drawer | Pass, both engines | Shared sidebar, rail and palette test; active state and drawer assertions |
| WS-AC3: home, templates, existing execution | Pass, both engines | Existing workflow tests moved to `/workflows/new`; run detail/reload test |
| WS-AC4: draft preservation | Pass, both engines | Both existing composer draft/return tests retain their assertions |
| GitHub isolation | Pass | Published branch; managed worktree; `baseline-and-isolation.json` |
| Checkpoint review | Pending | WS-B has not started; final main/deployment approval remains required |

## Changed files

- Web shell: router, LiveAppShell, Sidebar, HistoryList, Panels, TopBar,
  WorkspaceNavigation and CommandPalette; SectionTabs deleted.
- Workflows: WorkflowHome, WorkflowStatus, useWorkflowRuns, WorkflowsPage and
  WorkflowForm's initial template selection. Existing performers and run controls
  are retained; initial HTTP snapshot is protected against a newer SSE snapshot.
- Images: existing gallery renders inside the shell; embedded composer behavior
  and automatic seeds remain intact.
- Design/tests: production home/status fixtures; new shell navigation, cards,
  run/reload and accessibility evidence; three existing test files updated for
  the explicitly requested navigation change.
- Docs: supplied source references, implementation review and AGENTS authorization.
- Server/shared/package manifests: no changes.

## Deviations and implementation decisions

WS-A truthfully presents two working templates. It does not present fake custom
saved workflows, Blank creation, future templates or definition editing before
WS-B. All runs shows the existing latest-50 limit; Recent runs shows ten. Original
review, source, save, cancellation and retry controls remain available on the
builder's saved cards and the new detail route. Studio auto-collapse waits for
WS-C. Command palette chat-only actions are disabled on workspace pages.

The shared shell retains the selected chat/model, control drafts and pending
attachments when a workspace occupies the main pane. Returning through browser
history restores the same chat and draft. Workflows cannot accidentally upload a
file into the hidden chat composer. No ordinary chat payload rule was changed.

The provided spec's existing trailing whitespace at line 850 was retained to
preserve reference bytes. No product-source whitespace error remains.

## Runtime observations

No native inference or image/transcription job was executed against production.
All functional browser calls use the isolated fake app, fake runtime and fake
image worker. Ollama, interpreter selections, models and production settings are
unchanged. GitHub CLI 2.102.0 was installed with Jake's explicit authorization;
Jake completed browser sign-in. The initial unauthenticated push failure is
retained as a setup observation; the authenticated push succeeded. This tooling
installation adds no application dependency.

## Test output

`make check` passes: 532 Python tests and 39 frontend tests. Frontend type/lint/
format checks, contrast, API types/additivity, frozen prompt hashes, migration
row preservation, privacy and motion guards pass. Build passes.

First focused invocation: 38 passed, 4 failed. Failures involved unnamed/ambiguous
new card links and selectors; source edits during that development invocation
mean it is not release evidence. Explicit link labels and scoped selectors resolve
them. The corrected focused invocation passes all 20 cases in Chromium and WebKit.
The complete final browser invocation passes **505 cases, three existing skips**,
in one 43.3-minute run, Chromium and WebKit, on the frozen `ee788832` source.
No new skip, rerun-based qualification or post-run product correction follows.

Initial JavaScript: 245,249 gzip bytes versus 243,871 at baseline (+1,378), below
256,000 and the +8 KiB growth bound. Workflow routes remain lazy; no canvas library
is installed in WS-A. Fresh complete-run streaming render p95 is 3 ms in each engine; max 7.2 ms
Chromium / 5 ms WebKit. Only the streaming row renders. First-token overhead is
80.33 ms / 60.97 ms, under 150 ms. For 300-message scrolling, median / p95 is
16.7 / 16.7 ms Chromium and 17 / 21 ms WebKit. Raw measurements are retained
through the fresh-evidence manifest and `performance-summary.json`.

## QA gates

| Gate | Status/evidence |
|---|---|
| G-1 | Pass: `artifacts/workflow-studio/ws-a/make-check.log` |
| G-2 | Pass: one complete `make-e2e.log`, 505 passes / three existing skips |
| G-3 | Test-diff ledger below; no skip, timeout, target or rubric relaxation |
| G-4 | Pass: build/bundle and complete streaming/scroll measurements above |
| G-5 | Pass: new-state and full legacy axe/keyboard checks, both themes/widths/engines |
| G-6 | Pass: API additive/types checks; no API change |
| G-7 | Pass: existing migration preservation tests; no migration |
| G-8 | Pass: frozen prompt tests; server source unchanged |
| G-9 | Not triggered: Search/runs/providers unchanged. Historical factual failures are not regraded or qualified |
| G-10 | Pass: server golden/presence checks and full browser parameter captures |
| G-11 | Privacy guard pass; supplied and generated screenshots are synthetic, inspected separately |
| G-12 | Deployment invariant tests pass; installed hashes match; no publication/restart |
| G-13 | Pass: motion guard and complete normal/system/Always browser checks |
| G-14 | Production components at `/design?workflow-home`; existing builder/images/run states remain on `/design` |
| G-15 | Not applicable: no migration or deployment |
| G-16 | Not checked: no physical iPhone claim or new user acceptance invented |

C1–C16 remain guarded by the tests listed in QA §1, all passed where automated
in this complete invocation. C7 uses server and browser capture checks; C12/C13
also use passing legacy-import/deployment tests from `make check`. C8 retains its
existing native-answer limitations: a fake browser pass is not a new real-model
Web qualification. C10/C16 browser and keyboard results are emulated, not a
physical phone or VoiceOver acceptance.
VoiceOver remains outside the work list; the historical failure remains a limit.

## Test-diff ledger

| File and test | What changed | Why | Behavior still asserted? |
|---|---|---|---|
| composer-workflows: acceptance retry/saving/unsent draft | Open sidebar Workflows, choose the named template, return through real browser history | Tabs removed and home introduced | Yes: exact retry seed/key, no chat request, save cancellation, selected model and restored draft/focus |
| composer-workflows: automatic count/retry | Builder URL becomes `/workflows/new?template=brief_images` | Fixed builder moved | Yes: three automatic seeds, exact uncertain retry payload and review pause |
| composer-workflows: cancellation/same saved chat | Sidebar trip and real history return; actual restored URL replaces the removed tab href assertion | Requested navigation replaced the tab | Yes: cancel result, same chat ID and draft |
| images: durable close/reconnect/version/exports/removal | Leave through sidebar New chat instead of removed Back to chat | Images joins shared shell | Yes: real navigation away; saved job recovered and remaining assertions retained |
| workflows: creative and recording execution | Enter the new builder URL | Existing template UI retained at its new route | Yes: review, reconnect, variants, save cancellation, source retention and exact explicit parameters |

## Screenshots and preservation

New synthetic screenshots and axe summaries are in
`artifacts/workflow-studio/ws-a/browser/`, for 390/1440, light/dark, Chromium/WebKit.
States: empty, loading, populated, error/retry, reconnecting, run loading and run
unavailable. Existing synthetic workflow/image/source/review fixtures remain.

`baseline-and-isolation.json` verifies all 15 supplied source/reference files
against the original untracked documents, plus the installed 97-file server and
410 current-release static hashes. One initial manifest lookup mistook frontend
source hashes for installed server files and failed before mutation; the corrected
server manifest verifies. Original main's untracked source documents remain intact.
Archival retains 992 fresh outputs, restores 952 earlier tracked files byte for
byte, and moves 40 new fake settings captures into this namespace. New archived
screenshots receive a fake suffix if the historical test name omitted one.
Final verification confirms 20853 historical evidence/eval Git blobs,
280 frozen product/test files and 15 provided files unchanged after archival.
The installed 97-file server / 410 current static hashes still match.
The first per-file Git lookup was interrupted to batch metadata; its replacement
checks every historical blob, with no mutation during either verification. No old native report, eval input, threshold or answer is regraded.

## Open questions / next checkpoint

Review WS-A before WS-B, as required by the supplied spec. The existing approval
covers user-authored block calls and lazy `@xyflow/react` with attribution on this
branch. Next is the additive graph engine with immutable run snapshots, typed
references, private-source propagation, safe joins/reuse and byte-identical legacy
template parity. No new canvas dependency is needed before that review.
The live app and main remain unchanged until Jake's final okay.

## Isolated preview

`http://127.0.0.1:5173/workflows` serves this managed worktree against the separate
fake app on 18787 and fake runtime on 18080. It uses synthetic data; it is not the
Tailscale/live app. No production data is connected. Source, tests, build and
reviewable evidence are on the GitHub branch. This checkpoint is ready for WS-A
review; physical iPhone checking and final merge/deployment remain unapproved.
