#!/bin/bash
# Sets up local transcription on an Apple Silicon Mac:
#   1. installs ffmpeg and whisper.cpp with Homebrew
#   2. downloads the Whisper model and the voice-activity model (one time)
#   3. creates the inbox / done / failed / logs folders
#   4. installs the launchd agent that watches the inbox
#   5. transcribes a spoken test sentence to prove it works
#
# Safe to run again. Options:
#   --no-agent      set everything up but do not install the launchd watcher
#   --no-selftest   skip the spoken test sentence
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO"

INSTALL_AGENT=1
SELFTEST=1
for arg in "$@"; do
    case "$arg" in
        --no-agent) INSTALL_AGENT=0 ;;
        --no-selftest) SELFTEST=0 ;;
        *) echo "Unknown option: $arg" >&2; exit 2 ;;
    esac
done

step() { printf '\n==> %s\n' "$1"; }
die()  { printf '\nError: %s\n' "$1" >&2; exit 1; }

[ "$(uname -s)" = "Darwin" ] || die "This installer is for macOS."

case "$REPO/" in
    "$HOME/Desktop/"*|"$HOME/Documents/"*|"$HOME/Downloads/"*)
        [ "$INSTALL_AGENT" -eq 0 ] || die "This repo is inside Desktop, Documents or Downloads. macOS privacy
protection can stop a background service from reading those folders, so the
watcher would fail after a reboot. Either move the repo somewhere else in your
home folder (for example ~/local-transcribe), or run ./install.sh --no-agent
and start the watcher yourself with: bin/transcribe watch" ;;
esac

# --- Homebrew packages ------------------------------------------------------
step "Checking Homebrew"
if ! command -v brew >/dev/null 2>&1; then
    if [ -x /opt/homebrew/bin/brew ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        die "Homebrew is not installed. Install it from https://brew.sh and run this again."
    fi
fi

for formula in ffmpeg whisper-cpp; do
    if brew list --formula "$formula" >/dev/null 2>&1; then
        echo "$formula already installed"
    else
        step "Installing $formula"
        brew install "$formula"
    fi
done
command -v ffmpeg >/dev/null 2>&1 || die "ffmpeg is not on PATH after installing."
command -v whisper-cli >/dev/null 2>&1 || die "whisper-cli is not on PATH after installing whisper-cpp.
Find the binary with: brew list whisper-cpp
then set \"whisper_cli\" to its full path in config.json."

# --- Python (standard library only; nothing is pip-installed) ----------------
step "Finding Python 3.9+"
PY=""
for candidate in "$(brew --prefix)/bin/python3" /usr/bin/python3; do
    if [ -x "$candidate" ] && "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
        PY="$candidate"
        break
    fi
done
if [ -z "$PY" ]; then
    brew install python
    PY="$(brew --prefix)/bin/python3"
fi
echo "$PY" > .python
echo "Using $PY ($("$PY" --version 2>&1))"

# --- Local settings ---------------------------------------------------------
[ -f config.json ] || { cp config.example.json config.json; echo "Created config.json"; }
[ -f glossary.txt ] || { cp glossary.example.txt glossary.txt; echo "Created glossary.txt"; }

# --- Models -----------------------------------------------------------------
# The only network use in this project: a one-time download of model weights.
# Nothing is ever uploaded, and transcription itself runs fully offline.
config_path() {
    PYTHONPATH="$REPO" "$PY" -c "from localtranscribe.config import load_config; print(load_config().path('$1'))"
}
download() {
    local url="$1" dest="$2" min_bytes="$3" size
    if [ -s "$dest" ]; then
        echo "Already have $(basename "$dest")"
        return
    fi
    mkdir -p "$(dirname "$dest")"
    echo "Downloading $(basename "$dest")"
    curl -L --fail --progress-bar -C - -o "$dest.part" "$url" \
        || die "Download failed: $url"
    size=$(wc -c < "$dest.part" | tr -d ' ')
    [ "$size" -ge "$min_bytes" ] || die "$(basename "$dest") is only $size bytes; the download looks wrong. Delete $dest.part and try again."
    mv "$dest.part" "$dest"
}

step "Fetching models"
MODEL_PATH="$(config_path model)"
VAD_PATH="$(config_path vad_model)"
download "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/$(basename "$MODEL_PATH")" "$MODEL_PATH" 50000000
download "https://huggingface.co/ggml-org/whisper-vad/resolve/main/$(basename "$VAD_PATH")" "$VAD_PATH" 300000

# --- Folders and checks -----------------------------------------------------
step "Checking the setup"
bin/transcribe doctor || die "Setup is incomplete; see the FAIL lines above."

# --- Spoken self-test -------------------------------------------------------
if [ "$SELFTEST" -eq 1 ]; then
    step "Self-test: speaking a sentence with macOS 'say' and transcribing it"
    TMP="$(mktemp -d)"
    say -o "$TMP/selftest.aiff" "This is a test of the local transcription pipeline. If you can read this sentence, it works."
    if bin/transcribe run "$TMP/selftest.aiff" --out-dir "$TMP"; then
        echo "(Self-test passed if the sentence above reads correctly.)"
    else
        rm -rf "$TMP"
        die "Self-test failed; see the message above."
    fi
    rm -rf "$TMP"
fi

# --- launchd watcher --------------------------------------------------------
if [ "$INSTALL_AGENT" -eq 1 ]; then
    step "Installing the launchd watcher"
    bin/transcribe install-agent
fi

INBOX="$(PYTHONPATH="$REPO" "$PY" -c "from localtranscribe.config import load_config; print(load_config().inbox_dir)")"
printf '\nAll set. Drop an audio file into:\n  %s\nand the transcript will appear in the done folder beside it.\n' "$INBOX"
