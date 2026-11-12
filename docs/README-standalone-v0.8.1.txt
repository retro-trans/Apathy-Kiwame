Apathy - Gakkou de Atta Kowai Hanashi - Kiwame
English patch v0.8.1 - standalone Windows installer
retro-trans / binhlt0402
https://github.com/retro-trans/Apathy-Kiwame

INSTALL WITHOUT RETRO TRANS TOOLS
1. Close the game. Extract the ENTIRE ZIP to a writable folder, such as Downloads.
2. Double-click Apply.cmd. It finds the Steam game folder or lets you choose it.
3. Wait for the verified-success message, then launch the game through Steam.

Do not just unzip over the game and expect the translation to be installed.
Apply.cmd must run once. Keep all the extracted files together. No Retro Trans
Tools, Python installation or separate xdelta program is required. The included
patcher uses Windows PowerShell and the bundled decoder. Windows 10/11, 64-bit.
Allow at least 4 GB free space on the game drive for staging and backup.

SUPPORTED INPUT
Your own ORIGINAL Japanese Steam installation: app 2283710, build 10331351,
with both original kiwame.exe and kiwame.tpatch. The installer verifies exact
SHA-256 hashes, creates a temporary combined source, applies the delta and
checks the complete English executable before replacing the installed file.
It keeps original backups under .retro-trans-backup. Saves remain unchanged.

This produces the SAME English executable as Retro Trans Tools 0.8.1 patches.
Normal music and effects remain enabled. One Life passage uses the approved
labelled, three-page non-graphic summary; story content matches patch 0.8.0.

UPGRADING FROM AN EARLIER ENGLISH PATCH
This standalone ZIP applies to the ORIGINAL Japanese files, not a different
English executable. If you used the 0.8.0 standalone installer, close the game
and run Undo.cmd from THAT OLD package first. It restores the original game
without rolling back your current saves. Then run Apply.cmd from this ZIP.
For a direct, approximately 247 KB upgrade from the public English 0.8.0
executable, use Retro Trans Tools 0.5.23 or later instead of this full ZIP.

If you manually replaced the executable, restore your verified original first.
An external development package.nw layout is not supported: preserve saves and
restore the original game layout. Never copy an older save backup over your
current progress as part of restoring game files. Unsupported inputs are refused.

UNDO
Close the game and run Undo.cmd from this ZIP. It restores the verified original
executable from this installer's backup and preserves your CURRENT saves.
Do not delete the original backup. Undo.cmd only manages its exact installed
version; it cannot undo a later executable copied in manually.

STEAM UPDATES
An official update or file verification can replace the English executable.
Reapply only when the original files match this supported build. A changed
official build needs a compatible translation patch; checksum checks stay enabled.

OPTIONAL COMMAND LINE
powershell -NoProfile -ExecutionPolicy Bypass -File .\Patch-Apathy-Kiwame.ps1 -GameFolder "D:\Steam\steamapps\common\Apathy_kiwame" -DryRun
Remove -DryRun to install. Dry run checks compatibility without changing files.

CHECKSUMS
Standalone-SHA256SUMS-v0.8.1.txt on the release page verifies this ZIP.
BUNDLE-SHA256SUMS.txt inside this ZIP lists every other included file.
The separate canonical SHA256SUMS.txt on the release page covers the Tools
assets; it is unchanged. Windows PowerShell can check a downloaded file:
Get-FileHash .\Apathy-Kiwame-English-v0.8.1-Standalone.zip -Algorithm SHA256

STATUS AND CREDIT
The English is AI-produced, with AI accuracy, editorial and proofreading passes.
Human proofreading and wider playtesting remain welcome. This release does not
claim that every combination of story flags has been tested.
This is a free unofficial fan translation. You must own the game. No complete
game, original Japanese script dump, user saves or QA runtime is included.
GenEi LateGo P v2 by o_tamon and contributors: SIL Open Font License 1.1.
Xdelta 3.2.0 by Joshua MacDonald: Apache License 2.0. Notices are in licenses/.
Original game rights remain with their creators and publishers. Keep the patch
free; do not sell prepatched games or charge for access to the download.

Report issues: https://github.com/retro-trans/Apathy-Kiwame/issues
Community: https://discord.gg/MssepShjmB
