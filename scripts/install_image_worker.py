"""Install public worker source; reuse approved private interpreter/model weights."""
import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = Path.home() / ".local/share/workbench"
REVISION = "e7b7dc27f91deacad38e78976d1f2b499d76a294"


def install(home: Path, python: Path, model: Path) -> None:
    if not python.is_file() or not model.is_dir() or model.name != REVISION:
        raise ValueError("The approved interpreter and pinned model must already exist")
    home.mkdir(mode=0o700, parents=True, exist_ok=True)
    home.chmod(0o700)
    shutil.copyfile(ROOT / "image_worker/product/worker.py", home / "worker.py")
    (home / "worker.py").chmod(0o600)
    for name, text in ((".python", str(python) + "\n"),
                       ("config.json", json.dumps({"model_path": str(model)}, indent=2) + "\n")):
        (home / name).write_text(text)
        (home / name).chmod(0o600)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--home", type=Path, default=BASE / "image-worker/product")
    parser.add_argument("--python", type=Path, default=BASE / "image-worker/i0/venv/bin/python")
    parser.add_argument("--model", type=Path, default=BASE / "models/image/huggingface/hub/models--black-forest-labs--FLUX.2-klein-4B/snapshots" / REVISION)
    args = parser.parse_args()
    if args.apply:
        install(args.home.expanduser().absolute(), args.python.expanduser().absolute(), args.model.expanduser().absolute())
        print("Worker source installed. Existing interpreter and shared weights reused; no downloads.")
    else:
        print("Plan: copy the public worker only; reference the existing private interpreter and pinned weights.")


if __name__ == "__main__":
    main()
