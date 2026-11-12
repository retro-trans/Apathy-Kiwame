"""Package the issued 0.8.1 full delta with the verified standalone installer.

Dry run by default. The target executable, published delta and canonical Tools
assets are never changed; this only adds an optional ZIP and separate checksum.
"""
import argparse
import json
from pathlib import Path
import shutil
from zipfile import ZipFile, ZIP_STORED

from steam_game import ROOT
from release_patch import digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    version = '0.8.1'
    issued = json.loads((ROOT / 'docs/release-v0.8.1-verification.json').read_text(encoding='utf-8'))
    assets = ROOT / 'work/debug/retro-trans-release-0.8.1/assets-reviewed'
    meta_path = assets / 'BUILD-MANIFEST.json'
    assert digest(meta_path) == issued['public_downloads']['BUILD-MANIFEST.json']['sha256']
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    patch = next(p for p in meta['patches'] if p['source_version'] == 'original')
    payload = assets / patch['patch']
    assert digest(payload) == patch['patch_sha256'] == issued['public_downloads'][payload.name]['sha256']
    assert payload.stat().st_size == patch['patch_bytes']
    # The issued Tools delta uses LZMA, which the old tiny decode-only build lacks.
    # Keep the unmodified full 3.2.0 binary under the launcher's decoder filename.
    decoder = ROOT / 'work/source/xdelta/xdelta3-3.2.0-windows-x86_64/xdelta3.exe'
    assert digest(decoder) == '6e812b38484d0c764291779fadee83ffbe2eceaccb4e3a21f8a043a02654a01e'
    stage = ROOT / ('work/debug/standalone-' + version + '-final')
    archive_name = 'Apathy-Kiwame-English-v' + version + '-Standalone.zip'
    print(json.dumps(dict(version=version, archive=archive_name, target_sha256=patch['target_sha256'],
                          published_delta_unchanged=True, requires_retro_trans_tools=False, apply=args.apply)))
    if not args.apply:
        return
    assert not stage.exists(), 'Use a fresh staging directory; do not overwrite an earlier bundle.'
    bundle = stage / 'bundle'; bundle.mkdir(parents=True)
    licenses = bundle / 'licenses'; licenses.mkdir()
    shutil.copy2(payload, bundle / payload.name)
    shutil.copy2(decoder, bundle / 'xdelta3decode.exe')
    for name in ['Apply.cmd', 'Undo.cmd', 'Patch-Apathy-Kiwame.ps1']:
        shutil.copy2(ROOT / 'tools/distribution' / name, bundle / name)
    for name in ['LICENSE.txt', 'NOTICE.txt']:
        shutil.copy2(ROOT / 'tools/fonts/genei-latin' / name, licenses / ('GenEi-' + name))
    shutil.copy2(ROOT / 'tools/distribution/xdelta-LICENSE.txt', licenses / 'xdelta-LICENSE.txt')
    shutil.copy2(ROOT / 'LICENSE', bundle / 'LICENSE')
    shutil.copy2(ROOT / 'docs/README-standalone-v0.8.1.txt', bundle / 'README.txt')
    files = patch['combined_source']['files']
    manifest = dict(version=version, steam_build='10331351', app_id='2283710',
        source_files={p['name']: dict(sha256=p['sha256'], size=p['bytes']) for p in files},
        source_order=[p['name'] for p in files], source_sha256=patch['source_sha256'],
        target_sha256=patch['target_sha256'], target_size=patch['target_bytes'],
        patch_file=payload.name, patch_sha256=patch['patch_sha256'],
        decoder_sha256=digest(decoder), layout='embedded', package_files=2009)
    (bundle / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    sums = ['{}  {}'.format(digest(p), p.relative_to(bundle).as_posix())
            for p in sorted(bundle.rglob('*')) if p.is_file()]
    (bundle / 'BUNDLE-SHA256SUMS.txt').write_text('\n'.join(sums) + '\n', encoding='ascii')
    archive = stage / archive_name
    with ZipFile(archive, 'w', compression=ZIP_STORED) as output:
        for path in sorted(bundle.rglob('*')):
            if path.is_file():
                assert path.suffix.lower() != '.sav' and 'qa-profile' not in path.parts
                output.write(path, path.relative_to(bundle).as_posix())
    with ZipFile(archive) as check:
        assert check.testzip() is None
        assert 'kiwame.exe' not in check.namelist() and 'kiwame.tpatch' not in check.namelist()
    checksum = stage / ('Standalone-SHA256SUMS-v' + version + '.txt')
    checksum.write_text(digest(archive) + '  ' + archive.name + '\n', encoding='ascii')
    proof = dict(version=version, archive=archive.name, bytes=archive.stat().st_size,
                 sha256=digest(archive), target_sha256=patch['target_sha256'],
                 installer_sha256=digest(bundle / 'Patch-Apathy-Kiwame.ps1'),
                 canonical_assets_unchanged=True, published=False)
    (stage / 'bundle-verification.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
