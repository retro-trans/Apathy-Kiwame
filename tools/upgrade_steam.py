"""Upgrade an existing verified Steam patch while preserving its current saves."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import subprocess
from zipfile import ZipFile

from install_steam import digest
from scenario import write_json
from steam_game import ROOT, BUILD, VERSION, INSTALL_MARKER, archive_paths, find_game


def hashes(folder):
    return {p.relative_to(folder).as_posix(): digest(p) for p in folder.rglob('*') if p.is_file()}


def saves(folder):
    return {p.relative_to(folder).as_posix(): digest(p) for p in folder.rglob('*.sav') if p.is_file()}


def require_closed(game):
    paths = subprocess.check_output(['powershell', '-NoProfile', '-Command',
        "Get-Process -Name kiwame -ErrorAction SilentlyContinue | ForEach-Object { $_.Path }; exit 0"], text=True)
    if str(game / 'kiwame.exe').casefold() in paths.casefold():
        raise ValueError('Close the main Steam game before updating it.')


def upgrade(apply=False):
    game = find_game(None).resolve(strict=True)
    marker = game / INSTALL_MARKER
    previous_bytes = marker.read_bytes()
    previous = json.loads(previous_bytes)
    if previous['steam_build'] != BUILD or previous['qa_runtime']:
        raise ValueError('Unsupported installed patch.')
    if previous['version'] == VERSION:
        raise ValueError('This version is already installed.')
    require_closed(game)
    destination = game / 'package.nw'
    if hashes(destination) != previous['package_files']:
        raise ValueError('Installed package differs from its installation record; no files changed.')
    if digest(game / 'kiwame.exe') != previous['runtime_sha256']:
        raise ValueError('Installed runtime changed.')
    if digest(game / 'kiwame.tpatch') != previous['originals']['kiwame.tpatch']:
        raise ValueError('Official patch changed.')
    original, _ = archive_paths(game)
    with ZipFile(original) as archive:
        stock_manifest = archive.read('package.json')
    preview = ROOT / 'work/output' / f'kiwame-{VERSION}'
    package = preview / 'package.nw'
    proof = json.loads((ROOT / f'work/ui/verified_{VERSION}.json').read_text(encoding='utf-8'))
    if proof['version'] != VERSION or proof['clipping'] != 0 or not proof['ready']:
        raise ValueError('Candidate has not passed verification.')
    if hashes(package) != proof['preview_package_files']:
        raise ValueError('Candidate package changed after verification.')
    if digest(preview / 'kiwame.exe') != previous['runtime_sha256']:
        raise ValueError('Candidate runtime differs from the installed runtime.')
    entry = (package / 'index.html').read_bytes()
    debug_tag = b'<script src="./debug-runtime.js"></script>'
    if entry.count(debug_tag) != 1:
        raise ValueError('Unexpected preview entry markup.')
    entry = entry.replace(debug_tag, b'')
    files = {p.relative_to(package).as_posix(): p for p in package.rglob('*')
             if p.is_file() and p.name != 'debug-runtime.js'}
    if any(p.suffix.lower() == '.sav' or 'qa-profile' in p.parts for p in files.values()):
        raise ValueError('QA state in package.')
    saved = saves(game)
    staging = game / f'package.nw.installing-{VERSION}'
    rollback = game / f'package.nw.rollback-{previous["version"]}'
    if staging.exists() or rollback.exists():
        raise ValueError('An earlier staging or rollback folder already exists.')
    backup = ROOT / 'work/source' / ('steam-upgrade-' + VERSION + '-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    print(f'Upgrade Steam {previous["version"]} -> {VERSION}: {len(files)} package files')
    print('Preserve current save files:', ', '.join(saved))
    print('Keep the installed runtime, official patch and original backup unchanged.')
    print('Retain the previous package for rollback:', rollback)
    if not apply:
        return
    if shutil.disk_usage(game).free < sum(p.stat().st_size for p in files.values()) + 100_000_000:
        raise ValueError('Not enough room to stage the update.')
    backup.mkdir(parents=True, exist_ok=False)
    (backup / INSTALL_MARKER).write_bytes(previous_bytes)
    for name in saved:
        target = backup / 'saves' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(game / name, target)
        if digest(target) != saved[name]:
            raise ValueError('Current save backup mismatch: ' + name)
    staging.mkdir()
    expected = {}
    for name, source in files.items():
        target = staging / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if name == 'package.json':
            target.write_bytes(stock_manifest)
        elif name == 'index.html':
            target.write_bytes(entry)
        else:
            shutil.copy2(source, target)
        expected[name] = digest(target)
        if name not in ('package.json', 'index.html') and expected[name] != proof['preview_package_files'][name]:
            raise ValueError('Staged file mismatch: ' + name)
    require_closed(game)
    if saves(game) != saved or hashes(destination) != previous['package_files']:
        raise ValueError('The installed game changed during staging; update stopped.')
    deployment = dict(previous, version=VERSION, save_files=saved, package_files=expected,
                      upgraded=datetime.now().isoformat(), previous_version=previous['version'],
                      upgrade_backup=str(backup), rollback_package=str(rollback))
    destination.rename(rollback)
    try:
        staging.rename(destination)
        if hashes(destination) != expected or saves(game) != saved:
            raise ValueError('Post-install verification failed.')
        temporary = marker.with_suffix('.tmp')
        write_json(temporary, deployment)
        temporary.replace(marker)
    except BaseException:
        if destination.exists():
            destination.rename(staging)
        rollback.rename(destination)
        marker.write_bytes(previous_bytes)
        raise
    write_json(backup / 'upgrade.json', deployment)
    write_json(ROOT / f'work/ui/steam-install-{VERSION}.json', deployment)
    print('Installed and verified', VERSION, '; all current Steam saves unchanged.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    upgrade(parser.parse_args().apply)
