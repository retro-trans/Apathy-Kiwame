"""Package the verified English scrolling-letter movie without rebuilding it."""
from hashlib import sha256
import json
from pathlib import Path
from steam_game import ROOT


def artwork(asset_root, maps):
    spec=json.loads((ROOT/'work/ui/self-help-movie.json').read_text(encoding='utf-8'))
    source=Path(asset_root)/spec['source']
    if sha256(source.read_bytes()).hexdigest()!=spec['source_sha256']:
        raise ValueError('Unexpected original Self-Help movie.')
    payload=(ROOT/spec['rendered']).read_bytes()
    if sha256(payload).hexdigest()!=spec['rendered_sha256']:
        raise ValueError('English Self-Help movie differs from the verified preview.')
    maps.setdefault('movies',{})[spec['map_key']]=spec['target']
    maps.setdefault('captions',{}).pop(spec['map_key'],None)
    return {Path(asset_root)/'video'/spec['target']:payload}
