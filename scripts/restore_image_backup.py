"""Offline full backup restore, into a new private directory only."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
from app.images.backup import restore

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--backup", required=True, type=Path)
parser.add_argument("--destination", required=True, type=Path)
args = parser.parse_args()
count = restore(args.backup.resolve(), args.destination.expanduser().absolute())
print(f"Restored database and {count} image outputs into the new directory.")
