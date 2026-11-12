"""Build a verified binary-only Steam patch; original game data stays local."""
import argparse,copy,json,shutil,struct,subprocess,sys,zlib
from hashlib import sha256,file_digest
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED,ZIP_STORED
from steam_game import ROOT,VERSION,BUILD,archive_paths,find_game,INSTALL_MARKER

def digest(p):
    with Path(p).open('rb')as f:return file_digest(f,'sha256').hexdigest()
def hashes(p):return {f.relative_to(p).as_posix():digest(f)for f in p.rglob('*')if f.is_file()}
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def copy_bytes(source,target,size):
    while size:
        b=source.read(min(size,1024*1024))
        if not b:raise ValueError('Unexpected archive EOF')
        target.write(b);size-=len(b)
def stage(apply):
    old=ROOT/'work/output/kiwame-0.1.24';new=ROOT/f'work/output/kiwame-{VERSION}'
    proof=json.loads((ROOT/'work/ui/verified_0.1.24.json').read_text(encoding='utf-8'))
    assert hashes(old/'package.nw')==proof['preview_package_files']and not new.exists()
    print(json.dumps({'version':VERSION,'source':'verified0.1.24','changes':['title version metadata','preview window title'],'target':str(new),'apply':apply}))
    if not apply:return
    shutil.copytree(old,new,ignore=shutil.ignore_patterns('*.sav','qa-profile'))
    p=new/'package.nw';ui=json.loads((p/'english-ui.js').read_text(encoding='utf-8').removeprefix('window.kiwameEnglishUI = ').strip().rstrip(';'));assert ui['titleCredit']['version']=='0.1.24';ui['titleCredit']['version']=VERSION
    (p/'english-ui.js').write_text('window.kiwameEnglishUI = '+json.dumps(ui)+';\n',encoding='utf-8')
    m=json.loads((p/'package.json').read_text(encoding='utf-8'));m['window']['title']=f'Apathy Kiwame {VERSION} QA';(p/'package.json').write_text(json.dumps(m),encoding='utf-8')
    manifest=hashes(p);diff=[x for x in manifest if manifest[x]!=proof['preview_package_files'][x]];assert set(diff)=={'english-ui.js','package.json'}
    write(ROOT/f'work/ui/release-{VERSION}-staging.json',{'version':VERSION,'previous_proof_sha256':digest(ROOT/'work/ui/verified_0.1.24.json'),'changed_files':diff,'preview_package_files':manifest,'all_other_files_identical':True})
def build(apply):
    preview=ROOT/f'work/output/kiwame-{VERSION}';package=preview/'package.nw';staged=json.loads((ROOT/f'work/ui/release-{VERSION}-staging.json').read_text(encoding='utf-8'));assert hashes(package)==staged['preview_package_files']
    game=find_game(None);original,official=archive_paths(game);scratch=ROOT/f'work/debug/release-{VERSION}-build'
    out=ROOT/'work/output';bundle=scratch/'bundle';patch_name=f'Apathy-Kiwame-English-v{VERSION}.xdelta'
    print(json.dumps({'version':VERSION,'source_files':[original.name,official.name],'source_sizes':[original.stat().st_size,official.stat().st_size],'patch':patch_name,'embedded_target_local_only':True,'apply':apply}))
    if not apply:return
    assert not scratch.exists();scratch.mkdir();bundle.mkdir()
    production={p.relative_to(package).as_posix():p for p in package.rglob('*')if p.is_file()and p.name!='debug-runtime.js'}
    assert not any(p.suffix.lower()=='.sav'or'qa-profile'in p.parts for p in production.values())
    changed={};entry=(package/'index.html').read_bytes();needle=b'<script src="./debug-runtime.js"></script>';assert entry.count(needle)==1;changed['index.html']=entry.replace(needle,b'')
    with ZipFile(original)as base:changed['package.json']=base.read('package.json');offset=min(i.header_offset for i in base.infolist())
    golden={name:sha256(changed[name]).hexdigest()if name in changed else digest(path)for name,path in production.items()}
    target=scratch/'kiwame.exe';source=scratch/'source.bin'
    with source.open('wb')as dest:
        for path in [original,official]:
            with path.open('rb')as f:shutil.copyfileobj(f,dest,1024*1024)
    with original.open('rb')as f,target.open('wb')as dest:copy_bytes(f,dest,offset)
    done=set();counts={'base_raw':0,'official_raw':0,'fresh':0}
    # Preserve source compressed records verbatim and in source order. This prevents
    # unrelated copyrighted media from turning into literal patch payloads.
    with ZipFile(target,'a',allowZip64=True)as output:
        for label,path in [('base_raw',original),('official_raw',official)]:
            with ZipFile(path)as archive,path.open('rb')as raw:
                items=sorted(archive.infolist(),key=lambda i:i.header_offset)
                for n,item in enumerate(items):
                    name=item.filename
                    if name in done or name not in production or name in changed or item.is_dir():continue
                    expected=production[name]
                    if item.file_size!=expected.stat().st_size:continue
                    crc=0
                    with expected.open('rb')as f:
                        for chunk in iter(lambda:f.read(1024*1024),b''):crc=zlib.crc32(chunk,crc)
                    if crc!=item.CRC:continue
                    end=items[n+1].header_offset if n+1<len(items)else archive.start_dir
                    info=copy.copy(item);info.header_offset=output.fp.tell();raw.seek(item.header_offset);copy_bytes(raw,output.fp,end-item.header_offset)
                    output.filelist.append(info);output.NameToInfo[info.filename]=info;output.start_dir=output.fp.tell();output._didModify=True;done.add(name);counts[label]+=1
        for name,path in production.items():
            if name in done:continue
            info=ZipInfo(name,date_time=(2026,11,12,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16
            output.writestr(info,changed.get(name,path.read_bytes()),compresslevel=6);counts['fresh']+=1
    with ZipFile(target)as z:
        assert len(z.infolist())==len(set(z.namelist()))==len(golden)
        assert set(z.namelist())==set(golden)
        for name,expected in golden.items():
            with z.open(name)as f:assert file_digest(f,'sha256').hexdigest()==expected,name
        assert b'debug-runtime.js'not in z.read('index.html')
    exe=ROOT/'work/source/xdelta/xdelta3-3.2.0-windows-x86_64/xdelta3.exe';decoder=exe.with_name('xdelta3decode.exe')
    patch=bundle/patch_name
    subprocess.run([str(exe),'-e','-A','-S','none','-s',str(source),str(target),str(patch)],check=True)
    recovered=scratch/'decoded.exe';subprocess.run([str(decoder),'-d','-s',str(source),str(patch),str(recovered)],check=True);assert digest(recovered)==digest(target)
    shutil.copy2(decoder,bundle/'xdelta3decode.exe')
    for name in ['Patch-Apathy-Kiwame.ps1','Apply.cmd','Undo.cmd']:
        shutil.copy2(ROOT/'tools/distribution'/name,bundle/name)
    licenses=bundle/'licenses';licenses.mkdir()
    for name in ['LICENSE.txt','NOTICE.txt']:shutil.copy2(ROOT/'tools/fonts/genei-latin'/name,licenses/('GenEi-'+name))
    shutil.copy2(ROOT/'tools/distribution/xdelta-LICENSE.txt',licenses/'xdelta-LICENSE.txt')
    shutil.copy2(ROOT/'LICENSE',bundle/'LICENSE')
    manifest={'version':VERSION,'steam_build':BUILD,'app_id':'2283710','source_files':{'kiwame.exe':{'sha256':digest(original),'size':original.stat().st_size},'kiwame.tpatch':{'sha256':digest(official),'size':official.stat().st_size}},'source_order':['kiwame.exe','kiwame.tpatch'],'source_sha256':digest(source),'target_sha256':digest(target),'target_size':target.stat().st_size,'patch_file':patch_name,'patch_sha256':digest(patch),'decoder_sha256':digest(decoder),'layout':'embedded','package_files':len(golden)}
    write(bundle/'manifest.json',manifest)
    shutil.copy2(ROOT/'docs/README-v0.8.0.txt',bundle/'README.txt')
    archive=out/f'Apathy-Kiwame-English-v{VERSION}.zip';assert not archive.exists()
    with ZipFile(archive,'w',compression=ZIP_STORED)as z:
        for f in sorted(bundle.rglob('*')):
            if f.is_file():z.write(f,f.relative_to(bundle).as_posix())
    shutil.copy2(ROOT/'docs/README-v0.8.0.txt',out/f'README-v{VERSION}.txt')
    (out/'SHA256SUMS.txt').write_text(f'{digest(archive)}  {archive.name}\n{digest(out/f"README-v{VERSION}.txt")}  README-v{VERSION}.txt\n',encoding='ascii')
    write(ROOT/f'work/ui/release-{VERSION}-patch-build.json',{'version':VERSION,'completed':True,'source_originals':manifest['source_files'],'source_concatenation_sha256':manifest['source_sha256'],'target_sha256':manifest['target_sha256'],'raw_record_counts':counts,'package_files':len(golden),'production_package_files':golden,'exact_decode_roundtrip':True,'release_zip':archive.name,'release_zip_sha256':digest(archive),'release_zip_size':archive.stat().st_size,'patch_bytes':patch.stat().st_size,'bundle_entries':[p.relative_to(bundle).as_posix()for p in bundle.rglob('*')if p.is_file()],'target_contains_no_QA_runtime':True})
    print(json.dumps({'completed':True,'raw_records':counts,'patch_bytes':patch.stat().st_size,'release_zip_bytes':archive.stat().st_size}),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['stage','build']);p.add_argument('--apply',action='store_true');a=p.parse_args();(stage if a.action=='stage'else build)(a.apply)
