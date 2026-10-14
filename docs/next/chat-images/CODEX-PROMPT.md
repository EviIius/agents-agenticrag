# Prompts to paste into Codex

One checkpoint at a time. Each prompt assumes this folder is at `docs/next/chat-images/` in the repository, including `prototype.html` and `reference/`.

Give Codex your decisions from `CHAT-IMAGES-SPEC.md` §E first. CI-A needs J-I1 and J-I2. CI-B needs J-I3, J-I4 and J-I5.

---

## CI-A: the working indicator

```text
Read AGENTS.md, docs/next/QA-REQUIREMENTS.md, docs/next/PHASE-4-POLISH-AND-MOTION.md (C1–C4),
then docs/next/chat-images/CHAT-IMAGES-SPEC.md (all of it). Open
docs/next/chat-images/prototype.html in a browser and send a message with Search and Think on;
look at reference/indicator-*.png. Match that look and motion. Where the prototype and the spec
differ, the spec wins.

Build checkpoint CI-A only (Part B). Stop with docs/CHAT-IMAGES-CI-A-REPORT.md using the SPEC §H4
template plus QA §8, with evidence for CI-AC1 to CI-AC6 and every gate.

My decisions: J-I1 = <Playful / Plain> by default. J-I2 = <yes / no>.

Rules that matter most here:
- Web only. No server file changes, no new dependency, no new model call.
- Replace WaitingDots with WorkingLine and AtelierMark (built from web/public/icons/mark.svg).
  Do not use any other company's logo.
- Real stages always win over status words: queued, loading model and the live search step
  label come first. Status words appear only while waiting for the first token.
- The thought ticker shows the model's own reasoning text from reasoning.delta, rAF-batched.
  No summarizing call. Thinking starts closed.
- Screen readers hear phase changes only; words and ticker are aria-hidden.
- Motion in web/src/styles/motion.css with stroke-dasharray, transform and opacity only.
  Everything stops under both reduced-motion triggers. performance.spec.ts thresholds unchanged.
- Every new state on /design. Screenshots use synthetic data and "fake" in the file name.
```

## CI-B: image turns in the chat

```text
Read AGENTS.md, docs/next/QA-REQUIREMENTS.md and docs/next/chat-images/CHAT-IMAGES-SPEC.md Part A,
§C and §D. Read server/app/images/ (jobs.py, engine.py), server/app/api/images.py,
server/app/runs/context.py, migration 009, web/src/components/chat/Composer.tsx and
web/src/components/images/ImagesPage.tsx first. Open prototype.html, switch on Image, create two
images, and look at reference/composer-*, image-* and phone-*.

Build checkpoint CI-B only. Add the AGENTS.md amendment from §E first, with today's date and only
the parts I approved. Stop with docs/CHAT-IMAGES-CI-B-REPORT.md (§H4 plus QA §8), evidence for
CI-AC7 to CI-AC16 and every gate.

My decisions: J-I3 = <yes / no>. J-I4 = <yes / no>. J-I5 = <yes / no>.

Rules that matter most here:
- Additive only: one migration (next free number) adding messages.kind and message_images; new
  routes; optional new fields on Message. G-6 and G-7 must pass.
- Image turns are excluded from text-model context. Golden capture for an ordinary chat is
  unchanged, and a new capture proves image turns are absent.
- Progress comes only from ImageJob state and completed_steps over the existing
  /api/images/events stream. No client timer advances progress. Never poll.
- POST /api/chats/{id}/images is idempotent per request key; seeds are resolved before sending.
- The develop field and reveal use transform and opacity only; reveal plays once, only for images
  finished in this session.
- Remove ImagesWorkspace from the composer. The Gallery keeps working and links back to chats.
- No new model call: image-first chats are titled from the prompt.
- Image prompts in tests and evidence are synthetic; use server/tests/fake_image.py.
```

## CI-C: viewer and iteration

```text
Read docs/next/chat-images/CHAT-IMAGES-SPEC.md A5, A6, A8 (export) and §D, and look at
reference/viewer-*.png and the prototype's viewer (click a finished image; use the arrow keys).

Build checkpoint CI-C only. Stop with docs/CHAT-IMAGES-CI-C-REPORT.md (§H4 plus QA §8), evidence
for CI-AC17 to CI-AC22, the motion videos in §D2 and every gate.

Rules that matter most here:
- The viewer is the existing Radix Dialog with a FLIP transform from the clicked frame, 320 ms,
  and it closes back to that frame. Focus returns to the frame.
- More like this and Refine create new turns with parent_id set to the source job.
- Ask about it appears only for models that report vision and uses the existing attachment path.
- Phone: three images in a scroll-snap row with dots; actions always visible; swipe and pinch in
  the viewer (WebKit at 390 px).
```
