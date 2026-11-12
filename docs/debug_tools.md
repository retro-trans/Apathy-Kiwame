# Apathy Kiwame translation QA

The Windows Steam build uses NW.js and TyranoScript 4.5. The browser debugger exposes the running interpreter, page input, and screenshots. Game state lives in JavaScript objects, so there are no emulator registers, console memory addresses, or framebuffer scratch regions to maintain.

## Launch and attach

Run from the project folder with Python 3.11 and Node 22 or later. The project builds a local copy by combining the app archive in `kiwame.exe` and the official `kiwame.tpatch`. Its own save files and browser profile stay under the test folder. The launcher mutes playback and uses loopback port `9229`. Set `KIWAME_QA_PORT` in the same shell before launching and running the client to override it.

Since 0.1.19, only the QA launcher sets `KIWAME_QA_AUDIO_MUTE=1`, temporarily for its child process. It also passes `--mute-audio`. Double-clicking the local build keeps the game's normal music and effects. Earlier debug builds wrapped every media `play()` call with unconditional muting, which incorrectly silenced ordinary launches too. The normal-launch regression check leaves the environment variable unset and uses only the process audio flag to keep automated testing quiet; media state must remain unmuted, at nonzero volume, with advancing playback time and no decode error.

`tools/qa-session.mjs` provides the shared debugger connection and screenshot heartbeat for native regression checks. A debugger target already attached by another client may omit its socket address; finish that client before opening another connection.

Its `ensureInitialized` helper completes normal first/title startup before a RAM fixture is loaded. Save snapshots contain game state but do not contain global `SE`/`BGM` alias tables from `settei/teisu.ks`. Loading a snapshot too early can therefore leave direct-file sound cues usable while an alias-based route stops. The ED120 fixture exposed this setup mistake; its corrected run passes after normal startup. This is a QA initialization correction, not a game-script patch.

For the isolated Life candidate, `work/source/qa-inoti-routes.mjs` follows actual choices from the route start and records pause bounds and ending codes. ED116 uses a blanked page throughout traversal and metadata-only inspection around the retained-original scene; it must never capture that passage or its artwork. The generic `state` command includes displayed text, so do not use it to inspect that scene. `qa-inoti-menus.mjs` measures all102fresh/visited choice variants separately from story prompts. `qa-inoti-fixed-grid.mjs` covers grid choices and cross-attempt snapshots. `qa-inoti-runtime-guards.mjs` uses only synthetic punctuation at the retained-range boundaries. `qa-inoti-audio.mjs` observes actual sound clocks, native waits, caption bounds and natural ends; `--load-cleanup` checks an ordinary audio-restoring load. The optional debug mode `bgm_over:true` deliberately preserves playback and must not be mistaken for ordinary load behavior. The focused fixtures use disposable RAM snapshots and do not write player saves.

```powershell
py -3.11 tools/steam_game.py --english --debug --output work/debug/kiwame-new --dry-run
py -3.11 tools/steam_game.py --english --debug --output work/debug/kiwame-new
.\tools\start-qa.ps1 -GameFolder work/debug/kiwame-new
node tools/qa.mjs state
.\tools\start-qa.ps1 -GameFolder work/debug/kiwame-new -Stop
```

| Command after `node tools/qa.mjs` | Result |
| --- | --- |
| `state` | Current scenario, one-based source line, tag, interpreter order, stop state and visible controls |
| `inspect '.current_span'` | Text, computed font, writing direction and screen bounds |
| `metrics` | Actual canvas widths of narrow and wide Latin glyphs and current dialogue dimensions |
| `advance` | Click the game's event layer to advance text |
| `click '.op.event-setting-element'` | Click one specific visible game control |
| `screenshot work/ui/new-capture.png` | Capture the game page to a new PNG without taking focus |
| `trace` | Enable tracing or read the last 200 interpreter dispatches with line and tag names |
| `snapshot first-choice` / `saved first-choice` | Capture or read named state and variable copies in the current QA process |
| `jump op.ks '*start'` | Load a scenario or label from a paused scene. The target runs its normal commands. |
| `preview 'Sample dialogue'` / `clearPreview` | Draw temporary plain text through the current message renderer without running the next script order or writing to the backlog |
| `reload` | Reparse the active scenario from disk at a strong stop and swap its tag list only if order, tag kinds and line numbers match |

## Interpreter and reload boundaries

`TYRANO.kag.stat.current_scenario` identifies the active script. `TYRANO.kag.ftag.current_order_index` indexes `array_tag`. `is_strong_stop`, `is_adding_text`, and `is_trans` determine whether the game is paused at an idle menu or choice. `nextOrder` dispatches tags. `getMessageInnerLayer` locates the current text region, and the stock `text` tag draws preview text. Existing buttons keep their click handlers. The snapshot command records state for inspection during the current process. It does not restore a game.

To apply updated English rows to a running test copy, run `py -3.11 tools/scenario.py refresh --test-folder work/debug/kiwame-new --scenario op.ks --dry-run`, inspect the affected file, and run it again without `--dry-run`. Then call `reload` while at a menu or choice. Reload takes effect on the next script order. Restart the test copy for changed layouts, asset substitutions, initialized macros, other startup data, or changed tag structure. The preview command uses the current message style and accepts plain text. Use normal play or `jump` for real scene portraits, effects, and choices.

## Coverage

The combined 0.1.22 debug candidate is `work/debug/kiwame-0.1.22-combined-draft2`, separate from the main Steam game and current delivered preview. `qa-site-routes.mjs` follows the native choice controls without shortening either eight-second wait. `qa-all-ending-list.mjs` checks all 147 revealed or locked labels through the native three pages. `qa-remaining-source-defects.mjs` records the original expression and asset-loader failures without executing a destructive error/reset path. `tools/remaining_routes.py` prepares only the three confirmed command repairs; its default invocation is read-only.

`qa-jyuku-art.mjs` and `qa-art-directory.mjs` render SVG previews inside the isolated native renderer, then remove their temporary overlays. These fixtures do not certify actual scene timing, picture interaction or every protected pixel. A single debugger client may use the QA port at a time. The startup guard observes transient script calls even when they inherit the native strong-stop flag; it does not restart a still-loading instance.

The Life phase-one checks are frozen before the combined script/runtime changes. Recheck that phase with `py -3.11 work/source/check-inoti-english-candidate.py --frozen`; its saved input manifest verifies all archived input hashes. Final combined-build evidence must bind to its own files.

The current combined candidate is `work/debug/kiwame-0.1.22-combined-draft3`. `tools/field_coverage.py` accounts for every extracted field while masking the retained passage before scanning. `check-combined-candidate.py` reproduces the new script/engine/artwork components and hashes all 472 original media files. `qa-remaining-menus.mjs` checks every new fresh/visited label. `qa-flow-combined.mjs` checks all 35,331 eligible native break commands, including a substitution after a comma; its earlier failed fixture assumed the next token was always literal text. Production reflow did not change for that correction. `qa-dynamic-hobby.mjs` checks all three canonical values with the real embedded-text renderer without changing branch state; it does not stand in for old-slot or choice-path tests.

`work/source/qa-remaining-routes.mjs` follows real Jyuku or Syorei choice controls. Run its `dry-run` capture ID first to inspect paths. A unique capture ID writes immutable final evidence and a separate live progress file. Native RAM menu snapshots reside in `work/debug/route-bank-<route>-draft3-v2`; the index hashes each snapshot and binds its scenario, English runtime and UI map. Prefix keys include the initial-story context, so the two ED079 conditions cannot share a checkpoint accidentally. Loading checks the actual controls and canonical `f` values. These fixtures never load or modify user slots.

The Jyuku `edges` selection requires the completed matching ending proof before following unvisited logical options through an ending or natural return. Reused and newly measured pauses remain separate. The Syorei runner records board command and caption mutation times without changing production timers. Direct jumps clear stale input flags only in the private harness. A prior pause was resolved by clearing native `is_stop`; an earlier sound-channel attribution was unproven. Ending flags precede an asynchronous return jump, so the harness waits for the native `s` in title/storyteller before loading another snapshot. The earlier checkpoint race was a harness issue, not evidence of a production timer defect.

Choice coverage is derived from observed menu stop lines and selected native controls, never planned source IDs alone. The first-visit family menu at6452 and repeat menu at6471 share two labels/targets. `first-visit` combines the completed ending evidence and completed paths from the earlier exploration, then restores a real repeat-question checkpoint, preserves the prompt, changes only the private read flag and enters the native branch at6412. The flag has only two source references,6424/6530; the fixture checks canonical `f` equality and the one-key `sf` change before saving a separate context-bound checkpoint. The failed `g` fixture emptied the prompt and is excluded from reuse; revision2 preserves it. Empty ranges are not text clipping. This is an explicitly controlled branch-entry check, not a new full playthrough from the opening.

`work/source/qa-jyuku-focused.mjs` prepares focused native entries for the Hello? cue, the hidden-message paper hold and three narrow text frames. Run its `dry-run` capture ID before a new evidence ID. It preserves original timing and audio playback, uses RAM-only native snapshots, compares restored text/canonical state, and restores the private player names afterward. Its new checks require native execution before being treated as evidence. `work/source/refresh-boundary-status.py` updates a separate current disposition report after checking its input hashes; the historical source audit remains unchanged. Its default run only previews the report; `--write` records it.

`work/source/qa-all-ending-list.mjs <new-id> revealed hovers` now targets draft3 and adds real pointer movement over each of the14 group hit areas. It checks the mapped image, native dimensions and clearing on pointer exit while retaining the147-label checks. `work/source/qa-common-credits.mjs <new-id>` observes the unchanged native scroll, checks that all44 reviewed ink rows enter the viewport, captures the seven translated role headings and waits for the natural title return. Both tools have separate `dry-run` plans; neither has native completion evidence yet.

The Summoning Incident builder outlines the proportional font with `fonttools==4.57.0`, pinned in `tools/requirements-art.txt`. Font outlines make each generated SVG independent of an external font lookup. Its final artwork report withdraws an earlier missing-glyph hypothesis after full-detail image inspection confirmed the complete text. Common-art pixel comparisons use the same decoded RGBA representation; they do not claim identity between different JPEG decoders.

`py -3.11 tools/scenario.py inventory --dry-run` reports the known script fields. `verify` validates the source digests and applies the English fragments in memory, preserving script line counts, inline tags, branch targets and other untouched source bytes. Image text, runtime-generated strings, videos, and route-specific layouts have a separate audit in [translation status](translation_status.md).

## Final0.1.22 verification

The delivered preview is `work/output/kiwame-0.1.22`; automated progress is excluded and the user's preview saves are preserved independently of Steam. `qa-common-title-newspaper.mjs` exercises six active title hover groups, normal opening choices and native message hide/show. It excludes the commented-out storyteller title control. `qa-life-pendant-final.mjs` stays before500 and stops at425 after both views. Its initial failed fixtures recorded an idle guard/transient source-array issue without reading protected content. `qa-site-timers-final.mjs` uses original timed command blocks and disposable RAM snapshots. The earlier boot fixture stopped at a normal macro pause; the corrected fixture advances through it. These are harness corrections.

`qa-normal-media-final.mjs` tests a normal launch with the QA environment mute unset. Only the process audio flag silences automated observation; the actual title media stays unmuted at nonzero volume. A temporary muted video element checks native decode/play/three seeks for all16 rebuilt containers. `draft5-component-scope.json` separately proves encoded media/timing equivalence and limits reuse of older route evidence to unchanged components. `prepare-final-0122.py` verifies bound evidence, creates a new output and separately backs up/copies user preview saves; it is intentionally one-shot. All final native reports use unique capture IDs and preserve failed historical evidence.

The main Steam0.1.22 package has no debug runtime. `verify-steam-0122.mjs b` observes normal startup and never selects gameplay or writes a save slot. Its initial attempt connected before jQuery loaded; the corrected observer waits for the engine, continuing the same instance. Final startup, font and music checks pass, then the owned instance closes gracefully. `final-install-audit-0.1.22.json` confirms all main/preview save bytes, both package manifests, ten active archives and a single latest output.

## Life non-graphic adaptation0.1.23

`tools/life_summary.py` previews the61-field mapping by default; `--apply` writes safe English rows and marks the private working rows accordingly. `strip_jp.py` then exports the reviewed English copy. `tools/text_flow.py` classifies the68 original breaks as adapted-summary boundaries; all existing7,806 soft joins remain identical. `tools/ui.py` and the fresh builder install the neutral background, summary metadata and ES5 `life-summary.js`. Its three displayed pages retain native tag indices and paragraph pauses. The Save/Load menu wrappers sanitize view metadata only; raw getSaveData remains unchanged for later saving. The load wrapper sanitizes rendered legacy layers before native mounting and never rewrites the input save object.

`qa-life-summary-0123.mjs` targets final draft3 and compares old/native metadata without rendering original restricted text. It measures the safe compiled summary, backlog and synthetic legacy snapshots. `qa-life-summary-menu-0123.mjs` requires its in-memory fixtures and uses private file slots0/1, never user saves. Run each with `dry-run` first and a unique evidence ID. `qa-inoti-summary-route-0123.mjs` keeps the original blanked-window ED116 regression. The final output excludes every QA *.sav. `promote-summary-0123.py` defaults to read-only checks and explicitly binds reuse of unchanged story-flow code.
