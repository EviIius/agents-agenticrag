"""Build the exact named reader and separate invented-database checker. No live store access."""

import argparse
import hashlib
import json
import os
import plistlib
import stat
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = "dev.agenticrag.aether.messages-reader"


def build(output: Path) -> dict:
    output = output.expanduser().absolute()
    output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if output.parent.is_symlink() or stat.S_IMODE(output.parent.stat().st_mode) != 0o700:
        raise ValueError("The trial parent must be a private directory.")
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    bundle = output / "Aether Messages Reader.app"
    executable = bundle / "Contents/MacOS/MessagesReader"
    executable.parent.mkdir(parents=True)
    (bundle / "Contents/Info.plist").write_bytes(
        plistlib.dumps(
            {
                "CFBundleIdentifier": IDENTITY,
                "CFBundleName": "Aether Messages Reader",
                "CFBundleDisplayName": "Aether Messages Reader",
                "CFBundleExecutable": "MessagesReader",
                "CFBundlePackageType": "APPL",
                "CFBundleVersion": "1",
                "CFBundleShortVersionString": "0.1.0",
                "LSMinimumSystemVersion": "13.0",
            }
        )
    )
    folder = ROOT / "tools/mac_desktop"
    core = (folder / "MessagesStore.swift").read_bytes()
    for name, source, target in [
        (
            "source.snapshot.swift",
            core + (folder / "MessagesStoreTrial.swift").read_bytes(),
            executable,
        ),
        (
            "fixtures.snapshot.swift",
            core + (folder / "MessagesStoreFixtures.swift").read_bytes(),
            output / "StoreFixtures",
        ),
    ]:
        path = output / name
        path.write_bytes(source)
        os.chmod(path, 0o600)
        subprocess.run(["/usr/bin/swiftc", "-O", str(path), "-o", str(target)], check=True)
    subprocess.run(
        ["/usr/bin/codesign", "--sign", "-", "--identifier", IDENTITY, str(bundle)], check=True
    )
    subprocess.run(["/usr/bin/codesign", "--verify", "--strict", str(bundle)], check=True)
    manifest = {
        "protocol": 1,
        "identity": IDENTITY,
        "source_sha256": hashlib.sha256(
            (output / "source.snapshot.swift").read_bytes()
        ).hexdigest(),
        "files": {
            str(p.relative_to(bundle)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(bundle.rglob("*"))
            if p.is_file()
        },
        "signing": "exact-build local ad-hoc; production signing not qualified",
        "real_store_access": False,
    }
    file = output / "build-manifest.json"
    file.write_text(json.dumps(manifest, indent=2) + "\n")
    os.chmod(file, 0o600)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))
