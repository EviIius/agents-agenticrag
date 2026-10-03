#!/usr/bin/env python3
"""Stand-in for whisper-cli, so the tests run without model weights.

It accepts the same flags the pipeline passes to the real whisper-cli, insists
on the input format Whisper needs (16 kHz, mono, 16-bit), and writes JSON in
whisper.cpp's layout. "Speech" is wherever the audio is not silent, so the
tests can check timing and channel handling.

Controlled by environment variables:
  FAKE_WHISPER_TEXT       text for the segments (default: "speech")
  FAKE_WHISPER_FAIL       exit 1 with an error message
  FAKE_WHISPER_SLEEP      seconds to wait before answering (a long job)
  FAKE_WHISPER_PID_FILE   write this process's pid here
  FAKE_WHISPER_OLD_BUILD  behave like a build without --vad / --carry-initial-prompt
  FAKE_WHISPER_ARGS_LOG   append the received arguments (JSON lines) here
"""
import array
import json
import os
import sys
import wave


HELP = """usage: whisper-cli [options] file0 file1 ...
  -oj,       --output-json          [false  ] output result in a JSON file
             --prompt PROMPT        [       ] initial prompt
             --carry-initial-prompt [false  ] always prepend initial prompt
             --vad                  [false  ] enable Voice Activity Detection (VAD)
  -vm FNAME, --vad-model FNAME      [       ] VAD model path
"""
OLD_HELP = """usage: whisper-cli [options] file0 file1 ...
  -oj,       --output-json          [false  ] output result in a JSON file
             --prompt PROMPT        [       ] initial prompt
"""


def main(argv):
    old_build = bool(os.environ.get("FAKE_WHISPER_OLD_BUILD"))
    if "--help" in argv:
        sys.stderr.write(OLD_HELP if old_build else HELP)
        return 0
    if old_build and ("--vad" in argv or "--carry-initial-prompt" in argv):
        print("error: unknown argument", file=sys.stderr)
        return 1
    args = {"extra": []}
    it = iter(argv)
    for token in it:
        if token in ("-m", "-f", "-of", "-l", "-t", "--prompt", "-vm"):
            args[token] = next(it)
        elif token in ("-oj", "-np", "--carry-initial-prompt", "--vad"):
            args[token] = True
        else:
            args["extra"].append(token)

    log_path = os.environ.get("FAKE_WHISPER_ARGS_LOG")
    if log_path:
        with open(log_path, "a") as fh:
            fh.write(json.dumps(argv) + "\n")
    if os.environ.get("FAKE_WHISPER_PID_FILE"):
        with open(os.environ["FAKE_WHISPER_PID_FILE"], "w") as fh:
            fh.write(str(os.getpid()))
    if os.environ.get("FAKE_WHISPER_SLEEP"):
        import time
        time.sleep(float(os.environ["FAKE_WHISPER_SLEEP"]))
    if os.environ.get("FAKE_WHISPER_FAIL"):
        print("error: failed to initialize whisper context", file=sys.stderr)
        return 1
    if not os.path.exists(args.get("-m", "")):
        print("error: model not found", file=sys.stderr)
        return 2

    with wave.open(args["-f"], "rb") as wav:
        fmt = (wav.getframerate(), wav.getnchannels(), wav.getsampwidth())
        if fmt != (16000, 1, 2):
            print("error: expected 16 kHz mono 16-bit, got %r" % (fmt,), file=sys.stderr)
            return 3
        samples = array.array("h", wav.readframes(wav.getnframes()))

    # One segment per stretch of non-silent audio (100 ms windows).
    window = 1600
    regions, start = [], None
    for i in range(0, len(samples), window):
        chunk = samples[i:i + window]
        loud = max((abs(v) for v in chunk), default=0) > 500
        if loud and start is None:
            start = i
        elif not loud and start is not None:
            regions.append((start, i))
            start = None
    if start is not None:
        regions.append((start, len(samples)))

    text = os.environ.get("FAKE_WHISPER_TEXT", "speech")

    def stamp(ms):
        h, rem = divmod(ms, 3600000)
        m, rem = divmod(rem, 60000)
        s, ms = divmod(rem, 1000)
        return "%02d:%02d:%02d,%03d" % (h, m, s, ms)

    transcription = []
    for a, b in regions:
        t0, t1 = a * 1000 // 16000, b * 1000 // 16000
        transcription.append({
            "timestamps": {"from": stamp(t0), "to": stamp(t1)},
            "offsets": {"from": t0, "to": t1},
            "text": " " + text,
        })
    with open(args["-of"] + ".json", "w") as fh:
        json.dump({"result": {"language": args.get("-l", "en")},
                   "transcription": transcription}, fh)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
