"""Build precise English puzzle lettering over preserved original game art."""
import argparse
from base64 import b64encode
from hashlib import sha256
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
LAYOUT=ROOT/'work/ui/inoti-puzzles.json'


def repair_grid(script):
    """Seven exact English-build repairs, confirmed in the original native engine."""
    lines=script.splitlines(keepends=True)
    if len(lines)!=7599:raise ValueError('Unexpected Life physical line count.')
    replacements={5294:(b'hukuzawa/CG/'+ '問題3.jpg'.encode(),b'hukuzawa/CG/'+'問題3.png'.encode()),
                  6110:('target=*シーン100'.encode(),'target=*シーン5100'.encode())}
    for number in range(1,6):
        replacements[5390+number]=(f'exp="ボタン{number}=false"'.encode(),f'exp="sf.ボタン{number}=false"'.encode())
    for number,(before,after) in replacements.items():
        if lines[number-1].count(before)!=1:raise ValueError(f'Unexpected grid command at{number}.')
        lines[number-1]=lines[number-1].replace(before,after)
    result=b''.join(lines)
    changed=[index+1 for index,(a,b) in enumerate(zip(script.splitlines(),result.splitlines())) if a!=b]
    if changed!=sorted(replacements):raise ValueError('Unexpected controller changes.')
    return result


def encoded(path):
    return b64encode(path.read_bytes()).decode('ascii')


def puzzle_artwork(background,number):
    layout=json.loads(LAYOUT.read_text(encoding='utf-8'))
    item=layout[f'puzzle{number}']
    source=background/'hukuzawa/CG'/item['source_image']
    clean=ROOT/item['clean_plate']
    x,y,width,height=item['patch_rect']
    feather=item['patch_feather_pixels']
    shade=item['patch_shade_alpha']
    font=encoded(ROOT/'tools/fonts/genei-latin/GenEiLateGoP_v2.ttf')
    elements=[
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="960" height="690" viewBox="0 0 960 690">',
        '<defs><style>@font-face{font-family:KiwameLatin;src:url(data:font/ttf;base64,'+font+');}</style>',
        f'<clipPath id="lettering"><rect x="{x}" y="{y}" width="{width}" height="{height}"/></clipPath>',
        '<linearGradient id="fade-x"><stop offset="0" stop-color="white" stop-opacity="0"/>'
        f'<stop offset="{feather["horizontal"]/width}" stop-color="white"/><stop offset="{1-feather["horizontal"]/width}" stop-color="white"/>'
        '<stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>',
        '<linearGradient id="paper-shade" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="black" stop-opacity="{shade[0]}"/>'
        f'<stop offset="1" stop-color="black" stop-opacity="{shade[1]}"/></linearGradient>',
        '<linearGradient id="fade-y" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="white" stop-opacity="0"/>'
        f'<stop offset="{feather["vertical"]/height}" stop-color="white"/><stop offset="{1-feather["vertical"]/height}" stop-color="white"/>'
        '<stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>',
        f'<mask id="mask-x" maskUnits="userSpaceOnUse" x="0" y="0" width="960" height="690"><rect x="{x}" y="{y}" width="{width}" height="{height}" fill="url(#fade-x)"/></mask>',
        f'<mask id="mask-y" maskUnits="userSpaceOnUse" x="0" y="0" width="960" height="690"><rect x="{x}" y="{y}" width="{width}" height="{height}" fill="url(#fade-y)"/></mask></defs>',
        f'<image width="960" height="690" xlink:href="data:image/png;base64,{encoded(source)}"/>',
        f'<g mask="url(#mask-x)"><g clip-path="url(#lettering)" mask="url(#mask-y)">'
        f'<image width="960" height="690" xlink:href="data:image/png;base64,{encoded(clean)}"/>'
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="url(#paper-shade)"/></g></g>',
        '<g fill="#151815" font-family="KiwameLatin,sans-serif">',
    ]
    for block in item['text_blocks']:
        for index,text in enumerate(block['lines']):
            baseline=block['top']+block['font_size']+index*block['line_height']
            elements.append(f'<text id="{block["id"]}-{index}" x="{block["x"]}" y="{baseline}" font-size="{block["font_size"]}" text-anchor="{block["anchor"]}">{escape(text)}</text>')
    elements.extend(['</g></svg>',''])
    return '\n'.join(elements).encode('utf-8')


def grid_hint_artwork(background):
    """Reposition only the read-only diagram; live text remains native game text."""
    layout=json.loads(LAYOUT.read_text(encoding='utf-8'))['puzzle3']['recommended_readonly_clue_card']
    left,top,width,height=layout['diagram_destination_rect_game']
    crop=' '.join(map(str,layout['diagram_source_crop_native']))
    from inoti_art import patched_image
    spec=json.loads((ROOT/'work/ui/inoti-lettering.json').read_text(encoding='utf-8'))['grid_backing']
    blank=patched_image(background/spec['source'],spec,'grid')
    diagram=encoded(background/'hukuzawa/CG/問題3.png')
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="960" height="690" viewBox="0 0 960 690">'+blank+
        f'<svg x="{left}" y="{top}" width="{width}" height="{height}" viewBox="{crop}" preserveAspectRatio="xMidYMid meet">'
        f'<image width="1920" height="1380" xlink:href="data:image/png;base64,{diagram}"/>'
        '</svg></svg>\n').encode('utf-8')


def artwork(asset_root,maps,scenario_bytes=None):
    layout=json.loads((ROOT/'work/ui/inoti-layout.json').read_text(encoding='utf-8'))
    maps.setdefault('choiceLayouts',{})['inoti.ks']=layout['choices']
    maps['inotiGridLifecycle']=True
    audio=json.loads((ROOT/'work/translation/en/audio/inoti.en.json').read_text(encoding='utf-8'))
    for item in audio['cues']:
        assert sha256((asset_root/'sound'/item['storage']).read_bytes()).hexdigest()==item['audio_sha256']
    maps.setdefault('audioCaptions',{})['inoti.ks']={str(item['line']):{key:item[key] for key in ['storage','start','end','text']} for item in audio['cues']}
    background=asset_root/'bgimage'
    files={}
    for number in (1,2):
        target=f'kiwame-en/inoti-puzzle-{number}.svg'
        files[background/target]=puzzle_artwork(background,number)
        maps['backgrounds'][f'hukuzawa/CG/問題{number}.png']=target
    target='kiwame-en/inoti-grid-hint.svg'
    files[background/target]=grid_hint_artwork(background)
    maps['backgrounds']['hukuzawa/CG/問題3.png']=target
    from inoti_art import extras
    files.update(extras(asset_root))
    maps['backgrounds'].update({'title/title_イノチA.png':'kiwame-en/inoti-title-white.svg',
        'title/title_イノチB.png':'kiwame-en/inoti-title-red.svg',
        'hukuzawa/CG/イノチ.png':'kiwame-en/inoti-pendant-name.svg'})
    maps['images'].update({'edlist/inoti.jpg':'kiwame-en/inoti-ending-hover.svg',
        'chara/hukuzawa/美和子プラカード.png':'kiwame-en/inoti-wrong-answer.svg'})
    scenario=asset_root/'scenario/inoti.ks'
    files[scenario]=repair_grid(scenario.read_bytes() if scenario_bytes is None else scenario_bytes)
    files[asset_root.parent/'inoti-grid.js']=(ROOT/'tools/inoti-grid.js').read_bytes()
    files[asset_root.parent/'audio-captions.js']=(ROOT/'tools/audio-captions.js').read_bytes()
    return files


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview',type=Path)
    args=parser.parse_args()
    background=ROOT/'work/debug/kiwame-base/package.nw/data/bgimage'
    drafts={f'inoti-puzzle-{number}.svg':puzzle_artwork(background,number) for number in (1,2)}
    drafts['inoti-grid-hint.svg']=grid_hint_artwork(background)
    from inoti_art import extras
    for path,raw in extras(background.parent).items():drafts[path.name]=raw
    original=(ROOT/'work/debug/kiwame-base/package.nw/data/scenario/inoti.ks').read_bytes()
    repaired=repair_grid(original)
    print('Two cipher cards and a read-only grid diagram; original interactive grid unchanged.')
    for name,raw in drafts.items():print(name,len(raw),'bytes')
    print('Controller preview changes only5294,5391–5395,6110;7599lines preserved. Not installed by this command.')
    if args.preview:
        target=args.preview.resolve()
        target.relative_to((ROOT/'work/debug').resolve())
        target.mkdir(parents=True,exist_ok=False)
        for name,raw in drafts.items():(target/name).write_bytes(raw)
        (target/'inoti-grid-repaired.ks').write_bytes(repaired)


if __name__=='__main__':main()
