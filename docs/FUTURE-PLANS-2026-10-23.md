# Future plans — themes, motion and useful local automation

23 October 2026. Jake asked to add the supplied ideas document and Theme Lab
to future plans while the approved corrected-mask comparison continues.
This records proposals, not implementation, installations or external actions.

## Current order

1. **Photo-editing trials closed:** PE5 compares focused regions; PE6 fixes brim
   overlap with one fresh acceptance generation. Full quality still falls short,
   so precision-editing release/further trials are shelved as Jake requested.
   Preserve the isolated branch/results and both installed checkpoints; ordinary
   live image tools remain. See `PHOTO-EDITING-PE6-REPORT.md`.
2. Review the themes checkpoint and the narrow local-workflow pilot below.
   Adding these ideas does not restart the stopped agent/Research trials or
   supersede the existing automation plan.
3. Add capture, notifications and scheduled work in individually reviewed scopes.
4. Consider messaging, browser tools, voice and desktop use after measured pilots.

## Themes and motion: TH1 / TH2

Source: `next/themes/README.md`, `THEMES-SPEC.md`, `CODEX-PROMPT.md` and
`aether-themes.patch`. The supplied ZIP is a compiled, static Theme Lab; the
patch is the integration source. The attached ideas document is broader than
the patch (for example, custom accents and computer use are future proposals).

- **Seven palettes:** Cobalt, Lime, Paper, Ember, Orchid, Midnight (dark only),
  Mono. Palette and light/dark mode are separate choices. Vivid fills and
  readable text/link accents have distinct tokens.
- **Theme motion:** multilingual greeting, theme-specific mark/status words,
  send entrance and circular theme switch. Keep input usable throughout;
  system/Always reduced motion must produce a still final greeting.
- **Integration:** synced palette/greeting preferences, before-paint appearance,
  theme icons/manifests, Settings and `/design?themes` coverage.
- **Pending decisions:** J12/J13 (palette/language choices), **J18** (decorative
  greeting up to 4.5 seconds outside the one-second settle rule), **J19** (named
  `theme-reveal` clip-path exception), **J20** (Newsreader across Paper's UI).
  The supplied prompt's suggested yes values are not Jake's authorization.
- **Checkpoint:** isolated `codex/themes-th1-th2` branch, product review before
  merge/publication. Palette foundation and optional motion exceptions can be
  reviewed separately. Preserve the current rules until decisions are explicit.

### Readiness observed here

`git apply --check` succeeds on the current `codex/masked-photo-editing` tree
(`028b73c1` before this planning work). The patch was **not applied**. A clean
patch check is not a runtime, visual, payload or release pass.

The source changes `server/app/db/settings.py`; it is not solely web work.
An approved release must include compatible server/web preference handling.
The supplied report claims 148 unit tests, 855 contrast pairs and Chromium
checks; those are Claude's results, not independently reproduced here.

Required integration evidence: fresh full check and fake-runtime browser suites
in Chromium/WebKit; every palette/mode at phone/desktop sizes; Paper menu and
sidebar fit; persisted/synced settings; no first-paint flash; reduced motion;
greeting duration/input readiness; and real iPhone/PWA review. Check bundle cost
and lazy loading: the current editor branch entry was already 255,964 of the
256,000 gzip-byte budget. Do not hide unrelated motion failures by broadly
excluding animations from `settle()`.

Verify Safari/icon/tinting behavior on the actual installed phone/browser before
presenting removal/re-addition of the Home Screen app as a required user step.
No icon, font, theme preference, motion guard or deployment changes happen now.

## Local-AI backlog

| Scope | Useful first version | Gate / decision before implementation |
|---|---|---|
| Capture (CAP) | Explicit screenshot/region attach from a Mac or iPhone Shortcut; preview before send | Named endpoint/permission scope, cleanup policy, measured vision capability and latency; no inference from model names |
| Workflow triggers / Night shift (NS) | Chosen folder → transcribe → summary/actions → chosen local output; then bounded schedules | Existing `LOCAL-AUTOMATION-NEXT-STEPS.md`: durable deduplication, stable-file detection, restart/catch-up policy, capacity limits, pause/cancel and output review |
| Notifications | Run finished or needs approval | Explicit subscription, no unchanged-state noise, Home Screen/device tests; not a Codex automation created by this note |
| Helper model / visible routing | Show actual model and reason; consider faster titles/planning | Frozen matched task/payload/speed/resource evidence and named model-call approval; no automatic model switch |
| Runtime/speed experiments | Evaluate proposed Ollama/MLX/MTP variants in isolation | Verify availability, runtime-reported capabilities and compatibility first; named upgrade/download scope; keep live fallback |
| Memory across chats | Readable, editable, deletable user facts with provenance | Consent, per-chat inclusion controls, correction/deletion and backup behavior; no silent extraction |
| iMessage drafts (IM1) | Draft-and-approve for a selected thread | Separate bridge/dependency and narrowly granted permissions; no Messages database access or sends now; thread binding, duplicate handling and explicit Send/Edit/Skip |
| iMessage auto-reply (IM2) | Optional later allowlist | Separate authorization after a useful draft pilot; exclusions/rate limits/quiet hours, kill switch, disclosure decision and verified send history |
| Browser use (BU) | Separate browser profile, read page text first; reviewed actions | Qualified loop/task evidence, explicit tools/time/step limits, safe sessions and submit approval; vendor benchmarks do not qualify Aether |
| Desktop use (CU) | VM-only feasibility pilot | Named software/download/license/resource scope; measured tasks and written go/no-go before real desktop access |
| Voice (VOICE) | Push-to-talk, optional local speech output | Named engine/dependency trial and phone latency/cancellation QA; distinct from the previously removed VoiceOver work |

## Claims to verify before trials

The supplied ideas document's version numbers, model/MLX/MTP availability,
computer-use scores, speed rankings, VM sizes, Apple browser support and Messages
automation details are research leads. They have not been independently verified
in this checkpoint. Source links and candidate names do not establish that an
installed model supports image/tool inputs or that it performs these tasks well.

Use current primary sources and measured Mac tests when each scope is selected.
Keep stopped Hermes/PydanticAI/native-loop/Research outcomes intact; their
frameworks or vendor benchmarks do not supply a production qualification.

## Provided material

- Repository source set: `docs/next/themes/` (supplied untracked files preserved).
- Local ideas Markdown and `Aether Theme Lab.zip`: read-only reference copies in
  Downloads; content hashes recorded in the comparison checkpoint's
  `future-plan-inputs.json`. The ZIP was listed and its entry HTML inspected,
  without executing its JavaScript or attaching it to the live origin.
- Existing priority/automation notes: `APP-DIRECTION-AND-WORKFLOWS.md` and
  `LOCAL-AUTOMATION-NEXT-STEPS.md`.

No roadmap item above creates an unattended run, grants account/app permissions,
installs a dependency, amends motion rules or authorizes another model call. The
separate PE4/PE5/PE6 native allowances are exhausted.
