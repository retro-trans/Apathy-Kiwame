"""Export proofread English rows from a local bilingual working file."""

import argparse
import json
from pathlib import Path
import re
from zipfile import ZipFile

from scenario import render, write_json
from steam_game import ROOT, find_game, merged_members, archive_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("working", type=Path)
    parser.add_argument("--game", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    work = json.loads(args.working.read_text(encoding="utf-8-sig"))
    scenario = work["scenario"]
    if not re.fullmatch(r"data/scenario/(?:[a-z0-9_]+/)*[a-z0-9_]+\.ks", scenario, re.I):
        parser.error("Invalid scenario path.")
    rows = {key: [part.replace('\u2026', '...').replace('\u22ef', '...').replace('\u2025', '..')
                  for part in value["en"]]
            for key, value in work["rows"].items() if value.get("status") == "proofread"}
    if not rows:
        parser.error("No proofread fields to export.")
    clean = {"scenario": scenario, "source_sha256": work["source_sha256"], "rows": rows}
    game = find_game(args.game)
    original_exe, original_patch = archive_paths(game)
    with ZipFile(original_exe) as base, ZipFile(original_patch) as update:
        archive, info = merged_members(base, update)[scenario.casefold()]
        render(archive.read(info), clean)
    name = scenario[len("data/scenario/"):-3].replace("/", "__") + ".en.json"
    target = ROOT / "work" / "translation" / "en" / name
    if target.exists():
        previous = json.loads(target.read_text(encoding="utf-8-sig"))
        if set(previous["rows"]) - set(rows):
            parser.error("The working file is missing previously exported fields.")
    print(f"{len(rows)} English fields -> {target}")
    if not args.dry_run:
        staging = target.with_suffix(".tmp")
        write_json(staging, clean)
        staging.replace(target)


if __name__ == "__main__":
    main()
