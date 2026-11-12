"""Prepare six narrowly scoped English UI substitutions without writing game files.

patches(package) returns verified output bytes for the installer. The command line
is read-only by default; --preview writes only to a separate work/debug directory.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT / "work/debug/kiwame-base/package.nw"
SOURCE_SHA256 = {
    "data/system/Config.tjs": "68bf76ccfa28a1a873384e097642126aa8affa263df7721dad0e8f2b5fa072ca",
    "tyrano/libs.js": "69067d5543c2bee2c0911986cd008327e1d4f439ef6feaca7c35a9da65372da5",
    "tyrano/plugins/kag/kag.parser.js": "c48ab15b06a2ab44e5dcc435f9122d18ed07a7b1cd4da4629a0c7f67f20f6ad0",
}

# Japanese UI terms are the exact source anchors, not scenario prose. Keep the
# surrounding call/concatenation bytes in each anchor unchanged.
SAVE_UNAVAILABLE = "この環境はセーブ機能を利用できません。ローカルで実行している場合などに発生します"
SAVE_RESET_CONFIRM = "セーブデータが壊れている可能性があります。セーブデータを初期化しますか？"
RULES = {
    "data/system/Config.tjs": (
        ("startup_title", 3, 1,
         ";System.title=アパシー学校であった怖い話　極\n",
         ";System.title=Apathy Kiwame\n"),
    ),
    "tyrano/libs.js": (
        ("save_unavailable", [743, 782, 841], 3,
         f'alert("{SAVE_UNAVAILABLE}");\r\n            $.confirmSaveClear();',
         'alert("Saving is unavailable in this environment. This can happen when the game is run locally.");\r\n            $.confirmSaveClear();'),
        ("save_reset_confirm", 752, 1,
         f"if(confirm('{SAVE_RESET_CONFIRM}')){{",
         "if(confirm('The save data may be corrupted. Reset the save data?')){"),
        ("save_reset_feedback", 753, 1,
         'alert("初期化");\r\n           localStorage.clear();',
         'alert("Resetting save data.");\r\n           localStorage.clear();'),
    ),
    "tyrano/plugins/kag/kag.parser.js": (
        ("config_error_prefix", 2, 1,
         r'error_str+="Error:Config.tjs\u306b\u8aa4\u308a\u304c\u3042\u308a\u307e\u3059/\u884c:"+i+""',
         'error_str+="Error in Config.tjs at line "+i+""'),
        ("unbalanced_if", 7, 1,
         r'if(this.deep_if!=0){alert("[if]\u3068[endif]\u306e\u6570\u304c\u4e00\u81f4\u3057\u307e\u305b\u3093\u3002\u30b7\u30ca\u30ea\u30aa\u3092\u898b\u76f4\u3057\u3066\u307f\u307e\u305b\u3093\u304b\uff1f");this.deep_if=0}',
         'if(this.deep_if!=0){alert("The numbers of [if] and [endif] tags do not match. Check the scenario.");this.deep_if=0}'),
    ),
}


def _digest(raw):
    return sha256(raw).hexdigest()


def _read_sources(package):
    package = Path(package).resolve()
    sources = {}
    for relative, expected in SOURCE_SHA256.items():
        path = package / relative
        raw = path.read_bytes()
        actual = _digest(raw)
        if actual != expected:
            raise ValueError(f"Unexpected source SHA256 for {relative}: {actual}; expected {expected}")
        sources[path] = raw
    return package, sources


def patches(package) -> dict[Path, bytes]:
    """Return patched bytes for the exact audited sources; never write or run them."""
    package, sources = _read_sources(package)
    result = {}
    for relative, rules in RULES.items():
        path = package / relative
        original = sources[path]
        modified = original
        for name, _lines, expected, old, new in rules:
            old, new = old.encode("utf-8"), new.encode("utf-8")
            count = modified.count(old)
            if count != expected:
                raise ValueError(f"Unexpected anchor count for {relative}:{name}: {count}; expected {expected}")
            if new in modified:
                raise ValueError(f"English replacement already present for {relative}:{name}")
            modified = modified.replace(old, new)

        # Removing the allowed literal changes must reconstruct the exact input.
        reconstructed = modified
        for name, _lines, expected, old, new in reversed(rules):
            old, new = old.encode("utf-8"), new.encode("utf-8")
            if reconstructed.count(new) != expected:
                raise ValueError(f"Unexpected output anchor count for {relative}:{name}")
            reconstructed = reconstructed.replace(new, old)
        if reconstructed != original:
            raise ValueError(f"Unapproved byte changes in {relative}")
        if (modified.count(b"\r\n"), modified.count(b"\n")) != (original.count(b"\r\n"), original.count(b"\n")):
            raise ValueError(f"Line endings changed in {relative}")
        if relative == "data/system/Config.tjs":
            old_ids = [line for line in original.splitlines(keepends=True) if line.startswith(b";projectID=")]
            new_ids = [line for line in modified.splitlines(keepends=True) if line.startswith(b";projectID=")]
            if old_ids != [b";projectID=kiwame\n"] or new_ids != old_ids:
                raise ValueError("Config projectID changed")
        result[path] = modified
    return result


def describe(package, prepared=None):
    """Describe the proposed byte changes without any Japanese source text dump."""
    package = Path(package).resolve()
    prepared = patches(package) if prepared is None else prepared
    files = []
    for path, modified in prepared.items():
        relative = path.relative_to(package).as_posix()
        original = path.read_bytes()
        files.append({
            "file": relative,
            "source_sha256": _digest(original),
            "modified_sha256": _digest(modified),
            "source_bytes": len(original),
            "modified_bytes": len(modified),
            "lines": len(original.splitlines()),
            "changes": [{"id": rule[0], "source_lines": rule[1], "occurrences": rule[2]}
                        for rule in RULES[relative]],
            "unapproved_byte_changes": 0,
            "line_endings_preserved": True,
        })
    return {"status": "prepared only; no game files written", "package": str(package),
            "files": files, "source_locations_changed": 8,
            "startup_titles": 1, "direct_error_message_formats": 5,
            "saves_or_storage_invoked": False, "projectID_preserved": True}


def _within(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _preview_destination(value, package):
    destination = Path(value).resolve()
    debug_root = (ROOT / "work/debug").resolve()
    original_base = DEFAULT_PACKAGE.parent.resolve()
    if not _within(destination, debug_root):
        raise ValueError("Preview output must be a separate directory under work/debug")
    if (destination == debug_root or _within(destination, original_base)
            or destination == package or _within(destination, package)
            or _within(package, destination)):
        raise ValueError("Preview output cannot overlap the source package or original base")
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--preview", type=Path,
                        help="Write only the three prepared files into a separate work/debug directory")
    args = parser.parse_args(argv)
    package = args.package.resolve()
    prepared = patches(package)
    report = describe(package, prepared)
    if args.preview is not None:
        destination = _preview_destination(args.preview, package)
        # Verify every destination before the first write. Existing foreign files
        # are not overwritten; this CLI never updates a game package in place.
        outputs = {destination / path.relative_to(package): data for path, data in prepared.items()}
        for path, data in outputs.items():
            if path.exists() and path.read_bytes() != data:
                raise ValueError(f"Preview output already contains different bytes: {path}")
        for path, data in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        report["status"] = "preview only; source package unchanged"
        report["preview"] = str(destination)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
