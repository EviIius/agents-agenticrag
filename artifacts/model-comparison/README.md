# Approved model comparison evidence

These files contain only synthetic everyday/Library tasks and recorded public
Web evidence. No actual recordings, private Library files or transcript text
were used. Model weights and credentials are not included.

The human approved the named Qwen 3.8 download, an isolated 32K profile and three
matched pairs on 8 October 2026. Research remains shelved. Production prompts,
sampling, APIs, deployment and the default model are unchanged.

## Inputs and execution

- `../../docs/model-comparison/frozen-inputs.json`: frozen input hashes.
- `preflight.json`, `pull.json`, `installed-model.json`, `baseline-show.json`:
  observed runtime, installed digests and packaged model parameters.
- `smoke-*.json`, `smoke-review.json`: four ordered smoke checks and manual review.
- `pairs.json`: declared order, every attempt, elapsed time and residency snapshots.
- `pair-*-everyday.json`: complete answers and actual app answer payloads.
- `pair-*-streams.jsonl`: retained Web/Library request payloads and stream events.
- `pair-*-review.json`: human-style semantic review by Codex, without model judges.
- Original Web/Library reports remain under `server/evals/{web,library}/reports`.

Everyday score and grounding are separate: satisfying an arithmetic rubric does
not excuse an extra unsupported assertion. A numeric 4.0 satisfies the declared
numeric quantity just as 4 does; strings, booleans and malformed JSON do not.
Automated citation and lexical checks are retained, including their limitations.
The public corpus is historical comparison evidence, not a live freshness oracle.

## Retained setup failures

The first Web child failed its import path before a Web model call. The second
used an incorrect historical fixture root; its 10/25 result is retained and marked
setup-invalid, rather than counted as a matched comparison. The orchestration
pause used to correct that root interrupted the initial Library run before its
final report. Its 39 completed synthetic answers were recovered read-only into
`pair-1-baseline-library-interrupted.json`; its missing final benchmark prevents
qualification. Full valid Web and Library runs followed with the frozen intended
corpus. No quality failure was retried into a pass.

Raw stream retention was added after that interruption. Evaluator-only final
unload is skipped to avoid forcibly ejecting a user's model. Live inference and
transcription activity are checked before each suite. Snapshots are not peak
memory measurements; first stream delta can be reasoning rather than visible
answer text. Three pairs do not establish statistical significance.
