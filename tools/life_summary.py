"""Install the user-approved non-graphic Life summary without shifting native orders."""
import argparse,json
from pathlib import Path
from hashlib import sha256
from scenario import render,scan,write_json
ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/'work/translation/en/adaptations/inoti-summary.json'
def spec():return json.loads(SPEC.read_text(encoding='utf-8'))
def repair_background(raw):
    s=spec();lines=raw.splitlines(keepends=True);n=s['background_line']-1
    expected=('[bg storage=hukuzawa/'+'ベッド2.jpg'+' time=0]').encode()
    assert lines[n].rstrip(b'\r\n')==expected,'Unexpected summary background command'
    lines[n]=lines[n].replace(expected,b'[bg storage=kuro.jpg time=0]')
    return b''.join(lines)
def prepare_export(apply=False):
    s=spec();path=ROOT/'work/translation/en/inoti.en.json';d=json.loads(path.read_text(encoding='utf-8'))
    held=json.loads((ROOT/'work/ui/inoti-original-language-exception.json').read_text(encoding='utf-8'))['field_ids']
    raw=(ROOT/'work/debug/kiwame-base/package.nw/data/scenario/inoti.ks').read_bytes()
    _,fields,_=scan(raw);assert len(held)==61
    new={k:[next((p['text']for p in s['pages']if str(p['show'])==k.split(':')[0]),s['placeholder'])]for k in held}
    assert all(len(fields[k][1])==1 for k in held),'Text-tag positions require one original fragment per field'
    for k,v in new.items():assert k not in d['rows'] or d['rows'][k]==v
    d['rows'].update(new);d['adapted_fields']=held;d['adaptation_spec']='adaptations/inoti-summary.json'
    built=render(raw,d);assert len(built.splitlines())==7599
    print(json.dumps({'adapted_source_fields':61,'summary_pages':s['pages'],'placeholders_suppressed':58,'apply':apply},indent=2))
    if apply:
        write_json(path,d)
        working=ROOT/'work/source/inoti.working.json'
        work=json.loads(working.read_text(encoding='utf-8'))
        for k,v in new.items():
            assert k in work['rows']
            work['rows'][k].update(en=v,status='proofread',adaptation='User-approved non-graphic summary; omitted text slots are runtime-suppressed.')
        write_json(working,work)
def install(package,maps):
    s=spec();path=package/'data/scenario/inoti.ks';path.write_bytes(repair_background(path.read_bytes()))
    maps['lifeSummary']=s
    (package/'life-summary.js').write_bytes((ROOT/'tools/life-summary.js').read_bytes())
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');prepare_export(p.parse_args().apply)
