"""Build the English credit roll as transparent, outlined Latin text.

Default CLI validates and reports only. --apply writes the one mapped SVG.
The original 690x4000 geometry and native scroll scenario remain unchanged.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from steam_game import ROOT
from syorei_art import _Font, _SVG

SPEC = ROOT / 'work/ui/credits-roll.json'
TEXT = ROOT / 'work/translation/en/credits.en.json'


def artwork(asset_root, maps):
    spec = json.loads(SPEC.read_text(encoding='utf-8'))
    text = json.loads(TEXT.read_text(encoding='utf-8'))
    source = Path(asset_root) / spec['source']
    if sha256(source.read_bytes()).hexdigest() != spec['source_sha256']:
        raise ValueError('Unexpected original credit roll.')
    original = next(i for i in json.loads((ROOT/'work/ui/common-lettering.json').read_text(encoding='utf-8'))['items'] if i['kind']=='staff')
    font = _Font(ROOT/spec['font'])
    outliner = _SVG(b'', '.png', font)
    parts, bounds = [], []
    if len(text['rows']) != len(original['rows']) or len(text['rows']) != 44:
        raise ValueError('Credit row count changed.')
    for row, translated in zip(original['rows'],text['rows']):
        if row['row'] != translated['row'] or row['kind'] != translated['kind']:
            raise ValueError('Credit order or attribution group changed.')
        value = translated['text']
        if not value or not value.isascii():
            raise ValueError('Credits require Latin/ASCII text.')
        size = spec['role_font_size'] if row['kind']=='role' else spec['name_font_size']
        while font.width(value,size)>spec['maximum_width'] and size>spec['minimum_font_size']:
            size -= 1
        if font.width(value,size)>spec['maximum_width']:
            raise ValueError('Credit exceeds the source image width: '+value)
        ymin, ymax = 0, 0
        for character in value:
            if character==' ':continue
            pen=BoundsPen(font.glyphs)
            font.glyphs[font.cmap[ord(character)]].draw(pen)
            if pen.bounds:
                ymin=min(ymin,pen.bounds[1]);ymax=max(ymax,pen.bounds[3])
        top = row['source_ink_bounds_xyxy'][1]
        baseline = top+ymax*size/font.units
        bottom = baseline-ymin*size/font.units
        color = '#ff0000' if row['kind']=='role' else '#ffffff'
        parts.append(outliner.text(value,spec['x'],baseline,size,fill=color))
        bounds.append({'row':row['row'],'kind':row['kind'],'text':value,'font_size':size,
                       'bounds':[spec['x'],top,spec['x']+font.width(value,size),bottom]})
    for previous,following in zip(bounds,bounds[1:]):
        if previous['bounds'][3]+8>following['bounds'][1]:
            raise ValueError('Credit rows overlap.')
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="690" height="4000" viewBox="0 0 690 4000" preserveAspectRatio="none" role="img" aria-label="Game credits">'
           '<title>Game credits</title>'+''.join(parts)+'</svg>\n').encode('utf-8')
    images=maps.setdefault('images',{})
    if images.get(spec['map_key']) not in (None,'kiwame-en/common-staff.png',spec['target']):
        raise ValueError('Unexpected existing credit mapping.')
    images[spec['map_key']]=spec['target']
    return {Path(asset_root)/'fgimage'/spec['target']:svg},bounds


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    maps={};files,bounds=artwork(args.assets,maps)
    print(json.dumps({'apply':args.apply,'mapping':maps,'rows':len(bounds),'geometry':[690,4000],
                      'output':[{ 'path':str(p),'sha256':sha256(raw).hexdigest()}for p,raw in files.items()],
                      'bounds':bounds}))
    if args.apply:
        for path,raw in files.items():
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(raw)


if __name__=='__main__':main()
