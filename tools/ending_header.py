"""Translate the base Ending List heading as font outlines over its original image."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from syorei_art import _Font, _SVG, _rect
from steam_game import ROOT


def artwork(asset_root, maps):
    spec = json.loads((ROOT / 'work/ui/ending-list-header.json').read_text(encoding='utf-8'))
    raw = (Path(asset_root) / spec['source']).read_bytes()
    if sha256(raw).hexdigest() != spec['source_sha256']:
        raise ValueError('Unexpected Ending List base background.')
    font = _Font(ROOT / 'tools/fonts/genei-latin/GenEiLateGoP_v2.ttf')
    if font.width(spec['text'], spec['font_size']) > spec['cover_box'][2]:
        raise ValueError('Ending List header exceeds its lettering box.')
    svg = _SVG(raw, '.jpg', font)
    svg.add('<defs><clipPath id="ending-header-only">' + _rect(spec['cover_box'], 'white') + '</clipPath></defs>')
    svg.add('<g clip-path="url(#ending-header-only)">')
    svg.add(_rect(spec['cover_box'], 'black'))
    svg.add(svg.text(spec['text'], spec['x'], spec['baseline'], spec['font_size'], fill='white'))
    svg.add('</g>')
    # BG_IMG uses uppercase ED.jpg; accept the on-disk lowercase spelling too.
    backgrounds = maps.setdefault('backgrounds', {})
    backgrounds['ED.jpg'] = spec['target']
    backgrounds['ed.jpg'] = spec['target']
    return {Path(asset_root) / 'bgimage' / spec['target']: svg.finish()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    maps = {}
    assets = artwork(args.assets, maps)
    print(json.dumps(dict(mapping=maps, output=[str(p) for p in assets], apply=args.apply)))
    if args.apply:
        for path, raw in assets.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)


if __name__ == '__main__':
    main()
