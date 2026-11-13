"""Package the image-generated notebook edit at its original in-game canvas size."""
import argparse
from base64 import b64encode
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from PIL import Image
from steam_game import ROOT


def artwork(asset_root, maps):
    spec = json.loads((ROOT / 'work/ui/rpg-notebook-cover.json').read_text(encoding='utf-8'))
    if sha256((Path(asset_root) / spec['original']).read_bytes()).hexdigest() != spec['original_sha256']:
        raise ValueError('Unexpected original notebook image.')
    raw = (ROOT / spec['image']).read_bytes()
    if sha256(raw).hexdigest() != spec['image_sha256']:
        raise ValueError('Unexpected image-generated notebook edit.')
    with Image.open(BytesIO(raw)) as image:
        if list(image.size) != spec['generated_size']:
            raise ValueError('Unexpected notebook edit dimensions.')
    # Native placement only: keep all generated PNG bytes intact. No vector
    # reconstruction, artificial rotation, raster resizing or retouching.
    encoded = b64encode(raw).decode('ascii')
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           'width="960" height="690" viewBox="0 0 960 690" role="img" '
           'aria-label="Old School Building Field Notes, Sadao Hino">'
           '<image width="960" height="690" preserveAspectRatio="xMidYMid meet" '
           'xlink:href="data:image/png;base64,' + encoded + '"/></svg>\n').encode('utf-8')
    maps.setdefault('images', {})['rpg/note_top.png'] = spec['target']
    return {Path(asset_root) / 'fgimage' / spec['target']: svg}


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
