# 7B test changes

- `server/tests/fake_runtime.py`: additive answer fixture for requests containing
  Library passages. It returns text from the first synthetic selected passage
  and numeric citations, with an uncited directive. Existing ordinary/chat/web
  branches and embedding behavior are unchanged. No assertion is removed.
- New `server/tests/test_library_answers.py`: 15 cases covering one answer call,
  exclusivity, privacy, failures, stop, historical citations, scoped vector
  completeness, budgets, a deletion between retrieval and snapshot storage,
  and the approved prompt refinements anchored to the original plan/hash.
- New `server/tests/test_library_eval.py`: three grading guards covering exact
  numbers, citations, selected pages, the 34-case distribution and safety checks.
- New `web/tests/library-answers.spec.ts`: 14 browser cases across both engines;
  phone/desktop layouts and light/dark themes; cited answers, sources, deleted
  originals, notices, disabled control and ten design states. Development fixes
  corrected a wrong localStorage theme key and coarse-pointer tooltip expectations.
  The final run asserts actual `data-theme` values and exposes mobile disabled
  reasons through the scope popover as well as the control's accessible description.
- Existing frontend unit/browser test files are unchanged. Five existing design
  fixtures gain `library_enabled: false` to satisfy the additive response type.
- Existing prompt, API, migration, sampling and core tests retain their assertions.
- `server/tests/test_prompt_hashes.py`: a new assertion freezes Library version
  3; the existing Phase 3 hash test remains unchanged. Before/after Library
  reports are linked in `docs/PHASE-7-REPORT.md`; no original hash is relaxed.

Focused runs are development evidence. The final complete suite passes in one
invocation: 431 passed and three existing skips, 37.5 minutes (`e2e.txt`).

- Full-run fixture isolation correction: the new Library fixture now sets
  server-backed appearance theme/font/size/motion explicitly before navigation.
  Earlier Settings tests legitimately persisted dark theme, overriding the
  localStorage light hint and failing both light cases. The `data-theme`
  assertion, every interaction, timeout and accessibility check are unchanged.
  No production behavior changes. The failed/interrupted run remains in
  `e2e-theme-isolation-failure.txt`; a new complete run is required.

- Preview accuracy correction: new Library design fixtures now omit answer
  citations/sources in searching, empty and failed states, omit inline citations
  and mark sources uncited in the uncited state, and show disabled controls for
  missing prerequisites. Removed the duplicate standalone citation demonstration.
  New state assertions check these distinctions, in addition to the existing axe
  and keyboard checks. No existing core test, timeout or assertion was weakened.
  The interrupted run at 183 passes is retained and not counted as a full pass.

- Touch-target correction: both new Library buttons now have 44-pixel targets,
  and the composer toolbar wraps when needed. A new 320-pixel case in both
  engines asserts their dimensions/bounds with a reasoning model, Send bounds,
  and no horizontal page overflow. Existing core assertions and timeouts remain
  intact. SPEC G6 requires 44×44 touch targets; the former compact widths did
  not meet that requirement. The interrupted run is retained separately.

- Existing tablet picker test remains completely unchanged. A full-run failure
  measured only 0.99814 viewport intersection after shrinking the viewport. The
  product now leaves one existing spacing unit below Radix's computed maximum
  height to avoid subpixel clipping. This is a geometry fix, not an assertion
  tolerance or timeout increase. The precise source of the rounding is unproven.
