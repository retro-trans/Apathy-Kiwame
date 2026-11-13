# Retro Trans Tools integration — 0.8.2

Use [Retro Trans Tools 0.5.23 or later](https://github.com/retro-trans/retro-trans-tools/releases/latest)
for **Apathy - Gakkou de Atta Kowai Hanashi - Kiwame**.

1. Close the game. In Automatic, choose Folder for the original Japanese Steam
   build 10331351 containing both kiwame.exe and kiwame.tpatch, or Browse to a
   public English 0.8.0/0.8.1 executable for a smaller direct upgrade.
2. Choose Latest and a new output filename, then Patch. Every input, download
   and complete output is verified. Already-current executables are recognized.
3. Keep your original backup. Copy the verified output into the closed Steam
   game as kiwame.exe. Leave current saves, DLLs and official kiwame.tpatch in
   place, then launch normally through Steam.

The original files are combined temporarily by the app; no manual combining is
needed. Inputs and existing outputs are never overwritten. Allow 4 GB free space.

The optional [standalone ZIP](https://github.com/retro-trans/Apathy-Kiwame/releases/download/v0.8.2/Apathy-Kiwame-English-v0.8.2-Standalone.zip)
needs no Retro Trans Tools, Python or separate xdelta app. Extract the whole ZIP
and run Apply.cmd against the supported original Japanese files. For an older
standalone installation, first run Undo.cmd from its old ZIP, then Apply.cmd
from this one. Both preserve current progress. Read the
[standalone instructions](README-standalone-v0.8.2.txt).

An external development package.nw layout is different from the public embedded
executable. Preserve saves and restore the original layout before patching.
Do not mix an external package with a public English executable.

## Undo and future updates

Each standalone Undo.cmd manages its exact installed version. For a Tools
installation, restore the original executable from your verified backup while
the game is closed. Keep current saves; do not restore an older save backup as
part of an upgrade. Steam verification or official updates can replace the
translation. Reapply only to supported original hashes; changed official files
require a compatible translation build. Earlier releases remain unchanged.

## Maintainer workflow

Run tools/release_update.py with content, assets and standalone, first without
--apply to inspect each plan. Content starts from the exact issued 0.8.1
executable, replaces reviewed staged assets and includes the verified English
letter movie. Unchanged compressed records remain byte-identical; every package
file is compared, and QA runtime/profile/save exclusions are checked.

The registered shared release library builds and fully decodes the original
combined-source delta and both direct upgrades. All routes produce the same
verified executable. The standalone uses the same full delta and established
Windows PowerShell installer. Complete game executables, originals, local
configuration, QA profiles and saves remain local.

After explicit user publication approval, upload the three deltas, standard
manifest/validation/checksums, notices ZIP, and optional standalone ZIP with its
separate checksum. Refresh and verify the shared catalog after publication.
Never replace issued assets or tags on older releases.
