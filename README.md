# Apathy - Gakkou de Atta Kowai Hanashi - Kiwame — translation project

English fan translation and tools for **Apathy - Gakkou de Atta Kowai Hanashi - Kiwame** (Windows / Japanese Steam
edition, app **2283710**, build **10331351**).

## Contribute

The ordinary script is translated, but the English still needs human proofreading
and wider playtesting. Please send bug reports, awkward lines and route details
through [Issues](https://github.com/retro-trans/Apathy-Kiwame/issues), or join the
community for this project and the next:

**[discord.gg/MssepShjmB](https://discord.gg/MssepShjmB)**

## Play it

The current release is **[v0.8.1](https://github.com/retro-trans/Apathy-Kiwame/releases/tag/v0.8.1)**.
It includes the English dialogue and choices, all 147 ending titles, interface and
story lettering, proportional Latin text, the readable backlog, and 16 translated
streamer videos. The title screen identifies the patch version and retro-trans.

One Life passage is represented by a **labelled, three-page non-graphic summary**.
Its 61 original fields are adapted rather than translated individually. The
summary retains the story context and outcome while omitting explicit details.

### Apply with Retro Trans Tools

You need your own supported Japanese Steam installation and
**[Retro Trans Tools 0.5.23 or later](https://github.com/retro-trans/retro-trans-tools/releases/latest)**
for 64-bit Windows. No Python installation is required.

1. Close the game and open Retro Trans Tools.
2. In **Automatic**, choose **Folder** and select the game folder containing
   the original `kiwame.exe` and `kiwame.tpatch`. For an upgrade from the public
   0.8.0 English version, use **Browse** to select its patched `kiwame.exe`.
3. Choose **Latest**, select a new output filename, and click **Patch**.
4. Keep a backup of the existing executable. Copy the verified output into the
   game folder as `kiwame.exe`, then launch normally through Steam. Leave your
   save files, DLLs and official `kiwame.tpatch` in place.

The app downloads the matching patch and verifies every input and output. The
full patch is about **162 MB**; the upgrade from public 0.8.0 is about **247 KB**.
Allow at least 4 GB free space for the full workflow and backups. Normal music
and sound effects remain enabled. The app never overwrites original inputs,
existing outputs or saves; copying the verified executable is a separate step.

| Input | Requirement |
| --- | --- |
| `kiwame.exe` | Original Japanese executable from Steam build 10331351 |
| `kiwame.tpatch` | Matching official publisher patch from the same build |
| Public English 0.8.0 executable | Recognized directly for the smaller upgrade |
| Earlier local `package.nw` development patch | Preserve saves and restore the original game layout before using the original-file route |

See [the complete Tools instructions](docs/RETRO_TRANS_TOOLS.md), including
backups, undo and future updates. The release contains bare xdelta patches,
`BUILD-MANIFEST.json`, `VALIDATION.json`, `SHA256SUMS.txt` and license notices.
The app combines the two original source files temporarily; no manual file
combining is needed. Version 0.8.1 changes distribution and the title version
credit; story content is unchanged from 0.8.0.

The earlier [0.8.0 installer ZIP](https://github.com/retro-trans/Apathy-Kiwame/releases/tag/v0.8.0)
and its [instructions](docs/README-v0.8.0.txt) remain available unchanged.

### Standalone ZIP — no Retro Trans Tools required

Download **[Apathy-Kiwame-English-v0.8.1-Standalone.zip](https://github.com/retro-trans/Apathy-Kiwame/releases/download/v0.8.1/Apathy-Kiwame-English-v0.8.1-Standalone.zip)**,
extract the entire ZIP to a writable folder, close the game, and double-click
**Apply.cmd**. It finds the Steam folder or lets you choose it, checks the
supported original files, keeps a verified backup and installs the same 0.8.1
English executable. Launch normally through Steam after the success message.
No Retro Trans Tools, Python or separate xdelta app is required.

This full installer needs the original Japanese build 10331351. To upgrade an
older standalone installation, run **Undo.cmd from that old package first**, then
Apply.cmd from the new ZIP; both preserve current saves. The Tools route above
offers the smaller direct upgrade from the public English 0.8.0 executable.
See the [standalone instructions](docs/README-standalone-v0.8.1.txt).
The separate [Standalone-SHA256SUMS-v0.8.1.txt](https://github.com/retro-trans/Apathy-Kiwame/releases/download/v0.8.1/Standalone-SHA256SUMS-v0.8.1.txt)
verifies this optional ZIP; the existing Tools assets and canonical checksums
remain unchanged.

### Undo / Steam updates

For the standalone 0.8.1 ZIP, close the game and run **Undo.cmd from that ZIP**.
It restores the verified original executable while preserving current saves.

For a Tools-installed version, close the game and restore the original executable
from your retained backup, leaving current saves in place. The older 0.8.0
`Undo.cmd` only manages its exact installed version; it cannot undo a newer
executable copied into place. Its verified original backup remains under
`.retro-trans-backup` if you used that installer. Do not restore an old save backup
unless you intend to roll back progress.

A page captured in an older save can retain its previously rendered text until
you advance. The next script text uses the installed translation. The Life
adaptation also replaces old scene text and thumbnails in memory before display.

Steam file verification or an official update can replace the modified
executable. Reapply only when the original files match the supported hashes.
Keep the original backup and your saves.

## Check the translation

The English overlays are in [`work/translation/en`](work/translation/en), keyed
by scenario and original source-field location. Each overlay records the source
SHA-256; the renderer refuses a different source or damaged fragment structure.
These files contain English, not a dump of the Japanese script.

With your own supported game and original backup available:

```powershell
python tools/scenario.py verify --scenario op.ks --dry-run
python tools/field_coverage.py
```

The coverage report separates ordinary translated fields, adapted fields and
blank HTML layout entries. A complete field inventory does not mean every
possible route-state combination has been played.

## Translate it

Start with **[TRANSLATING.md](TRANSLATING.md)**. Edit a local working copy, check
accuracy and nearby context, edit for clarity and character voice, then proofread.
Keep placeholders, commands, deliberate pauses and source-field positions.

```powershell
python tools/scenario.py export --scenario op.ks --dry-run
python tools/strip_jp.py work/source/op.working.json --dry-run
```

Run the export without `--dry-run` only when ready. Commit the resulting
`*.en.json` overlay, never the local Japanese working file.

The repository includes the script and layout tools. Some optional artwork
regeneration and historical QA commands depend on local clean plates and test
fixtures, which are not redistributed. Players should use the verified release
patch rather than attempting a complete artwork rebuild from a fresh checkout.

## What is here

| Path | Contents |
| --- | --- |
| `TRANSLATING.md` | Editing, review and source-safety workflow |
| `TOOLS.md` | Extraction, rendering, debug and distribution tools |
| `tools/` | Source-checked script renderer, English UI/runtime helpers, artwork tooling and release patcher |
| `work/translation/en/*.en.json` | 29 English script/UI overlays |
| `work/translation/en/adaptations/` | Non-graphic Life summary and editorial decisions |
| `work/translation/en/media/` | English timed lettering/caption data |
| `work/glossary/` | 18 glossary files with names, terms and references |
| `work/ui/` | Selected editable UI specifications and field-coverage metadata |
| `docs/` | Typography, integration and route-review notes |
| `CHANGELOG.md` | Build history, fixes and limitations |

Original archives, unpacked game data, local working scripts, save files, full
test builds, clean plates and native QA captures stay local. Release downloads
contain a binary patch and installer, not a complete game or prepatched executable.

## Using these tools

Development uses Python 3.11 and Node 22 or later. Most checks need the original
game source. Read each tool's help and preview changes before writing them.
`tools/release_patch.py stage` and `build` are read-only unless passed `--apply`.
`tools/strip_jp.py` writes an export unless passed `--dry-run`.

For automated native checks, the isolated QA launcher mutes only its child
process. Ordinary Steam and preview launches retain sound. Debugging and route
evidence are described in [docs/debug_tools.md](docs/debug_tools.md).

## Do not sell this

This is a free, unofficial fan translation. Please keep the patch and its
downloads free. Do not sell prepatched game copies or put downloads behind
payment or advertising gates. You need your own copy of the game.

The original game, script, characters and assets belong to their respective
creators and publishers. The repository's license grants no rights to the game.

## Credits

| Role | Credit |
| --- | --- |
| Project direction, testing and release | [binhlt0402](https://github.com/binhlt0402), retro-trans |
| Translation passes, editing, reverse engineering and tools | OpenAI Codex, directed by the project lead |
| Proportional font | [GenEi LateGo P v2 by o_tamon](https://okoneya.jp/font/genei-latin.html), with its original contributors and SIL OFL 1.1 notices |
| Binary patching | [Xdelta 3.2.0 by Joshua MacDonald](https://github.com/jmacd/xdelta/tree/v3.2.0), Apache 2.0 |
| Original game | The original creators and publishers; original copyright credits are preserved |

The README follows the structure of the organization's
[SRW-Z project](https://github.com/retro-trans/SRW-Z). Its contributors and
proofreading statistics are not claimed for this game.

## Status

| Area | v0.8.1 coverage |
| --- | --- |
| Ordinary text | 36,145 translated fields |
| Life adaptation | 61 original fields represented by 3 summary pages |
| Blank layout | 140 HTML-only inventory entries |
| Total known inventory | 36,346 fields accounted for; no unknown gaps |
| Ending List | 147 revealed and 147 locked labels checked |
| New route checks | 13 Life, 4 Revenge Site, 25 cram-school and 5 Summoning Incident ending codes, plus earlier route evidence |

### Human proofreading

The translation is AI-produced. Accuracy, editorial and proofreading passes in
the project records are AI passes unless explicitly attributed otherwise. There
is no complete, counted human script-proofreading total yet. User playtesting,
layout reports and listening checks are valuable, but are not counted as a human
read-through of every line.

Native playtests check route outcomes, text fit, graphics, captions and selected
save/load/timer behavior. They do not cover every combination of story flags.
Version 0.8.0 is the first public release, not a claim that further corrections
will be unnecessary.
