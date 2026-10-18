# Native agent loop

- `NATIVE-AGENT-LOOP-PLAN.md`: Claude's original supplied proposal, unchanged.
- `../../NATIVE-AGENT-LOOP-REVIEW.md`: source/evidence review and corrections.
- `../../AGENT-LOOP-N0-REPORT.md`: isolated implementation and QA checkpoint.
- `../../AGENT-LOOP-N1-PLAN.md`: frozen bounded trial and scope resolution.
- `../../AGENT-LOOP-N1-REPORT.md`: original result, stopped at four native calls
  after H02's per-bullet citation failure; not qualified.
- `../../AGENT-CITATION-COVERAGE-REPORT.md`: offline detector catches the four
  missing bullet citations; 47 tests pass; candidate was then tested separately.
- `../../AGENT-CITATION-COVERAGE-PLAN.md`: original prepared C1 scope.
- `../../AGENT-C1-RETEST-PLAN.md`: approved C1 execution contract.
- `../../AGENT-C1-RETEST-REPORT.md`: **latest result — failed and stopped after one
  call**. The model skipped available retrieval; no answer gain is established.

N0 is implemented; N1 and C1 have run and stopped under their first-failure rules.
Hermes and PydanticAI evidence remains preserved. End this candidate and retain
the existing single-shot Search/Library product. No further prompt/framework
campaign, N2/N3, main merge or deployment follows automatically.
