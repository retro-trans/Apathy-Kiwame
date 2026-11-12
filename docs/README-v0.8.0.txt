APATHY KIWAME - ENGLISH PATCH v0.8.0
retro-trans / binhlt0402
https://github.com/retro-trans/Apathy-Kiwame

REQUIRES YOUR OWN JAPANESE STEAM COPY
App 2283710, Steam build 10331351. The patcher verifies SHA-256 hashes of
kiwame.exe and kiwame.tpatch before changing anything. Other builds and old
development package.nw installations are not supported by this standalone patch.

INSTALL (Windows 10/11, 64-bit)
1. Close the game. Extract this entire ZIP to a writable folder.
2. Double-click Apply.cmd. It finds the Steam game folder, or lets you choose it.
3. Wait for the verified-success message, then launch the game through Steam.

No Python or separate patching app is required. Allow at least 4 GB free disk
space on the game drive. The patcher combines your original kiwame.exe followed
by kiwame.tpatch in a temporary source file and applies the bundled binary delta.
The original files are backed up under .retro-trans-backup inside the game folder.
All existing save files are preserved. Normal game music/effects remain enabled.
An older saved page can retain its previous text until you advance; following
script text uses the translation. Old Life-passage text is replaced by the summary.

OPTIONAL COMMAND LINE
powershell -NoProfile -ExecutionPolicy Bypass -File .\Patch-Apathy-Kiwame.ps1 -GameFolder "D:\Steam\steamapps\common\Apathy_kiwame" -DryRun
Remove -DryRun to install. Keep the entire extracted ZIP together.

UNDO
Close the game and run Undo.cmd. This restores the verified original executable
from the backup and preserves your CURRENT saves. It does not restore old progress.
Steam file verification can overwrite the patch; reapply it after restoring the
supported original build. Do not delete your save files or the original backup.

WHAT IS TRANSLATED
36,145 ordinary text fields, all 147 ending titles, interface/choices, remaining
story lettering, the GenEi proportional Latin font and 16 translated streamer videos.
The61 source fields of one Life passage are represented by a labelled, three-page
non-graphic summary. They are adapted, not61 individual literal translations.
140 inventoried entries are blank HTML layout; no known scenario fields remain
unaccounted for. Original Japanese names/logos/copyright and engine identifiers
may remain where they are proper credits or internal data.

STATUS
The English is AI-produced and has undergone AI accuracy, editing and proofreading
passes. This is not a claim of complete human proofreading. Native route tests and
focused menu/audio/save checks passed; every story-flag combination has not been
playtested. Report issues with a screenshot, scene, choices, and patch version.

LICENSES AND CREDIT
This is an unofficial free fan patch. You must own the game. No complete game,
original Japanese script dump, saves or QA runtime is distributed in this ZIP.
GenEi LateGo P v2 by o_tamon and its contributors: SIL Open Font License1.1.
Xdelta 3.2.0 by Joshua MacDonald: Apache License2.0. Notices are in licenses/.
The original game and assets remain the property of their respective creators.

Do not sell the patch, prepatched game copies, or access to the download.
Contribute / report issues: https://github.com/retro-trans/Apathy-Kiwame/issues
Community: https://discord.gg/MssepShjmB
