"""Letter the two Revenge Site images over clipped clean plates."""
import argparse,json
from pathlib import Path
from xml.sax.saxutils import escape
from inoti_art import patched_image,start
ROOT=Path(__file__).resolve().parents[1]

def artwork(background):
    spec=json.loads((ROOT/'work/ui/site-lettering.json').read_text(encoding='utf-8'))
    files={}
    for name in ['title','pc']:
        item=spec[name];body=patched_image(background/item['source'],item,'site'+name)
        if name=='title':
            style='fill="#c6c3bf" stroke="#12100f" stroke-width="1.3" paint-order="stroke"'
        else:
            body+='<defs><filter id="display-glow" x="-10%" y="-20%" width="120%" height="140%"><feGaussianBlur stdDeviation="0.35"/></filter></defs>'
            style='fill="white" filter="url(#display-glow)"'
        body+=f'<text id="english-{name}" x="{item["x"]}" y="{item["baseline"]}" font-family="Georgia,serif" font-size="{item["font_px"]}" text-anchor="middle" {style}>{escape(item["text"])}</text>'
        files[f'site-{name}.svg']=(start(960,690)+body+'</svg>\n').encode('utf-8')
    return files

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--preview',type=Path);args=parser.parse_args()
    files=artwork(ROOT/'work/debug/kiwame-base/package.nw/data/bgimage')
    print('Two English Revenge Site overlays; only clipped lettering patches change.')
    for name,raw in files.items():print(name,len(raw),'bytes')
    if args.preview:
        target=args.preview.resolve();target.relative_to((ROOT/'work/debug').resolve());target.mkdir(parents=True,exist_ok=False)
        for name,raw in files.items():(target/name).write_bytes(raw)

if __name__=='__main__':main()
