# Workflow Studio implementation review

12 October 2026 · baseline `dce4c49` · isolated branch `codex/workflow-studio`

## Assessment

The redesign is a sound direction. A persistent sidebar and shared shell resolve
the duplicate navigation and make Workflows and Images ordinary destinations.
The home page, canvas, Blocks panel and Inspector establish a clear desktop
editing flow. Outline plus a settings sheet is a practical phone editing flow.
The prototype is a visual and interaction reference; production execution must
continue to use durable server state, explicit model choices and the existing
capacity lease.

The five checkpoints are a useful sequence: WS-A navigation, WS-B graph engine,
WS-C editing, WS-D run controls, WS-E knowledge and logic. Each remains a review
stop. The live app and main checkout stay on the accepted build until Jake's
final approval. WS-F extras and autonomous Research are outside this work.

## Reference review

Read README, CODEX-PROMPT, the complete Workflow Studio spec and prototype source,
alongside SPEC and QA requirements. Visually inspected all eleven supplied fake
screenshots: home, chat without tabs, Studio, both Inspectors, Quick add, writing,
paused and complete runs, phone Outline and Inspector sheet. The supplied files
are retained without modification.

Codex exercised the prototype in Chromium: zoom, tidy, undo, insertion on a
connection (8 → 9 nodes), Run, approval pause and completion, theme and reduced
motion. At 390 px the initial Outline opens its Inspector sheet and insertion
adds a ninth row. Palette drag creates a ninth node. These are simulated runs;
no native model, image or transcription work was invoked.

The inspection also retained three harness limitations: an initial attempt to
read `doc` failed because the prototype encloses it in an IIFE; the first phone
selector used `.ol-node` rather than `.ol-row`; a separate attempted node move
did not change its style, and the follow-up second Undo was disabled. Port-drag
confirmation did not follow that failure. This is not a claim of complete
prototype interaction qualification. Production canvas behavior needs WS-C tests.

The prototype's timer-driven progress, fake data, abbreviated prompts, model-name
formatting, partially functional settings and toast-only commands are not product
implementations. External Google Fonts are not carried into the app.

## Required engine refinements before WS-B

1. **Execution order and identity.** §11.1 uses canvas position to break
   topological ties, while §11.3 excludes positions from the execution hash.
   Moving blocks could change invocation order without changing that hash.
   Use a stable order independent of layout for execution; layout order remains
   a presentation concern. Test parallel-ready blocks and both legacy templates.
2. **Snapshots and seeds.** A snapshot keyed only by `(def_id, graph_hash)` cannot
   preserve distinct full layouts with the same execution graph. Separate the
   immutable run snapshot identity from the execution fingerprint. Resolve
   automatic seeds once after idempotent request lookup, save them, and reuse
   exactly on uncertain acceptance and retry.
3. **Output reuse.** A block config hash alone does not prove its prior output
   still applies. Reuse requires identical resolved inputs, model settings,
   original source identity/version and upstream dependencies. Invalidate the
   affected descendants and branch decisions; refuse an incomplete reuse plan.
4. **Skip and joins.** Disabled outgoing paths are defined as not taken. Preserve
   that explicit behavior rather than silently bypassing nodes. Validate fallback
   edges, unreachable required references, inactive branches and join readiness.
   Distinguish structural skip from a user decision to continue after failure.
5. **Old-client compatibility.** The legacy run schema parses its `input_json`
   as `WorkflowCreate`. Graph inputs have a different shape. Define a compatible
   legacy endpoint projection or separation before storing graph runs, so old
   cached clients, export/source routes and snapshots keep working. Migration
   010 has no state CHECK constraint; the issue is typed legacy parsing, not SQL
   prohibiting `skipped`. Preserve the old POST execution path and payloads.
6. **Multiple private sources.** One legacy `source_json` is insufficient for a
   graph with multiple transcripts or documents. Keep originals independently,
   with durable typed references and provenance; do not overwrite an earlier
   original. Propagate private-source restrictions through all downstream blocks,
   including Compose, approvals, conditions and user-edited values.
7. **Typed outputs.** Image/audio references are not arbitrary text substitutions.
   Resolve typed inputs and Save results separately from text templating. Preserve
   literal values, original timestamps, escaping and exact optional-line behavior
   required by the legacy parity test. No silent truncation or hidden prompt text.

These refinements should be recorded as WS-B implementation decisions and verified
before proceeding to the builder. They do not require a new agent, model, package
or app-authored prompt. Classification evaluation targets and the future motion
guard amendment retain their specific review gates.

## WS-A boundaries

Only the two existing templates are offered. Blank/custom workflow creation,
definition CRUD, future templates and fake saved definitions are absent until
their server support exists. Recent runs show ten entries from the existing
snapshot/SSE; All runs truthfully shows its current latest-50 limit. The current
builder remains at `/workflows/new?template=…`; a run opens its existing review,
source, retry, cancel and save card. Sidebar auto-collapse waits for WS-C.

No server, API, migration, prompt, sampling, default, application dependency or
native invocation changes belong to WS-A. `@xyflow/react` and user-written block
calls are approved only on this isolated branch for their later checkpoints.

## Remaining qualification limits

The graph architecture makes execution repeatable and recoverable; it does not
qualify factual model outputs. Existing meeting-pack failures remain documented,
and those outputs remain drafts for human review. Research stays shelved.
Physical iPhone checking of this redesign has not occurred. VoiceOver remains
outside the current work list, with its historical failure retained.
