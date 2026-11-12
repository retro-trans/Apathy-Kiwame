"""Build Kazama's annotated ritual boards and their English answer captions."""

import json
from base64 import b64encode
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]


def artwork(asset_root, maps):
    sources = ROOT / 'work' / 'ui'
    board = json.loads((sources / 'kazama-board.json').read_text(encoding='utf-8'))
    layout = json.loads((sources / 'kazama-layout.json').read_text(encoding='utf-8'))
    background = asset_root / 'bgimage'
    originals = background / 'kazama'
    files = {}
    for index, frame in enumerate(board['frames']):
        source = frame['source']
        image = b64encode((originals / source).read_bytes()).decode('ascii')
        labels = []
        for column in board['kana_columns_right_to_left']:
            for roman, y in zip(column['labels'], column['centers_y'], strict=True):
                if roman is None or (frame.get('burned') and roman in board['variants']['burned']['missing']):
                    continue
                labels.append(f'<text x="{column["x"]}" y="{y + 43}">{escape(roman)}</text>')
        labels.extend(('<text x="265" y="193">YES</text>', '<text x="697" y="193">NO</text>'))
        coin = frame.get('coin')
        clip = ''
        foreground = ''
        if coin:
            ellipse = f'cx="{coin["x"]}" cy="{coin["y"]}" rx="{coin["rx"]}" ry="{coin["ry"]}"'
            clip = f'<clipPath id="coin"><ellipse {ellipse}/></clipPath>'
            foreground = '<use xlink:href="#scene" clip-path="url(#coin)"/>'
        markup = (
            '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            'width="960" height="690" viewBox="0 0 960 690">'
            '<defs><image id="scene" width="960" height="690" '
            f'xlink:href="data:image/{"png" if source.endswith(".png") else "jpeg"};base64,{image}"/>'
            f'{clip}</defs><use xlink:href="#scene"/>'
            '<g fill="#243635" stroke="#e3e1d9" stroke-width="1.7" paint-order="stroke" '
            'text-anchor="middle" font-family="Segoe Print, Georgia, serif" '
            'font-size="17" font-weight="bold">'
            + ''.join(labels) + f'</g>{foreground}</svg>\n'
        )
        target = f'kiwame-en/kazama-board-{index:02}.svg'
        files[background / target] = markup.encode('utf-8')
        maps['backgrounds'][f'kazama/{source}'] = target
    maps.setdefault('choiceLayouts', {})['kazama.ks'] = layout['choices']
    maps['boardCaptions'] = layout['captions']
    return files
