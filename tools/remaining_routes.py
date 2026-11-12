"""Exact source repairs confirmed by the isolated native original-loader baseline."""
from pathlib import Path
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
RULES={
 'jyuku.ks':(10766,{
  5628:('sf.新堂334==4 | | sf.新堂334==5','sf.新堂334==4 || sf.新堂334==5'),
  9317:('sindo/yuki/足跡.jpg','sindo/yuki/足跡.png')}),
 'syorei.ks':(6602,{1537:('storage=ノイズ音.ogg','storage=ノイズ.ogg')})}
def repair(name,raw):
    count,rules=RULES[name];lines=raw.splitlines(keepends=True)
    if len(lines)!=count:raise ValueError('Unexpected physical line count: '+name)
    for number,(before,after) in rules.items():
        before,after=before.encode('utf-8'),after.encode('utf-8')
        if lines[number-1].count(before)!=1:raise ValueError(f'Unexpected original command {name}:{number}')
        lines[number-1]=lines[number-1].replace(before,after)
    built=b''.join(lines)
    changed=[n+1 for n,(a,b) in enumerate(zip(raw.splitlines(),built.splitlines())) if a!=b]
    if changed!=sorted(rules):raise ValueError('Unapproved source repair')
    return built
def readable_startup(raw):
    """Let the player read the complete English disclaimer before continuing."""
    lines=raw.splitlines(keepends=True)
    if len(lines)!=823 or lines[10].strip()!=b'[wait time=1500]':
        raise ValueError('Unexpected startup disclaimer wait')
    lines[10]=lines[10].replace(b'[wait time=1500]',b'[l]')
    return b''.join(lines)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--preview',type=Path);a=p.parse_args()
    proof=json.loads((ROOT/'work/ui/remaining-original-defects-a.json').read_text(encoding='utf-8'));assert proof['completed']
    files={}
    for name,(_,rules) in RULES.items():
        raw=(ROOT/'work/debug/kiwame-base/package.nw/data/scenario'/name).read_bytes()
        files[name]=repair(name,raw)
        print(name,'exact command repairs at',','.join(map(str,rules)))
    if a.preview:
        target=a.preview.resolve();target.relative_to((ROOT/'work/debug').resolve());target.mkdir(parents=True,exist_ok=False)
        for name,raw in files.items():(target/name).write_bytes(raw)
if __name__=='__main__':main()
