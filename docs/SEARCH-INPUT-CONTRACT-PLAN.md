# Proposed next Search checkpoint: verify the input to a transformation

11 October 2026. **For review; no implementation or inference authorized by this
document.** The corrected bounded trial is in `SEARCH-REPAIR-RETEST-REPORT.md`.

## Why change the approach

The native planner returns a valid `transform` plan for a page whose text is not
supplied. The added generic instruction does not correct this first case. The
server accepts the task label without checking whether the requested material
exists in the available context. The answer then skips the web evidence entirely.
Changing more wording alone does not provide that missing check.

Investigate one isolated **input-reference contract**, keeping the existing one
planner and one answer call. Before claiming this will work, freeze and test the
actual source, schema, prompts and host checks. This is a proposed behavior/schema
change, requiring the next reviewed scope; it is not part of today's retest.

## Concrete requirements

1. Build a host-owned inventory of actual supplied material from the selected
   conversation branch, quoted/body text, document attachments and transcript
   outputs. A request, title, URL or filename alone is not the material it names.
   Use opaque references and bounded previews, respecting existing context limits
   and recording/web protection. Do not re-read private inputs into eval logs.
2. Require a proposed transformation to identify its available input. The host
   verifies the reference and any selected text range against the original
   content. It rejects unknown references, invented text and a missing resource
   passed off as supplied content. A whole instruction must not automatically
   qualify as the text to transform.
3. Keep literal transformations working, including unquoted short translations
   such as translating a supplied word. Treat those as literal input, distinct
   from transforming an external document. Preserve quoted URLs as text when
   the user asks to edit that text. No report/person/topic keyword exceptions.
4. If an external resource's content is missing, use the existing lookup/fallback
   path rather than accepting an unsupported transformation. Use the existing
   query budget and utility call; do not add a repair call, retry loop, verifier
   model, agent, routing mode or provider. Preserve creative/math/conversation
   behavior and unset answer sampling.
5. Verify follow-up references against what was actually supplied: “summarize
   your previous answer” can have an input; a previous refusal to access a manual
   does not supply that manual. Attachments need first-class references: currently
   the planner receives raw message text while answer context adds file/transcript
   bodies. Fixing text-only cases must not break uploaded-document summaries.

An existing message ID or an exact substring alone cannot prove that the selected
text is the requested document's content. **Reference validation is not a general
semantic guarantee.** The distinction between an earlier answer, a title and a
missing resource must be demonstrated in prospective cases. If a reliable rule
cannot be established, retain the failure and report the limitation.

## Qualification before product changes

- First test host resolution and rejection offline with synthetic quoted text,
  unquoted translation, supplied documents/transcripts, absent pages, title-only
  mentions, earlier answers, earlier refusals, stale/unknown references and mixed
  requests. This checks plumbing, not model compliance.
- Freeze one candidate implementation/schema/prompt and the complete real-runtime
  order before inference. Preserve original targets, original 25 cases/corpus,
  this 24-case suite and every failed trial. Any additional ambiguity cases form
  a separate declared corpus, with a held-out split before candidate inference.
- Reuse the corrected native wire/trace validation. Measure both arms on identical
  evidence; review identity, time, source support, injection exposure and missing
  information separately from regex/lexical scores. Do not reinterpret the
  abstention regex discrepancy as an identity hallucination or silently regrade it.
- Stop at protocol, mandatory candidate/support or G9 failure. Qualification still
  requires the three original-suite candidate runs at 25/25, unchanged E12/G9
  comparisons, live Web and repository/browser release checks. No new exemption.

No dependency, model/runtime download, default change, extra model call, production
deployment or Research restart is proposed. Images remains held. After Search and
the Images release gates pass, review Images on the phone, then W1 ordered drafts
with explicit models and human review of factual output. Broader agents remain
later scope.
