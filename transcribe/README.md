# local-transcribe

Offline transcription for an Apple Silicon Mac. Drop an audio file into a
folder and a transcript appears next to it. Audio never leaves the machine:
there are no cloud APIs, no accounts and no telemetry. The only network use
is the one-time download of the model weights during install.

    inbox/meeting.wav  ->  done/meeting.wav    the original, untouched
                           done/meeting.txt    plain text
                           done/meeting.srt    timestamped
                           done/meeting.json   everything, incl. raw Whisper text

## Install

Requires macOS on Apple Silicon and [Homebrew](https://brew.sh).

Put the repo anywhere in your home folder **except** Desktop, Documents or
Downloads (macOS privacy protection can block background services there), then:

    ./install.sh

This installs `ffmpeg` and `whisper-cpp` with Homebrew, downloads the Whisper
model (about 1.6 GB) and a small voice-activity model into `models/`, creates
the folders below, speaks a test sentence with `say` and transcribes it, and
installs a launchd agent that watches the inbox. It is safe to run again.

Python 3.9 or newer is used, standard library only. Nothing is pip-installed.

## Folders

Everything lives under `~/Transcription` (change `data_dir` in `config.json`):

| Folder | What it holds |
|---|---|
| `inbox/` | Drop audio here. |
| `done/` | The audio plus its `.txt`, `.srt` and `.json`. |
| `failed/` | Audio that could not be transcribed, with a `.log` saying why. |
| `logs/` | `watcher.log` (activity) and `watcher.launchd.log` (crashes). |

The watcher waits until a file has stopped changing for 10 seconds before
touching it, and for WAV files also checks that the whole file has arrived.
Audio is only read and moved, never changed or deleted. If a name is already
taken in `done/`, the newcomer gets `-2`, `-3` and so on.

To retry a failed file, move it from `failed/` back into `inbox/`.

## Other ways to run it

    bin/transcribe run recording.wav        # one file; transcript beside it
    bin/transcribe run call.wav --channels split
    bin/transcribe doctor                   # check binaries, models, folders
    bin/transcribe status                   # is the launchd watcher running?
    bin/transcribe watch --once             # empty the inbox now, then exit

## Glossary

`glossary.txt` holds names that transcripts get wrong:

    GSMOS = Gismo, GISMO
    BUSCRT = bus cart, BuzzCART
    FCTDS

The left side is the correct spelling. The right side lists wrong forms seen
in transcripts; it is optional. Add a line, save, and the next recording uses
it. No restart is needed.

Two things happen with it. The correct forms are given to Whisper as a
vocabulary hint, so it is more likely to write them correctly. Then any wrong
form that still appears is replaced (ignoring case and spacing). The `.json`
keeps Whisper's original wording as `raw_text` and lists every replacement
under `glossary_corrections`, so you can see exactly what was changed.

`glossary.txt` and `config.json` are in `.gitignore`, so internal names stay
out of version control. `glossary.example.txt` is the committed template.

## Logs

    tail -f ~/Transcription/logs/watcher.log
    cat ~/Transcription/failed/<name>.log

`watcher.log` records each file picked up, how long it took, and any
warnings. If the setup is broken (model missing, ffmpeg gone), the watcher
says so there and leaves files waiting in the inbox rather than failing them.

## Settings

Edit `config.json` (created from `config.example.json`). The useful ones:

| Key | Default | Meaning |
|---|---|---|
| `data_dir` | `~/Transcription` | Parent of inbox, done, failed, logs. |
| `model` | `models/ggml-large-v3-turbo.bin` | Whisper model file. |
| `use_vad` | `true` | Skip silence, which stops Whisper inventing text in pauses. |
| `language` | `en` | Or `auto`. |
| `channels` | `mix` | `split` gives one speaker per channel (below). |
| `speaker_labels` | `Speaker 1`, `Speaker 2` | Names used in split mode. |
| `watcher.settle_seconds` | `10` | Quiet time before a file is picked up. |

After changing `data_dir` or moving the repo, run `./install.sh` again. To
use the larger, slower `large-v3` model, set `model` to
`models/ggml-large-v3.bin` and run `./install.sh` again to download it.

## Calls recorded with one speaker per channel

With `"channels": "split"`, each channel is transcribed on its own and the
results are merged by timestamp with speaker labels. This is off by default
because an ordinary stereo recording of a room would come out as the same
words twice. Turn it on per file with `--channels split`, or for everything
in `config.json`.

## Why whisper.cpp

The engine is [whisper.cpp](https://github.com/ggml-org/whisper.cpp) with the
`large-v3-turbo` model.

- One Homebrew package, no Python environment to maintain, GPU-accelerated
  through Metal on Apple Silicon.
- The model is loaded for each recording and released afterwards, so between
  recordings it uses no memory at all. That matters on a machine that also
  keeps a large LLM loaded.
- Voice-activity detection is built in.

MLX-based Whisper is faster (about 2x in one recent benchmark) but needs its
own Python environment. For a folder that is processed unattended, speed
matters less than having few moving parts. The engine is isolated in
`localtranscribe/whisper.py` if that changes.

## Tests

    python3 -m unittest discover -s tests -t .

The tests need `ffmpeg` but no model: they generate recordings in field
recorder formats (96 kHz / 24-bit stereo, four-track, float, m4a, flac, mp3)
and use a stand-in for `whisper-cli`.

## Uninstall

    ./uninstall.sh

Stops and removes the launchd agent. Recordings, transcripts and models stay.

## Notes

- The watcher is a launchd *agent*, so it starts when you log in. For a Mac
  that should recover from a power cut with nobody there, turn on automatic
  login.
- Not built yet: a localhost HTTP service, the harness `transcribe` tool with
  LLM clean-up, and phone upload over Tailscale.

## Use from another program

Workbench runs this engine as a subprocess; no Python imports or shared service are needed.

| Call | Result |
|---|---|
| `bin/transcribe doctor --json` | Setup checks as JSON. Exit 0 when ready, 1 when a blocking check fails. |
| `bin/transcribe run <audio> --out-dir <dir> --quiet [--channels split]` | Writes `<dir>/<stem>.json`, `.txt`, `.srt`; stdout stays empty. |
| Run exit code | 0: done; 1: failed (last stderr line gives the reason); 130: cancelled. |
| SIGTERM to `run` | Stops ffmpeg/Whisper children, clears scratch files and exits 130. |

The source audio is kept unchanged. Read transcript content from the result JSON and keep
stderr private. The engine reads its own local config and glossary on each run.

## Workbench vendored source

Public engine source from Transcription commit `1019564`. Workbench runs `bin/transcribe` as a subprocess. Weights, personal config, glossary, and interpreter selection are ignored by Git. Workbench deployment installs this folder inside its installed app; recordings and transcripts never belong in this folder.
