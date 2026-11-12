"""Install the verified English preview into Steam, retaining original archives and saves."""
import argparse
from datetime import datetime
from hashlib import file_digest,sha256
import json
from pathlib import Path
import shutil
from zipfile import ZipFile

from steam_game import ROOT,BUILD,VERSION,INSTALL_MARKER,find_game
from scenario import write_json


def digest(path):
    with path.open('rb') as stream:return file_digest(stream,'sha256').hexdigest()


def saves(folder):
    return {p.name:digest(p) for p in folder.glob('*.sav')}


def install(apply=False):
    game=find_game(None).resolve(strict=True)
    tested=ROOT/'work/output'/f'kiwame-{VERSION}'
    proof=json.loads((ROOT/f'work/ui/verified_{VERSION}.json').read_text(encoding='utf-8'))
    if proof['version']!=VERSION or proof['soft_breaks']!=3593 or proof['clipping']:
        raise ValueError('The tested build did not pass verification.')
    package=tested/'package.nw'
    destination=game/'package.nw'
    staging=game/f'package.nw.installing-{VERSION}'
    marker=game/INSTALL_MARKER
    if any(p.exists() for p in (destination,staging,marker)):
        raise ValueError('This installer expects the original Steam layout; an installation already exists.')
    original=game/'kiwame.exe'
    with ZipFile(original) as archive:
        offset=min(item.header_offset for item in archive.infolist())
        stock_manifest=archive.read('package.json')
    stub=tested/'kiwame.exe'
    with original.open('rb') as stream:
        prefix=stream.read(offset)
    if stub.stat().st_size!=offset or sha256(prefix).hexdigest()!=digest(stub):
        raise ValueError('The verified runtime does not match the installed Steam executable.')
    entry=(package/'index.html').read_bytes()
    debug_tag=b'<script src="./debug-runtime.js"></script>'
    if entry.count(debug_tag)!=1:raise ValueError('Unexpected QA entry-page markup.')
    entry=entry.replace(debug_tag,b'')
    files={p.relative_to(package).as_posix():p for p in package.rglob('*') if p.is_file() and p.name!='debug-runtime.js'}
    if any(p.suffix.lower()=='.sav' or 'qa-profile' in p.parts for p in files.values()):raise ValueError('QA state in package.')
    saved=saves(game)
    print('Steam installation:',game)
    print('Version:',VERSION,'| package files:',len(files),'| original runtime prefix verified')
    print('Preserve Steam saves:',list(saved),'| retain official kiwame.tpatch unchanged')
    print('Normal manifest and entry page; exclude the QA runtime and test saves.')
    backup=ROOT/'work/source'/('steam-original-'+BUILD+'-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    print('Original-file backup:',backup)
    if not apply:return
    import subprocess
    processes=subprocess.check_output(['powershell','-NoProfile','-Command',
        "Get-Process -Name kiwame -ErrorAction SilentlyContinue | ForEach-Object { $_.Path }; exit 0"],text=True)
    if str(original).casefold() in processes.casefold():raise ValueError('Close the Steam game before installation.')
    required=sum(p.stat().st_size for p in files.values())+stub.stat().st_size
    if shutil.disk_usage(game).free<required+100_000_000:raise ValueError('Not enough room to stage the Steam package.')
    backup.mkdir(parents=True,exist_ok=False)
    originals={}
    for name in ('kiwame.exe','kiwame.tpatch',*saved):
        shutil.copy2(game/name,backup/name)
        originals[name]=digest(backup/name)
        if originals[name]!=digest(game/name):raise ValueError('Backup mismatch: '+name)
    write_json(backup/'backup.json',{'game':str(game),'build':BUILD,'originals':originals,'save_files':saved})
    staging.mkdir()
    expected={}
    for name,source in files.items():
        target=staging/name;target.parent.mkdir(parents=True,exist_ok=True)
        if name=='package.json':target.write_bytes(stock_manifest)
        elif name=='index.html':target.write_bytes(entry)
        else:shutil.copy2(source,target)
        value=digest(target)
        if name not in ('package.json','index.html') and value!=digest(source):raise ValueError('Staging mismatch: '+name)
        expected[name]=value
    if saves(game)!=saved:raise ValueError('Steam saves changed during staging; installation stopped.')
    staging.rename(destination)
    try:
        shutil.copy2(stub,original)
        if digest(original)!=digest(stub):raise ValueError('Runtime installation mismatch.')
        if saves(game)!=saved:raise ValueError('Steam saves changed during installation.')
        deployment={'version':VERSION,'steam_build':BUILD,'game':str(game),'backup':str(backup),
                    'originals':originals,'save_files':saved,'runtime_sha256':digest(stub),
                    'package_files':expected,'qa_runtime':False,'installed':datetime.now().isoformat()}
        write_json(marker,deployment)
        write_json(ROOT/f'work/ui/steam-install-{VERSION}.json',deployment)
    except BaseException:
        shutil.copy2(backup/'kiwame.exe',original)
        destination.rename(staging)
        raise
    print('Installed and verified',VERSION,'in the Steam game; all Steam saves unchanged.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    install(args.apply)
