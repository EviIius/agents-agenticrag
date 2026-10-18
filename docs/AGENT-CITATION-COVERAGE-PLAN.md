# Offline agent citation coverage checkpoint

18 October 2026 · continuation of failed native N1, not a reset of its ledger.

## Scope and acceptance

1. Build an isolated pure detector for obvious uncited Markdown list items and
   table data rows when issued sources exist. Scan each item's own text: a parent,
   introduction, heading, sibling or table header citation must not cover it.
2. Ignore examples in code, quoted material and ordinary headings; handle wrapped
   items, nested items and separate paragraphs within an item conservatively.
   Link labels, escaped brackets and unknown IDs are not valid issued citations.
3. Return explicit diagnostics; never label an answer supported or qualified.
   Sentence-level and semantic claim support remain outside this detector.
   Prose or unsupported Markdown must not be described as a citation pass.
4. Demonstrate an optional metadata warning on a **copy** of a completed native
   message. Preserve content, reasoning, parts, status, stats and existing notices.
   Ordinary chats and incomplete messages do not acquire an agent warning.
5. Replay both retained N1 answers without model calls. H01 should produce no
   obvious structural gap; H02 must identify all four uncited bullet items.
   Retain hashes and old grades unchanged. This is detection, not answer repair.
6. Use synthetic positive/negative fixtures covering local citation scope, code,
   escaping, links, tables and no-source/calculator answers. No new package.

The prototype stays under `experiments/native_coverage/`. Application source and
the original N1 harness remain frozen. No UI, new migration, deployment or fresh
native call occurs. The source-kind prompts already require per-item citations;
they are not rewritten in this offline checkpoint.

## Unexecuted candidate for a later bounded retest

Detection alone cannot improve native answers. Prepare **one** generic v2 agent
prompt candidate: append this format reminder after the otherwise unchanged v1
agent prompt and its existing source-kind rules:

```text
Write each factual list item with its own inline citation at the end of that item.
Citations in a heading or introductory sentence do not cite later items.
Apply the same rule to each factual table row.
```

This adds no topic, source ID, example fact, sampling value, tool or model call.
Freeze both web/Library candidate hashes separately from v1. Do not modify the
old prompt files or disguise the old failure as a candidate result. The candidate
is unexecuted; it may fail. No structured selector or separate answer call returns.

**Proposed retest C1, not executed/authorized by this offline checkpoint:**

- New independent, durable stopped-on-failure ledger; never reset N1's four calls.
- At most 36 native calls on the same exact installed 32K profile, model-default
  thinking, no sampling overrides, unchanged runtime and shared scheduler.
- Same frozen original six tasks, H04's predeclared Library-only mapping, two
  ordered series. First required failure stops all further native calls.
- Preserve v1 answer baselines. Check the actual wire v2 hash on every request;
  no quiet prompt edits or automatic retries. Include the new detector, original
  required facts/references and manual assertion/support/citation review.
- Require 12/12 full passes, H05 injection refusal and H06 unsupported-information
  refusal, original budgets and zero sampled swap growth. Detector acceptance
  alone is insufficient. No quality/time target is loosened.
- If C1 fails, retain its result and recommend keeping single-shot Search/Library
  as the product. No further prompt/framework campaign follows automatically.
- A pass permits only review for N2's separately budgeted real-retrieval tests.
  It does not authorize app activation, a main merge or deployment.

## Parsing limits and references

This is a conservative structural detector, not a full Markdown parser or a
factual-sentence classifier. A cited bullet can still contain unsupported text
or multiple sentences with inadequate citation placement. Complex containers,
HTML, math and ambiguous Markdown need separate handling; no absence of gaps
proves completeness. Non-factual lists may be flagged because the detector does
not infer which statements are factual.

Parser edge cases are informed by the primary
[CommonMark list rules](https://spec.commonmark.org/0.31.2/#list-items) and
[GFM table rules](https://github.github.com/gfm/#tables-extension-).
No standards-conformance claim or copied spec examples are made.

Stop with H4 evidence and the concrete C1 plan before any native retest.
