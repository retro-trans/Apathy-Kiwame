"""Archive a local preview as verified reverse Xdelta patches against its successor."""

import argparse
from hashlib import file_digest
from pathlib import Path
import subprocess
import tempfile

from scenario import write_json
from steam_game import ROOT


def files(folder):
    return {path.relative_to(folder).as_posix(): path for path in folder.rglob("*")
            if path.is_file() and path.suffix.lower() != ".sav" and
            "qa-profile" not in path.relative_to(folder).parts}


def digest(path):
    with path.open("rb") as source:
        return file_digest(source, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("older", type=Path)
    parser.add_argument("newer", type=Path)
    parser.add_argument("--xdelta", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    older, newer, xdelta = (item.resolve(strict=True) for item in (args.older, args.newer, args.xdelta))
    output = ROOT / "work" / "output"
    if older == newer or any(folder.parent != output for folder in (older, newer)):
        parser.error("Choose two distinct builds under work/output.")
    for folder in (older, newer):
        if not (folder / "package.nw" / "debug-runtime.js").is_file():
            parser.error(f"Missing isolated QA package in {folder}")
    archive = ROOT / "work" / "patches" / older.name
    if archive.exists():
        parser.error(f"Patch archive already exists: {archive}")
    old_files, new_files = files(older), files(newer)
    remove = sorted(new_files.keys() - old_files.keys())
    changes = {}
    for name, old in sorted(old_files.items()):
        new = new_files.get(name)
        before = digest(old)
        after = digest(new) if new else None
        if before != after:
            changes[name] = {"patch": f"{name}.xdelta", "source_sha256": after, "target_sha256": before}
    print(f"{newer.name} -> {older.name}: {len(changes)} reverse deltas, {len(remove)} removed files")
    for name in changes:
        print(f"  {name}")
    if args.dry_run:
        return
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=archive.parent) as work:
        scratch = Path(work)
        stage = scratch / "archive"
        stage.mkdir()
        for name, change in changes.items():
            patch = stage / change["patch"]
            patch.parent.mkdir(parents=True, exist_ok=True)
            source = ["-s", str(new_files[name])] if name in new_files else []
            recovered = scratch / "recovered"
            subprocess.run([str(xdelta), "-e", *source, str(old_files[name]), str(patch)], check=True)
            subprocess.run([str(xdelta), "-d", *source, str(patch), str(recovered)], check=True)
            if digest(recovered) != change["target_sha256"]:
                raise ValueError(f"Xdelta verification failed for {name}")
            recovered.unlink()
        write_json(stage / "manifest.json", {"source": newer.name, "target": older.name,
                                            "changes": changes, "remove": remove})
        stage.rename(archive)


if __name__ == "__main__":
    main()
