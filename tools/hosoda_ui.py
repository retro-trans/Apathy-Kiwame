"""Prepare Hosoda's photographed letters without changing the original JPEGs.

Default: inspect English lettering and bounds. --preview writes isolated SVG drafts.
The drafts are deliberately not installed until all exposed lettering is reviewed.
"""
import argparse
from base64 import b64encode
import json
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'work/ui/hosoda-lettering.json'


def title_artwork(background):
    # This first card has the original blank envelope graphic. Adding English
    # to it preserves that graphic while avoiding any Japanese title lettering.
    source = background / 'title/軍人の遺書1.png'
    encoded = b64encode(source.read_bytes()).decode('ascii')
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="960" height="690">'
            f'<image width="960" height="690" xlink:href="data:image/png;base64,{encoded}"/>'
            '<text x="480" y="240" text-anchor="middle" fill="white" font-family="Georgia,serif" font-size="43">A Soldier\'s</text>'
            '<g fill="black" text-anchor="middle" font-family="Georgia,serif" font-size="21">'
            '<text x="487" y="370">Last</text><text x="487" y="402">Letter</text></g></svg>\n').encode('utf-8')


def artwork(asset_root, maps):
    layout = json.loads((ROOT / 'work/ui/hosoda-layout.json').read_text(encoding='utf-8'))
    maps.setdefault('choiceLayouts', {})['hosoda.ks'] = layout['choices']
    spec = json.loads(SPEC.read_text(encoding='utf-8'))
    background = asset_root / 'bgimage'
    files = {}
    for item in spec['images']:
        target = 'kiwame-en/' + item['output']
        files[background / target] = render(background / item['source'], item)
        maps['backgrounds'][item['source']] = target
    target = 'kiwame-en/hosoda-soldier-title.svg'
    files[background / target] = title_artwork(background)
    maps['backgrounds']['title/軍人の遺書2.png'] = target
    # Stock BG_IMG has a leading slash and omits title/ for the first card.
    maps['backgrounds']['/軍人の遺書1.png'] = 'title/軍人の遺書1.png'
    return files


def render(original, item):
    """Return an SVG overlay; all uncovered photograph pixels remain original."""
    with Image.open(original) as picture:
        pixels = picture.convert('RGB')
        if pixels.size != (960, 690):
            raise ValueError('Expected the original 960x690 photograph.')
        definitions, layers = [], []
        if item.get('clean_plate'):
            clean = ROOT / 'work/ui' / item['clean_plate']
            clean_data = b64encode(clean.read_bytes()).decode('ascii')
            definitions.append(f'<image id="clean" width="960" height="690" xlink:href="data:image/png;base64,{clean_data}"/>')
        for name, points in item.get('regions', {}).items():
            polygon = ' '.join(f'{x},{y}' for x,y in points)
            definitions.append(f'<clipPath id="{name}"><polygon points="{polygon}"/></clipPath>')
        for index, patch in enumerate(item['erase']):
            x, y, width, height = patch['rect']
            if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > 960 or y + height > 690:
                raise ValueError('Erase patch is outside the photograph.')
            name = f'patch-{index}'
            if item.get('clean_plate'):
                # Blend only reviewed lettering patches from the clean plate.
                # The photograph outside these patches is the original JPEG.
                definitions.append(f'<filter id="{name}-edge" x="-15%" y="-35%" width="130%" height="170%"><feGaussianBlur stdDeviation="1.5"/></filter>')
                definitions.append(f'<mask id="{name}-clean" maskUnits="userSpaceOnUse" x="0" y="0" width="960" height="690"><rect x="{x}" y="{y}" width="{width}" height="{height}" fill="white" filter="url(#{name}-edge)"/></mask>')
                clip = f' clip-path="url(#{patch["clip"]})"' if patch.get('clip') else ''
                layers.append(f'<g{clip}><use xlink:href="#clean" mask="url(#{name}-clean)"/></g>')
                continue
            # Sample the paper around the patch rather than choosing flat white.
            points = [(x, max(0, y-3)), (x+width-1, max(0, y-3)),
                      (x, min(689, y+height+3)), (x+width-1, min(689, y+height+3))]
            def paper_color(point):
                px, py = point
                samples = [pixels.getpixel((sx, sy))
                           for sx in range(max(0, px-8), min(960, px+9))
                           for sy in range(max(0, py-8), min(690, py+9))]
                # Ink and notebook rules are darker than paper. A light quantile
                # avoids dragging those strokes into a broad replacement patch.
                samples.sort(key=lambda rgb: sum(rgb))
                return samples[int((len(samples)-1) * .8)]
            colors = ['#%02x%02x%02x' % paper_color(point) for point in points]
            name = f'patch-{index}'
            definitions.extend([
                f'<linearGradient id="{name}-top"><stop stop-color="{colors[0]}"/><stop offset="1" stop-color="{colors[1]}"/></linearGradient>',
                f'<linearGradient id="{name}-bottom"><stop stop-color="{colors[2]}"/><stop offset="1" stop-color="{colors[3]}"/></linearGradient>',
                f'<linearGradient id="{name}-fade" x2="0" y2="1"><stop stop-color="white" stop-opacity="0"/><stop offset="1" stop-color="white"/></linearGradient>',
                f'<mask id="{name}-mask"><rect x="{x}" y="{y}" width="{width}" height="{height}" fill="url(#{name}-fade)"/></mask>',
                f'<filter id="{name}-blur" x="-20%" y="-100%" width="140%" height="300%"><feGaussianBlur stdDeviation="{patch.get("feather", 2)}"/></filter>'
            ])
            clip = f' clip-path="url(#{patch["clip"]})"' if patch.get('clip') else ''
            layers.append(f'<g{clip}><g filter="url(#{name}-blur)"><rect x="{x}" y="{y}" width="{width}" height="{height}" fill="url(#{name}-top)"/>'
                          f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="url(#{name}-bottom)" mask="url(#{name}-mask)"/></g></g>')
    for index, block in enumerate(item['text']):
        x, y = block['x'], block['y']
        transform = f' transform="rotate({block["rotate"]} {x} {y})"' if block.get('rotate') else ''
        filtered = ''
        if block.get('blur'):
            definitions.append(f'<filter id="text-{index}"><feGaussianBlur stdDeviation="{block["blur"]}"/></filter>')
            filtered = f' filter="url(#text-{index})"'
        lines = ''.join(f'<text x="{x}" y="{y + i * block.get("line_height", block["size"] * 1.3)}">{escape(line)}</text>'
                        for i, line in enumerate(block['lines']))
        clip = f' clip-path="url(#{block["clip"]})"' if block.get('clip') else ''
        layers.append(f'<g{clip}><g{transform}{filtered} fill="#242825" font-family="Segoe Print,Georgia,serif" '
                      f'font-size="{block["size"]}" text-anchor="{block.get("anchor", "start")}">{lines}</g></g>')
    clip = ''
    if item.get('clip'):
        points = ' '.join(f'{x},{y}' for x,y in item['clip'])
        definitions.append(f'<clipPath id="paper"><polygon points="{points}"/></clipPath>')
        clip = ' clip-path="url(#paper)"'
    original_data = b64encode(original.read_bytes()).decode('ascii')
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            'width="960" height="690" viewBox="0 0 960 690"><defs>' + ''.join(definitions) + '</defs>'
            f'<image width="960" height="690" xlink:href="data:image/jpeg;base64,{original_data}"/>'
            f'<g{clip}>' + ''.join(layers) + '</g></svg>\n').encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', type=Path)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_text(encoding='utf-8'))
    if args.preview:
        destination = args.preview.resolve()
        destination.relative_to((ROOT / 'work/debug').resolve())
        if destination.exists():
            raise ValueError('Choose a new preview folder to retain prior artwork drafts.')
    originals = ROOT / 'work/debug/kiwame-base/package.nw/data/bgimage'
    files = {}
    for item in spec['images']:
        files[item['output']] = render(originals / item['source'], item)
        print(item['id'] + ': ' + ' / '.join(line for block in item['text'] for line in block['lines']))
    files['hosoda-soldier-title.svg'] = title_artwork(originals)
    print("soldier-title: A Soldier's / Last / Letter; original blank envelope card retained")
    print(spec['status'])
    if args.preview:
        destination.mkdir(parents=True)
        for name, data in files.items():
            (destination / name).write_bytes(data)


if __name__ == '__main__':
    main()
