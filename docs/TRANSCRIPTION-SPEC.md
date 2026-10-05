# Workbench: audio transcription (Phase T)

**Upload a recording in the chat, get a transcript, then ask the local model about it.**

| | |
|---|---|
| Version | 1.0 · 3 Oct 2026 |
| Written by | Claude, for Jake |
| Built by | Codex |
| Extends | `docs/SPEC.md` (still the main plan; this file adds one phase to it) |
| Written against | `agents-agenticrag` branch `rebuild` at `b5fd739`; `Transcription` repo v0.1.0 |
| Ships with | `docs/transcription/engine.patch`, `cleanup_guard.py`, `cleanup_guard_cases.json` |

> **Codex:** everything in `docs/SPEC.md` and `AGENTS.md` still applies. This file adds **Phase T**. Where it changes a SPEC rule it says so in §3, and nowhere else. Build it in the order in §11 and stop at each checkpoint with the §H4 report.

---

## 0. Prompt to paste into Codex

```text
Read docs/SPEC.md, AGENTS.md and docs/TRANSCRIPTION-SPEC.md completely before writing any code.

Build Phase T from docs/TRANSCRIPTION-SPEC.md. It has two checkpoints: T1, then T2. Stop after each
one and give me the §H4 report as docs/PHASE-T-REPORT.md, with evidence for every T-AC in §11.

Start with §3 (add the amendments to SPEC.md and AGENTS.md verbatim), then §4 (the engine patch,
in the separate Transcription repo at ~/Documents/GitHub/Transcription).

Rules that matter most here:
- No new Python or npm packages. The transcription engine is an external program run as a subprocess.
- Never commit a real recording, its filename or any transcript text: not in fixtures, tests,
  artifacts, screenshots, reports or logs. Use the fake engine, or recordings made with macOS `say`.
- The only new model call is transcript clean-up (§6), and only in T2.
- Do not start Phase 3 work. Do not change Phase 2 search behaviour except the guard in §5.11.
- If the real engine behaves differently from §4, record what you saw and stop to ask.
```

---

## 1. What this adds

Workbench today accepts images and small text files as attachments. Phase T adds a third kind: **audio**. Transcription is done by the existing `Transcription` repo (called "the engine" below), which already works on this Mac from the command line.

```text
Composer: (+) › Add recording, or drop / paste a file
   │  POST /api/attachments            streamed to disk, never held in memory
   ▼
transcripts row "queued"  ──►  one job at a time
   │  <engine>/bin/transcribe run <file> --out-dir <scratch> --quiet
   ▼
transcript saved in workbench.db  ──►  SSE: transcription.done
   │
   ├─ chip: "20:45 · 3,412 words · ≈6.1K tokens"   open, copy or download the transcript
   ├─ send a message: the transcript goes to the local model with that message
   └─ (T2) "Clean up with {model}": punctuation and paragraphs, checked word for word
```

The phone path needs nothing extra: Workbench is already reachable over Tailscale Serve, so attaching a recording from the phone is the upload route.

**Measured on this Mac (CLI, 2 Oct):** a 20 min 46 s recording (717 MB, 48 kHz, 24-bit, 4 channels) transcribed in 28 s.

**How long a recording fits in a chat** (estimates, at about 150 spoken words a minute and the §C8 budget):

| Model context | Tokens available to the prompt | Speech that fits |
|---|---|---|
| 16,384 | about 12,000 | about 45 minutes |
| 32,768 | about 24,300 | about 90 minutes |

Longer recordings still transcribe and can be read and downloaded; they can't be sent to a model that small (§5.10).

## 2. Decisions already made

Jake can change any of these before handing this over. Codex should not.

| # | Decision | Why |
|---|---|---|
| 1 | The engine is **called as a subprocess**. Its code is not copied into Workbench or imported. | One implementation of the audio handling, glossary and Whisper flags, with its own tests. No new dependency (§C1). |
| 2 | Transcription starts **at upload**, not when the message is sent. | The transcript is useful on its own, and the context meter and overflow check need the text before sending. |
| 3 | The original audio is **kept** with the chat and deleted when the chat is deleted. | A recording uploaded from the phone may exist nowhere else. It also allows re-transcribing. |
| 4 | **Web search does not run** in a chat that contains a recording (setting, default on). | The search planner sees earlier answers, which would summarise the meeting. Queries built from them would leave the Mac. |
| 5 | Clean-up is **manual** and guarded by code, never automatic. | It is an extra model call and can change meaning. The guard keeps any section whose wording changed. |
| 6 | **One** recording is transcribed at a time. | The engine takes a lock anyway, and Whisper shares the GPU with Ollama. |
| 7 | The engine's location is an **environment variable**, not a setting in the app. | A path to a program must not be editable through the web API. |
| 8 | Real recordings and transcripts **never enter the repo**. | The recordings are work meetings. |

## 3. Amendments to SPEC.md and AGENTS.md

Add these verbatim as the first step of T1.

**`docs/SPEC.md`**, after the last "User follow-up" block at the top:

```markdown
**User amendment — 3 October 2026 (Phase T):** Add local audio transcription as specified in
`docs/TRANSCRIPTION-SPEC.md`. Audio becomes a third attachment kind. Transcription runs through
the separate `Transcription` repo as a subprocess, found through `WORKBENCH_TRANSCRIBE_HOME`; no
packages are added. One model call is added to the allowed list: transcript clean-up, started
only by the user. Web search does not run in a chat that contains a recording unless the user
turns that protection off. Real recordings and transcript text are never committed, logged or
used as fixtures. Phase T is independent of Phase 3 and does not start it.
```

**`AGENTS.md`**, replace the model-call rule and add two lines under "Hard rules":

```markdown
- No extra modes/agents/model calls. Allowed model calls: answer, search planner, title,
  transcript clean-up (TRANSCRIPTION-SPEC §6).
- Transcription runs the external engine at WORKBENCH_TRANSCRIBE_HOME as a subprocess. No new packages.
- Never commit, log or screenshot a real recording, its filename or transcript text.
```

The spec sections this phase extends: §B3 (the "voice output" non-goal stands; audio *input* is now in scope), §C2 (new `server/app/transcribe/` and `db/attachments.py`), §C3, §C4, §C8, §C9, §C12, §D8, §G4 and §H2. Each is covered below.

---

## 4. The engine (separate repo: `~/Documents/GitHub/Transcription`)

Do this part in the `Transcription` repo, as its own commit there.

### 4.1 Changes

1. **Restore `.gitignore`.** It is missing from the copy on this Mac. Create it with the content below. Then run `git ls-files config.json glossary.txt .python models`; if anything other than `models/.gitkeep` is listed, untrack it with `git rm --cached` and tell Jake, because `glossary.txt` holds internal system names.

   ```gitignore
   config.json
   glossary.txt
   .python
   models/*
   !models/.gitkeep
   __pycache__/
   *.pyc
   .DS_Store
   ```

2. **Apply `docs/transcription/engine.patch`** from the Workbench repo: `git apply <path>/engine.patch`. It was tested against v0.1.0 and does two things:
   - `doctor --json` prints the setup checks as one JSON object.
   - `run` handles SIGTERM and Ctrl-C: it stops `ffmpeg` and `whisper-cli`, removes its scratch files, prints `Transcription cancelled.` and exits 130. Before the patch a terminated `run` left `whisper-cli` running in the background.
3. **Run the engine's tests:** `$(cat .python) -m unittest discover -s tests -t .` must report 44 tests, all passing.
4. **Add to the engine README** a short "Use from another program" section with the table in §4.2.

If the patch does not apply cleanly, stop and report the conflict. Do not rewrite the engine.

### 4.2 Contract Workbench relies on

| Call | Result |
|---|---|
| `bin/transcribe doctor --json` | JSON on stdout (Appendix B). Exit 0 when ready, 1 when a blocking check fails. |
| `bin/transcribe run <audio> --out-dir <dir> --quiet [--channels split]` | Writes `<dir>/<stem>.json`, `.txt` and `.srt`. Prints nothing on stdout. |
| exit code of `run` | `0` done · `1` failed, last stderr line is `Transcription failed: <reason>` · `130` cancelled |
| SIGTERM to `run` | Stops within a few seconds, no child processes left, exit 130 |

- `<stem>` is the audio file's name without its extension. Workbench stores uploads as `<attachment id><ext>`, so the result is `<attachment id>.json`.
- The result JSON is described in Appendix A. Workbench reads `text`, `raw_text`, `segments`, `warnings`, `glossary_corrections`, `source`, `engine`, `processing` and `channel_mode`. Unknown keys are ignored.
- The engine never changes or deletes the audio it is given.
- The engine reads its own `config.json` and `glossary.txt` from its repo root. Workbench does not pass a config.

---

## 5. Server

### 5.1 Configuration (extends §C3)

| Variable | Default | Purpose |
|---|---|---|
| `WORKBENCH_TRANSCRIBE_HOME` | *(empty)* | Root of the engine repo; the program is `<home>/bin/transcribe`. Empty, missing or not executable means the feature is off. |

Add `transcribe_home: Path | None = None` to `Settings` in `server/app/config.py`. For development: `WORKBENCH_TRANSCRIBE_HOME=~/Documents/GitHub/Transcription make dev-server`.

### 5.2 Layout (extends §C2)

```text
server/app/
├─ transcribe/
│  ├─ engine.py        # subprocess wrapper: status(), run(); nothing else touches the engine
│  ├─ jobs.py          # TranscriptionManager: queue, events, cancel, recover
│  ├─ cleanup.py       # T2: chunking, prompt, word-preservation guard
│  └─ glossary.py      # T2: read and write the engine's glossary file
├─ db/attachments.py   # attachment + transcript rows → schemas (listed in §C2, not yet written)
├─ db/migrations/002_audio.sql
└─ api/transcription.py   # /transcription/* ; attachment routes stay in api/attachments.py
server/tests/
├─ fake_transcribe/bin/transcribe   # fake engine (§10.1)
└─ test_transcription.py
shared/cleanup_guard_cases.json     # T2, moved from docs/transcription/
```

Add `transcribe` to `TARGETS` in `scripts/check_coverage.py` (80% line coverage, same as `providers`, `runs` and `search`).

`create_app` builds `app.state.transcription = TranscriptionManager(...)` in the lifespan, calls its `recover()` after `runs.recover()`, and its `close()` on shutdown before `runs.close()`.

### 5.3 Database (extends §C4): `002_audio.sql`

SQLite cannot alter a CHECK constraint, so the table is rebuilt.

```sql
CREATE TABLE attachments_new (
  id TEXT PRIMARY KEY,
  message_id TEXT REFERENCES messages(id) ON DELETE CASCADE,
  kind TEXT NOT NULL CHECK (kind IN ('image','text','audio')),
  filename TEXT NOT NULL, mime_type TEXT NOT NULL, bytes INTEGER NOT NULL,
  path TEXT NOT NULL,
  created_at TEXT NOT NULL
);
INSERT INTO attachments_new
  SELECT id, message_id, kind, filename, mime_type, bytes, path, created_at FROM attachments;
DROP TABLE attachments;
ALTER TABLE attachments_new RENAME TO attachments;
CREATE INDEX attachments_message ON attachments(message_id);

CREATE TABLE transcripts (
  attachment_id TEXT PRIMARY KEY REFERENCES attachments(id) ON DELETE CASCADE,
  status TEXT NOT NULL CHECK (status IN ('queued','transcribing','ready','failed','cancelled')),
  channels TEXT NOT NULL DEFAULT 'mix' CHECK (channels IN ('mix','split')),
  started_at TEXT,
  error_json TEXT,                 -- {"code","message"} when failed
  duration_seconds REAL,
  text TEXT,                       -- engine "text": Whisper output with glossary corrections
  raw_text TEXT,                   -- engine "raw_text": Whisper output, untouched
  segments_json TEXT,              -- engine "segments"
  meta_json TEXT,                  -- engine source, engine, processing, warnings,
                                   -- glossary_corrections, channel_mode
  cleaned_text TEXT,               -- T2
  cleanup_status TEXT CHECK (cleanup_status IN ('running','ready','failed')),  -- NULL = never run
  cleanup_json TEXT,               -- T2: model, chunks, kept_original, changed_words, error
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
```

Test the migration on a version-1 database that already holds an image and a text attachment: both rows survive, and an `audio` row can be inserted.

Transcript text lives in the database, not in files. The audio file lives at `attachments/<id><ext>` under `DATA_DIR`, mode `0600`, like other attachments.

### 5.4 Schemas (extends `schemas.py`)

```python
class CleanupInfo(BaseModel):
    status: Literal["running", "ready", "failed"]
    model: MessageModel | None = None
    chunks: int = 0
    done: int = 0
    kept_original: int = 0          # sections left as transcribed by the guard
    changed_words: int = 0
    error: ErrorDetail | None = None

class TranscriptInfo(BaseModel):    # carried on every audio Attachment
    status: Literal["queued", "transcribing", "ready", "failed", "cancelled"]
    channels: Literal["mix", "split"] = "mix"
    started_at: str | None = None
    error: ErrorDetail | None = None
    duration_seconds: float | None = None
    word_count: int | None = None
    token_estimate: int | None = None      # round(len(best text) * 0.3)
    elapsed_seconds: float | None = None
    speed_x_realtime: float | None = None
    engine_model: str | None = None
    warnings: list[str] = Field(default_factory=list)
    correction_count: int = 0
    cleanup: CleanupInfo | None = None

class Attachment(BaseModel):
    id: str
    kind: Literal["image", "text", "audio"]
    filename: str
    mime_type: str
    bytes: int
    transcript: TranscriptInfo | None = None   # audio only

class TranscriptSegment(BaseModel):
    start: float
    end: float
    speaker: str | None = None
    text: str
    raw_text: str

class Correction(BaseModel):
    found: str
    replaced_with: str
    count: int

class Transcript(BaseModel):
    attachment: Attachment
    text: str
    raw_text: str
    cleaned_text: str | None = None
    segments: list[TranscriptSegment]
    corrections: list[Correction]
```

"Best text" means `cleaned_text` when clean-up finished, otherwise `text`.

`Attachment(**row)` is built in two places today (`db/messages.py::message` and `api/chats.py::start_message`). Move both to one function in `db/attachments.py` that also loads the transcript summary.

### 5.5 HTTP API (extends §C9)

| Method & path | Body → Response | Step |
|---|---|---|
| `POST /attachments` (multipart `file`, optional form field `channels`) | → 201 `Attachment`. Audio is streamed to disk, gets `transcript.status = "queued"`, and its job starts. | T1 |
| `GET /attachments/pending` | → `Attachment[]`: audio attachments not yet sent, newest first. Declare this route before `/{identifier}`. | T1 |
| `DELETE /attachments/{id}` | → 204. Unsent only; 409 `attachment_sent` otherwise. Cancels any job, deletes the rows and the file. | T1 |
| `GET /attachments/{id}/events` | SSE (§5.6) | T1 |
| `GET /attachments/{id}/transcript` | → `Transcript`. 409 `transcript_not_ready` unless status is `ready`. | T1 |
| `GET /attachments/{id}/transcript/download?format=txt\|srt\|json&variant=best\|original\|raw` | File download. `srt` is built from the segments and is not available for the cleaned text. | T1 |
| `POST /attachments/{id}/transcribe` | `{channels: "mix"\|"split"}` → 202 `Attachment`. Starts over (retry, or a different channel mode). 409 `transcription_active` if a job is running. Clears any clean-up. | T1 |
| `POST /attachments/{id}/cancel` | → 202. Cancels transcription or clean-up, whichever is running. | T1 |
| `GET /transcription/status` | → `{configured, ready, version, checks: [{name, ok, detail, blocking}], glossary_terms}` | T1 |
| `POST /attachments/{id}/cleanup` | `{connection_id, model_id}` → 202 `Attachment` | T2 |
| `DELETE /attachments/{id}/cleanup` | → 204. Discards the cleaned text. | T2 |
| `GET /transcription/glossary` · `PUT /transcription/glossary` | `{text}` → `{text, terms}` | T2 |
| `GET /_schema/transcription-event` | → `TranscriptionEvent`; exists only for type generation, like `/_schema/run-event` | T1 |

`GET /bootstrap` gains `features.transcription` (true when the engine status is ready).

The existing `GET /attachments/{id}` serves the audio file for audio attachments.

### 5.6 SSE events for an attachment

Same framing as §C10: `event`, `id: <seq>`, `data`. Resume with `Last-Event-ID`. A Pydantic discriminated union `TranscriptionEvent` is exported to TypeScript.

| Event | Data |
|---|---|
| `transcription.queued` | `{position}` |
| `transcription.started` | `{started_at}` |
| `transcription.done` | `{attachment}` |
| `transcription.failed` | `{attachment}` (the reason is in `attachment.transcript.error`) |
| `transcription.cancelled` | `{attachment}` |
| `cleanup.started` | `{attachment}` |
| `cleanup.progress` | `{done, total}` |
| `cleanup.done` | `{attachment}` |
| `cleanup.failed` | `{attachment}` |
| `stream.closed` | `{}` |

- A job keeps an append-only event list for 15 minutes after it ends, as runs do.
- If a client connects when no job is in memory for that attachment, the server sends one event describing the stored state (`transcription.done`, `.failed` or `.cancelled`) and then `stream.closed`.
- There is no percentage for transcription, because the engine doesn't report one. The UI shows elapsed time from `started_at` (§B2 principle 5). Clean-up progress is real: finished chunks out of total.

The event log in `runs/manager.py::Run` (`emit`, `tail`) is the pattern to follow. Extracting it into a small shared class used by both is fine; copying it is also fine.

### 5.7 Engine wrapper (`transcribe/engine.py`)

- `status(refresh=False)` runs `doctor --json` with a 20 s timeout and caches the result for 30 s. No home configured, a missing program, a timeout or unparseable output all give `configured`/`ready = False` with a plain reason; they never raise.
- `run(audio, out_dir, channels)` uses `asyncio.create_subprocess_exec` with an **argument list** (never a shell): `[<home>/bin/transcribe, "run", str(audio), "--out-dir", str(out_dir), "--quiet"]`, plus `"--channels", "split"` when asked. `stdin` and `stdout` go to `DEVNULL`; `stderr` is piped and only its last 8 KB kept; `cwd` is the engine home; `start_new_session=True`.
- Exit 0: read `<out_dir>/<audio stem>.json` and return it. A missing or invalid file is a failure.
- Exit 130: raise cancelled.
- Any other exit: raise `transcription_failed` with the last non-empty stderr line, the `Transcription failed: ` prefix removed, cut to 300 characters.
- On `asyncio.CancelledError`: send SIGTERM, wait up to 10 s, then SIGKILL; re-raise.
- Hard limit of 4 hours per job.
- Never log stderr content, transcript text or the user's filename. Log the attachment id, duration and timing only.

### 5.8 Jobs (`transcribe/jobs.py`)

- One `asyncio.Semaphore(1)` for the engine. A waiting job emits `transcription.queued {position}`.
- Each job is an `asyncio.Task` independent of any HTTP request, as runs are (§C7).
- Steps: set `transcribing` and `started_at`; run the engine into `DATA_DIR/transcribe-tmp/<attachment id>/`; store the result; set `ready`; remove the scratch folder in `finally`.
- `word_count = len(text.split())`. `duration_seconds` comes from the result's `source.duration_seconds`.
- `recover()` at startup: rows still `queued` or `transcribing` become `failed` with code `transcription_interrupted`; `cleanup_status = 'running'` becomes `failed`. Leftover `transcribe-tmp/` folders are removed.
- `cancel(id)`: cancels the task, sets `cancelled`, emits the event.
- Deleting a chat (`api/chats.py::delete` and `delete_all`) first cancels jobs for that chat's attachments. The existing code already unlinks the files; the `transcripts` rows go by cascade.

### 5.9 Upload (extends §D8 and `api/attachments.py`)

- **Accepted audio:** the `audio_extensions` list from the engine status (`.wav .mp3 .m4a .aac .flac .ogg .opus .aif .aiff .caf .mp4 .mov .webm` and a few more). The stored `mime_type` comes from the extension, not from the client.
- **Engine not ready:** 422 `transcription_unavailable`.
- **Streaming:** copy the `UploadFile` to `attachments/<id><ext>.part` in 1 MiB chunks, counting bytes, then rename. Never call `file.read()` for the whole file. Over **4 GiB** returns 413 `audio_too_large` and removes the partial file.
- **Disk space:** if the request has a `Content-Length` and free space under `DATA_DIR` is less than that plus 5 GiB, return 507 `disk_full` before reading the body.
- The engine decides whether a file is really audio. An unreadable file fails the job with the engine's reason; the upload itself succeeds.
- Images and text files behave exactly as before.

### 5.10 Sending and context (extends §C8)

- `start_message` refuses an audio attachment whose transcript is not `ready`: 422 `transcript_not_ready`.
- In `runs/context.py::assemble`, an audio attachment is inlined before the user's text, like a text file:

  ```text
  <transcript name="{filename}" duration="{H:MM:SS}">
  {best text}
  </transcript>
  ```

  The filename is escaped with `html.escape(..., quote=True)`. In split-channel transcripts the text already carries speaker labels.
- The transcript stays in the history for follow-up questions, as text files do.
- The existing budget applies. A transcript that doesn't fit raises `context_overflow` before the runtime is called.
- `Context` gains `has_recording: bool`, true when any message on the path has an audio attachment.
- `Send.content` still needs at least one character. A recording alone can't be sent; the user asks something about it.

### 5.11 Web search guard

In `runs/generate.py`, where the web hook is called:

- If `context.has_recording` and the setting `transcription.block_web` is true, **do not call the web hook**, including for `force_web`. Set `run.message.web = WebInfo(status="skipped", notice=ErrorDetail(code="search_blocked_recording", message=""))` and emit `search.skipped {reason: "recording"}`.
- Otherwise behave as today.

New setting key in `db/settings.py`: `transcription.block_web`, default `true`, boolean-validated.

Test it by counting search and fetch calls on the fake web: zero in a blocked chat.

### 5.12 Housekeeping

- At startup and every 24 hours, delete attachments of any kind that were never sent and are more than 7 days old: rows and files. Today a removed chip leaves its file behind; with recordings that matters.
- `DELETE /attachments/{id}` is what the composer's remove button calls for audio.

### 5.13 Error codes and copy (extends §C12)

| Code | Where shown | Copy (exact) | Actions |
|---|---|---|---|
| `transcription_unavailable` | (+) menu item, disabled | "Recordings need the transcription engine" | — |
| `audio_too_large` | toast | "Recordings can be up to 4 GB." | — |
| `disk_full` | toast | "There isn't enough free space on the Mac for this recording." | — |
| `upload_failed` (client) | chip | "Upload didn't finish" | Retry (re-pick the file) |
| `transcription_failed` | chip | "Couldn't transcribe: {detail}" | Retry · Remove |
| `transcription_interrupted` | chip | "Interrupted because the server restarted" | Retry · Remove |
| `transcript_not_ready` | Send tooltip | "Waiting for the transcript" | — |
| `transcript_too_large` (client) | chip, warning colour | "About {n} tokens: more than {model} can take ({m}). Choose a model with a larger context." | Choose model |
| `no_speech` (derived: ready, 0 words) | chip | "No speech found" | Remove |
| `search_blocked_recording` | notice above the answer | "Web search is off in chats with a recording, so nothing from it leaves this Mac." | — |
| `cleanup_failed` | transcript panel | "Clean-up failed: {detail}. The transcript is unchanged." | Try again |
| *(clean-up, partial)* | transcript panel | "{k} of {n} sections were left as transcribed because the clean-up changed their wording." | — |

As in §C12, none of this text goes into `message.content`. For `search_blocked_recording`, the "Search anyway" link in `SearchActivity` is not shown.

---

## 6. Clean-up (T2)

Implementation note (5 October 2026): the reference guard now lives at
`server/app/transcribe/cleanup.py`, with its unchanged test vectors at
`shared/cleanup_guard_cases.json`. Historical reference paths below describe
the supplied design source; the exact prompt in §6.2 is unchanged.

The user starts it from the transcript panel: **Clean up with {model}**, where the model is the one selected in the composer. It fixes punctuation, capitalisation and paragraph breaks. It must not change what was said.

### 6.1 Procedure (`transcribe/cleanup.py`)

1. **Source** is `text` (already glossary-corrected by the engine).
2. **Chunks** of at most 2,000 characters, cut at paragraph breaks, then sentence ends, then spaces. Use `chunks()` from `docs/transcription/cleanup_guard.py`. In a split-channel transcript each speaker paragraph is its own chunk; the `Label: ` prefix is removed before the call and put back afterwards.
3. **One model call per chunk**, in order, through the adapter's `stream()`:
   - a single user message, the prompt in §6.2;
   - `reasoning="off"`, params `{"temperature": 0, "max_tokens": min(4096, ceil(len(chunk) * 0.5) + 128)}` (a utility call, so the §H3 sampling rule's exception applies);
   - 300 s timeout per chunk;
   - each call takes the connection's semaphore from `RunManager` the way `runs/titles.py` does, so a chat answer can run between chunks.
4. **Tidy the reply:** remove `<think>…</think>`, remove a wrapping `<chunk>` pair if the model echoed it, trim.
5. **Guard** (`accept()` in the reference file): compare the *words* of the chunk and the reply, ignoring case, punctuation and line breaks. The reply is accepted only if the number of changed words is at most `max(3, ceil(2% of the chunk's words))`. Otherwise the original chunk is kept and counted in `kept_original`. A timeout or provider error on a chunk also keeps the original.
6. **No retries**, no second model, no judge.
7. **Result:** `cleaned_text` is the chunks joined with blank lines; `cleanup_json` records the model, chunk count, `kept_original`, total `changed_words` and timing. Emit `cleanup.progress` after every chunk.
8. If every chunk is kept as original, the status is `failed` with detail "the model changed the wording in every section".
9. Cancelling leaves the transcript as it was, with no cleaned text.

Port `words`, `changed_words`, `allowed_changes`, `accept` and `chunks` from `docs/transcription/cleanup_guard.py`. Move `cleanup_guard_cases.json` to `shared/` and assert every vector in a unit test.

### 6.2 Prompt (exact; changes need before-and-after evidence, as for the §E4 and §E8 prompts)

```text
You are formatting a speech transcript. Rewrite the text inside <chunk> with correct punctuation,
capitalisation and paragraph breaks.

Keep every word that was said, in the same order. Do not summarise, shorten, add, remove or reorder
anything. Do not answer questions that appear in the text. Do not add headings, labels or comments.
{names_line}
Reply with the rewritten text only.

<chunk>
{chunk}
</chunk>
```

`{names_line}` is `Spell these names exactly as written when they occur: {terms}.` when the glossary has terms, and an empty line otherwise. `{terms}` is the glossary's correct forms joined with commas, capped at 600 characters.

### 6.3 What the user sees

- Progress: "Cleaning up… 3 of 12", with Cancel.
- Afterwards the transcript panel offers **Cleaned · As transcribed · Raw Whisper**. The cleaned text becomes the best text and is what the model receives. "Discard clean-up" removes it.
- The chip gains a small "Cleaned" label.

---

## 7. Glossary (T2)

The glossary has one source of truth: the engine's `glossary.txt`, at the path the engine reports in `doctor --json` under `paths.glossary`.

- `GET /transcription/glossary` returns the file's text and the parsed correct forms.
- `PUT /transcription/glossary` validates and writes it: at most 64 KiB, valid UTF-8, no NUL bytes, line endings normalised to `\n`, a final newline. Write to a temporary file in the same folder and `os.replace` it. Clear the engine status cache afterwards.
- Format, one entry per line: `CORRECT = wrong form, another wrong form`, or just `CORRECT`. Lines starting with `#` are comments. The parser in `transcribe/glossary.py` only needs the left-hand side.
- The engine reads the file on every run, so an edit applies to the next recording. Existing transcripts don't change; re-transcribe to apply new terms.

---

## 8. Web UI

Build from the existing primitives and tokens (§H3 Do 4). Two components are added to §G4.

### 8.1 Composer (extends §G4.9)

- **(+) menu:** third item **Add recording**. When `features.transcription` is false it is disabled and reads "Recordings need the transcription engine".
- **Routing:** in `LiveAppShell.upload`, a file is a recording when its extension is in the audio list. Drop, paste and the picker all work. The drop overlay reads "Drop images, text files or recordings".
- **Upload with progress:** add `uploadWithProgress(file, onProgress, signal)` to `lib/attachments.ts`, using `XMLHttpRequest` (fetch can't report upload progress). Images and text files keep using `api()`.
- **Send is disabled** while any attached recording is not `ready`; the tooltip reads "Waiting for the transcript". The composer stays editable.
- **Search toggle:** when the chat's visible path or the composer holds a recording and `transcription.block_web` is on, the toggle is shown off and `aria-disabled`, with the tooltip "Search is off in chats with a recording".
- **Context meter:** pending attachments are added to the used tokens in every case, not only in a new chat: 800 per image, `bytes × 0.3` per text file, `token_estimate` per recording.
- **Starters:** when a ready recording is attached and the text box is empty, show three chips: **Summarize**, **Action items**, **Decisions**. Each inserts a short starter ("Summarize this recording.") and focuses the box. They don't send.
- **Restore after reload:** on load, `GET /attachments/pending` puts unsent recordings back in the composer and reattaches their event streams.
- **Editing a message that has attachments:** the edit box shows "Attachments aren't carried over when you edit. Ask a follow-up instead." This is existing behaviour, now stated.

### 8.2 `AudioChip` (new, §G4.15)

One chip per recording, in the composer and on sent user messages. Icon: `AudioLines` from lucide.

| State | Content |
|---|---|
| Uploading | filename · "Uploading 42%" · cancel |
| Upload failed | filename · "Upload didn't finish" |
| Queued | filename · "Waiting for another recording" · cancel |
| Transcribing | filename · "Transcribing 0:42" (elapsed) · cancel |
| Ready | filename · "20:45 · 3,412 words · ≈6.1K tokens" · menu |
| Ready, too large for the model | as Ready, warning colour, plus the `transcript_too_large` copy |
| Ready, no speech | filename · "No speech found" |
| Failed / Interrupted | filename · copy from §5.13 · Retry |
| Cancelled | filename · "Cancelled" · Retry |
| Cleaning (T2) | filename · "Cleaning up… 3 of 12" · cancel |
| Cleaned (T2) | as Ready, with a "Cleaned" label |

- The chip body opens the transcript panel when ready.
- **Menu:** Open transcript · Download text · Download subtitles (.srt) · Download details (.json) · Download audio · Transcribe again · Transcribe again, one speaker per channel · Clean up with {model} (T2) · Remove (composer only).
- "Too large" is computed in the browser from `token_estimate` and the selected model: `context_length − clamp(context_length × 0.25, 1024, 8192) − 256`.
- On a sent message the chip replaces the plain filename link that `LiveThread` renders today.
- Live state comes from a small zustand store keyed by attachment id, fed by `attachTranscription(id)` in `lib/sse.ts` (a plain `EventSource`; no polling).

### 8.3 `TranscriptSheet` (new, §G4.16)

A Sheet on desktop and a Drawer on phones, built like `SourcesSheet`.

- **Header:** filename; a meta line "20:45 · 3,412 words · large-v3-turbo · transcribed in 28 s".
- **View:** Text / Timestamps. Timestamps lists each segment as `[mm:ss] text`, with the speaker label when there is one.
- **Version** (when clean-up exists): Cleaned · As transcribed · Raw Whisper.
- **Notes**, collapsed by default: engine warnings; glossary corrections as "Gismo → GSMOS ×3"; the clean-up summary.
- **Footer:** Copy · Download ▾ · Clean up with {model} (T2).
- The transcript is rendered as plain text with `white-space: pre-wrap`, never as Markdown or HTML.

### 8.4 Settings › Transcription (new pane, after Search)

- **Status:** a dot and "Ready" or "Not set up", then the engine's checks as a list (name, ok or not, detail). When not configured, show the variable name `WORKBENCH_TRANSCRIBE_HOME` and one line on what to set it to.
- **Privacy:** switch "Keep web search off in chats with a recording" (`transcription.block_web`).
- **Glossary** (T2): a textarea with the file's text, a one-line format hint, Save, and the count of terms.

### 8.5 `/design` and screenshots

Add every `AudioChip` state, the `TranscriptSheet` in both views and with all three versions, the Settings pane in ready and not-set-up states, the disabled Search toggle, the blocked-search notice and the composer starters. All of it uses the fake engine and is labelled as fake (§H2). Screenshots at 390 and 1440, light and dark, go to `artifacts/phase-t/`.

---

## 9. Privacy and security

1. **Nothing leaves the Mac.** Audio goes to the local engine; transcript text goes only to the local Ollama connection. The engine's only network use is the one-time model download done by its installer.
2. **Web search guard** (§5.11) is on by default and covers forced search too.
3. **No real content in the repo.** Fixtures, tests, eval files, artifacts, screenshots and reports use the fake engine or recordings made with `say`. For the checks Jake runs on real recordings (T-AC12), the report carries numbers only.
4. **Logs** carry attachment ids, sizes, durations and timings. Never transcript text, engine stderr or filenames.
5. **The engine path** comes only from the environment. No API reads or writes it. The engine is started with an argument list; the audio path is `<id><ext>`, where `<ext>` comes from the allowed list, so no user text reaches the command line.
6. **Transcripts are untrusted input** to the model, like web pages: wrapped in `<transcript>` tags and never treated as instructions by any host code. In the UI they are plain text.
7. **Stored files** are mode `0600` under `DATA_DIR`. The existing host allowlist and same-origin checks apply to the new routes unchanged.
8. **Recommended, not required:** set `WORKBENCH_TAILSCALE_OWNER` now that the app holds meeting content.

---

## 10. Tests (extends §H2)

### 10.1 Fake engine (`server/tests/fake_transcribe/bin/transcribe`)

An executable Python script that honours the §4.2 contract. `serve_app.py` and the test fixtures point `transcribe_home` at `server/tests/fake_transcribe`. Its output always says it is fake.

`doctor --json` returns a ready status; the glossary path is `$FAKE_TRANSCRIBE_GLOSSARY` when set.

`run` reads the first line of the "audio" file as a directive. Test files are small text files with audio extensions.

| First line | Behaviour |
|---|---|
| *(anything else)* | 75 s, three segments, text "Fake transcript. This recording is not real. …" |
| `#fake:words N` | N words, for the too-large case |
| `#fake:speakers` | two speakers, `channel_mode: "split"` when run with `--channels split` |
| `#fake:silence` | no segments, warning "No speech was detected in this recording." |
| `#fake:glossary` | one entry in `glossary_corrections`, and different `text` and `raw_text` |
| `#fake:slow S` | waits S seconds; on SIGTERM exits 130 |
| `#fake:fail REASON` | stderr `Transcription failed: REASON`, exit 1 |

For clean-up, `tests/fake_runtime.py` recognises the first line of the §6.2 prompt and replies with the chunk plus added punctuation and a paragraph break. If the chunk contains `FAKE-REWRITE`, it replies with a one-sentence summary so the guard rejects it.

### 10.2 Unit and integration tests (`server/tests/test_transcription.py`)

- Migration from version 1 keeps existing rows and allows `audio`.
- Engine wrapper against the fake engine: success, failure message, cancel (process gone), missing home, bad JSON.
- Upload: streamed (patch the limit to a small value and check 413 and that no partial file remains); unsupported type; engine not ready.
- Jobs: queue order and `position`; cancel; `recover()`; events replay with `Last-Event-ID`; snapshot event when no job is in memory.
- Send: refused until ready; the captured request to the fake runtime has the `<transcript …>` block before the user's text; a follow-up still includes it.
- Context overflow for a `#fake:words` transcript larger than the model window.
- Web guard: zero search calls in a chat with a recording, including `force_web`; searches run when the setting is off.
- Deleting a chat removes the audio file and the transcript row; `DELETE /attachments/{id}` refuses a sent attachment.
- Housekeeping removes old unsent attachments and keeps recent ones.
- T2: every vector in `shared/cleanup_guard_cases.json`; chunking keeps every word within the limit; a full clean-up run with one rejected chunk; cancel; glossary read, write and validation.
- `make api-types` regenerated; the contract check passes.

### 10.3 E2E (`web/tests/transcription.spec.ts`; Chromium and WebKit, fake engine and fake runtime)

| ID | Flow |
|---|---|
| T-1 | Add a recording: progress, transcribing, ready; open the panel; both views |
| T-2 | Ask about it; the answer streams; a follow-up works |
| T-3 | Send is disabled while transcribing; reload mid-job restores the chip and finishes |
| T-4 | Failure, then Retry; cancel; remove |
| T-5 | Search toggle disabled and the notice shown; no "Search anyway" |
| T-6 | Too-large warning and model switch |
| T-7 | *(T2)* Clean-up with progress; a rejected section is reported; version switch; discard |
| T-8 | *(T2)* Edit the glossary in Settings |
| T-9 | Engine not configured: disabled menu item and the Settings pane state |
| T-10 | Axe on the new UI, both themes |

---

## 11. Build order and acceptance

### T1: upload, transcribe, ask

1. §3 amendments. §4 engine patch in the `Transcription` repo.
2. Config, migration, schemas, `db/attachments.py`.
3. Engine wrapper, jobs, events, upload, the new routes.
4. Send rules, context, web guard, housekeeping.
5. Web: upload with progress, `AudioChip`, `TranscriptSheet`, composer changes, Settings status and privacy switch, `/design`.
6. Tests and screenshots.

**Stop for review after T1.**

### T2: clean-up and glossary

1. `cleanup.py` with the guard and vectors; the fake-runtime behaviour.
2. Clean-up routes and events; UI for progress, versions and discard.
3. Glossary routes and the Settings editor.
4. Tests and screenshots.

### Acceptance criteria (each needs a test or recorded evidence)

| ID | Criterion | Step |
|---|---|---|
| T-AC1 | The engine patch is applied; the engine's 44 tests pass; `bin/transcribe doctor --json` reports `ok: true` on the Mac mini. `.gitignore` is restored and nothing private is tracked. | T1 |
| T-AC2 | Without `WORKBENCH_TRANSCRIBE_HOME`, the menu item is disabled with its reason and an audio upload returns `transcription_unavailable`. | T1 |
| T-AC3 | A 1 GB file uploads with a real progress figure and the server's memory grows by less than 100 MB during it (state how it was measured). An over-limit upload returns 413 and leaves no partial file. | T1 |
| T-AC4 | A `say` recording becomes a transcript through the **real** engine. The chip shows duration, words and tokens; the panel shows text and timestamps; all three downloads open. | T1 |
| T-AC5 | The request captured by the fake runtime contains the `<transcript>` block before the user's text; a follow-up contains it too; regenerate works. | T1 |
| T-AC6 | Sending while transcribing is blocked in the UI and by the API. | T1 |
| T-AC7 | Reload mid-transcription: the chip returns and finishes correctly. Server restart mid-job: "Interrupted…" and Retry works. | T1 |
| T-AC8 | Cancel leaves no `transcribe`, `ffmpeg` or `whisper-cli` process (`pgrep` output in the report). Remove deletes the file. | T1 |
| T-AC9 | An unreadable file fails with the engine's reason and can be retried. | T1 |
| T-AC10 | In a chat with a recording and Search on, no search or page request is made, the notice shows and "Search anyway" does not. With the setting off, search runs. | T1 |
| T-AC11 | A transcript larger than the model's window warns before sending and returns `context_overflow` if sent. | T1 |
| T-AC12 | **Jake's check, numbers only:** the 21-minute TP-7 file from the desktop, and one recording from the iPhone over the Tailscale URL. Report file size, upload time, transcription time and memory pressure with the 32K Qwen model loaded. No filenames or text. | T1 |
| T-AC13 | A search of the repo, `artifacts/` and the server log finds no transcript text and no real filenames. | T1, T2 |
| T-AC14 | Deleting a chat removes its audio file and transcript row. | T1 |
| T-AC15 | Clean-up against the fake runtime: progress events, a rejected section kept and counted, version switch, cleaned text used in the next request, discard. | T2 |
| T-AC16 | Clean-up of a `say` recording of about five minutes with the real Qwen model: time taken, sections kept as original, total changed words. | T2 |
| T-AC17 | A term added in Settings is in the engine's `glossary.txt` and appears in the next result's `engine.prompt`. Invalid input is refused. | T2 |
| T-AC18 | Every new state is on `/design`; axe has no serious or critical violations; `make check` and `make e2e` pass; `server/app/transcribe` has at least 80% line coverage. | T1, T2 |

Making a test recording on the Mac: `say -o sample.aiff "This is a test recording for Workbench."`

The report is `docs/PHASE-T-REPORT.md`, using the §H4 template. Evidence goes under `artifacts/phase-t/`.

---

## 12. Note for Phase 3 deployment (do not build now)

The engine repo is in `~/Documents`. A service started by launchd can be refused access to Desktop, Documents and Downloads by macOS privacy protection. In development this doesn't arise, because the server is started from a terminal.

When Phase 3 writes `scripts/deploy.sh`, it should give the installed app its own copy of the engine, in the same way it installs the app itself:

- sync the engine repo to `~/.local/share/workbench/transcribe`, excluding `.git`, `models/`, `config.json`, `glossary.txt` and `.python`;
- on the first install, copy those four from the source repo (the model is about 1.6 GB);
- set `WORKBENCH_TRANSCRIBE_HOME` to that folder in the plist.

After that, the glossary edited in Settings is the installed copy's. Confirm this plan with Jake when Phase 3 starts.

## 13. Not in this phase

- Converting or shrinking audio in the browser before upload; resumable uploads.
- An audio player, or jumping to a point in the recording from the transcript.
- Speaker recognition beyond one-speaker-per-channel.
- Summarising recordings longer than the context window (that belongs with the Library and research work in Part F).
- Searching transcript text from the sidebar; including transcripts in chat exports.
- Automatic clean-up; choosing a different clean-up model per chunk; retries.
- A `transcribe` tool for agents. The seam is `transcribe/engine.py::run`, which a Part F tool can wrap later.
- Carrying attachments over when a message is edited.
- The watched inbox folder. It stays in the engine repo and is independent of Workbench.

## 14. Open questions for Jake

1. **What are the TP-7's four channels?** If each is a separate microphone or call side, "one speaker per channel" will label them. If they are two stereo pairs of the same room, mixing is right.
2. **Should Phase T run before the Phase 2 iPhone review closes?** It touches the composer and `LiveAppShell`, which that review is also looking at.
3. **Is the `Transcription` GitHub repo private?** The missing `.gitignore` means `glossary.txt` may already have been pushed.

---

## Appendix A. Engine result JSON (`<stem>.json`)

The content below is invented.

```json
{
  "source": {
    "duration_seconds": 75.2, "sample_rate": 48000, "channels": 4, "codec": "pcm_s24le",
    "bits_per_sample": 24, "container": "wav", "audio_streams": 1, "size_bytes": 43315244,
    "file": "0f3c….wav"
  },
  "engine": {
    "pipeline_version": "0.1.0", "runtime": "whisper.cpp", "model": "ggml-large-v3-turbo.bin",
    "vad": "ggml-silero-v6.2.0.bin", "language": "en",
    "prompt": "This recording mentions DataHub and PostgreSQL."
  },
  "channel_mode": "mix",
  "processing": {"finished_at": "2026-10-03T09:14:07-04:00", "elapsed_seconds": 3.1, "speed_x_realtime": 24.3},
  "warnings": [],
  "glossary_corrections": [{"found": "data hub", "replaced_with": "DataHub", "count": 2}],
  "text": "The bakery opens at seven on weekdays. We moved the DataHub job last week.\n",
  "raw_text": "The bakery opens at seven on weekdays. We moved the data hub job last week.\n",
  "segments": [
    {"start": 0.4, "end": 3.1, "speaker": null,
     "text": "The bakery opens at seven on weekdays.", "raw_text": "The bakery opens at seven on weekdays."},
    {"start": 3.4, "end": 6.0, "speaker": null,
     "text": "We moved the DataHub job last week.", "raw_text": "We moved the data hub job last week."}
  ]
}
```

- `text` paragraphs are separated by blank lines. With `channel_mode: "split"`, each paragraph starts with its speaker label and segments carry `speaker`.
- An empty `text` with the warning "No speech was detected in this recording." is a successful run.

## Appendix B. `doctor --json`

```json
{
  "ok": true,
  "version": "0.1.0",
  "config": "/Users/…/Transcription/config.json",
  "checks": [
    {"name": "ffmpeg", "ok": true, "detail": "/opt/homebrew/bin/ffmpeg  (ffmpeg version 9.0.2 …)", "blocking": true},
    {"name": "whisper_cli", "ok": true, "detail": "/opt/homebrew/bin/whisper-cli  (whisper.cpp version: 1.9.4)", "blocking": true},
    {"name": "model", "ok": true, "detail": "/Users/…/models/ggml-large-v3-turbo.bin  (1.62 GB)", "blocking": true},
    {"name": "vad_model", "ok": true, "detail": "/Users/…/models/ggml-silero-v6.2.0.bin", "blocking": false},
    {"name": "glossary", "ok": true, "detail": "/Users/…/glossary.txt  (8 terms)", "blocking": false}
  ],
  "paths": {"data_dir": "/Users/…/Transcription", "glossary": "/Users/…/glossary.txt", "model": "/Users/…/models/ggml-large-v3-turbo.bin"},
  "channels": "mix",
  "audio_extensions": [".aac", ".aif", ".aiff", ".amr", ".caf", ".flac", ".m4a", ".mka", ".mov",
                       ".mp3", ".mp4", ".oga", ".ogg", ".opus", ".wav", ".webm", ".wma"]
}
```

The real output also lists `ffprobe` and the inbox, done, failed and logs folders. Keys are only ever added.

## Appendix C. How this maps to the original brief

| Brief | Where it lands |
|---|---|
| 1. Transcription service on localhost | Not needed. Workbench runs the engine directly; the inbox watcher covers unattended use. |
| 2. Watched folder | Done, in the engine repo. Unchanged. |
| 3. Harness `transcribe` tool with LLM clean-up, raw text kept | This phase. The harness has no tool calling yet (Part F), so it is an attachment pipeline; clean-up is §6; raw text is always kept. |
| 4. Phone to Mac over Tailscale, upload with a token | The Workbench composer on the phone, behind the existing Tailscale Serve, host allowlist and optional owner lock. |
| Glossary in its own editable file | The engine's `glossary.txt`, editable from Settings in T2. |

**User amendment — 3 October 2026 (deployment and storage):** Keep the engine’s public source under `transcribe/` in the Workbench repo and run it as a subprocess. Model weights, actual config, glossary and interpreter selection are ignored by Git; deployment copies them inside the installed app at `~/.local/share/workbench/app/transcribe` to avoid Documents access restrictions. Source recordings remain outside the repo. Uploaded audio is temporary by default: remove Workbench’s copy after durable transcription, preserving transcript text, raw text, timestamps and metadata. Failed/cancelled audio remains retryable until cleared. Settings offers opt-in audio retention and bulk clearing of inactive audio without deleting outputs or chats. This supersedes TRANSCRIPTION-SPEC decisions 1 and 3 and §12’s separate deployment folder. Jake authorized removal of existing uploaded audio copies.

Completed transcript outputs are kept even when unsent; seven-day housekeeping removes only unfinished unsent attachments.
