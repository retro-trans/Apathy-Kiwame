English patch **0.8.1** for **Apathy - Gakkou de Atta Kowai Hanashi - Kiwame**,
Japanese Steam edition, app 2283710, build 10331351.

### Standalone ZIP — no Retro Trans Tools required

Download **[Apathy-Kiwame-English-v0.8.1-Standalone.zip](https://github.com/retro-trans/Apathy-Kiwame/releases/download/v0.8.1/Apathy-Kiwame-English-v0.8.1-Standalone.zip)**,
extract the entire ZIP, close the game and run **Apply.cmd**. It finds the Steam
folder or lets you choose it, verifies the supported original Japanese build,
keeps original backups and installs the same English executable. No Retro Trans
Tools, Python or separate xdelta application is needed. Launch through Steam
after the verified-success message. Allow 4 GB free space.

This installer requires original Steam build 10331351. For an older standalone
English installation, run **Undo.cmd from the old package first**, then Apply.cmd
from this ZIP. Saves are preserved. This ZIP's Undo.cmd restores the original
executable while keeping current progress. Read the included README.txt and use
**Standalone-SHA256SUMS-v0.8.1.txt** to verify the ZIP.

### Patch and update with Retro Trans Tools

Requires **Retro Trans Tools 0.5.23 or later**. In Automatic, select the folder
containing your original `kiwame.exe` and `kiwame.tpatch`, choose Latest and a
new output filename, then Patch. Both original files are verified and combined
temporarily by the app; no manual concatenation is needed.

Already using the public 0.8.0 English executable? Select that executable for
the **247 KB upgrade**, instead of the **162 MB full patch**. Only exact supported
inputs are accepted. The app verifies the downloaded delta and the complete
output and preserves all inputs and saves.

Close the game, keep a backup of the existing executable, and copy the verified
output into the Steam game folder as `kiwame.exe`. Leave your save files, DLLs
and official `kiwame.tpatch` in place. Launch normally through Steam. An older
external development `package.nw` installation needs migration to the stock
layout first; see the [complete instructions](https://github.com/retro-trans/Apathy-Kiwame/blob/main/docs/RETRO_TRANS_TOOLS.md).

### Changes and checks

- Adds verified full and 0.8.0 upgrade paths for the shared patching app.
- Updates the title-screen credit to 0.8.1. Story, graphics, audio and the
  non-graphic Life adaptation are unchanged from 0.8.0.
- Both deltas decode to the same complete verified executable. All 2,009
  package files were compared; only the title version entry changes.
- Actual Automatic full and upgrade operations, current-version recognition,
  native title startup, proportional font and title audio were checked locally.
- Original source files and main Steam saves remain unchanged. No complete game,
  original script, user saves or QA runtime belongs in the release assets.

The AI-produced translation still needs human proofreading and broader
playtesting. GenEi and Xdelta notices/licenses remain applicable. This is a
free unofficial fan translation; you need your own supported copy of the game.
