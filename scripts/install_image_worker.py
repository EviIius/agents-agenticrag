"""Install reviewed public workers; reuse the existing interpreter and weights."""

import argparse
import fcntl
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = Path.home() / ".local/share/workbench"
REVISION = "e7b7dc27f91deacad38e78976d1f2b499d76a294"
FILES = ("worker.py", "edit_worker.py", "reference_contract.py", "reference_codec.py")


def replace(path: Path, raw: bytes) -> None:
    """Publish one private durable file without following an existing symlink."""
    fd, temporary = tempfile.mkstemp(prefix=".install-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def install(home: Path, python: Path, model: Path, *, lock: Path | None = None) -> None:
    """Caller quiesces the app first; native lock also refuses an occupied GPU slot.

    Preparation installs into a separate private staging home. Existing selector
    bytes are preserved; changing the interpreter/model needs its own approval.
    A failed update restores the previous named files. Unrelated files stay put.
    """
    if not python.is_file() or not os.access(python, os.X_OK):
        raise ValueError(
            "The approved image interpreter must already exist and be executable"
        )
    if not model.is_dir() or model.name != REVISION:
        raise ValueError("The approved pinned model must already exist")
    if home.is_symlink() or (home.exists() and not home.is_dir()):
        raise ValueError("Worker home must be a private directory")
    payload = {}
    for name in FILES:
        source = ROOT / "image_worker/product" / name
        if source.is_symlink() or not source.is_file():
            raise ValueError("Reviewed worker source is missing")
        payload[name] = source.read_bytes()
    payload[".python"] = (str(python) + "\n").encode()
    payload["config.json"] = (
        json.dumps({"model_path": str(model)}, indent=2) + "\n"
    ).encode()
    for name in payload:
        if (home / name).is_symlink():
            raise ValueError("Worker files must not be symlinks")
    if (home / ".python").exists():
        if (home / ".python").read_text().strip() != str(python):
            raise ValueError(
                "Existing interpreter selector differs; runtime change not authorized"
            )
        payload[".python"] = (home / ".python").read_bytes()
    if (home / "config.json").exists():
        if json.loads((home / "config.json").read_text()) != {"model_path": str(model)}:
            raise ValueError(
                "Existing model selector differs; model change not authorized"
            )
        payload["config.json"] = (home / "config.json").read_bytes()
    lock = lock or BASE / "data/native.lock"
    lock.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError(
                "Native worker is active; quiesce it before installation"
            ) from None
        home.mkdir(mode=0o700, parents=True, exist_ok=True)
        home.chmod(0o700)
        before = {
            name: (home / name).read_bytes() if (home / name).exists() else None
            for name in payload
        }
        try:
            for name, raw in payload.items():
                replace(home / name, raw)
            directory = os.open(home, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except BaseException:
            for name, raw in before.items():
                if raw is None:
                    (home / name).unlink(missing_ok=True)
                else:
                    replace(home / name, raw)
            raise
    finally:
        os.close(fd)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--home", type=Path, default=BASE / "image-worker/product")
    parser.add_argument(
        "--python", type=Path, default=BASE / "image-worker/i0/venv/bin/python"
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=BASE
        / "models/image/huggingface/hub/models--black-forest-labs--FLUX.2-klein-4B/snapshots"
        / REVISION,
    )
    args = parser.parse_args()
    if args.apply:
        install(
            args.home.expanduser().absolute(),
            args.python.expanduser().absolute(),
            args.model.expanduser().absolute(),
        )
        print(
            "Reviewed generation/edit workers installed; existing interpreter/weights reused."
        )
    else:
        print(
            "Plan: quiesce the app, install four reviewed worker/CPU files, "
            "preserve selectors. No downloads."
        )


if __name__ == "__main__":
    main()
