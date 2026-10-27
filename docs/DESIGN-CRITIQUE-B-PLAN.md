# Part B — truthful chat and controls

25 October 2026. Jake said “cotinue” after Part A was merged and published.
Work on `codex/design-critique-b`, leaving main and the installed app unchanged.
Follow B1–B9 in the supplied critique, with J22/J23 already approved.

## Implementation boundaries

- Existing schema 14 retains image references and exposes no-store previews.
  Reuse these endpoints; no migration is needed. Original filenames were never
  stored, so historic edits say “Edit photo · Photo reference”. Cleared or damaged
  inputs remain visibly unavailable; do not manufacture a thumbnail or original.
  Compare the normalized reference used by the engine, labelled as such.
- Default edits apply only inside image mode, to the visible branch's last image
  reply, with its thumbnail shown before send. Ordinary text sends remain text.
  Create image is an explicit escape to generation. No cross-branch fallback.
- Continue and Retry require a user click; use existing answer request paths.
  Continue names its parent explicitly and does not consume draft attachments.
- Model grouping uses runtime family metadata, never tag-based capabilities.
  Preserve stored display names. The exact Qwen display alias requested in B4 is
  a presentation mapping only; unknown tags remain literal, and eval variants
  are not automatically hidden. Existing stored visibility preferences apply.
- Chat controls retain unset sampling, presets, system prompts, reasoning and
  configured context limits. Thinking appears only in Tools; “Max” sends the
  unchanged runtime value `xhigh`. One Save commits only changed setting groups;
  failure leaves the remaining draft dirty and retryable.
- Feature starters invoke existing attachment/Library flows. Recent prompts are
  derived from existing history on demand, not a separate browser history store.

## Verification and review

Synthetic component/design states and browser assertions cover provenance,
reference clearing, Create/Edit, branch switching, stopped/empty replies,
explicit continuation, parameter preservation, controls saving/rejection, model
variants and feature starters. Retain earlier evidence and every failure. Record
all changed existing tests in the ledger; no weakened assertions or thresholds.
Run make check and one full make e2e, both engines, plus applicable QA gates and
390/1440 light/dark screenshots. Native inference is not part of this checkpoint.
Stop with H4 and a draft PR before merge or publication. Physical iPhone and
installed Safari review remain pending; no VoiceOver pass is claimed.
