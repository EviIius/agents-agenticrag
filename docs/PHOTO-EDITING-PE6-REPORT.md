# PE6 — overlap correction and bounded acceptance report

23 October 2026 · isolated `codex/masked-photo-editing`, draft PR #9.

## Summary

The selection dialog now reviews editable/protected areas before applying them.
One fresh FLUX head edit completes in 21.678 seconds. The corrected selection
allows the brim to cover the intended forehead/hair area and removes the
detached fragment. Protected facial features remain exact. The full photo still
has an inside-mask background seam and imperfect retained-glove finish/coverage.
**Precision-editing release and further native trials are shelved as agreed.**

## Done-when checklist

| Item | Result | Evidence under `artifacts/photo-editing/pe6-20261023/` |
|---|---|---|
| One correction, maximum one new native call | Complete, one consumed | Native result/progress, private append-only reservation |
| Explicit overlap review; read-only until Adjust | Pass | 26 Chromium/WebKit browser checks and synthetic screenshots |
| Preserve mask serialization, Cancel, rejected send and retry | Pass | Existing payload/ownership checks through the new review step |
| Forehead overlap with remaining facial features protected | Pass | CPU preflight, synthetic CPU test and independent RGB audit |
| Resource, health, actual steps, owned reaping and export | Pass | `results.json`, `pixel-audit.json` |
| Whole-photo cap and two-glove quality | **Fails full quality** | Bound private manual review; original/old/new comparison |
| Stop rather than launch another trial | Complete | Single slot exhausted, this closeout and roadmap status |
| Live/source/model preservation | Pass | `preservation.json` |

## Changed files

- Web: `PhotoMaskEditor.tsx` adds Review selection, read-only preview and Adjust
  selection; explicitly explains that an addition may cover existing details.
  The current Paint/Protect, zoom/pan, Undo/Redo and exact selection payload stay
  in use. `/design?photo-edit&state=selection-review` exposes the interaction.
- Browser tests cover the two-step interaction, blocked accidental strokes/
  keyboard undo during review, Adjust/Cancel, existing rejected-send/retry
  identity, and phone controls in both themes. A scoped artifact-directory
  override prevents overwriting the earlier PE2/PE4 screenshots.
- `image_worker/masked_accept/`: one-slot controller/launcher, frozen preparation,
  independent CPU audit and synthetic process/pixel checks. The native FLUX
  worker/recipe is unchanged. No product server/worker is changed.
- Plan, AGENTS closeout and roadmap status. Only synthetic UI captures and
  sanitized measurements enter Git; all actual media/coordinates stay private.

## Deviations from SPEC.md

Jake approved one correction and bounded acceptance check after PE5. Earlier
budgets stay closed. The new controller narrows the PE4 controller to one FLUX
slot; Qwen is undeclared. The native execution, lease, verification and reaping
body is retained. No helper, retry or post-result selection adjustment occurs.

The new protection promise is explicit: the selected forehead/hair region can
be covered, while the remaining visible facial features and every unselected
pixel stay exact. It would be incorrect to claim the entire old face outline
is unchanged: **7,808 pixels within that outline were deliberately allowed to
change and did change.** All 29,561 pixels in the revised visible-feature outline
remain unchanged, including the eyes/nose/mouth area. No automatic face detector
or face-protection model is introduced.

The final whole-photo review combines the single fresh head output with the
predeclared **PE5 FLUX front/rear glove** outputs. Those gloves are retained
earlier generations, not a newly executed three-step workflow or best-of search.
No Qwen output is substituted. This is one task/seed and does not establish
general consistency, coexistence or release qualification.

## Runtime observations

| Measurement | Actual |
|---|---:|
| New native invocations | **1 FLUX; 0 Qwen** |
| Total measured job | 21.678 s |
| Initialization | 1.831 s |
| Generation/decode | 19.434 s |
| Peak MLX allocation | 18,659,198,390 bytes |
| Swap growth | 0 MiB |
| Maximum combined residency/health observation | 0.0152 s |
| Unselected pixels preserved in combined image | 3,010,609 |
| Protected visible-feature pixels changed | **0 of 29,561** |

The 24 GiB MLX / 1 GiB cache / 512 MiB swap-growth and existing time/health
bounds remain in place. MLX measurements are allocations, not total machine
RAM. Actual denoising steps 0–4 complete; owned reaping occurs under the shared
lease. The head export matches the head composite pixel for pixel. The three
regional masks are disjoint; combination changes nothing outside their union.

### Quality judgment by Codex

- **Boundary correction succeeds:** the cap is coherent and the brim stays
  attached instead of losing a front fragment. The forehead overlap was decided
  before generation and the visible facial features stay exact.
- **Full request still falls short:** a circular/tonal background patch remains
  inside the head selection; the retained rear glove has soft, incomplete
  coverage. The new head pass does not erase those existing limitations.
- The prior native result was also reprojected on CPU as a labelled diagnostic,
  using its original context transform. The new selection changes the generation
  crop, so applying it with the wrong old/new transform would be invalid. That
  diagnostic is not counted as a fresh generation or an independent quality pass.

No quality acceptance of this new result is attributed to Jake. Under the agreed
stopping rule, this mixed outcome shelves the precision release and ends native
testing. Ordinary installed image functionality is not removed or republished.

### Storage

The new native/composite/export PNGs total **9,386,557 bytes**. The combined PNG
adds **4,200,615 bytes**, for **13,587,172 bytes** across those four files. This
excludes retained-glove copies, inputs, masks, contexts, metadata and review
media. Sampled job storage is retained separately; logical/inode/kernel counts
are observed measurements, not deduplicated physical APFS usage.

## Test output

- Frontend TypeScript, ESLint, formatting and **132 unit tests pass**.
- **26 focused browser tests pass**, Chromium and WebKit, including both phone
  themes at 390 × 600 and 390 × 750, read-only review, Adjust/Cancel, protection,
  zoom/pan, selection limits, rejected send and retry identity.
- **Two new CPU/process tests pass:** a synthetic forehead-occlusion/visible-
  feature invariant and one-slot success/exhaustion/undeclared-Qwen refusal.
  The initial one-test controller run also passes and is retained separately.
- The first CPU mask candidate intersects the protected-feature polygon and is
  refused before any native invocation. Narrowing the brush and reviewing hair
  coverage produces the final frozen 20-stroke mask. These are CPU-only
  preparation iterations; no selection changes follow the fresh generation.
- Build, motion rules and **110 contrast token pairs pass**. Initial JS is
  **255,961 / 256,000 gzip bytes**; the dialog remains lazy loaded.
- Native process, resource, source/output binding, direct RGB preservation and
  export checks pass. All source/input/model/installed preservation and local/
  normally verified HTTPS health checks pass. Ollama remains 0.35.0.
- Initial new Python import-order formatting is corrected before freezing.
  Full `make check` and the full browser suite were not rerun; targeted checks
  above are evidence for this isolated correction, not a production release.
  Product-wide gates remain necessary before any later cherry-pick/merge.
- No new physical iPhone or VoiceOver pass is claimed.

## Screenshots

Synthetic captures under `browser/` include painting and overlap review in light/
dark Chromium/WebKit phone layouts. Real originals, selection/feature overlays,
old-native diagnostic, fresh head and combined photo are kept only in the private
review at `http://127.0.0.1:8773/review.html`, served on loopback.

## Open questions for Jake

No further image trial is needed for this checkpoint. Precision editing is
shelved; keep the branch/evidence and both model checkpoints. Main and the live
app are unchanged. The next roadmap review can consider the supplied themes
checkpoint and the narrow recording-folder workflow pilot, each under its
existing decision/permission boundaries. No theme patch, schedule, agent trial,
new model call, merge or deployment is started by this closeout.
