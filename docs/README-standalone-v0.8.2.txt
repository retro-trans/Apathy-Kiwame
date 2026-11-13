Apathy - Gakkou de Atta Kowai Hanashi - Kiwame
English patch v0.8.2 - standalone Windows installer
retro-trans / binhlt0402
https://github.com/retro-trans/Apathy-Kiwame

INSTALL
1. Close the game. Extract the ENTIRE ZIP to a writable folder.
2. Double-click Apply.cmd and choose the supported original Steam game folder.
3. Wait for verified success, then launch normally through Steam.

No Retro Trans Tools, Python or separate xdelta program is needed. Do not just
unzip into the game folder: Apply.cmd must run. Windows 10/11, 64-bit, with
Windows PowerShell. Allow at least 4 GB free space for staging and backups.

SUPPORTED INPUT
Your own original Japanese Steam edition: app 2283710, build 10331351, with
both original kiwame.exe and kiwame.tpatch. Exact hashes are checked before
installation. Original backups are kept under .retro-trans-backup. All current
system and slot save files are preserved. Normal music/effects remain enabled.

UPGRADING
For an older standalone English version, first run Undo.cmd from THAT version's
ZIP. It restores the original executable without rolling back current saves.
Then run Apply.cmd from this ZIP. If you manually copied a newer executable,
restore your verified original before using this installer.

Retro Trans Tools 0.5.23 or later also offers smaller direct upgrades from the
public English 0.8.0 and 0.8.1 executables. Select that executable in Automatic,
choose Latest and a new output filename, then copy the verified output into the
closed Steam game as kiwame.exe. Keep your original backup and current saves.

An external development package.nw installation is unsupported by this
installer. Preserve saves and restore the stock game layout first. Unsupported
inputs are refused. Never replace current saves with an older backup as part
of an upgrade.

UNDO
Close the game and run Undo.cmd from this ZIP. It restores this installer's
verified original executable and preserves CURRENT saves. Keep the original
backup. Undo.cmd only manages its exact installed version.

WHAT CHANGED
Half-second choice input delay, rapid-click RPG choice protection, natural RPG
text wrapping and spacing, old-save display repairs, horizontal opening text,
English Ending List heading in both pointer states, original-style English
game-over effect, improved notebook cover, rebuilt scrolling English letter,
and all 44 credit rows. Six credited-name spellings remain provisional; see
the release notes. The three-page non-graphic Life adaptation is unchanged.

CHECKSUMS
Standalone-SHA256SUMS-v0.8.2.txt on the release page verifies this ZIP.
BUNDLE-SHA256SUMS.txt lists all other files inside it. The separate canonical
SHA256SUMS.txt covers the Tools patch assets.

STEAM UPDATES
Steam verification or an official update can replace the translated executable.
Reapply only to supported original hashes. A changed official build requires a
compatible patch; checksum protections remain enabled.

OPTIONAL COMMAND LINE
powershell -NoProfile -ExecutionPolicy Bypass -File .\Patch-Apathy-Kiwame.ps1 -GameFolder "D:\Steam\steamapps\common\Apathy_kiwame" -DryRun
Remove -DryRun to install.

The English is AI-produced and still needs human proofreading and wider
playtesting. This free unofficial patch requires your own game. No complete
game, original Japanese script dump, user saves or QA runtime is distributed.
GenEi LateGo P v2: SIL Open Font License 1.1. Xdelta: Apache License 2.0.
Notices are included under licenses/. Original game rights remain with their
creators and publishers. Keep this patch free.

Issues: https://github.com/retro-trans/Apathy-Kiwame/issues
Community: https://discord.gg/MssepShjmB
