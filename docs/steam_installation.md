# Main Steam installation

Version 0.1.20 was installed at the user's request in `M:/Steam/steamapps/common/Apathy_kiwame`. Launch the game normally from Steam.

The installed game uses the verified runtime prefix and an external `package.nw` containing the tested English assets. Its original `package.json` preserves the publisher's application name and window settings. The entry page excludes the QA script, and no debugging or mute launch flags are installed. The official `kiwame.tpatch` remains unchanged; its contents are already merged into the English package and automatic reapplication is disabled by the tested configuration.

The original executable, publisher patch, and pre-install Steam save are backed up under `work/source/steam-original-10331351-20261111-121856`. `backup.json` records their SHA256 checksums. The game folder's `kiwame-english-install.json` records the installed version, backup location, and checksums of all 1,925 package files. Steam's own save was retained unchanged; preview saves were not imported.

`tools/install_steam.py` previews this first-install operation by default; `--apply` performs it after checking the game is closed. It refuses to overwrite an existing installation. For future extraction and build verification, `steam_game.archive_paths()` selects and verifies the original archives in the backup. `scenario.py`, `strip_jp.py`, and `draft.py` use that helper, so they continue to read the original Japanese source after the Steam executable has been replaced with its runtime prefix.

Native startup verification ran the executable from the actual Steam folder, reached its English title menu, checked the 3,593-break reflow map, and confirmed the absence of the QA runtime. The title music played with `muted=false`, nonzero volume, advancing playback time, and no decoder error. The temporary verification process was stopped, all installed files were checked, and Steam's save was restored to its exact pre-check bytes. Evidence is in `work/ui/steam-0.1.20-startup.json`, `steam-0.1.20-title.png`, and `steam-0.1.20-verified.json`.

To undo the installation, close the game, move the installed `package.nw` folder out of the game folder, restore `kiwame.exe` from the original-file backup, and move the installation marker out of the game folder. Retain the current Steam save files. The untouched publisher patch can stay in place. Do not restore the old backed-up save unless the user specifically requests reverting progress.
