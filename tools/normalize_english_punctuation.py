"""Normalize English ellipses; preserve fields, fragments, and script controls."""
import argparse
import json
from pathlib import Path
from scenario import render, write_json
from steam_game import ROOT


def normalize(text):
    return text.replace('\u2026', '...').replace('\u22ef', '...').replace('\u2025', '..')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    total = 0
    for path in sorted((ROOT / 'work/translation/en').glob('*.en.json')):
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        changes = []
        for key, parts in data['rows'].items():
            after = [normalize(text) for text in parts]
            if after != parts:
                changes.append((key, parts, after))
                data['rows'][key] = after
        if not changes:
            continue
        render((ROOT / 'work/debug/kiwame-base/package.nw' / data['scenario']).read_bytes(), data)
        print(path.name, len(changes), 'fields')
        for key, before, after in changes[:2]:
            print(' ', key, ascii(before), '->', ascii(after))
        total += len(changes)
        if args.write:
            write_json(path, data)
    print(total, 'fields', 'written' if args.write else 'planned (dry run)')


if __name__ == '__main__':
    main()
