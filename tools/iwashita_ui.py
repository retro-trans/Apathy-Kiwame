"""Install reviewed horizontal choice positions for Iwashita's route."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def artwork(asset_root, maps):
    layout = json.loads((ROOT / 'work/ui/iwashita-layout.json').read_text(encoding='utf-8'))
    maps.setdefault('choiceLayouts', {})['iwashita.ks'] = layout['choices']
    return {}
