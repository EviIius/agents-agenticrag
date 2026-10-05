# Phase 5: everyday chat

**For:** Codex · **Depends on:** Phase 4 accepted · **Reads with:** `QA-REQUIREMENTS.md`

Small, separate additions that make daily use better. Each one is additive: new tables, new nullable columns, new endpoints. Nothing in the run pipeline, the search pipeline, the transcription pipeline or any prompt changes.

Three checkpoints, each shippable on its own. **Stop for review after each.**

| Checkpoint | Adds |
|---|---|
| 5A | Presets · a clearer Chat settings save · model display names |
| 5B | PDF and Word attachments |
| 5C | Folders · automatic backups · (optional) fork a chat |

---

## 1. Rules for this phase

- **No new packages.** `pypdf` is already a dependency; Word files are read with the standard library.
- **No new model calls.** Presets are stored values, not modes. They never change which pipeline runs.
- **Sampling rule unchanged.** A preset sends exactly the parameters it stores, and none it does not.
- **Additive API.** Existing request and response fields keep their names, types and meaning. `scripts/check_api_additive.py` (QA §3) enforces it.
- **Migrations** are numbered from `005`, transactional, and tested against the Phase 3 database fixture (QA §3, G-7).
- **Privacy.** Document text and document filenames are treated like recordings: never in logs, fixtures, screenshots or reports. Tests use the synthetic files in §3.5.

**`AGENTS.md`, append:**

> **User amendment (Phase 5, October 2026):** build `docs/next/PHASE-5-EVERYDAY-CHAT.md`. Presets, folders, document attachments and automatic backups are now in scope; this lifts the Phase 0–3 non-goal on folders. Document text and filenames follow the recording privacy rule. No new packages and no new model calls.

## 2. Checkpoint 5A: presets, save clarity, display names

### 2.1 Presets

A preset is a named system prompt plus sampling parameters. Applying one **copies** its values into the chat. Editing or deleting a preset later never changes an existing chat.

**Migration `005_presets.sql`**

```sql
CREATE TABLE presets (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE COLLATE NOCASE,
  system_prompt TEXT,                      -- NULL = use the global default
  params_json TEXT NOT NULL DEFAULT '{}',  -- only keys the user set
  position INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
```

New setting `default_preset_id` (nullable) in `db/settings.py` `DEFAULTS`.

**API** (`api/presets.py`; schemas in `schemas.py`; regenerate `api-types.ts`)

| Route | Body | Notes |
|---|---|---|
| `GET /api/presets` | | ordered by `position`, then name |
| `POST /api/presets` | `{name, system_prompt?, params?}` | `params` validated by the existing `Parameters` model; 409 `preset_name_taken` |
| `PATCH /api/presets/{id}` | any of `name`, `system_prompt`, `params`, `position` | |
| `DELETE /api/presets/{id}` | | clears `default_preset_id` if it pointed here |
| `POST /api/chats` | gains optional `preset_id` | if omitted and `default_preset_id` is set, apply that one |

Applying to an existing chat needs no new route: the client reads the preset and sends the existing `PATCH /api/chats/{id}`.

Presets store `temperature`, `top_p`, `top_k`, `max_tokens`, `seed` and the system prompt. They do **not** store reasoning level or context length: both depend on the model.

**Web**

- Chat settings panel, first control: a **Preset** select: "None", each preset, a separator, "Save as preset…", "Manage presets…". Choosing a preset fills the panel and marks it unsaved (§2.2).
- Settings gains a **Presets** section after Models: list, rename, edit, delete (AlertDialog), "Use for new chats" (one at most), move up and down.
- Command palette: "Apply preset…" opens the same list.

### 2.2 Chat settings: one clear save

This is the first priority from Codex's own Phase 2 UI review ("inline settings validation and one clear save result"). Keep explicit saving; make its state obvious.

- A sticky footer holds **Save settings** (primary, disabled until something changed) and **Reset to model defaults** (ghost). After saving, the button reads "Saved" with a check for 1.5 s. Keep the label "Save settings" so existing selectors hold.
- Validation is inline, under the field, as you type. An invalid field blocks Save and says why. Nothing invalid is ever sent.
- **Context length moves into its own group** with its own **Apply** button and the note "Applies to {model} in every chat." It is a model preference (`PUT /api/models/prefs`), not a chat setting, and today it is saved by the same button as the chat's parameters.
- "Save as model defaults" becomes a text button inside the Sampling group.
- Leaving the panel with unsaved changes keeps them in the panel and shows a dot on the Chat settings button; nothing is discarded silently.

### 2.3 Model display names

`model_prefs.display_name` exists, `PUT /api/models/prefs` accepts it, and the registry honors it. There is no control for it.

- Settings › Models: each row gets **Rename**. An empty name restores the runtime's name.
- When a model has a display name, the picker shows it as the title and the runtime id in the muted line. Picker search matches both.
- No automatic prettifying. The name is whatever Jake types.

## 3. Checkpoint 5B: PDF and Word attachments

Attach a document to a message; its text goes to the model the same way a text file does today. This is not the Library (Phase 7): there is no retrieval, and the whole text must fit the model's context.

### 3.1 Extraction (`server/app/documents/extract.py`, new package)

```python
@dataclass
class Extracted:
    text: str            # UTF-8, page markers included for PDFs
    pages: int | None
    chars: int

def extract(path: Path, suffix: str) -> Extracted: ...
```

| Type | How | Notes |
|---|---|---|
| `.pdf` | `pypdf.PdfReader`, `page.extract_text()` per page | Insert `\n\n[Page N]\n` before each page so answers can name pages. |
| `.docx` | `zipfile` + `xml.etree.ElementTree` over `word/document.xml` | Paragraphs in order; table rows as tab-separated lines. Headers, footers, comments and tracked deletions are skipped. |

Use bounded extraction concurrency and a 30-second timeout. Cancelling an `asyncio.to_thread` await does not stop its thread: hold capacity until the worker actually ends and guarantee eventual temporary-file cleanup. For hard execution limits, use a supervised subprocess with the existing interpreter. Cap DOCX expanded bytes, entry count, XML size and extracted text, and enforce PDF page/text limits during extraction. Phase 7 reuses this module unchanged.

Also extend the plain-text list (`TEXT` in `api/attachments.py`) with: `.jsx .xml .toml .ini .go .rs .java .c .cpp .h .rb .swift .kt .tex .srt .vtt`. The web `accept` string must come from the same list: have the server report it (for example in `/api/bootstrap`), the way `/api/transcription/status` already reports `audio_extensions`.

### 3.2 Upload (`POST /api/attachments`, same route)

1. Stream the upload to a private `.part` file in 1 MiB chunks, as audio does. Limit 50 MB.
2. Extract. Reject with the codes in §3.4.
3. Write the extracted text to `attachments/{id}.txt`. **Delete the original file.** Only text is kept, the same way audio is temporary by default.
4. Insert the attachment with `kind='text'`, the original `filename` and `mime_type`, and `bytes` = size of the extracted text (so context estimates stay correct).

Because `kind` stays `'text'`, `runs/context.py` needs no change: the model receives `<file name="report.pdf">…</file>` exactly as for a `.md` file.

**Migration `006_attachment_meta.sql`:** `ALTER TABLE attachments ADD COLUMN meta_json TEXT;` holding `{"source":"pdf","pages":12,"chars":48211}`. The `Attachment` schema gains an optional `document: {source, pages, chars, token_estimate}`.

### 3.3 Web

- "+" menu: **Add document** (PDF, Word). Drop and paste accept the same types. The drop overlay reads "Drop images, documents, text files or recordings".
- Chip in the composer and on the sent message: document icon, filename, "12 pages · ≈8.4K tokens". Selecting it opens a sheet titled "What the model received" with the extracted text and Copy. Reuse the transcript sheet's layout.
- The context ring includes the document's estimate. If it will not fit, warn before sending, with the same wording pattern and model-switch behavior as an over-long transcript.
- Editing a message with a document shows the existing "Attachments aren't carried over when you edit" note.

### 3.4 Errors (add to §C12 and to `errors.ts`)

| Code | HTTP | Copy |
|---|---|---|
| `document_no_text` | 422 | "This PDF has no selectable text. Scanned documents aren't supported yet." |
| `document_encrypted` | 422 | "This PDF is password-protected. Remove the password and try again." |
| `document_unreadable` | 422 | "Couldn't read this file. It may be damaged." |
| `document_too_large` | 413 | "Documents can be up to 50 MB and 1,500 pages." |
| `document_timeout` | 422 | "This document took too long to read." |

`document_no_text` applies when the extracted text averages fewer than 20 non-space characters per page. No partial file remains after any failure.

### 3.5 Synthetic fixtures (`server/tests/fixtures/documents/`)

Generate them in a script, commit the script and the outputs: `two-pages.pdf` (text on both pages), `table.docx`, `scanned.pdf` (a page with no text operators), `encrypted.pdf` (via `pypdf` `encrypt`), `damaged.pdf` (truncated). Every word in them is invented.

## 4. Checkpoint 5C: folders, backups, fork

### 4.1 Folders

**Migration `007_folders.sql`**

```sql
CREATE TABLE folders (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  position INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
ALTER TABLE chats ADD COLUMN folder_id TEXT REFERENCES folders(id) ON DELETE SET NULL;
CREATE INDEX chats_folder ON chats(folder_id, updated_at DESC);
```

**API:** `GET`/`POST /api/folders`, `PATCH`/`DELETE /api/folders/{id}`. `Chat` gains `folder_id`. `ChatPatch` gains `folder_id`; use `model_fields_set` to tell "absent" from "set to null". `GET /api/chats` gains `folder=<id>` and `folder=none`; without the parameter it returns what it returns today.

**Web**

- Sidebar: a **Folders** group above Pinned. Each folder is a collapsible row with a count; its chats load when opened. Chats in a folder no longer appear under Today, Yesterday and so on. Search still finds everything and shows the folder name beside the title.
- Chat menu: **Move to folder ▸** (each folder, "New folder…", "Remove from folder").
- Folder menu: Rename, Delete. Deleting a folder returns its chats to the history; the dialog says so. It never deletes a chat.
- One level only. No drag and drop in this phase.

### 4.2 Automatic backups (`server/app/backup.py`)

The database now holds chats, transcripts and settings. Deployment already backs it up; nothing does between deployments.

- On startup, if the newest `auto-*.db` is older than 24 hours, make one. Then once a day at 03:30 local time.
- Use SQLite's online backup (`aiosqlite` connection `.backup(target)`), write to `data/backups/auto-YYYYMMDD-HHMM.db` with mode `0600`, keep the newest seven `auto-*` files. Never touch the deploy script's own backups.
- Skip, and record a warning in Settings, if free disk space is below twice the database size.
- `GET /api/backup` returns `{last_at, count, bytes, warning?}`; `POST /api/backup` makes one now.
- Settings › Data: "Last backup: today 03:30 · 7 kept · 41 MB" and **Back up now**. One sentence states that attachments on disk are not included and how to restore (documented in `README.md`: stop the service, preserve the current data directory, restore the backup into a clean database location without stale WAL/SHM sidecars, start it and verify chats/transcripts; rehearse this on a copied data folder. A database-only backup does not restore attachment or library files).

This is a daily timer, not polling of run state; the "never poll" rule is about streaming.

### 4.3 Optional: fork a chat

Do this only if 5C is otherwise finished and green. It is separable.

`POST /api/chats/{id}/fork` with `{message_id}` creates a new chat containing a copy of the visible path up to that message: text, reasoning, stats and stored sources, with new ids. Attachments are **not** copied; the new chat's first screen says so. Title: the original plus " (fork)", `title_source='user'`. Entry point: message actions overflow, "Continue in a new chat".

## 5. Not in this phase

OCR, images inside PDFs, spreadsheets, slide decks, EPUB. Nested folders, drag and drop, per-folder instructions or files. Presets that change model, search state or reasoning. Restore from the UI. Cloud backup. Sharing links.

## 6. Tests

| Area | Tests |
|---|---|
| Presets | Unit: CRUD, unique name, parameter validation, default cleared on delete. Integration: `POST /chats` applies explicit and default presets. E2E: create from the panel; apply to a new chat; the fake runtime's captured request contains exactly the preset's parameters and no others; editing the preset afterwards leaves the chat unchanged. |
| Save clarity | E2E: Save disabled until dirty; invalid value blocks Save with an inline message; context Apply calls only `/models/prefs`; existing `parameters.spec.ts` and `load-selection.spec.ts` pass with selector changes listed in the ledger. |
| Display names | E2E: rename, picker shows both, search matches both, empty restores. |
| Documents | Unit: each fixture; page markers; each error code; no file left after failure; timeout. Integration: upload → send → the captured prompt contains `<file name="two-pages.pdf">` and both page markers. E2E: add, chip, sheet, overflow warning, removal. Memory: a 50 MB upload does not raise server RSS by more than 20 MB (same method as T-AC3). |
| Folders | Unit and integration: CRUD, move, `ON DELETE SET NULL`, list filters. E2E: create, move, collapse, delete folder keeps chats, search shows folder. Migration test: Phase 3 fixture database upgrades with identical chat and message hashes. |
| Backups | Unit with a temp directory and an injected clock: creation, retention of seven, low-disk skip, deploy backups untouched. Integration: the backup opens as a valid database with the same row counts. |
| Design | Every new state on `/design`; axe in both themes at 390 and 1440. |

## 7. Acceptance criteria

| ID | Criterion |
|---|---|
| P5-AC1 | A preset applied to a chat sends exactly its stored parameters (request capture). An empty preset sends none. |
| P5-AC2 | Editing or deleting a preset does not change any existing chat (database assertion). |
| P5-AC3 | Chat settings cannot send an invalid value; Save reflects dirty and saved states; context length saves only through its own Apply. |
| P5-AC4 | A renamed model shows its display name everywhere a model name appears; the runtime id stays visible in the picker. |
| P5-AC5 | A two-page PDF and a Word file with a table reach the model with correct text and page markers (captured prompt). |
| P5-AC6 | Scanned, encrypted, damaged, oversize and slow documents fail with the §3.4 copy and leave no file behind. |
| P5-AC7 | The original document is not on disk after upload; only extracted text is. |
| P5-AC8 | No document text or filename appears in logs, artifacts or screenshots (privacy audit, QA G-11). |
| P5-AC9 | Folders: create, move, rename, delete; deleting a folder deletes no chat; `GET /api/chats` without `folder` returns the same set as before for a database with no folders. |
| P5-AC10 | A backup exists within one minute of first start, one per day after, seven kept; Back up now works; restore steps in the README were rehearsed on a copy and the result is recorded. |
| P5-AC11 | All gates in QA §3 hold at each checkpoint, including the additive-API check and the migration test. |
| P5-AC12 | Web answers are unchanged: `make eval-web` offline replay matches the Phase 4 baseline. |

Report each checkpoint in `docs/PHASE-5-REPORT.md`.

**User clarification — 5 October 2026 (preset precedence):** Jake delegated the
conflict between exact preset-only sampling and the frozen model-default pipeline
to Codex ("Do what you think is best."). Preserve saved model defaults: a preset
overrides only the values it stores; unspecified values inherit the user's saved
model defaults, otherwise the runtime default. Empty presets add no sampling
values of their own. This refines P5-AC1; no provider/run pipeline change is needed.
