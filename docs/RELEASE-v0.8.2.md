English patch **0.8.2** for **Apathy - Gakkou de Atta Kowai Hanashi - Kiwame**,
Japanese Steam edition, app 2283710, build 10331351.

### Changes

- Choices ignore clicks and touches for 0.5 seconds after the menu finishes
  drawing. Early presses are discarded, including when a menu is loaded from a
  save. The RPG choice-drawing/navigation guard also prevents missing-label
  errors caused by rapid clicking. Timed battles keep their original deadlines.
- Fixes merged words and unnatural RPG dialogue breaks, including 292
  continuations. Original click pauses and scenario positions remain intact;
  older rendered save text is repaired in memory.
- Fixes sideways English on opening pages after an ending and on older saves.
- Keeps the Ending List heading English when the pointer leaves an entry.
- Recreates the English game-over animation with the original ripple, color
  separation and fade; improves the English notebook cover using the original
  artwork as reference.
- Rebuilds the Self-Help letter as scrolling English over the original montage.
  All 428 reviewed words, original frame timing and original audio are retained.
  Covered pixels are restored; small cleanup marks may remain. The final book
  photograph retains an English title caption.
- Translates all 44 credit-roll rows. Six obscure credited names/resource names
  use approved provisional Latin readings, listed in the
  [credit review](https://github.com/retro-trans/Apathy-Kiwame/blob/main/docs/credits-roll-0.8.2-review.md).

### Install or update

**Retro Trans Tools:** use
[0.5.23 or later](https://github.com/retro-trans/retro-trans-tools/releases/latest).
Select the original game folder containing `kiwame.exe` and `kiwame.tpatch`, or
select a public English **0.8.0 or 0.8.1** executable for a smaller direct
upgrade. Choose Latest and a new output filename. After verification, close the
game, retain your original backup and copy the output into the Steam folder as
`kiwame.exe`. Leave saves, DLLs and the official `kiwame.tpatch` in place.

**Standalone:** download
[Apathy-Kiwame-English-v0.8.2-Standalone.zip](https://github.com/retro-trans/Apathy-Kiwame/releases/download/v0.8.2/Apathy-Kiwame-English-v0.8.2-Standalone.zip),
extract the whole ZIP to a writable folder, close the game and run **Apply.cmd**.
No Retro Trans Tools, Python or separate xdelta application is required. This
installer needs the supported original Japanese files. For an older standalone
English installation, run **Undo.cmd from its old ZIP first**, then Apply.cmd
from this ZIP. Both operations preserve current saves. Allow 4 GB free space.

An external development `package.nw` installation needs migration to the stock
layout before either route; preserve saves and original backups. Read the
[complete instructions](https://github.com/retro-trans/Apathy-Kiwame/blob/main/docs/RETRO_TRANS_TOOLS.md).
Steam updates or verification can replace the patched executable; changed
original hashes require a compatible new patch.

### Verification and limitations

The full patch and both direct upgrades decode to the same verified executable.
The standalone installer uses that same full delta. The release contains no
complete game, original script dump, user saves or QA runtime. Original files
and the user's running Steam installation are unchanged by release preparation.

This remains an AI-produced fan translation requiring human proofreading and
broader playtesting. The labelled three-page non-graphic Life adaptation is
unchanged. GenEi and Xdelta notices/licenses are included. The patch is free,
unofficial and requires your own supported copy of the game.
