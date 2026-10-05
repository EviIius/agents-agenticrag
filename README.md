# Workbench

Local Ollama chat, optional web search and local audio transcription. The build plan is
[docs/SPEC.md](docs/SPEC.md); phase reports and synthetic evidence document verification.

## Setup and development

Requires Python ≥3.12, uv, Node ≥22.12 and npm. `scripts/tool-env.sh` also finds the
isolated tools under `~/.local/share/workbench/tools`. Ollama must already be running.

```sh
make setup
make build
make dev-server
# In a second terminal:
make dev
```

The server uses **127.0.0.1:8787**, one worker. Vite uses 5173 and proxies `/api` to
that server. Stop the installed launchd service before starting a development server.
`/design` contains labelled synthetic states and is disabled in production.

```sh
make check          # lint, types, unit/integration tests, coverage, contrast, API types
make e2e            # Chromium + iPhone-sized WebKit; isolated fake runtime/data
make api-types      # regenerate the frontend API contract after schema edits
make eval-web       # repeatable Phase 2 search evaluation
make fmt
```

E2E owns 8787 while running; never point it at the live server. Fixtures and screenshots
must use synthetic audio and text. Real recordings, their names, transcripts, account
keys and personal glossary content do not belong in Git or logs.

## Use

Select a chat model; **Load** also selects it. Context presets respect the model's
configured operational limit. Sampling controls left at **Model default** are omitted
from requests. The standard Llama variant is hidden through a stored user preference.

Web search uses configured free providers, with Ollama Search preferred when its key
is saved in Settings → Search. Keys stay in the private database. Search may send
queries to those providers; chats containing recordings block it by default.

**⌘/Ctrl+K** opens chat search and actions. **⌘/Ctrl+/** opens shortcuts. Chat menus
support rename, pin, title-based Markdown/JSON export and deletion.

## Recordings and storage

Use **Add attachment → Add recording** for WAV and supported audio formats. Upload
progress is measured; transcription jobs run sequentially and continue if the browser
closes. Review text or timestamps, download text/SRT/JSON, or ask the local Ollama model
about the transcript. A transcript larger than the model's context can still be downloaded.

**Audio is temporary by default.** Workbench removes its uploaded copy after saving the
transcript to SQLite. Original/raw text, timestamps and metadata remain saved until the
attachment or chat is removed. Original files on your phone or computer are unaffected.
Failed/cancelled audio remains available for Retry; unfinished unsent attachments expire
after seven days. Completed transcript outputs are preserved even before sending them
to a chat; remove the attachment or chat explicitly when you no longer want its outputs.

Settings → Transcription provides **Keep original audio after transcription** (opt-in)
and **Clear stored audio**, with a confirmation and storage count. Clearing skips active
jobs and preserves transcripts/chats. Removed audio cannot be downloaded or transcribed
again without re-uploading the original. Startup also clears completed historical audio
when retention is off. Clearing removes private copies directly rather than filling Trash.

Engine source is under `transcribe/`, vendored from commit `1019564` of the Transcription
repo. It runs as a subprocess, without an added package. Its weights, `config.json`,
`glossary.txt` and `.python` are ignored by Git; recordings never belong there. The engine
requires the existing ffmpeg, ffprobe and whisper-cli installation. With local engine
assets prepared:

```sh
WORKBENCH_TRANSCRIBE_HOME="$PWD/transcribe" make dev-server
```

Settings shows setup checks. T1 transcription is implemented; manual model cleanup and
glossary editing remain the separate T2 checkpoint. See [the transcription spec](docs/TRANSCRIPTION-SPEC.md).

## Deployment and Tailscale

```sh
./scripts/deploy.sh               # print and verify the deployment plan
make deploy                      # build, back up, install and restart
# When a known development preview currently owns 8787:
make deploy DEPLOY_ARGS='--preview-pid <verified PID>'
```

Deployment discovers and **reuses the existing Workbench launchd label**, copies its
allowed hosts, verifies the existing Tailscale route and keeps the bind/port unchanged.
It installs code in `~/.local/share/workbench/app`, data in `~/.local/share/workbench/data`
and private logs in `~/.local/share/workbench/logs`. The engine is installed inside
`app/transcribe`; first deployment copies the ignored weights/config/glossary/interpreter
selection. Later deployments preserve installed private engine assets. This avoids
launchd access to the source checkout in macOS Documents. No recordings are copied.

The script makes a consistent SQLite backup and keeps the latest ten timestamped backups.
The original launchd plist is saved privately beside them. A failed bootstrap/health check
restores the immediately previous plist. Existing installed package/data remain intact.
For reverting a **new app build**, check out a previously verified Workbench commit and
redeploy; restore a matching database backup if a migration requires it.

The current service label is `dev.agenticrag.workbench`:

```sh
launchctl kickstart -k "gui/$(id -u)/dev.agenticrag.workbench"
```

Keep Tailscale Serve unchanged: HTTPS on the tailnet forwards to 127.0.0.1:8787. Put the
MagicDNS hostname in `WORKBENCH_ALLOWED_HOSTS`; optionally restrict access further with
`WORKBENCH_TAILSCALE_OWNER`. Service logs should contain operational identifiers and counts,
never transcript content or original recording names.

### iPhone installation and offline behavior

Open the Tailscale HTTPS URL in Safari, choose **Share → Add to Home Screen**, then open
Workbench from that icon. The standalone shell uses safe areas and the visible keyboard
viewport. Verify installed-app input, offline behavior and warm-load performance on a
physical phone before closing Phase 3. VoiceOver has a reported failure and is
deferred for this build; support is not claimed.

The service worker caches public shell/hashed assets and never `/api` responses, audio,
transcripts or streamed messages. Without the Mac connection, the shell shows a connection
error; chat and transcription require connectivity. A waiting update displays **A new
version is available → Reload**; content arriving does not force a reload. Clear Safari's
site data if recovering an obsolete local cache.

## Import and rollback to the old app

Settings → Data → **Import old chats** reads the previous SQLite file read-only, converts
conversations into linear message chains, and adds **Imported** to titles. Repeating the
import skips conversations already imported. It imports text, not old recording files.
CLI equivalent:

```sh
. scripts/tool-env.sh
uv run --directory server python ../scripts/import_legacy.py \
  --source "$HOME/.local/share/agenticrag/.data/workbench-chats.db" \
  --data-dir "$HOME/.local/share/workbench/data"
```

The previous source remains recoverable on branch `legacy/chat-web-0.5` and tag `legacy-0.5`.
For a full rollback, stop the Workbench job, restore
`~/.local/share/workbench/data/backups/launchd-before-phase3.plist` to its original
`~/Library/LaunchAgents/dev.agenticrag.workbench.plist` path, then bootstrap that plist.
It points at the untouched old package under `~/.local/share/agenticrag`. Alternatively,
check out the legacy branch in a separate checkout and follow its setup instructions.
Legacy data is only read for import; the new database is independent.

## Codex usage limits and app availability

Atelier runs as the existing `dev.agenticrag.workbench` launchd service, independently of Codex. The local Ollama runtime handles chat; the installed transcription engine runs as a subprocess. A Codex weekly limit stops development assistance, not the installed app. Keep the Mac awake and connected to Tailscale to use it from your phone. Web search still depends on its configured provider.

The verified Phase 4C fallback is commit `9b48ce8` on `codex/phase-4-motion`. To restore that build, use a separate checkout of that commit and run `scripts/deploy.sh --apply`; the script backs up the database and retains the service label, data paths and Tailscale configuration. Do not overwrite or reset a checkout containing unsaved work.
