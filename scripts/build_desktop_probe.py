"""Build/sign AS1-A source in isolation. Never open apps or request permission."""

import argparse
import hashlib
import json
import os
import plistlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = "dev.agenticrag.aether.desktop-trial"


def build(output: Path) -> dict[str, object]:
    output = output.expanduser().absolute()
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    bundle = output / "Aether Desktop Trial.app"
    executable = bundle / "Contents/MacOS/DesktopTrial"
    executable.parent.mkdir(parents=True)
    info = {
        "CFBundleIdentifier": IDENTITY,
        "CFBundleName": "Aether Desktop Trial",
        "CFBundleDisplayName": "Aether Desktop Trial",
        "CFBundleExecutable": "DesktopTrial",
        "CFBundlePackageType": "APPL",
        "CFBundleVersion": "1",
        "CFBundleShortVersionString": "0.1.0",
        "LSUIElement": True,
        "LSMinimumSystemVersion": "13.0",
    }
    (bundle / "Contents/Info.plist").write_bytes(plistlib.dumps(info))
    source = ROOT / "tools/mac_desktop/Probe.swift"
    subprocess.run(["/usr/bin/swiftc", "-O", str(source), "-o", str(executable)], check=True)
    subprocess.run(
        ["/usr/bin/codesign", "--sign", "-", "--identifier", IDENTITY, str(bundle)], check=True
    )
    subprocess.run(["/usr/bin/codesign", "--verify", "--strict", str(bundle)], check=True)
    files = {
        str(p.relative_to(bundle)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(bundle.rglob("*"))
        if p.is_file()
    }
    manifest = {
        "protocol": 1,
        "identity": IDENTITY,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "files": files,
        "signing": "local ad-hoc; exact-build qualification only",
        "native_executed": False,
    }
    file = output / "build-manifest.json"
    file.write_text(json.dumps(manifest, indent=2) + "\n")
    os.chmod(file, 0o600)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    options = parser.parse_args()
    print(json.dumps(build(options.output), indent=2))
