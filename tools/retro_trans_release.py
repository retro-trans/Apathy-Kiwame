"""Prepare a Retro Trans Tools release candidate; dry run unless --apply is given.

Original game files and complete translated binaries stay local. This command
does not install anything, change saves, push commits or publish a release.
"""
import argparse
import copy
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from steam_game import ROOT, archive_paths, find_game
from release_patch import copy_bytes, digest


NAME = 'Apathy - Gakkou de Atta Kowai Hanashi - Kiwame'
IDS = [dict(platform='PC', kind='steam-app-id', id='2283710')]


def embedded_candidate(source, target, version):
    """Keep every unchanged compressed game record; replace only the credit."""
    with ZipFile(source) as original:
        infos = sorted(original.infolist(), key=lambda item: item.header_offset)
        old = original.read('english-ui.js')
        ui = json.loads(old.decode('utf-8').removeprefix('window.kiwameEnglishUI = ').strip().rstrip(';'))
        assert ui['titleCredit']['version'] == '0.8.0'
        ui['titleCredit']['version'] = version
        replacement = ('window.kiwameEnglishUI = ' + json.dumps(ui) + ';\n').encode('utf-8')
        with source.open('rb') as raw, target.open('xb') as output:
            copy_bytes(raw, output, infos[0].header_offset)
        with ZipFile(target, 'a', allowZip64=True) as output, source.open('rb') as raw:
            for index, item in enumerate(infos):
                if item.filename == 'english-ui.js':
                    continue
                end = infos[index + 1].header_offset if index + 1 < len(infos) else original.start_dir
                info = copy.copy(item); info.header_offset = output.fp.tell()
                raw.seek(item.header_offset); copy_bytes(raw, output.fp, end - item.header_offset)
                output.filelist.append(info); output.NameToInfo[info.filename] = info
                output.start_dir = output.fp.tell(); output._didModify = True
            info = ZipInfo('english-ui.js', date_time=(2026, 11, 12, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED; info.external_attr = 0o100644 << 16
            output.writestr(info, replacement, compresslevel=6)
        with ZipFile(target) as result:
            assert set(result.namelist()) == set(original.namelist())
            assert len(result.infolist()) == len(original.infolist()) == 2009
            for name in original.namelist():
                assert result.read(name) == (replacement if name == 'english-ui.js' else original.read(name)), name
            assert b'debug-runtime.js' not in result.read('index.html')
    return dict(changed_files=['english-ui.js'], package_files=2009,
                target_sha256=digest(target), target_bytes=target.stat().st_size)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tools', required=True, type=Path, help='Reviewed Retro Trans Tools checkout with combined-source support.')
    parser.add_argument('--version', default='0.8.1')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+', args.version) or args.version == '0.8.0':
        parser.error('Use a new 0.x.y candidate version.')
    tools = args.tools.resolve(strict=True)
    original, official = archive_paths(find_game(None))
    previous = ROOT / 'work/debug/release-0.8.0-build/kiwame.exe'
    issued = json.loads((ROOT / 'docs/release-v0.8.0.json').read_text(encoding='utf-8'))
    assert digest(previous) == issued['target_sha256']
    for name, path in [('kiwame.exe', original), ('kiwame.tpatch', official)]:
        assert digest(path) == issued['source_files'][name]['sha256']
    scratch = ROOT / ('work/debug/retro-trans-release-' + args.version)
    print(json.dumps(dict(version=args.version, tools=str(tools), directory=str(scratch),
                         operations=['version credit only', 'combined-source full delta', '0.8.0 upgrade delta',
                                     'round-trip verification', 'registered publication metadata'], apply=args.apply)))
    if not args.apply:
        return
    assert not scratch.exists(), 'Use a new candidate directory; never overwrite a prior build.'
    scratch.mkdir()
    target = scratch / 'kiwame.exe'
    proof = embedded_candidate(previous, target, args.version)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    common = dict(edition='Steam build 10331351', language='en', target_format='exe', target=str(target))
    config = dict(game_id='apathy-kiwame', game_name=NAME, platform='PC', version=args.version,
                  source_commit=commit, package_ids=IDS, patches=[
        dict(common, patch='Apathy-Kiwame-Steam-original-to-' + args.version + '.xdelta',
             source_version='original', source_format='bin', source_files=[
                 dict(name='kiwame.exe', source=str(original)), dict(name='kiwame.tpatch', source=str(official))]),
        dict(common, patch='Apathy-Kiwame-Steam-0.8.0-to-' + args.version + '.xdelta',
             source_version='0.8.0', source_format='exe', source=str(previous))])
    config_path = scratch / 'release-local.json'
    config_path.write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    sys.path.insert(0, str(tools))
    from retro_trans.release import build_release, validate_directory
    from retro_trans.game_library import read, validate_registration
    library = read(tools / 'retro_trans/resources/game-library.json')
    manifest = build_release(config_path, scratch / 'assets', cache=scratch / 'cache', library=library)
    validate_directory(scratch / 'assets')
    validate_registration(manifest, 'retro-trans/Apathy-Kiwame', library)
    proof.update(version=args.version, manifest_sha256=digest(scratch / 'assets/BUILD-MANIFEST.json'),
                 full_and_upgrade_roundtrips=True, published=False, installed=False,
                 patch_bytes={p['patch']: p['patch_bytes'] for p in manifest['patches']})
    (scratch / 'verification.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
