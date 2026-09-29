# Evaluation v3: prepare a real document test

The existing 24-question set is a development diagnostic. Its four documents produce seven
passages, fewer than the retriever's eight-result limit. It cannot measure search quality or
whether Agentic recovers evidence that Fixed missed. Keep its scores out of automatic routing.

## Build an isolated library

Choose documents that resemble actual use. The target is 100–300 documents and at least 2,000
current passages, including long PDFs, tables, near-duplicates, and two versions of at least
one document. The builder accepts Markdown, text, DOCX, and PDF, and never changes the live
workbench library:

```bash
PYTHONPATH=src python scripts/build_evaluation_corpus.py \
  --db .data/evaluation-v3.db --source-dir /absolute/path/to/test-documents
```

Files in a source directory get paths relative to that directory. For a versioned document,
provide a JSONL manifest instead (paths are relative to the manifest):

```jsonl
{"path":"snapshots/guide-old.pdf","logical_path":"guides/guide.pdf"}
{"path":"snapshots/guide-current.pdf","logical_path":"guides/guide.pdf"}
```

The second line becomes the current version. Keep the source files and the frozen database,
and record their hashes. The same embedding model, parser, and chunk settings must be used
through a comparison round.

## Label questions before comparing models

Target at least 150 questions. Include simple lookups, tables, follow-ups, multi-document
questions, second-hop questions whose missing fact does not share words with the original
question, and questions the library cannot answer. Each answerable case needs a short exact
quote and its logical document path. Use `split: "dev"` for cases you can inspect and tune on;
reserve `split: "locked"` for the final comparison. Do not inspect individual locked failures
while changing prompts or code.

```jsonl
{"id":"guide-limit","question":"What limit does the current guide set?","collection":"evaluation","scopes":["private"],"split":"locked","category":"table_lookup","answerable":true,"required_quotes":[{"logical_path":"guides/guide.pdf","quote":"Exact passage from the current guide"}]}
```

Run the preflight before a model comparison:

```bash
PYTHONPATH=src python scripts/audit_evaluation_corpus.py \
  .data/evaluation-v3.db examples/evaluation-v3.jsonl --strict
```

The audit checks size, both splits, gold quotes against current documents, duplicate questions,
PDF presence, and version coverage. It reports what is missing; passing it still requires a
human review of the question labels and whether each quote actually supports the expected
answer. A matching quote proves provenance, not entailment.

Use `compare --split dev` while developing. Run the locked split only after the route, model,
and prompts are frozen, then compare paired cases with failures and latency included. Do not
turn automatic model selection on from the current tiny test set.
