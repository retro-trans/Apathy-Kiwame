"""Account for every extracted field, without reproducing original scenario prose."""
import argparse,json,re
from hashlib import sha256
from zipfile import ZipFile
from scenario import scan,render,translations
from steam_game import ROOT,find_game,archive_paths,merged_members

def audit():
    exports=translations(ROOT/'work/translation/en')
    exception=json.loads((ROOT/'work/ui/inoti-original-language-exception.json').read_text(encoding='utf-8'))
    held=set(exception['field_ids']);assert len(held)==61
    adapted=exception.get('mode')=='non_graphic_summary'
    summary=json.loads((ROOT/exception['adaptation_spec']).read_text(encoding='utf-8')) if adapted else None
    jp=re.compile(r'[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9f]')
    report={'scope':'Extracted display fields only; excludes image lettering, media speech and runtime-generated display values.',
        'files':[],'english_fields':0,'retained_fields':0 if adapted else 61,'adapted_fields':61 if adapted else 0,'nonlinguistic_layout_fields':0,
        'unknown_missing':[],'Japanese_in_English_rows':[],'source_hash_errors':[],'fragment_errors':[],
        'extra_keys':[],'render_validation_errors':[]}
    original,update=archive_paths(find_game(None));seen=set()
    with ZipFile(original) as base,ZipFile(update) as patch:
        for archive,info in merged_members(base,patch).values():
            name=info.filename
            if not name.startswith('data/scenario/') or not name.endswith('.ks'):continue
            raw=archive.read(info);masked=raw
            retained=held if name=='data/scenario/inoti.ks' else set()
            if retained:
                # Mask before decoding/scanning; keep physical line positions.
                masked=b''.join(b'\n' if 3356<=n<=3438 else line for n,line in enumerate(raw.splitlines(keepends=True),1))
            lines,fields,_=scan(masked);data=exports.get(name);rows=data['rows'] if data else {}
            seen.add(name)
            if data and sha256(raw).hexdigest()!=data['source_sha256']:report['source_hash_errors'].append(name)
            missing=[];layout=[]
            for key,(number,spans) in fields.items():
                if key in rows:
                    if len(spans)!=len(rows[key]):report['fragment_errors'].append([name,key])
                    if any(jp.search(value) for value in rows[key]):report['Japanese_in_English_rows'].append([name,key])
                    continue
                visible=''.join(lines[number-1][a:b] for a,b in spans)
                if name=='data/scenario/ED.ks' and not re.sub(r'<[^>]*>','',visible).strip():layout.append(key)
                else:missing.append(key);report['unknown_missing'].append([name,key])
            report['extra_keys'].extend([name,key] for key in set(rows)-set(fields)-(retained if adapted else set()))
            if data:
                try:
                    built=render(raw,data)
                    if len(built.splitlines())!=len(raw.splitlines()):raise ValueError('Physical lines changed')
                    for key in retained:
                        if adapted:
                            expected=next((p['text']for p in summary['pages']if str(p['show'])==key.split(':')[0]),summary['placeholder'])
                            assert rows[key]==[expected]
                        else:
                            assert key not in rows
                            n=int(key.split(':')[0])-1
                            assert built.splitlines(keepends=True)[n]==raw.splitlines(keepends=True)[n]
                except (AssertionError,ValueError) as error:report['render_validation_errors'].append({'scenario':name,'error':str(error)})
            report['english_fields']+=len(rows)-(len(retained)if adapted else 0);report['nonlinguistic_layout_fields']+=len(layout)
            report['files'].append({'scenario':name,'original_sha256':sha256(raw).hexdigest(),
                'fields':len(fields)+len(retained),'english':len(rows)-(len(retained)if adapted else 0),'retained':0 if adapted else len(retained),'adapted':len(retained)if adapted else 0,
                'layout_only':layout,'missing':missing,'export_sha256':sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest() if data else None})
    report['extra_scenarios']=sorted(set(exports)-seen)
    report['inventoried_fields']=sum(x['fields'] for x in report['files'])
    report['accounted_fields']=report['english_fields']+report['retained_fields']+report['adapted_fields']+report['nonlinguistic_layout_fields']
    report['all_extracted_fields_accounted']=not any(report[k] for k in ['unknown_missing','Japanese_in_English_rows','source_hash_errors','fragment_errors','extra_keys','render_validation_errors','extra_scenarios']) and report['accounted_fields']==report['inventoried_fields']
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    report=audit()
    print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
    if args.write:(ROOT/'work/ui/english-field-coverage.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if not report['all_extracted_fields_accounted']:raise SystemExit(1)
if __name__=='__main__':main()
