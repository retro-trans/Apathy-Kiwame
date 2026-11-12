"""Inventory player-facing TyranoScript fields and apply English rows by source digest."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from steam_game import ROOT, BUILD, find_game, merged_members, archive_paths


JAPANESE = re.compile(r"[\u3000-\u30ff\u3400-\u9fff\uff00-\uffef]")
TAG_NAME = re.compile(r"\s*(\w+)")
ATTR = re.compile(r"(?<!\S)(\w+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s]+))")
VISUAL = {"glink": {"text"}, "link": {"text"}, "ptext": {"text"}, "pushlog": {"text"},
          "title": {"name"}, "ED": {"text"}, "button": {"hint"}, "chara_new": {"jname"},
          "ruby": {"text"}, "選択肢": {"text"}}
TAG_FIELD_NAMES = {"選択肢": "rpg_choice"}
SPACE = "\ue001"
ENGLISH_CHOICE = "\ue000"
ENDING_TITLE = re.compile(r'''^\s*"(ED[0-9]{3})"\s*:\s*'\1 (?P<title>[^']+)'\s*,?\s*$''')


def split_tags(line):
    """Yield (start, end, is_tag), matching this engine's bracket depth rules."""
    depth = 0
    start = 0
    for i, char in enumerate(line):
        if char == "[":
            if depth == 0:
                if start < i:
                    yield start, i, False
                start = i
            depth += 1
        elif char == "]" and depth:
            depth -= 1
            if depth == 0:
                yield start, i + 1, True
                start = i + 1
    if depth == 0 and start < len(line):
        yield start, len(line), False


def text_fields(line):
    """Return fields, with literal spans grouped once per original display row."""
    content = line.strip()
    if not content or content.startswith((";", "*")):
        return []
    left = len(line) - len(line.lstrip())
    if content.startswith("#"):
        end = content.find(":")
        name = content[1:end if end >= 0 else len(content)].strip()
        offset = line.index(name, left + 1) if name else 0
        return [("speaker", [(offset, offset + len(name))])] if JAPANESE.search(name) else []
    if content.startswith("_"):
        content = content[1:]
        left += 1
    spans = [(1, len(content), True)] if content.startswith("@") else list(split_tags(content))
    plain = []
    fields = []
    seen = Counter()
    for start, end, is_tag in spans:
        if not is_tag:
            if JAPANESE.search(content[start:end]):
                plain.append((left + start, left + end))
            continue
        tag_start = start + int(not content.startswith("@"))
        tag_end = end - int(not content.startswith("@"))
        token = content[tag_start:tag_end]
        tag = TAG_NAME.match(token)
        if not tag or tag[1] not in VISUAL:
            continue
        for match in ATTR.finditer(token, tag.end()):
            if match[1] not in VISUAL[tag[1]]:
                continue
            key = f"{TAG_FIELD_NAMES.get(tag[1], tag[1])}.{match[1]}"
            seen[key] += 1
            group = next(group for group in (2, 3, 4) if match[group] is not None)
            value = match[group]
            if value.startswith(("&", "%")) or not JAPANESE.search(value):
                continue
            begin, finish = match.span(group)
            field = f"{key}.{seen[key]}"
            fields.append((field, [(left + tag_start + begin, left + tag_start + finish)]))
    return ([('text', plain)] if plain else []) + fields


def scan(raw):
    rows = {}
    audit = Counter()
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    script = False
    comment = False
    ending_table = False
    for number, line in enumerate(lines, 1):
        trimmed = line.strip()
        if trimmed == "/*":
            comment = True
        if trimmed in ("[iscript]", "@iscript") and not comment:
            script = True
        if comment or script:
            if script and not comment:
                if trimmed == "ED = {":
                    ending_table = True
                elif trimmed in ("};", "[endscript]", "@endscript"):
                    ending_table = False
                match = ENDING_TITLE.fullmatch(line) if ending_table else None
                if match and JAPANESE.search(match["title"]):
                    rows[f"{number}:ending_title"] = (number, [match.span("title")])
                    continue
            if JAPANESE.search(line) and not trimmed.startswith(("//", "*", ";")):
                audit["embedded_code_or_comment"] += 1
            if trimmed == "*/":
                comment = False
            if trimmed in ("[endscript]", "@endscript"):
                script = False
            continue
        fields = text_fields(line)
        for name, spans in fields:
            rows[f"{number}:{name}"] = (number, spans)
        if JAPANESE.search(line) and not fields and not trimmed.startswith((";", "*")):
            audit["other_japanese_outside_comments"] += 1
    return lines, rows, audit


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def translations(folder):
    patches = {}
    for path in sorted(folder.glob("*.en.json")):
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        scenario = data["scenario"]
        if not re.fullmatch(r"data/scenario/(?:[a-z0-9_]+/)*[a-z0-9_]+\.ks", scenario, re.I):
            raise ValueError(f"Invalid scenario path in {path.name}: {scenario}")
        if scenario in patches:
            raise ValueError(f"More than one translation file for {scenario}")
        patches[scenario] = data
    return patches


def render(raw, data):
    if sha256(raw).hexdigest() != data["source_sha256"]:
        raise ValueError(f"Source changed: {data['scenario']}")
    lines, rows, _ = scan(raw)
    changes = defaultdict(list)
    for key, segments in data["rows"].items():
        if key not in rows:
            raise ValueError(f"Unknown field {key} in {data['scenario']}")
        number, spans = rows[key]
        if not isinstance(segments, list) or len(segments) != len(spans):
            raise ValueError(f"Wrong number of fragments at {key}")
        field = key.split(":", 1)[1]
        for (start, end), value in zip(spans, segments):
            value = value.replace('\u2026', '...').replace('\u22ef', '...').replace('\u2025', '..') if isinstance(value, str) else value
            if (not isinstance(value, str) or not value.strip() or JAPANESE.search(value) or
                    re.search(r"[\r\n\[\]<>&\ue000\ue001]", value)):
                raise ValueError(f"Invalid translation at {key}")
            if field == "ending_title":
                value = value.replace("\\", "\\\\").replace("'", "\\'")
            elif field not in ("text", "speaker"):
                quote = lines[number - 1][start - 1]
                if quote in value and quote in ('"', "'"):
                    raise ValueError(f"Translation contains the enclosing quote at {key}")
                value = value.replace(" ", SPACE)
                if field.startswith("glink.text."):
                    value = ENGLISH_CHOICE + value
            changes[number - 1].append((start, end, value))
    for index, replacements in changes.items():
        for start, end, value in sorted(replacements, reverse=True):
            lines[index] = lines[index][:start] + value + lines[index][end:]
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    return "".join(lines).encode(encoding)


def apply_translations(package, folder):
    for scenario, data in translations(folder).items():
        target = package / scenario
        target.write_bytes(render(target.read_bytes(), data))
        print(f"  {scenario}: {len(data['rows'])} English fields")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inventory", "export", "verify", "refresh"))
    parser.add_argument("--game", type=Path)
    parser.add_argument("--scenario")
    parser.add_argument("--test-folder", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.command == "export" and not args.scenario:
        parser.error("export requires --scenario, e.g. op.ks")
    game = find_game(args.game)
    if args.command == "refresh":
        if not args.test_folder:
            parser.error("refresh requires --test-folder.")
        package = args.test_folder.resolve(strict=True) / "package.nw"
        if ROOT / "work" not in package.parents or not (package / "debug-runtime.js").is_file():
            parser.error("Choose an isolated QA copy under work.")
    patches = translations(ROOT / "work" / "translation" / "en")
    inventory = {}
    original_exe, original_patch = archive_paths(game)
    with ZipFile(original_exe) as base, ZipFile(original_patch) as update:
        for archive, info in merged_members(base, update).values():
            path = info.filename
            if not path.startswith("data/scenario/") or not path.endswith(".ks"):
                continue
            if args.scenario and path != f"data/scenario/{args.scenario}":
                continue
            raw = archive.read(info)
            lines, rows, audit = scan(raw)
            patch = patches.get(path)
            if patch:
                built = render(raw, patch)
                if args.command == "refresh":
                    print(f"  {path}: {len(patch['rows'])} fields -> {package / path}")
                    if not args.dry_run:
                        target = package / path
                        staging = target.with_suffix(".ks.tmp")
                        staging.write_bytes(built)
                        staging.replace(target)
            inventory[path] = {"source_sha256": sha256(raw).hexdigest(), "fields": len(rows),
                               "english": len(patch["rows"]) if patch else 0, **audit}
            if args.command == "export" and not args.dry_run:
                output = ROOT / "work" / "source" / (args.scenario.replace("/", "__") + ".json")
                if output.exists():
                    parser.error(f"Export already exists: {output}")
                write_json(output, {"scenario": path, "source_sha256": sha256(raw).hexdigest(),
                                    "rows": {key: {"line": lines[number - 1].rstrip("\r\n"),
                                                   "source": [lines[number - 1][start:end] for start, end in spans]}
                                             for key, (number, spans) in rows.items()}})
                print(output)
    if not inventory:
        parser.error("No matching scenario files.")
    if args.command == "verify" and not args.scenario and set(patches) - set(inventory):
        parser.error("One or more translation files do not match a game scenario.")
    if args.command == "inventory" and not args.dry_run:
        write_json(ROOT / "docs" / "scenario_inventory.json", {"steam_build": BUILD, "files": inventory})
    print(f"{len(inventory)} scenarios | {sum(entry['fields'] for entry in inventory.values()):,} extracted fields | "
          f"{sum(entry['english'] for entry in inventory.values()):,} English fields")


if __name__ == "__main__":
    main()
