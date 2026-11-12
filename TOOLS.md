# Translation and patch tools

| Tool | Purpose |
| --- | --- |
| `scenario.py` | Inventory and source-hash-checked rendering of English fragments |
| `strip_jp.py` | Export proofread English from a local bilingual working file; use `--dry-run` first |
| `field_coverage.py` | Account separately for ordinary English, adapted fields and blank layout |
| `text_flow.py` | Audit natural English joins while preserving native source positions |
| `steam_game.py` | Prepare an isolated development build from owned original archives |
| `ui.py` and route artwork helpers | Install reviewed layouts/lettering; some clean plates remain local-only |
| `english.js`, `english.css` | Proportional English rendering, choices, backlog and compatibility helpers |
| `audio-captions.js` | Source-supported sound-clock captions and cleanup |
| `inoti-grid.js` | Save/load lifecycle for the adapted Life puzzle |
| `life_summary.py`, `life-summary.js` | Non-graphic adaptation with native order/save compatibility |
| `title-credit.js` | Title-only retro-trans credit and current build version |
| `start-qa.ps1`, `qa-session.mjs`, `qa.mjs` | Isolated native debugging; never use on player saves |
| `release_patch.py` | Build a binary delta and verify exact decode reproduction |
| `distribution/Patch-Apathy-Kiwame.ps1` | Standalone Windows installer/undo with source, target and save checks |
| `archive_build.py` | Verify reverse Xdelta archives of older local builds |

The standalone release installer needs no Python. Development uses Python 3.11,
Node 22+, and the dependencies needed by the selected artwork tool. FontTools is
pinned in `tools/requirements-art.txt`; other artwork tools use Pillow/NumPy.

`release_patch.py` starts from a locally verified preview and owned stock
archives. It preserves unchanged ZIP records so the delta can reference the
player's original compressed game data. It excludes QA code, verifies every
embedded output file, then decodes the finished patch and checks the entire
target hash. Its default mode only reports; `--apply` writes local artifacts.

The public installer concatenates the two verified stock inputs, decodes to a
staged executable, checks the result, rechecks that the game is closed and saves
are unchanged, and keeps a verified original backup before replacing anything.
Undo restores the original executable while retaining current saves.

Earlier project-specific `install_steam.py` / `upgrade_steam.py` scripts describe
the external development layout and require local verification manifests. Use
the release ZIP's `Apply.cmd` for a normal public installation.
