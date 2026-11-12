# Retro Trans Tools integration — 0.8.1

Game: **Apathy - Gakkou de Atta Kowai Hanashi - Kiwame**.

This release requires **Retro Trans Tools 0.5.23 or later**. Earlier apps cannot
read its schema-3 combined-source manifest. The existing 0.8.0 release remains
unchanged. Download the [compatible Windows app](https://github.com/retro-trans/retro-trans-tools/releases/latest)
before refreshing the catalog.

## Player workflow

1. Close the game and start Retro Trans Tools 0.5.23 or later.
2. In Automatic, use Folder to choose the original Steam game folder, or Browse
   to `kiwame.exe` or `kiwame.tpatch`. Both originals from Steam build 10331351
   must be together under those names. Their exact contents are verified.
3. To upgrade a public 0.8.0 English installation, Browse to its patched
   `kiwame.exe` instead. The app recognizes it and selects the smaller upgrade.
4. Choose Latest and a new output filename, then Patch. The app downloads and
   verifies the compatible delta and writes the verified English executable.
5. Keep a backup of the current `kiwame.exe`. Copy the verified output into
   the game folder as `kiwame.exe`. Leave the DLLs, official `kiwame.tpatch`
   and all save files in place, then launch through Steam normally.

Automatic never overwrites original files, existing outputs or saves. The
original Japanese `kiwame.exe` plus `kiwame.tpatch` are combined only in a
temporary file; users do not need to combine them themselves. That temporary
file is removed on completion, cancellation or failure. Allow 4 GB free space
for the ordinary original-to-English workflow and backups.

The earlier `Apply.cmd` / `Undo.cmd` manage their own exact installed version.
They will not upgrade or undo a manually replaced newer executable. Preserve
the original backup; undo a Tools installation by restoring that executable
while leaving current save files in place.

An external development `package.nw` installation is not the public embedded
0.8.0 executable and is not a supported incremental input. Preserve saves and
restore the original game layout before using the original-file route. Do not
mix external `package.nw` content with the new embedded executable.

Future translation releases can publish ordinary executable-to-executable
upgrade deltas. Latest follows verified available routes; an already-current
executable is recognized without patching again. An official Steam update that
changes required source files still needs a newly supported translation build.

## Maintainer workflow

Register `apathy-kiwame` / PC / `steam-app-id` / `2283710` in the shared library.
Use the reviewed combined-source Tools checkout and preview the build first:

```powershell
python tools/retro_trans_release.py --tools path/to/retro-trans-tools
python tools/retro_trans_release.py --tools path/to/retro-trans-tools --apply
```

The tool checks original and issued 0.8.0 hashes, creates a 0.8.1 embedded target
with only `english-ui.js`'s title version changed, preserves unchanged compressed
records and verifies all 2,009 package files. It builds full and incremental
deltas, decodes both, and checks the entire target, registration and metadata.
Only the two deltas, `BUILD-MANIFEST.json`, `VALIDATION.json`, `SHA256SUMS.txt`
and player documentation may be uploaded. Complete game executables, combined
sources, private configuration, original files, profiles and saves stay local.

The local build is under `work/debug/retro-trans-release-0.8.1`; private absolute
paths are excluded from its public manifest. Its verified target SHA-256 is
`55f523091dc62de6d73cdc1fb9d2dcb3b675a4ab47acf4a6688d08dcab693f95`.
Full patch: 162,330,751 bytes. Upgrade from public 0.8.0: 246,802 bytes.

Future releases still require the user's explicit approval. Do not alter the
issued 0.8.0 ZIP, checksums or original release tag.
