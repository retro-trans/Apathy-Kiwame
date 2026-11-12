"""Finalize audited release assets and preview-save preservation; default is a dry run."""
import argparse,json,shutil,subprocess
from hashlib import sha256,file_digest
from pathlib import Path
from zipfile import ZipFile,ZIP_STORED
from steam_game import ROOT,VERSION
def h(p):
    with p.open('rb')as f:return file_digest(f,'sha256').hexdigest()
def files(p):return {x.relative_to(p).as_posix():h(x)for x in p.rglob('*')if x.is_file()}
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');a=p.parse_args()
    scratch=ROOT/f'work/debug/release-{VERSION}-build';bundle=scratch/'bundle';preview=ROOT/f'work/output/kiwame-{VERSION}';old=ROOT/'work/output/kiwame-0.1.24';backup=ROOT/f'work/source/preview-preservation-{VERSION}'
    checks=read(f'work/ui/release-{VERSION}-installer-checks.json');assert checks['corrupt_payload_rejected_before_mutation']and checks['undo_restores_original_hash']and checks['fixture_saves_unchanged']
    assert h(ROOT/'tools/distribution/Patch-Apathy-Kiwame.ps1')==checks['installer_sha256']
    native=read(f'work/ui/release-{VERSION}-embedded-startup-a.json');assert native['completed']and native['titleCredit']['lines'][0]=='v'+VERSION
    build=read(f'work/ui/release-{VERSION}-patch-build.json');assert build['exact_decode_roundtrip']and build['target_contains_no_QA_runtime']
    stage=read(f'work/ui/release-{VERSION}-staging.json');assert files(preview/'package.nw')==stage['preview_package_files']
    prior=read('work/ui/verified_0.1.24.json');assert files(old/'package.nw')==prior['preview_package_files']
    saved={x.relative_to(old).as_posix():h(x)for x in old.rglob('*.sav')if x.is_file()};assert saved and not list(preview.rglob('*.sav'))and not backup.exists()
    patch=f'Apathy-Kiwame-English-v{VERSION}.xdelta';m=read(f'work/debug/release-{VERSION}-build/bundle/manifest.json');assert h(bundle/patch)==m['patch_sha256']and h(bundle/'xdelta3decode.exe')==m['decoder_sha256']
    expected={'Apply.cmd','Undo.cmd','Patch-Apathy-Kiwame.ps1','README.txt','LICENSE','manifest.json','xdelta3decode.exe',patch,'licenses/GenEi-LICENSE.txt','licenses/GenEi-NOTICE.txt','licenses/xdelta-LICENSE.txt'}
    print(json.dumps({'version':VERSION,'expected_bundle_entries':sorted(expected),'preview_saves_to_preserve':saved,'apply':a.apply},indent=2))
    if not a.apply:return
    paths=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-Process -Name kiwame -ErrorAction SilentlyContinue | ForEach-Object {$_.Path}; exit 0"],text=True);assert not paths.strip(),'Close games before final save snapshot'
    for name in ['Apply.cmd','Undo.cmd','Patch-Apathy-Kiwame.ps1']:shutil.copy2(ROOT/'tools/distribution'/name,bundle/name)
    shutil.copy2(ROOT/'LICENSE',bundle/'LICENSE');shutil.copy2(ROOT/f'docs/README-v{VERSION}.txt',bundle/'README.txt')
    assert set(files(bundle))==expected
    archive=ROOT/f'work/output/Apathy-Kiwame-English-v{VERSION}.zip';temporary=scratch/'final-package.zip';initial=scratch/'initial-package.zip';assert not temporary.exists()and not initial.exists()
    with ZipFile(temporary,'w',compression=ZIP_STORED)as z:
        for f in sorted(bundle.rglob('*')):
            if f.is_file():z.write(f,f.relative_to(bundle).as_posix())
    with ZipFile(temporary)as z:
        assert set(z.namelist())==expected and z.testzip()is None
        for name in z.namelist():assert sha256(z.read(name)).hexdigest()==h(bundle/name)
    assert archive.resolve().parent==ROOT/'work/output'and initial.resolve().parent==scratch
    archive.rename(initial);temporary.rename(archive)
    readme=ROOT/f'work/output/README-v{VERSION}.txt';shutil.copy2(ROOT/f'docs/README-v{VERSION}.txt',readme)
    (ROOT/'work/output/SHA256SUMS.txt').write_text(f'{h(archive)}  {archive.name}\n{h(readme)}  {readme.name}\n',encoding='ascii')
    shutil.copy2(bundle/'manifest.json',ROOT/f'docs/release-v{VERSION}.json')
    backup.mkdir()
    for name,value in saved.items():
        dest=backup/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/name,dest);assert h(dest)==value
        dest=preview/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(backup/name,dest);assert h(dest)==value
    assert {x.relative_to(preview).as_posix():h(x)for x in preview.rglob('*.sav')if x.is_file()}==saved
    assets={p.name:{'sha256':h(p),'bytes':p.stat().st_size}for p in [archive,readme,ROOT/'work/output/SHA256SUMS.txt']}
    write(ROOT/f'work/ui/release-{VERSION}-final-assets.json',{'version':VERSION,'ready':True,'files':assets,'bundle_entries':sorted(expected),'installer_sha256':h(bundle/'Patch-Apathy-Kiwame.ps1'),'patch_sha256':m['patch_sha256'],'no_game_archives_or_saves':True})
    write(ROOT/f'work/ui/verified_{VERSION}.json',{'version':VERSION,'ready':True,'clipping':0,'preview_package_files':stage['preview_package_files'],'preview_save_files':saved,'preview_save_backup':str(backup),'QA_saves_excluded':True,'public_release_requested':True,'release_assets':assets,'public_target_sha256':m['target_sha256'],'native_installer_output':f'work/ui/release-{VERSION}-embedded-startup-a.json','installer_checks':f'work/ui/release-{VERSION}-installer-checks.json','decode_roundtrip':f'work/ui/release-{VERSION}-patch-build.json','previous_verified_build':'work/ui/verified_0.1.24.json','scope':'All content matches verified0.1.24; only title version and preview window metadata change. Public embedded output verified natively, with font/audio/summary/title modules and no QA runtime.'})
    print(json.dumps({'ready':True,'assets':assets},indent=2),flush=True)
if __name__=='__main__':main()
