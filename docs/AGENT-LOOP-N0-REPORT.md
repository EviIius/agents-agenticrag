# Native agent loop N0 report

18 October 2026 · isolated branch `codex/native-agent-loop` · baseline `e7ffea2b`.

## Summary

Claude's native-adapter recommendation fits Aether's current scope. N0 implements
the dormant loop with the existing Pydantic and native Ollama transport. No real
model requests, packages, production activation, main merge or deployment occur.
The engineering checks below do not establish better answers or faster inference.
The assessment and plan corrections are in `NATIVE-AGENT-LOOP-REVIEW.md`.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Native tool payloads, calls and tool-result history | Pass, scripted | `test_agent_records.py`, `test_agent.py` |
| Ordinary requests unchanged, unset sampling absent | Pass | Existing `test_phase4_guards.py`; saved-answer baseline parity |
| Pydantic argument contracts and host permissions | Pass | `test_agent_tools.py`, `test_agent.py` |
| Six steps, bounded tools, 180 seconds and 70% estimated context | Pass, scripted | `test_agent.py`; at most one closing call inside the deadline |
| Connection/native capacity released during tools | Pass | Cancellation and semaphore cases in `test_agent.py` |
| Stop/Answer now/restart preserve text and ordered steps | Pass, scripted | `test_agent.py`; persisted parts and SSE replay |
| Stable issued source references and missing-citation flag | Pass, structural only | `test_agent.py`; no semantic qualification claimed |
| New v1 prompt frozen; old prompts unchanged | Pass | `test_agent_prompt.py`, existing frozen-prompt tests |
| All 240 historical streams parsed | Pass, no new qualification | `recorded-stream-replay.json` |
| Additive migration and previous-version rollback | Pass, synthetic | `test_agent_migration.py`, `rollback-attempt1.txt` |
| No new dependencies or production wiring | Pass | Dependency hashes and source/diff audit |
| Complete browser regression | Pass | `e2e-attempt1.txt`; one full invocation, both engines |

Artifacts named without a directory below are under `artifacts/agent-loop/n0/`.

## Changed files

- Server: native provider tool support; optional digest and message metadata;
  migration `014_agent_parts.sql`; message persistence and interrupted-step
  recovery; new `runs/agent.py`, `agent_tools.py`, `agent_sources.py`,
  `agent_prompt.py`.
- Web: generated API types only. No new setting, screen, component or send hook.
- Tests: synthetic native transport, contracts, budgets, permissions,
  cancellation, persistence, migration, frozen prompt, 240 saved streams and
  25-case/28-turn saved-answer transport parity.
- Tooling/docs: synthetic rollback rehearsal, original plan, review, report,
  isolated AGENTS authorization and retained execution artifacts.

## Deviations and boundaries

- N0's zero-model-call rule takes precedence over G-9's `make eval-web`, which
  still makes real Ollama calls even with offline retrieval. Instead, replayed
  all 25 saved web cases/28 turns through baseline and candidate transports:
  payload bytes and emitted events match. **This is not a fresh quality eval or
  full G-9 model-evaluation pass.** Production promotion remains gated.
- The hard deadline starts no closing call after expiry. A closing call after a
  step/context/Answer now stop uses only the remaining time. At expiry, partial
  output and metadata remain; no notice is appended to model content.
- Real web/Library handlers, DNS-pinned fetching, beta fallback and UI belong to
  N2/N3. N0 injects synthetic handlers; its URL syntax guard alone is not a full
  SSRF defense. The loop is not registered in the production generation path.
- The supplied plan's broad AGENTS paragraph was narrowed to N0. N1 model calls,
  a changed H04 fixture mapping, model admission, N2 timing changes and tag
  removal have not been approved or executed.

## Runtime observations

No new native-runtime behavior or model answer was observed. Tests use opaque
synthetic model metadata and scripted HTTP transports. The parser replay retains
the original 240 streams, including their original failures; parsing them does
not qualify another model digest. A socket audit guard refused connections to
native-runtime ports during validation. Actual native request admission/counting
must be instrumented separately in N1; `AgentInfo.calls` conservatively counts
attempted turns, including a turn waiting for native capacity.

## Test output

- Full `make check`: **798 Python, 126 frontend tests**, 110 contrast pairs;
  lint, format, mypy/TypeScript, coverage, API additive, motion and privacy pass
  (`check-attempt3.txt`). Baseline: 721 Python / 126 frontend.
- Focused final checks: **81 passed** (`focused-attempt5.txt`).
- Full `make e2e`: **719 passed, three unchanged skips, zero failed**, all 722
  scheduled tests in one Chromium/WebKit invocation (1.2 hours,
  `e2e-attempt1.txt`). No focused rerun substitutes for that run.
- `make build` and bundle measurement pass: **254,964 gzip bytes**, unchanged
  from accepted main, limit **256,000** (`build-attempt1.txt`, `bundle.json`).
- Initial failed commands are retained: the new helper initially supplied a
  duplicate client to an existing fixture; later lint/type checks found a long
  assertion and inferred type/default issues. The new helper/code was repaired;
  no existing assertion, timeout, performance target or skip was weakened.

Coverage from the complete check: providers 90.4%, runs 93.0%, search 89.8%,
transcribe 93.2%, documents 96.6%, Library 92.6%, images 90.0%, workflows 89.3%,
backup 93.8%, capacity 96.6%. The new loop is inside the existing runs target.

## Gates

| Gate | Status and evidence |
|---|---|
| G-1 | Pass: complete `make check`, counts and coverage above |
| G-2 | Pass: 719 passed / three existing skips / zero failed in one full invocation |
| G-3 | Pass: only schema-version assertions changed; ledger below |
| G-4 | Pass: unchanged bundle and all browser performance limits; measurements below |
| G-5 | Pass: complete axe/keyboard browser checks and contrast; no new UI |
| G-6 | Pass: API additive guard and generated types |
| G-7 | Pass: all previous column/row hashes preserved on the populated fixture |
| G-8 | Pass: new prompt hashes and unchanged existing hashes |
| G-9 | Limited: exact saved-answer transport parity; no fresh native quality eval |
| G-10 | Pass: original golden and baseline/candidate byte parity |
| G-11 | Pass: synthetic inputs, privacy guard; generated fake-browser outputs archived privately |
| G-12 | Pass: server invariants and complete PWA browser checks; installed hashes/health unchanged |
| G-13 | Pass: complete motion browser checks; no motion source changed |
| G-14 | No new UI state in N0; tool rows/settings remain N3 |
| G-15 | Pass: synthetic 14 startup and restored 13 previous-app startup |
| G-16 | Not checked for N0; no deployment or phone result invented |

## Test-diff ledger

| Existing file | Change | Why | Behavior retained? |
|---|---|---|---|
| `test_foundation.py` | Schema version 13 → 14 | Additive migration 014 | Yes; foundation checks unchanged |
| `test_documents.py` | Schema version 13 → 14 | Same migration | Yes; document and preservation assertions unchanged |
| `test_folders_backups.py` | Schema version 13 → 14 | Same migration | Yes; folder/backup assertions unchanged |
| `test_workflow_graph_storage.py` | Schema version 13 → 14 | Same migration | Yes; graph storage and original rows unchanged |
| `test_chat_images_migration.py` | Schema version 13 → 14 | Same migration | Yes; image-turn data and schema assertions retained |

## Budgets

| Metric | Original requirement | Previous recorded reference | N0 |
|---|---|---|---|
| Initial JavaScript | ≤256,000 B | Accepted main 254,964 B | 254,964 B; +0 |
| Streaming render p95 | ≤8 ms | Chromium/WebKit 1.3 / 2 ms | 3.1 / 3 ms |
| First-token render overhead | <150 ms | 100.98 / 61.14 ms | 65.75 / 67.31 ms |
| 300-message scroll median | <20 ms | 16.7 / 17 ms | 16.7 / 17 ms |
| Native inference / new packages | N0: 0 / 0 | — | 0 / 0 |
| Future N2 time targets | Median ≤90 s / p90 ≤200 s | Original targets | Unchanged; proposed 120/240 unapproved |

Browser reference values are the measurements stored at HEAD, not a fresh paired
performance experiment. Current tests render only the streaming row at 100
tokens/s with 300 history messages. Scroll p95 is 16.8 / 19 ms. Full raw values
and the recorded references are in `performance/summary.json`.

## Core unchanged

All rows below pass in the complete code/browser invocations. C8 retains the
explicit fresh-model-evaluation limitation in G-9; existing answer outcomes have
not been regraded or relabeled.

| Core | Evidence |
|---|---|
| C1 send/stream/stats | `chat.spec.ts` |
| C2 Stop/partial text | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 reconnect/resume | `chat.spec.ts`, `web.spec.ts` |
| C4 long answer/idle timeout | `chat.spec.ts` |
| C5 branches/history actions | `actions.spec.ts` |
| C6 load/select/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 explicit parameters | Python captures pass; `parameters.spec.ts` |
| C8 web/citations | Python search tests and saved-answer parity pass; `web.spec.ts` |
| C9 transcription/storage | Python tests pass; `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts` |
| C10 phone layout | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 shortcuts/PWA | `polish.spec.ts`, `pwa.spec.ts` |
| C12 legacy import | Pass: complete Python suite, read-only/idempotence checks |
| C13 deployment identity | Pass: `test_deployment.py`; no deployment performed |
| C14 untrusted content | Python SSRF tests pass; `foundation.spec.ts` |
| C15 performance | `performance.spec.ts`, chat frame/first-token checks |
| C16 accessibility | `foundation.spec.ts`, `review.spec.ts`, `phase3-accessibility.spec.ts` |

## Migrations and rollback

014 adds `messages.parts_json` (default `[]`) and nullable `agent_json`. No old
column/table is rebuilt or removed. The migration test projects and hashes every
previous column before/after and checks integrity, foreign keys and idempotence.

Rehearsal command: `PYTHONPATH=<private QA guard> UV_FROZEN=1 uv run --directory
server python ../scripts/rehearse_agent_rollback.py`. It creates synthetic
schema-13 data, backs it up with SQLite, boots candidate 14, restores the backup
and boots source `e7ffea2b`. Both health checks return 200; all 50 original
synthetic table projections remain. Elapsed **1.236 s**. No live database or
installed file is involved. Evidence: `rollback-attempt1.txt`.

## Evals and screenshots

Saved-answer web transport replay: 25 cases, 28 turns, byte-identical payloads and
equal events (`web-replay-parity.json`). Native stream parser replay: 240 saved
streams (`recorded-stream-replay.json`). New prompt hashes: `prompt-hashes.json`.
Neither changes the old cases, reports, grades or their qualification outcomes.
No fresh answer-quality, speed or N1 result is claimed.

No new product state exists to screenshot in N0. Complete-suite screenshots use
isolated fake data. All 1,617 changed historical generated files and 40 new
historical-path outputs are copied with verified hashes to the private QA
archive; old tracked evidence is restored byte-for-byte. No new screenshots are
committed. The archive manifest is `historical-evidence-preservation.json`;
new coverage and performance results remain under this checkpoint.

## Source and live-app preservation

`preservation-final.json` verifies all 191 frozen tested candidate source files,
548 accepted main source files, 114 installed server files and 425 installed
static files. The reproduced candidate build matches the same 425 static hashes.
All four dependency manifests/locks are unchanged. Normally verified local and
Tailscale HTTPS health checks return `ok: true`; no TLS bypass is used.

Hermes `4acc379f` and PydanticAI `d596ad53` remain unchanged. Their stopped private
ledgers retain four and 18 aggregate calls respectively; 18 includes the earlier
four Hermes calls, not 18 PydanticAI-only calls. Guarded N0 QA attempted zero
connections to native runtime ports. No new native qualification or production
activation is claimed.

## Known limitations and next review

- Structural citations do not prove claim support, relevance or completeness.
- N0's scripted controls do not qualify the everyday model or real retrieval.
- Existing title-before-first-send overwrite and misleading workflow search copy
  remain follow-ups, not hidden as agent work.
- VoiceOver's historical reported failure remains unresolved and outside this
  work list. The 3 October keyboard issue recovered after an iPhone restart;
  its cause was not established. No new phone claim is made.
- Review N0 before N1. Proposed N1 uses the daily 32K profile, ≤36 calls, two
  six-case series, first required failure stops. Resolve the H04 Library-only
  fixture mapping and experimental model admission first. Keep original quality
  targets and stopped trials. N2 real retrieval and N3 product integration remain
  separate decisions.
