"""Integrate the reviewed Revenge Site lettering and planned native menu geometry."""
import json
from pathlib import Path
from site_art import artwork as lettered_images
ROOT=Path(__file__).resolve().parents[1]
def artwork(asset_root,maps):
    layout=json.loads((ROOT/'work/ui/site-layout.json').read_text(encoding='utf-8'))
    assert len(layout['choices'])==16
    maps.setdefault('choiceLayouts',{})['site.ks']=layout['choices']
    files={}
    for name,data in lettered_images(asset_root/'bgimage').items():
        files[asset_root/'bgimage/kiwame-en'/name]=data
    maps['backgrounds'].update({'title/title_hukusyusite.jpg':'kiwame-en/site-title.svg',
        'site/PC画面.jpg':'kiwame-en/site-pc.svg'})
    return files
