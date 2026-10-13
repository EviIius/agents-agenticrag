# Chat images implementation review

13 October 2026 · supplied plan based on main `dce4c49` · isolated implementation
follows Workflow Studio WS-D; main/live publication still needs Jake's final okay.

## Assessment and decisions

Claude's design is a sound improvement: one composer, durable image turns and
existing jobs/SSE rather than a second mini-app. The waiting line uses Atelier's
own mark and actual reasoning/stage events. Retain the supplied appearance and
interactions. The prototype simulates inference and images; production must use
the existing engines and durable state.

Use the recommendations already included in the execution request: Playful with
Plain available, closed reasoning with a live ticker, saved image turns, both
image roles excluded from text context, and image-first titles from the prompt.
No new packages, models or model calls. CI-D extras remain gated.

Read the three supplied documents and prototype source; inspected all thirteen
reference images and exercised text reasoning and image creation in Chromium.
The supplied files remain byte-identical, with their initial hashes retained.

## Implementation refinements

1. **Waiting words cannot predict a token.** The proposed 400 ms pre-phase freeze
   is not observable from the existing stream. Apply real stages immediately;
   cancel a cosmetic transition when a real phase arrives. Never delay tokens.
2. **Acceptance must be atomic.** Existing job submission schedules work after
   committing its own rows. Chat acceptance needs a preparation path: commit
   request identity, both messages, all jobs and their ordered links together,
   then schedule workers. A lost response must resolve to the same turn/jobs.
3. **Deleted-chat provenance needs retained origin.** Cascading message-image
   links alone lose the distinction between a deleted chat and a standalone job.
   Keep a small origin/request record in the same additive migration. Preserve
   Gallery-owned files when chats or message links are deleted.
4. **Branches and context are separate.** Image messages remain ordinary tree
   ancestors for navigation; exclude both roles before text context construction.
   Prove mixed text/image histories and unchanged ordinary request captures.
   Coordinate acceptance with the existing same-chat text-run guard so an active
   answer cannot be displaced by an uncertain image submission.
5. **History and live reveals differ.** Only images observed completing in the
   current session may reveal. Restored history renders immediately; decode/load
   failure, removed files and interrupted jobs remain explicit states.
6. **Motion rules still apply.** Use transform-based progress fill, preserving
   real completed-step values. Activity drift is decorative, never a preview or
   fabricated progress. Both reduced-motion triggers stop every loop/transition.
7. **Refine records lineage.** This scope regenerates from an edited prompt;
   parent ids do not enable reference-image editing. Vision attachment requires
   runtime-reported vision support and an explicit Ask about it action.

## Sequence

CI-A is web-only and ends with its H4/QA review. CI-B adds the durable turns,
acceptance APIs and composer/card integration; migration 013 is next after WS-D's
012. CI-C adds viewer/iteration/export. Each retains its report and review stop.
The named optional features in CI-D need a later concrete scope.
