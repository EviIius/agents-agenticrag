# Phase 6: transcript clean-up, glossary, and more runtimes

**For:** Codex · **Depends on:** Phase 5 accepted (6A can run earlier; it has no dependency on Phase 5) · **Reads with:** `docs/TRANSCRIPTION-SPEC.md`, `docs/SPEC.md` §C5–C6, `QA-REQUIREMENTS.md`

Both halves of this phase are already designed in the repo's own specs and were deferred. This document proposes them; each checkpoint requires Jake’s authorization. It records what has changed since those specs were written, and adds the regression gates.

| Checkpoint | Adds | Designed in |
|---|---|---|
| 6A | Transcript clean-up and glossary editing ("T2") | `TRANSCRIPTION-SPEC.md` §6, §7, §8.3, §8.4, §10, §11 |
| 6B | A second runtime kind beside Ollama | `SPEC.md` §C5, §C6, Appendix A |

**Stop for review after each.**

---

**Scope gate:** the Ollama-only amendment remains in force. Do not implement 6B until Jake explicitly selects and approves a second runtime.

## 1. Checkpoint 6A: T2

Build T2 exactly as `TRANSCRIPTION-SPEC.md` describes: §6 (procedure, prompt, guard, what the user sees), §7 (glossary routes and format), the T2 parts of §8 and §10, and acceptance criteria T-AC15, T-AC16 and T-AC17. The database columns (`cleaned_text`, `cleanup_status`, `cleanup_json`) and the `cleanup.progress` event schema already exist from T1.

### 1.1 What changed since that spec was written

Apply these on top of it. Where they conflict with the spec, these win.

| Topic | Then | Now |
|---|---|---|
| Engine location | Separate repo; deployment folder to be decided | Vendored at `transcribe/`; installed at `~/.local/share/workbench/app/transcribe` (AGENTS amendment, 3 October) |
| Glossary file | "the path the engine reports in `doctor --json`" | Still the rule. In production that path is inside the installed app. `scripts/deploy.py` already preserves installed private engine assets; **add a deployment test** proving a glossary edited through the UI survives a redeploy. |
| Re-transcribing with new terms | Always possible | Only when audio was kept. Audio is temporary by default, so the glossary editor's note reads: "New terms apply to recordings you add from now on. To apply them to an older recording, add it again." Jake delegated retry visibility on 5 October. Keep the T1 "Transcribe again" entries visible and disabled when `audio_available` is false, with the re-upload explanation; enable them only when audio is available. |
| Reference guard | `docs/transcription/cleanup_guard.py` | Port it to `server/app/transcribe/cleanup.py` and move `cleanup_guard_cases.json` to `shared/`, as §6.1 says. Once the unit test asserts every vector, remove `cleanup_guard.py` and `cleanup_guard_cases.json` from `docs/transcription/`; leave `engine.patch`. |
| Model for clean-up | "the one selected in the composer" | Unchanged, plus: clean-up runs only on a **local** connection (the `recording_requires_local` check from `runs/context.py`). This matters once 6B exists. |

### 1.2 Rules that matter most

- The clean-up prompt in §6.2 is used exactly as written. A change needs before-and-after evidence, as for the §E4 and §E8 prompts.
- Clean-up is the one model call T2 adds. `AGENTS.md` already lists it as allowed.
- One call per chunk, no retries, no second model, no judge (§6.1 step 6).
- Clean-up never blocks chat: it takes the connection semaphore between chunks, the way `runs/titles.py` does.
- The glossary is personal. Its content never enters Git, logs, fixtures or screenshots. Tests use `transcribe/glossary.example.txt` or invented terms.
- Every T2 state goes on `/design`, built from the production components (Phase 4 rule).

### 1.3 Acceptance

T-AC15, T-AC16 and T-AC17 from `TRANSCRIPTION-SPEC.md` §11, plus:

| ID | Criterion |
|---|---|
| P6-AC1 | Every vector in `shared/cleanup_guard_cases.json` passes in Python. |
| P6-AC2 | With clean-up running on a 12-chunk synthetic transcript, a chat message sent to the same model starts streaming before clean-up finishes (integration test with the fake runtime). |
| P6-AC3 | Cancelling clean-up leaves `text`, `raw_text` and segments byte-identical (hash before and after). |
| P6-AC4 | A glossary saved through `PUT /transcription/glossary` survives `scripts/deploy.py` (deployment test in a temp directory). |
| P6-AC5 | All T1 tests still pass unchanged: upload, transcribe, review, download, ask, the web guard, audio retention and clearing. |
| P6-AC6 | Privacy audit clean (QA G-11). |

Report as an addition to `docs/PHASE-T-REPORT.md` under "T2 checkpoint".

---

## 2. Checkpoint 6B: a second runtime

### 2.1 Decision first

| ID | Decision | Why it blocks |
|---|---|---|
| J6 | Which runtime will Jake actually run beside Ollama: **LM Studio**, a local **OpenAI-compatible** server (MLX, llama.cpp, vLLM), or a **hosted** OpenAI-compatible endpoint? | §C5 rule 7: fixtures before code. Do not write an adapter that cannot be recorded against a real instance. Build only what J6 names. |

If J6 is "none for now", skip 6B. Nothing later depends on it.

### 2.2 What to build

`SPEC.md` §C5's table is the specification for each runtime kind: listing, capabilities, loaded state, load and unload, chat streaming, context, reasoning in and out, images, usage, finish reasons, JSON for utility calls, timeouts, error mapping and the retry-once rule for rejected optional fields. §C6 covers the registry. Follow them as written. Add `embed()` for OpenAI-compatible servers (`POST /v1/embeddings`), since `Adapter` now includes it.

Order of work:

1. `make record-fixtures` against the real runtime named in J6; save raw streams under `server/tests/fixtures/providers/` (plain text, reasoning, image, length stop, unknown model, model listing).
2. Adapter, tested against those recordings.
3. Registry and schema changes below.
4. Web changes below.
5. `/design` states and screenshots.

### 2.3 Ollama-only assumptions to remove

These crept in after the 1 October "Ollama only" amendment. Each must become runtime-neutral without changing Ollama's behavior.

| Where | Today |
|---|---|
| `providers/registry.py` | `adapters: dict[str, Ollama]`; constructs `Ollama(...)` directly. Becomes a factory keyed on `connection.kind`, typed as `Adapter`. |
| `providers/registry.py`, `providers/ollama.py` | Messages say "The Ollama connection is disabled or missing", "Choose an available Ollama model", "Cannot reach Ollama". Use the connection's name. |
| `schemas.py` | `ConnectionCreate.kind`, `Connection.kind`, `Detection.kind` are `Literal["ollama"]`. Widen to the three kinds the `connections` table already allows. |
| `api/connections.py` | Detection probes Ollama only. Add the J6 runtime's default address. `api_key` is accepted and never returned. |
| `web/src/components/app/Welcome.tsx`, `LiveAppShell.tsx` | "Looking for Ollama…", a hard-coded "Ollama" row, "Start Ollama on your Mac: `ollama serve`"; the shell's `onAdd` posts `kind: "ollama"` regardless of what was detected. |
| `web/src/components/app/ModelPicker.tsx` | Group heading fallback and footer mention Ollama (the trigger is fixed in Phase 4). |
| `web/src/components/settings/LiveSettings.tsx` | "Ollama runs locally on your Mac."; "Keep alive" shown for every connection (it is Ollama-only). |
| `web/src/lib/errors.ts` | Connection name defaults to "Ollama". |
| `README.md`, `AGENTS.md` | State that only Ollama is in scope. Add the amendment below. |

### 2.4 Behavior the UI must get right

- **Unknown is a real state.** A runtime that cannot report whether a model is loaded yields `loaded: null`. The picker already prints "Status unknown"; it must also hide Load and Eject for that model. Never guess.
- **Capabilities come from the runtime or from the user.** For OpenAI-compatible servers they are unknown; Settings › Models offers the per-model overrides the schema already has (`vision_override`) and the same for reasoning if the user turns it on. No name matching.
- **Context that is fixed at load** (LM Studio): changing it offers "Reload with N" rather than sending it per request.
- **Remote connections are labeled.** If a connection's host is not loopback, show a small "Remote" label beside the model name in the top bar and in the picker group. Recordings already refuse to go to a non-local connection; Phase 7 applies the same rule to library text. The tagline "Your models. Your Mac." should not be shown next to a remote model: hide it in the empty state when the selected model is remote.

**`AGENTS.md`, append:**

> **User amendment (Phase 6, date):** runtime kinds beyond Ollama are in scope again, limited to the kind(s) Jake named in J6, per `SPEC.md` §C5–C6 and `docs/next/PHASE-6-TRANSCRIPTION-T2-AND-RUNTIMES.md`. This supersedes the 1 October "Ollama only" amendment. Fixtures are recorded from the real runtime before adapter code is written.

### 2.5 Acceptance

| ID | Criterion |
|---|---|
| P6-AC7 | Ollama is unchanged: adapter tests against the existing recorded fixtures pass without edits; `parameters.spec.ts` request captures are identical; `make eval-web` offline replay matches baseline. |
| P6-AC8 | The new adapter passes against fixtures recorded from the real runtime; the recording command and date are in the report. |
| P6-AC9 | Sampling parameters the user did not set are absent from requests to the new runtime (request capture). |
| P6-AC10 | A rejected optional field is retried once without it and remembered in `connections.flags_json`; any other 400 is not retried (unit test). |
| P6-AC11 | A model with `loaded: null` shows "Status unknown" and no Load or Eject control (E2E, both engines). |
| P6-AC12 | A recording chat refuses a remote connection with `recording_requires_local` (existing test extended to the new kind). |
| P6-AC13 | First-run detection finds both runtimes when both are running, and works when only one is (E2E with the fake runtime's two protocols). |
| P6-AC14 | No string in the UI names Ollama unless the connection is an Ollama connection (grep check in `make check`, with an allowlist for the Ollama Search provider). |
| P6-AC15 | All gates in QA §3. |

Report as `docs/PHASE-6-REPORT.md`.

## 3. Not in this phase

Model routing or "Auto". Running one chat across two runtimes. Downloading or pulling models from the UI. API-key vaults beyond the existing private database column. Cloud-specific features (prompt caching, hosted tools).
