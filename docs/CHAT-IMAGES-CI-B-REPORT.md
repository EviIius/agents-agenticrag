# Chat images CI-B report

13–14 October 2026 · isolated `codex/workflow-studio` · baseline `72619f46` ·
source `3825196a` · main and installed application unchanged.

## Summary

Claude's image composer now creates durable prompt/reply turns in the chat.
Migration 013 adds message kind, ordered job links and retained request origins.
Acceptance commits all messages/jobs together before scheduling; uncertain retries
return the original turn. Existing workers, capacity, cancellation and SSE remain
the execution system. Text requests exclude both image roles.

Count, optional fixed seeds, progress, cancellation, retry branches, saving,
details, removal and Gallery links are implemented. Completed frames reveal once
in the session; restored history renders without that motion. Image-first titles
come from the prompt without a title call. No native inference or deployment.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| CI-AC7: additive migration; reload and branches | Passed | `test_chat_images_migration.py`, `test_chat_images.py`; reload/branch browser cases |
| CI-AC8: idempotent uncertain acceptance | Passed | Three concurrent submissions make two messages/three jobs; dropped-response browser case preserves key/seeds |
| CI-AC9: both image roles excluded | Passed | Exact mixed-context test plus 56 before/after payload comparisons over 25 original Web cases |
| CI-AC10: frame states | Passed | `/design?chat-images`; queued/preparing, steps 0–4, decoding, complete, cancellation, failure, interruption, removed and load failure |
| CI-AC11: real progress only | Passed | Fake worker pauses at step 2; no client timer advances steps; reload resumes the same state |
| CI-AC12: reveal once; no history reveal | Passed | Actual animation events counted once; reload counts zero; unit claim guard and reduced-motion checks |
| CI-AC13: sequential counts | Passed | Three linked jobs finish in order; two waiting frames say Next; status reports three outputs |
| CI-AC14: retry branch and scoped cancel | Passed | Retry returns a sibling with new seeds; previous branch restores original jobs; cancel leaves the other turn active |
| CI-AC15: events/snapshot reconnection | Passed | Reload during paused worker; existing EventSource stream/snapshot; no job polling |
| CI-AC16: one composer, drafts, command | Passed | Dropped-response/draft/handoff checks; `/image `; no `ImagesWorkspace` import in Composer |

Full checkpoint verification is recorded below; a fresh native G9 accuracy replay
remains outside this no-inference checkpoint. Do not treat synthetic tests as an
accuracy or physical iPhone pass.

## Changed files

- **Server:** `api/chat_images.py`; migration 013; schemas; `db/image_jobs.py` and
  message hydration; image manifest preparation; context metadata filter; router
  registration; image-regeneration guard. Optional origins/timing grow ImageJob.
- **Web:** unified Composer; separate draft maps; chat image acceptance/events
  hook; ImageTurn/frame/actions; LiveThread integration; Gallery provenance and
  New image navigation; lazy chat-image design preview; CSS motion; generated
  API types and compatibility aliases for optimistic pre-migration text rows.
- **Tests:** new synthetic API/migration/context and image state/browser checks;
  fake worker's paused-step control; approved old image-flow assertions adapted;
  existing migration version assertions incremented from 12 to 13.
- **Documentation/evidence:** execution plan, this report, AGENTS authorization,
  test ledger, source freeze, before/after context proof, rollback/API comparison,
  bundle report and retained browser/check attempts under `artifacts/chat-images/ci-b/`.

## QA gates

| Gate | Result / limits |
| --- | --- |
| G1: full check and coverage | 653 Python / 104 frontend; all required packages above 80%; 110 contrast pairs |
| G2: complete browser invocation | 595 passed, three existing skips, zero failures in one complete invocation (1.0 hour), Chromium + WebKit |
| G3: existing assertions | Retained; explicitly approved UI replacements are listed in the ledger; no lowered timeout/threshold or added skip |
| G4: bundle/performance | Initial JS 246,848 gzip bytes, +2,430 from CI-A; below 256,000 and +8,192. Render p95 2.4 / 3 ms; first-token overhead 74.37 / 67.65 ms (Chromium / WebKit), within unchanged thresholds |
| G5: axe/keyboard | 112 focused new-state axe checks pass in both engines, themes and widths; frame row is keyboard focusable; keyboard/focus semantics retained |
| G6: API only grows | Prior full OpenAPI contract compared during rollback; zero errors; existing requests gain no required fields |
| G7: old rows preserved | Synthetic v12 original-column projections and foreign-key/integrity checks pass; all existing rows become kind=text |
| G8: frozen prompts | Existing prompt hashes pass unchanged; the metadata filter is outside assembler prompt literals |
| G9: Web accuracy | **Not newly qualified.** Context/provider payload parity passes, and search/providers/generate/titles remain unchanged. `make eval-web` uses real Ollama even with recorded web; not run in this no-native-inference checkpoint. Existing native accuracy release gate remains open |
| G10: parameters/context | Ordinary captures preserved; both image roles absent from mixed history; user output overrides have exact payload parity; no new sampling defaults |
| G11: privacy | Synthetic prompts/outputs only; historical inputs and supplied references retained. Final privacy audit passes; synthetic screenshots reviewed by Codex; raw/fresh evidence archived separately |
| G12: service/PWA | Production port/label/route unchanged; installed/main preservation and existing tests retained; 97 server / 410 static hashes unchanged; local and verified HTTPS health pass; production /design remains 404 |
| G13: reduce motion | Both triggers stop develop, sheen, mark and progress transitions; a static completion does not later replay its reveal |
| G14: design coverage | Production frame component at `/design?chat-images`, all 14 frame/step states and counts 1/2/3, plus production composer |
| G15: rollback | Copied synthetic data: candidate schema 13 starts; whole schema-12 backup restored byte-identically; prior source starts; no live service changed |
| G16: physical phone | **Not checked.** Browser WebKit uses phone geometry; no physical iPhone or VoiceOver pass claimed |

## Deviations and limits

The reviewed refinements add retained origins to distinguish a deleted chat from
a standalone Gallery job, and prepare every manifest before the acceptance
transaction. Progress fills with transform, rather than animated width. Timing
comes from durable worker start/finish values, not a cosmetic client clock.

CI-C still owns the viewer, More like this, Refine, Ask about it, image exports,
and phone scroll-snap/dots. CI-B's three-image phone row scrolls and is keyboard
focusable. Gallery creates through a new chat; legacy job lineage remains covered
through its existing API. No native workflow trial, new package/model/runtime,
prompt/default/sampling change, Research restart or main/live promotion.

G9 is explicitly open for native accuracy, as it was in earlier image integration
evidence. The 56 context comparisons prove request equality, not factual accuracy,
semantic grounding, a new model qualification or a repeated real-runtime eval.

## Runtime observations

Used the existing fake engine and worker fixtures. Its step-2 pause is server
controlled; releasing it resumes actual events and output validation. Atomic
acceptance, same-chat text guard, process/capacity ownership, restart behavior and
retained artifacts have synthetic checks. No actual Ollama/image inference here.

Re-inspected Claude's composer/step/phone references and exercised the supplied
prototype's two-image flow. An initial prototype selector used button rather than
menuitemradio and timed out; the correct radio-menu selector succeeds. The
supplied prototype/reference files are unchanged.

## Test output and retained failures

- `make check`: 653 passed / 104 frontend, all coverage gates pass. Source frozen
  at `3825196a`; required coverage log is retained.
- `make e2e`: **595 passed, three existing skips, zero failures (1.0 hour)**
  in one complete invocation on frozen source. No stitched focused result is
  substituted for that run.
- Initial check stopped on one long test assertion. After formatting, another
  complete check had 651 passes and one prompt-hash failure: the new metadata
  discriminator literal was included in the conservative assembler literal hash.
  Moving that metadata traversal to its own helper restores the unchanged prompt
  hash; no baseline or prompt was edited.
- First focused browser attempt: 6 passed, 7 failed, 1 interrupted, 22 unrun.
  Retain errors/traces. Fixed scroll focus and error-button contrast. Corrected the
  test-only worker-release URL and status/card selectors; paused jobs had caused
  dependent failures. Interruption is not a complete run or acceptance evidence.
- Second focused attempt: 34 passed, 2 failed. Fixed the product's consumed image
  mode navigation flag, which reopened image mode after leaving Workflows.
  The same original handoff assertions then pass in both engines.
- First full invocation deliberately stopped after 314 passes, one interrupted
  case and 281 unrun (32.4 minutes). Review found omitted-versus-null parent
  idempotence and missing image-user branch controls. Both are fixed with new
  targeted tests, passing both engines. An explicit parent is now part of request
  identity; returning an existing request never changes the selected leaf. Image
  prompts retain copy/branch controls while text editing is unavailable. This
  interrupted run is not a complete acceptance pass. Its log, frozen source and
  available generated screenshots are retained; its temporary trace/recordings
  were overwritten by the next focused invocation and are unavailable. The final
  run is now fully archived before another browser invocation.
- Fixed-seed focused attempt initially failed twice because Radix correctly hides
  the background from the accessibility tree while its menu is open. The test
  now inspects the actual background button's disabled property; option closing
  explicitly restores composer focus. Both engines pass. The added fixed-seed
  case preserves validation, exact seed payload and two-output completion checks.
- Reveal-focused checks pass in both engines; real animation count is one,
  restored-history count zero. All earlier outcomes remain retained.

## Screenshots and preservation

Synthetic frame/step screenshots: `artifacts/chat-images/ci-b/browser/`, with
state, width, theme, engine and fake suffix. Regenerated historical regression
captures are archived separately, restoring original tracked evidence bytes.
Redundant unchanged copies from the interrupted attempt reference their exact
baseline Git blobs (7,305 files / 1,960,959,222 bytes); changed fresh captures are
retained. No historical or production file was removed.

Videos stay outside Git under `~/.local/share/workbench/qa/chat-images/ci-b/videos`.
Final manifests verify 552 source/test/config files, 323 unchanged core files,
33,141 historical evidence/eval/fixture blobs, 15 workflow reference files and
all 17 supplied chat-image files. Archive retains 1,206 fresh outputs and restores
1,166 historical files; 40 new fake captures are relocated. 584 available final
synthetic videos (76,665,428 bytes) are retained outside Git. A preservation check
before archiving correctly refused modified regression screenshots; restoration
and final verification now pass. The archive helper initially missed the known
CI-A ticker-performance metric; the corrected allowlist archives it without
changing tests or old evidence.

## Open questions for Jake

Review CI-B on this isolated branch before CI-C. Final merge/publication still
needs your explicit okay. The bounded local-LLM workflow proposal is prepared;
it has not run. The fake preview is restored at `http://127.0.0.1:5173`;
`artifacts/chat-images/ci-b/preview.json` links a synthetic two-image chat and
an unrun Studio template. The first template seed used the wrong field name and
was rejected with 422; `template_id` fixes that setup error. Opening the preview
in Codex returned queued, so a visibly opened tab is not claimed.
G9's fresh real-runtime accuracy check remains a separate release
decision; this report does not conceal or waive it.
