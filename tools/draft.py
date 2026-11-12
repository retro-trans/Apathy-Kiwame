"""Create local machine-translation references for editorial work, separate from the build."""

import argparse
import json
from hashlib import sha256
from pathlib import Path
import re
from zipfile import ZipFile

from scenario import scan, write_json
from steam_game import ROOT, BUILD, find_game, merged_members, archive_paths


def source_scenarios(game, scenario):
    original_exe, original_patch = archive_paths(game)
    with ZipFile(original_exe) as base, ZipFile(original_patch) as patch:
        for archive, member in merged_members(base, patch).values():
            name = member.filename
            if name.startswith("data/scenario/") and name.endswith(".ks"):
                if not scenario or name == f"data/scenario/{scenario}":
                    yield name, archive.read(member)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", type=Path)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--scenario")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.limit and (args.limit < 1 or not args.scenario):
        parser.error("--limit requires a scenario and a positive field count.")
    if not args.model.is_dir():
        parser.error("Supply an extracted local CTranslate2 model folder.")
    import ctranslate2
    import sentencepiece

    model = ctranslate2.Translator(str(args.model), device="cpu", compute_type="int8",
                                 inter_threads=3, intra_threads=2)
    source = sentencepiece.SentencePieceProcessor(model_file=str(args.model / "source.spm"))
    target = sentencepiece.SentencePieceProcessor(model_file=str(args.model / "target.spm"))
    glossary = json.loads((ROOT / "work" / "glossary" / "core.json").read_text(encoding="utf-8"))
    cache = {entry["ja"]: entry["en"] for entry in glossary["characters"] + glossary["terms"]}
    game = find_game(args.game)
    output = ROOT / "work" / "source" / "drafts" / BUILD
    scenarios = 0
    for name, raw in source_scenarios(game, args.scenario):
        scenarios += 1
        dest = output / (name.removeprefix("data/scenario/").replace("/", "__") + ".json")
        if dest.exists() and not args.dry_run and not args.limit:
            print(f"{name}: already drafted", flush=True)
            continue
        lines, fields, _ = scan(raw)
        items = list(fields.items())[:args.limit]
        fragments = {key: [lines[number - 1][start:end].strip() for start, end in spans]
                     for key, (number, spans) in items}
        pending = dict.fromkeys(value for segments in fragments.values() for value in segments if value not in cache)
        unique = list(pending)
        for start in range(0, len(unique), 384):
            texts = unique[start:start + 384]
            tokens = [source.encode(text, out_type=str) + ["</s>"] for text in texts]
            results = model.translate_batch(tokens, max_batch_size=24, beam_size=1, max_decoding_length=200)
            for original, translated in zip(texts, results):
                result = target.decode(translated.hypotheses[0]).strip()
                cache[original] = re.sub(r"[\r\n]+", " ", result)
        draft = {key: [cache[segment] for segment in segments] for key, segments in fragments.items()}
        if args.dry_run or args.limit:
            print(json.dumps(dict(list(draft.items())[:12]), ensure_ascii=True, indent=2))
        else:
            staging = dest.with_suffix(".tmp")
            write_json(staging, {"scenario": name, "source_sha256": sha256(raw).hexdigest(),
                                 "status": "unreviewed_reference", "rows": draft})
            staging.replace(dest)
        print(f"{name}: {len(draft):,} fields drafted", flush=True)
    if not scenarios:
        parser.error("No matching scenarios.")


if __name__ == "__main__":
    main()
