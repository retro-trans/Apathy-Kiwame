"""Build a content update from issued 0.8.1 and reviewed staged assets.

Every command is a read-only plan unless --apply is supplied. Original game
files, issued releases, user saves and the main Steam installation are read-only.
"""
import argparse
import copy
from hashlib import file_digest,sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED,ZIP_STORED

from steam_game import ROOT,archive_paths,find_game
from release_patch import copy_bytes,digest

VERSION='0.8.2'
SCRATCH=ROOT/'work/debug/retro-trans-release-0.8.2'
STAGE=ROOT/'work/debug/ending-list-header-0.8.2-staged'
BASE=ROOT/'work/debug/retro-trans-release-0.8.1/kiwame.exe'
TOOLS=ROOT/'work/debug/retro-trans-tools-combined'


def write(path,value):
    with path.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(value,indent=2)+'\n')


def replacements():
    plan=json.loads((STAGE/'install-plan.json').read_text(encoding='utf-8'))
    changed={}
    for name,item in plan['files'].items():
        path=STAGE/name
        if digest(path)!=item['sha256']:raise ValueError('Staged file changed: '+name)
        changed[name]=path.read_bytes()
    if digest(BASE)!='55f523091dc62de6d73cdc1fb9d2dcb3b675a4ab47acf4a6688d08dcab693f95':
        raise ValueError('Issued 0.8.1 executable changed.')
    ui=json.loads(changed['english-ui.js'].decode('utf-8').removeprefix('window.kiwameEnglishUI = ').strip().rstrip(';'))
    ui['titleCredit']['version']=VERSION
    from self_help_movie import artwork
    game=find_game(None)
    movie=artwork(game/'package.nw/data',ui)
    for path,raw in movie.items():changed[path.relative_to(game/'package.nw').as_posix()]=raw
    changed['english-ui.js']=('window.kiwameEnglishUI = '+json.dumps(ui)+';\n').encode('utf-8')
    return changed


def content(apply):
    changed=replacements()
    print(json.dumps({'version':VERSION,'apply':apply,'base':'issued 0.8.1','changed':{n:sha256(v).hexdigest()for n,v in changed.items()},'mainSteamChanged':False}),flush=True)
    if not apply:return
    SCRATCH.mkdir(exist_ok=False)
    target=SCRATCH/'kiwame.exe'
    with ZipFile(BASE) as original:
        infos=sorted(original.infolist(),key=lambda i:i.header_offset)
        with BASE.open('rb') as raw,target.open('xb') as output:
            copy_bytes(raw,output,infos[0].header_offset)
        with ZipFile(target,'a',allowZip64=True) as output,BASE.open('rb') as raw:
            for index,item in enumerate(infos):
                if item.filename in changed:continue
                end=infos[index+1].header_offset if index+1<len(infos) else original.start_dir
                info=copy.copy(item);info.header_offset=output.fp.tell()
                raw.seek(item.header_offset);copy_bytes(raw,output.fp,end-item.header_offset)
                output.filelist.append(info);output.NameToInfo[info.filename]=info
                output.start_dir=output.fp.tell();output._didModify=True
            for name,payload in changed.items():
                info=ZipInfo(name,date_time=(2026,11,14,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16
                output.writestr(info,payload,compresslevel=6)
        with ZipFile(target) as result:
            assert len(result.infolist())==len(set(result.namelist()))
            assert set(result.namelist())==set(original.namelist())|set(changed)
            golden={}
            for name in result.namelist():
                raw=result.read(name)
                assert raw==(changed[name] if name in changed else original.read(name)),name
                assert not name.endswith('.sav') and 'qa-profile' not in name and 'debug-runtime' not in name
                golden[name]=sha256(raw).hexdigest()
            assert b'debug-runtime' not in result.read('index.html')
            assert result.read('package.json')==original.read('package.json')
        proof={'version':VERSION,'targetSha256':digest(target),'targetBytes':target.stat().st_size,'packageFiles':golden,'changedFiles':{n:sha256(v).hexdigest()for n,v in changed.items()},'allOtherFilesIdentical':True,'noQaOrSaves':True,'mainSteamChanged':False}
        write(SCRATCH/'content-verification.json',proof)
        print(json.dumps({'targetSha256':proof['targetSha256'],'packageFiles':len(golden)}),flush=True)


def assets(apply):
    proof=json.loads((SCRATCH/'content-verification.json').read_text(encoding='utf-8'))
    assert digest(SCRATCH/'kiwame.exe')==proof['targetSha256']
    original,official=archive_paths(find_game(None))
    issued=json.loads((ROOT/'docs/release-v0.8.0.json').read_text(encoding='utf-8'))
    for path in [original,official]:assert digest(path)==issued['source_files'][path.name]['sha256']
    target=str(SCRATCH/'kiwame.exe')
    common={'edition':'Steam build 10331351','language':'en','target_format':'exe','target':target}
    patches=[dict(common,patch='Apathy-Kiwame-Steam-original-to-0.8.2.xdelta',source_version='original',source_format='bin',source_files=[{'name':p.name,'source':str(p)}for p in [original,official]])]
    for version,path in [('0.8.0',ROOT/'work/debug/release-0.8.0-build/kiwame.exe'),('0.8.1',BASE)]:
        if version=='0.8.0':assert digest(path)==issued['target_sha256']
        patches.append(dict(common,patch=f'Apathy-Kiwame-Steam-{version}-to-0.8.2.xdelta',source_version=version,source_format='exe',source=str(path)))
    config={'game_id':'apathy-kiwame','game_name':'Apathy - Gakkou de Atta Kowai Hanashi - Kiwame','platform':'PC','version':VERSION,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'package_ids':[{'platform':'PC','kind':'steam-app-id','id':'2283710'}],'patches':patches}
    print(json.dumps({'apply':apply,'patches':[p['patch']for p in patches],'sourceCommit':config['source_commit']}),flush=True)
    if not apply:return
    config_path=SCRATCH/'release-local.json';write(config_path,config)
    sys.path.insert(0,str(TOOLS))
    from retro_trans.release import build_release,validate_directory
    from retro_trans.game_library import read,validate_registration
    library=read(TOOLS/'retro_trans/resources/game-library.json')
    manifest=build_release(config_path,SCRATCH/'assets',cache=SCRATCH/'cache',library=library)
    validate_directory(SCRATCH/'assets');validate_registration(manifest,'retro-trans/Apathy-Kiwame',library)
    print(json.dumps({'patchBytes':{p['patch']:p['patch_bytes']for p in manifest['patches']},'allRoundtripsVerified':True}),flush=True)


def standalone(apply):
    assets=SCRATCH/'assets'
    manifest=json.loads((assets/'BUILD-MANIFEST.json').read_text(encoding='utf-8'))
    full=next(p for p in manifest['patches'] if p['source_version']=='original')
    print(json.dumps({'apply':apply,'standalone':'Apathy-Kiwame-English-v0.8.2-Standalone.zip','usesVerifiedFullDelta':True}),flush=True)
    if not apply:return
    bundle=SCRATCH/'standalone-bundle';bundle.mkdir(exist_ok=False)
    old=ROOT/'work/debug/standalone-0.8.1-final/bundle'
    for name in ['Apply.cmd','Undo.cmd','Patch-Apathy-Kiwame.ps1','xdelta3decode.exe','LICENSE']:
        shutil.copyfile(old/name,bundle/name)
    shutil.copytree(old/'licenses',bundle/'licenses')
    shutil.copyfile(ROOT/'docs/README-standalone-v0.8.2.txt',bundle/'README.txt')
    shutil.copyfile(assets/full['patch'],bundle/full['patch'])
    previous=json.loads((old/'manifest.json').read_text(encoding='utf-8'))
    previous.update(version=VERSION,target_sha256=full['target_sha256'],target_size=full['target_bytes'],patch_file=full['patch'],patch_sha256=full['patch_sha256'],package_files=len(json.loads((SCRATCH/'content-verification.json').read_text())['packageFiles']))
    write(bundle/'manifest.json',previous)
    sums=''.join(f'{digest(p)}  {p.relative_to(bundle).as_posix()}\n'for p in sorted(bundle.rglob('*'))if p.is_file())
    (bundle/'BUNDLE-SHA256SUMS.txt').write_text(sums,encoding='utf-8')
    archive=assets/'Apathy-Kiwame-English-v0.8.2-Standalone.zip'
    with ZipFile(archive,'x',compression=ZIP_STORED) as output:
        for path in sorted(bundle.rglob('*')):
            if path.is_file():output.write(path,path.relative_to(bundle).as_posix())
    (assets/'Standalone-SHA256SUMS-v0.8.2.txt').write_text(f'{digest(archive)}  {archive.name}\n',encoding='ascii')
    notices=assets/'Apathy-Kiwame-v0.8.2-Notices.zip'
    with ZipFile(notices,'x',compression=ZIP_DEFLATED) as output:
        for path in sorted((bundle/'licenses').iterdir()):output.write(path,'licenses/'+path.name)
        output.write(ROOT/'LICENSE','LICENSE')
        output.write(ROOT/'docs/RELEASE-v0.8.2.md','README.txt')
    sums=assets/'SHA256SUMS.txt'
    with sums.open('a',encoding='utf-8') as output:output.write(f'{digest(notices)}  {notices.name}\n')
    sys.path.insert(0,str(TOOLS))
    from retro_trans.release import validate_directory
    validate_directory(assets)
    with ZipFile(archive) as packaged:
        assert packaged.testzip() is None
        for name in packaged.namelist():assert sha256(packaged.read(name)).hexdigest()==digest(bundle/name)
    print(json.dumps({'zipBytes':archive.stat().st_size,'zipSha256':digest(archive),'bundleEntries':len(list(bundle.rglob('*')))}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['content','assets','standalone'])
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args();globals()[args.action](args.apply)


if __name__=='__main__':main()
