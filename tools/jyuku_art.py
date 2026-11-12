"""Return seven SHA-guarded Jyuku lettering assets without writing installation files."""
import argparse
from base64 import b64encode
from hashlib import sha256
import json
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'work/ui/jyuku-lettering.json'


def image_data(path):
    mime = 'image/jpeg' if path.suffix.lower() in ('.jpg', '.jpeg') else 'image/png'
    return 'data:' + mime + ';base64,' + b64encode(path.read_bytes()).decode('ascii')


def attrs(values):
    return ' '.join(f'{key}={quoteattr(str(value))}' for key, value in values.items())


def text_node(item):
    values = dict(item)
    text = values.pop('text')
    return '<text ' + attrs(values) + '>' + escape(text) + '</text>'


def source_image(path, extra=''):
    return f'<image width="960" height="690" xlink:href="{image_data(path)}" {extra}/>'


def clean_patch(original, item, ident):
    """Generated plate enters only precise approved lettering regions, halos included."""
    clean = ROOT / item['clean']
    if sha256(clean.read_bytes()).hexdigest() != item['clean_sha256']:
        raise ValueError(f'Jyuku {ident}: clean plate SHA mismatch')
    shapes = ''.join('<polygon points="' + points + '"/>' for points in item['patch_polygons'])
    # Ink-only extraction was rejected after native screenshots exposed gray
    # anti-alias halos. Whole local patches include those halos. Printed rules
    # inside these small regions come from the inspected clean plate; the rest
    # of every prop, all borders and all outside pixels remain original.
    if ident == 'paper':
        # An inset, feathered edge blends the photographic grain/rules without
        # letting generated pixels escape the approved outer polygons.
        result = ('<defs>' + source_image(clean, 'id="paper-clean-plate"')
                  + '<filter id="paper-feather"><feMorphology operator="erode" radius="2"/><feGaussianBlur stdDeviation="1.3"/></filter></defs>')
        for index, (points, offsets) in enumerate(zip(item['patch_polygons'], item['patch_rgb_offsets'])):
            name = f'paper-{index}'
            polygon = f'<polygon points="{points}"/>'
            transfer = ''.join(f'<feFunc{channel} type="linear" slope="1" intercept="{offset/255:.7f}"/>' for channel, offset in zip('RGB', offsets))
            result += (f'<defs><clipPath id="{name}-region">{polygon}</clipPath>'
                       f'<filter id="{name}-color" color-interpolation-filters="sRGB"><feComponentTransfer>{transfer}</feComponentTransfer></filter>'
                       f'<mask id="{name}-blend" maskUnits="userSpaceOnUse" x="0" y="0" width="960" height="690"><g fill="white" filter="url(#paper-feather)">{polygon}</g></mask></defs>'
                       f'<g clip-path="url(#{name}-region)" mask="url(#{name}-blend)"><use xlink:href="#paper-clean-plate" filter="url(#{name}-color)"/></g>')
        return result
    return (f'<defs><clipPath id="{ident}-region">{shapes}</clipPath></defs>'
            + f'<g clip-path="url(#{ident}-region)">' + source_image(clean) + '</g>')


def render(original, item, ident):
    head = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="960" height="690" viewBox="0 0 960 690">'
    body = '' if ident == 'accusation' else source_image(original)
    if ident in ('title', 'stamp'):
        # Keep original double underline. The red flower is isolated from the
        # white Japanese title without regenerating any of its contour pixels.
        body = '<rect width="960" height="690" fill="black"/>'
        if ident == 'stamp':
            body += ('<defs><filter id="red-only" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 1000 -1000 0 0 0"/></filter></defs>'
                     + source_image(original, 'filter="url(#red-only)"')
                     + '<g fill="black"><rect x="390" y="292" width="48" height="105"/><rect x="438" y="280" width="49" height="124"/><rect x="480" y="274" width="54" height="126"/></g>')
        body += '<path d="M323.5 379.5H615.5M323.5 390.5H615.5" stroke="white" stroke-width="2"/>'
    if 'clean' in item:
        body += clean_patch(original, item, ident)
    body += item.get('erase_svg', '')
    body += item.get('defs', '')
    for group in item['groups']:
        group = dict(group)
        texts = group.pop('texts')
        body += '<g ' + attrs(group) + '>' + ''.join(text_node(text) for text in texts) + '</g>'
    return (head + body + '</svg>\n').encode('utf-8')


def artwork(asset_root, maps):
    """Installer-compatible pure asset builder; asset_root is package.nw/data."""
    asset_root = Path(asset_root)
    spec = json.loads(SPEC.read_text(encoding='utf-8'))
    files, additions = {}, {'backgrounds': {}, 'images': {}}
    assert len(spec['assets']) == 7
    for ident, item in spec['assets'].items():
        original = asset_root / item['source']
        actual = sha256(original.read_bytes()).hexdigest()
        if actual != item['source_sha256']:
            raise ValueError(f'Jyuku {ident}: original SHA mismatch: {actual}')
        category = 'fgimage' if item['map'] == 'images' else 'bgimage'
        target = 'kiwame-en/jyuku-' + ident + '.svg'
        files[asset_root / category / target] = render(original, item, ident)
        additions[item['map']][item['source'].split('/', 1)[1]] = target
    # Do not partially mutate caller maps if a later source guard fails.
    for category, values in additions.items():
        maps.setdefault(category, {}).update(values)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--asset-root', type=Path, default=ROOT / 'work/debug/kiwame-base/package.nw/data')
    parser.add_argument('--preview', type=Path, help='Separate new directory under work/debug; never edits originals')
    args = parser.parse_args()
    maps = {}
    files = artwork(args.asset_root, maps)
    print(json.dumps({'assets': len(files), 'bytes': {path.name: len(data) for path, data in files.items()}, 'maps': maps}, ensure_ascii=False))
    if args.preview:
        target = args.preview.resolve()
        target.relative_to((ROOT / 'work/debug').resolve())
        if not target.name.startswith('jyuku-art-draft'):
            raise ValueError('Preview directory must start jyuku-art-draft')
        target.mkdir(parents=True, exist_ok=False)
        for path, data in files.items():
            (target / path.name).write_bytes(data)
        (target / 'maps.json').write_text(json.dumps(maps, indent=2, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()
