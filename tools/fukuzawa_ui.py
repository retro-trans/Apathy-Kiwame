"""Install Fukuzawa's reviewed choice positions and localized scene lettering."""
import json
from base64 import b64encode
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]


def artwork(asset_root, maps):
    layout = json.loads((ROOT / 'work/ui/fukuzawa-layout.json').read_text(encoding='utf-8'))
    maps.setdefault('choiceLayouts', {})['fukuzawa.ks'] = layout['choices']
    # The original script uses the other spelling of the folder for this one shot.
    clinic = 'hukuzawa/診療室.jpg'
    if not (asset_root / 'bgimage' / clinic).is_file():
        raise ValueError('Original clinic background is missing.')
    maps['backgrounds']['fukuzawa/診療室.jpg'] = clinic
    spec = json.loads((ROOT / 'work/ui/fukuzawa-lettering.json').read_text(encoding='utf-8'))
    background = asset_root / 'bgimage'
    files = {}
    title = spec['title']
    x, y, width, height = title['box']
    markup = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="690">'
        '<rect width="960" height="690" fill="#000"/>'
        f'<rect x="{x+8}" y="{y+8}" width="{width}" height="{height}" rx="20" fill="#fff"/>'
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="20" fill="#000" stroke="#fff" stroke-width="2"/>'
        '<g fill="#fff" text-anchor="middle" font-family="Georgia,serif" font-size="49">'
        f'<text x="{x+width/2}" y="{y+72}">{escape(title["lines"][0])}</text>'
        f'<text x="{x+width/2}" y="{y+138}">{escape(title["lines"][1])}</text></g></svg>\n'
    )
    target = 'kiwame-en/' + title['output']
    files[background / target] = markup.encode('utf-8')
    maps['backgrounds'][title['source']] = target
    for item in spec['images']:
        original = background / item['source']
        encoded = b64encode(original.read_bytes()).decode('ascii')
        definitions, overlays = [], []
        for block in item['blocks']:
            name = block['id']
            x, y, width, height = block['rect']
            fill = block.get('fill', '#ddd')
            covers = ''
            if block.get('sample_gradient'):
                from PIL import Image
                pixels = Image.open(original).convert('RGB')
                points = [(x,y),(x+width,y),(x,y+height),(x+width,y+height)]
                if 'transform' in block:
                    a,b,c,d,tx,ty = block['transform']
                    points = [(round(a*px+c*py+tx),round(b*px+d*py+ty)) for px,py in points]
                corners = [pixels.getpixel((max(0,min(pixels.width-1,px)),max(0,min(pixels.height-1,py)))) for px,py in points]
                colors = ['#%02x%02x%02x' % color for color in corners]
                for suffix, left, right in (('top',colors[0],colors[1]),('bottom',colors[2],colors[3])):
                    definitions.append(f'<linearGradient id="{name}-{suffix}"><stop stop-color="{left}"/><stop offset="1" stop-color="{right}"/></linearGradient>')
                definitions.append(f'<linearGradient id="{name}-fade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="white" stop-opacity="0"/><stop offset="1" stop-color="white"/></linearGradient>')
                definitions.append(f'<mask id="{name}-mask"><rect x="{x}" y="{y}" width="{width}" height="{height}" fill="url(#{name}-fade)"/></mask>')
                fill = f'url(#{name}-top)'
                covers = f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="url(#{name}-bottom)" mask="url(#{name}-mask)"/>'
            covers = f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}"/>' + covers
            feather = block.get('feather', 3)
            if feather:
                definitions.append(f'<filter id="{name}-cover" x="-15%" y="-35%" width="130%" height="170%"><feGaussianBlur stdDeviation="{feather}"/></filter>')
                covers = f'<g filter="url(#{name}-cover)">{covers}</g>'
            blur = block.get('blur', 0)
            filtered = ''
            if blur:
                definitions.append(f'<filter id="{name}-blur" x="-10%" y="-20%" width="120%" height="140%"><feGaussianBlur stdDeviation="{blur}"/></filter>')
                filtered = f' filter="url(#{name}-blur)"'
            transform = ''
            if 'transform' in block:
                transform = ' transform="matrix(' + ' '.join(map(str,block['transform'])) + ')"'
            texts = ''.join(f'<text x="{block["x"]}" y="{block["y"] + index * block["line_height"]}">{escape(line)}</text>' for index,line in enumerate(block['lines']))
            overlays.append(f'<g{transform}>{covers}<g{filtered} fill="{block.get("color","#fff")}" font-family="{block.get("font","Arial,sans-serif")}" font-size="{block["font_size"]}" text-anchor="{block.get("anchor","start")}">{texts}</g></g>')
        preserved = []
        for rect in item.get('preserve_rectangles', []):
            px,py,pw,ph = rect
            preserved.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}"/>')
        for polygon in item.get('preserve_polygons', []):
            preserved.append('<polygon points="' + ' '.join(f'{px},{py}' for px,py in polygon) + '"/>')
        restored = ''
        if preserved:
            definitions.append('<clipPath id="protected">' + ''.join(preserved) + '</clipPath>')
            restored = '<use xlink:href="#original" clip-path="url(#protected)"/>'
        markup = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="960" height="690" viewBox="0 0 960 690">'
                  '<defs>' + ''.join(definitions) + '</defs>'
                  f'<image id="original" width="960" height="690" xlink:href="data:image/{"png" if original.suffix==".png" else "jpeg"};base64,{encoded}"/>'
                  + ''.join(overlays) + restored + '</svg>\n')
        target = 'kiwame-en/' + item['output']
        files[background / target] = markup.encode('utf-8')
        maps['backgrounds'][item['source']] = target
    return files
