# 6A test-diff ledger

Compared with `47f2389`, no existing test assertion, timeout, skip or performance
threshold changed. Seven new server tests and eighteen new browser cases were
added. The four initial glossary failures used the wrong role in a new test;
the corrected navigation button interaction passed in both engines and widths.

| Existing support file | Additive change | Old behavior retained |
|---|---|---|
| server/tests/fake_runtime.py | Exact utility-prompt response and invented rejected chunk | Ordinary chat/search directives retained |
| server/tests/fake_transcribe/bin/transcribe | Invented cleanup/cancel fixtures, glossary in synthetic engine prompt | Existing directives retained |
| server/tests/serve_app.py | Glossary path inside isolated temporary data | Existing engine/runtime server preserved |
| scripts/privacy_audit.py | Phase 6 evidence scan and synthetic-name checks | Existing privacy checks retained |

The frozen T1 disabled retry controls remain visible after audio removal.
Jake delegated the plan conflict: “Do what you think is best.” AGENTS and the
6A plan document the chosen behavior; no old retry assertion was changed.
