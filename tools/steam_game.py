"""Read the supported Steam build and prepare an isolated NW.js test copy."""

import argparse
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import shutil
import tempfile
from zipfile import ZipFile
from hashlib import sha256


ROOT = Path(__file__).resolve().parents[1]
BUILD = "10331351"
APP_ID = "2283710"
VERSION = "0.8.2"
INSTALL_MARKER = "kiwame-english-install.json"


def archive_paths(game):
    """Keep extraction tied to the original archives after an in-place install."""
    marker = game / INSTALL_MARKER
    if not marker.is_file():
        return game / 'kiwame.exe', game / 'kiwame.tpatch'
    deployment = json.loads(marker.read_text(encoding='utf-8'))
    backup = Path(deployment['backup']).resolve(strict=True)
    try:
        if not any(backup.is_relative_to(root) for root in [(ROOT / 'work/source').resolve(), (game / '.retro-trans-backup').resolve()]):
            raise ValueError('Unrecognized original-backup directory')
    except ValueError:
        raise ValueError('The Steam original-file backup is outside this project.')
    paths = [backup / name for name in ('kiwame.exe','kiwame.tpatch')]
    for path in paths:
        with path.open('rb') as stream:
            checksum = sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                checksum.update(chunk)
            if checksum.hexdigest() != deployment['originals'][path.name]:
                raise ValueError(f'Original Steam archive backup changed: {path.name}')
    return tuple(paths)


def find_game(override):
    if override:
        game = Path(override).resolve(strict=True)
    else:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            steam = Path(winreg.QueryValueEx(key, "SteamPath")[0])
        libraries = [steam]
        vdf = steam / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            for path in re.findall(r'"path"\s+"([^"\n]+)"', vdf.read_text(encoding="utf-8")):
                libraries.append(Path(path.replace("\\\\", "\\")))
        game = next((p / "steamapps" / "common" / "Apathy_kiwame" for p in libraries
                     if (p / "steamapps" / f"appmanifest_{APP_ID}.acf").is_file()), None)
        if game is None:
            raise ValueError("Steam installation not found. Supply --game with the game folder.")
    manifest = game.parent.parent / f"appmanifest_{APP_ID}.acf"
    if not manifest.is_file() or not re.search(rf'"buildid"\s+"{BUILD}"', manifest.read_text(encoding="utf-8")):
        raise ValueError(f"Expected Steam build {BUILD} in the installation manifest.")
    for name in ("kiwame.exe", "kiwame.tpatch"):
        if not (game / name).is_file():
            raise ValueError(f"Missing {name} in {game}.")
    return game


def merged_members(base, update):
    members = {}
    for archive in (base, update):
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = info.filename
            path = PurePosixPath(name)
            windows_path = PureWindowsPath(name)
            if (path.is_absolute() or windows_path.drive or "\\" in name or
                    any(part in ("", ".", "..") for part in name.split("/"))):
                raise ValueError(f"Unexpected archive member {name!r}")
            members[name.casefold()] = (archive, info)
    return members


def prepare(game, destination, english, debug, dry_run):
    destination = destination.resolve()
    if destination.exists():
        raise ValueError(f"Choose a new test folder. This path already exists: {destination}")
    if destination == game or game in destination.parents:
        raise ValueError("Choose a test folder outside the Steam installation.")
    original_exe, original_patch = archive_paths(game)
    with ZipFile(original_exe) as base, ZipFile(original_patch) as update:
        members = merged_members(base, update)
        print(f"Steam build {BUILD}: {len(members)} merged files -> {destination}")
        for name in ("package.json", "data/scenario/op.ks", "data/system/config.tjs"):
            archive, info = members[name]
            print(f"  {info.filename} ({archive.filename.name if isinstance(archive.filename, Path) else Path(archive.filename).name})")
        if dry_run:
            return
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="kiwame-", dir=destination.parent) as staging:
            copy = Path(staging) / "test"
            package = copy / "package.nw"
            package.mkdir(parents=True)
            for archive, info in members.values():
                target = package / info.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
            offset = min(info.header_offset for info in base.infolist())
            with original_exe.open("rb") as source, (copy / "kiwame.exe").open("wb") as output:
                for remaining in range(0, offset, 1024 * 1024):
                    output.write(source.read(min(1024 * 1024, offset - remaining)))
            for name in ("d3dcompiler_47.dll", "ffmpegsumo.dll", "icudtl.dat", "libEGL.dll", "libGLESv2.dll", "nw.pak"):
                shutil.copy2(game / name, copy / name)
            shutil.copytree(game / "locales", copy / "locales")
            config = package / "data" / "system" / "Config.tjs"
            data = config.read_bytes()
            data, count = re.subn(rb"(?m)^;patch_apply_auto=true(?=\r?$)", b";patch_apply_auto=false", data)
            if count != 1:
                raise ValueError("Could not disable the already merged publisher update.")
            if english:
                # UI source guards use the already-merged baseline configuration.
                config.write_bytes(data)
                from engine_text import patches
                for path, raw in patches(package).items():
                    path.write_bytes(raw)
                data = config.read_bytes()
                from scenario import apply_translations
                from ui import install

                for original, english_value in ((b"vertical=true", b"vertical=false"),
                                                (b"defaultPitch=2", b"defaultPitch=0"),
                                                (b"defaultLineSpacing=22", b"defaultLineSpacing=11")):
                    data, count = re.subn(rb"(?m)^;" + original + rb"(?=\r?$)", b";" + english_value, data)
                    if count != 1:
                        raise ValueError(f"Unexpected English layout setting: {original.decode()}")
                apply_translations(package, ROOT / "work" / "translation" / "en")
                install(package)
                inject(package, "english-ui.js", copy_script=False)
                inject(package, "english.js")
                if (package / 'audio-captions.js').is_file():
                    inject(package, 'audio-captions.js', copy_script=False)
                if (package / 'inoti-grid.js').is_file():
                    inject(package, 'inoti-grid.js', copy_script=False)
                if (package / 'life-summary.js').is_file():
                    inject(package, 'life-summary.js', copy_script=False)
                if (package / 'title-credit.js').is_file():
                    inject(package, 'title-credit.js', copy_script=False)
                add_to_head(package, '<link href="./english.css" rel="stylesheet">')
            config.write_bytes(data)
            if debug:
                manifest = package / "package.json"
                metadata = json.loads(manifest.read_text(encoding="utf-8"))
                metadata["name"] = "kiwame-translation-debug"
                metadata["window"]["title"] = f"Apathy Kiwame {VERSION} QA"
                manifest.write_text(json.dumps(metadata), encoding="utf-8")
                inject(package, "debug-runtime.js")
            copy.rename(destination)


def inject(package, script, copy_script=True):
    if copy_script:
        shutil.copyfile(ROOT / "tools" / script, package / script)
    add_to_head(package, f'<script src="./{script}"></script>')


def add_to_head(package, html):
    entry = package / "index.html"
    markup = entry.read_bytes()
    marker = b"</head>"
    if markup.count(marker) != 1:
        raise ValueError("Expected one head tag in the game entry page.")
    entry.write_bytes(markup.replace(marker, html.encode("ascii") + b"\n" + marker))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "work" / "output" / f"kiwame-{VERSION}")
    parser.add_argument("--english", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        prepare(find_game(args.game), args.output, args.english, args.debug, args.dry_run)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
