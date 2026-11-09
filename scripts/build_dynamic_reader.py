"""Build/sign the dynamic selected-pane reader in isolation. Never open apps or request permission."""

import argparse
import hashlib
import json
import os
import plistlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = "dev.agenticrag.aether.desktop-trial"


def build(
    output: Path,
    read_boundary: Path | None = None,
    *,
    source_name: str = "ReadProbeDynamic.swift",
) -> dict[str, object]:
    boundary: bytes | None = None
    if read_boundary is not None:
        # Import the installed Pydantic contract without importing/launching macOS APIs.
        import sys

        sys.path.insert(0, str(ROOT / "server"))
        from app.assistant.mac_probe import private_read
        from app.assistant.mac_reader import ReadBoundary

        raw = private_read(read_boundary, 50_000)
        boundary = ReadBoundary.model_validate_json(raw).model_dump_json().encode()
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
    if source_name not in {
        "ReadProbeDynamic.swift",
        "ReadOnlySnapshot.swift",
        "SelectedMetadata.swift",
    }:
        raise ValueError("Choose a fixed reader source.")
    source = ROOT / "tools/mac_desktop" / (source_name if boundary else "Probe.swift")
    if boundary:
        resources = bundle / "Contents/Resources"
        resources.mkdir()
        (resources / "read-boundary.json").write_bytes(boundary)
    snapshot = output / "source.snapshot.swift"
    content = source.read_bytes()
    if source_name == "SelectedMetadata.swift" and boundary:
        shared = (ROOT / "tools/mac_desktop/ReadOnlySnapshot.swift").read_bytes()
        markers = (b"struct Area: Codable", b"extension Reader {", b"    func body(")
        if any(shared.count(marker) != 1 for marker in markers):
            raise ValueError("The frozen read-only definitions changed.")
        # Reuse only shape/selection and bounded metadata helpers. Exclude body
        # reading at source level rather than relying on the linker to remove it.
        shape = shared.split(markers[0])[0]
        text = markers[1] + shared.split(markers[1])[1].split(markers[2])[0] + b"}\n"
        content = shape + text + b"\n" + content
    snapshot.write_bytes(content)
    os.chmod(snapshot, 0o600)
    subprocess.run(["/usr/bin/swiftc", "-O", str(snapshot), "-o", str(executable)], check=True)
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
        "source_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
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
    parser.add_argument("--read-boundary", type=Path)
    options = parser.parse_args()
    print(json.dumps(build(options.output, options.read_boundary), indent=2))
