"""Build an outlined English RPG game-over card; dry-run unless --apply is set."""
import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from PIL import Image
from syorei_art import _Font, _SVG
from steam_game import ROOT


def artwork(asset_root, maps):
    spec = json.loads((ROOT / 'work/ui/rpg-game-over.json').read_text(encoding='utf-8'))
    asset_root = Path(asset_root)
    for source, checksum in [('animated_source', 'animated_sha256'), ('still_source', 'still_sha256')]:
        if sha256((asset_root / spec[source]).read_bytes()).hexdigest() != spec[checksum]:
            raise ValueError('Unexpected original RPG ending card: ' + spec[source])
    font = _Font(ROOT / 'tools/fonts/genei-latin/GenEiLateGoP_v2.ttf')
    if font.width(spec['text'], spec['font_size']) > spec['maximum_width']:
        raise ValueError('RPG ending line exceeds its safe width.')
    # The optional effect-analysis/native-render tools regenerate this English
    # clip. Normal builds verify and package it without a browser or OpenCV.
    animated = (ROOT / spec['rendered_animation']).read_bytes()
    if sha256(animated).hexdigest() != spec['rendered_animation_sha256']:
        raise ValueError('Unexpected English ending animation.')
    animation = Image.open(BytesIO(animated))
    durations = []
    for index in range(animation.n_frames):
        animation.seek(index)
        durations.append(animation.info['duration'])
    if (animation.size != (640, 460) or len(durations) != 78 or
            any(ms != 50 for ms in durations) or animation.info.get('loop') != 0):
        raise ValueError('Unexpected RPG ending animation timing.')
    outliner = _SVG(b'', '.jpg', font)
    letters = outliner.text(spec['text'], spec['center_x'], spec['baseline'],
                            spec['font_size'], fill='currentColor', anchor='middle')
    head = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            'width="960" height="690" viewBox="0 0 960 690" role="img" '
            'aria-label="And then it was all over...">'
            '<rect width="960" height="690" fill="black"/>'
            '<defs><g id="ending-letters">' + letters + '</g></defs>')
    still = (head + '<g color="white"><use xlink:href="#ending-letters"/></g></svg>\n').encode('utf-8')
    backgrounds = maps.setdefault('backgrounds', {})
    for source in ('rpg/siboued.gif', 'rpg/SIBOUED.gif'):
        backgrounds[source] = spec['target']
    for source in ('rpg/ED1.jpg', 'rpg/ed1.jpg'):
        backgrounds[source] = spec['still_target']
    return {asset_root / 'bgimage' / spec['target']: animated,
            asset_root / 'bgimage' / spec['still_target']: still}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    maps = {}
    output = artwork(args.assets, maps)
    print(json.dumps({'apply': args.apply, 'mapping': maps,
                      'output': {str(p): sha256(raw).hexdigest() for p, raw in output.items()}}))
    if args.apply:
        for path, raw in output.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)


if __name__ == '__main__':
    main()
