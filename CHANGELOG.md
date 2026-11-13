# Changelog

## 0.8.2 · 2026-11-14

- User requested publication of this build. Release preparation includes the
  completed fixes below and the verified English scrolling-letter movie, with
  full/original and direct 0.8.0/0.8.1 upgrade deltas plus a standalone installer.
  The unapproved portrait-name experiment is excluded. Earlier issued releases
  and the running main Steam installation remain unchanged.

- 2026-11-14: Translated the complete credit roll, including credited names and
  resource providers. Preserved all 44 rows, their attribution groups and source
  positions, with Latin font outlines on a transparent SVG. Backgrounds, music,
  original scroll commands and title-return timing remain unchanged. The user
  approved provisional Latin readings for obscure pen names; six uncertain
  spellings are identified in the [credit review](docs/credits-roll-0.8.2-review.md).
  All 44 rows passed the full native scroll and natural title-return check;
  see the [credit verification](docs/credits-roll-0.8.2-verification.json).
  Staged only; original assets, main Steam files and user saves are unchanged.

- 2026-11-14: Added a 500 ms input delay after story and RPG choice menus finish
  drawing, including restored menus. Early clicks and touches are discarded;
  a mouse press started during the delay cannot select a choice on release.
  Rapid clicking does not extend the delay. The existing drawing/navigation
  guard remains active, and timed battles retain their original deadlines.
  Delay state lives only on runtime elements, preserving save data and script
  positions. Staged with the other local fixes; main Steam remains unchanged.
  Native checks cover ordinary story choices, RPG drawing, rapid clicks, held
  presses, restored menus, both microscope choices and five timed battle menus;
  see the [cooldown verification](docs/choice-input-cooldown-0.8.2-verification.json).

- 2026-11-14: Prepared a full English scrolling-letter preview for the Self-Help
  movie. Reused the reviewed English text, set it in Latin handwriting, and
  matched the original paragraph positions, upward speed and ending fade. A
  motion mask removes the baked Japanese lettering over the original montage;
  the covered pixels are restored from their surroundings in the same frame.
  Original camera movement, scene transitions, duration and audio are retained.
  The final physical book shot keeps its English title caption. Preview only;
  main Steam files, saves and published downloads remain unchanged. Verified
  every video timestamp and original audio packet, plus nine native seek points;
  see the [preview verification](docs/self-help-scroll-0.8.2-preview-verification.json).

- 2026-11-13: Reproduced the Ending List heading reverting to Japanese on
  mouse-out in the old installation. Confirmed the already-staged base-heading
  translation fixes all 16 hover/mouse-out cases across 14 artwork groups and
  three pages, including backward navigation. The 147 ending entries remain
  intact. Added a native pointer regression check; no further production edits
  or Steam installation changes were needed. See the
  [hover verification](docs/ending-list-hover-0.8.2-verification.json).

- 2026-11-13: Fixed "Butmy" to "But my" and removed forced line breaks from
  292 RPG continuations, including both reported comma breaks. The RPG lr macro
  keeps its original click pause while using the reviewed separator. Audited
  all 1,158 RPG lr commands; preserve speaker labels, sentence ends and ritual
  staging. Existing ordinary-r wrapping maps are unchanged. Loaded legacy text
  and slots paused inside the old macro recover in memory without changing save
  files. Native checks cover all three reported passages and old-slot fixtures;
  14,646 parsed orders retain their indices and labels. See the
  [RPG text-flow verification](docs/rpg-text-flow-0.8.2-verification.json).

- 2026-11-13: Replaced the clean vector notebook redraw with an image-generation
  edit using the original cover as its target. The English preview retains the
  textured paper, lotus crest, cloth spine, framing and perspective. A native
  960x690 wrapper embeds the generated PNG unchanged. Lettering was visually
  checked and the asset decoded correctly in the game renderer. Staged only;
  original game art and user saves remain untouched. See the
  [notebook verification](docs/notebook-cover-0.8.2-verification.json).

- 2026-11-13: Matched the game-over effect using measured per-frame deformation
  and shading for each RGB channel. Native Canvas applies the travelling ripple,
  colour separation and fading to English lettering; the resulting GIF retains
  all 78 distinct frames, 50 ms timing and the 3.9-second loop. A side-by-side
  preview compares it with the original. Native playback and title return pass;
  main Steam files remain unchanged. See the
  [effect verification](docs/rpg-game-over-effect-0.8.2-verification.json).

- Fixed sideways English on the first opening page after an ending. The ending
  leaves vertical paragraph formatting behind even after the English state flag
  is reset; the shared English layout now clears that stale paragraph class too.
  It also repairs rendered paragraphs from older saves in memory, preserving the
  existing text, click spans and save files.
  Native ending-to-opening, first-choice and legacy-load checks pass; see the
  [opening layout verification](docs/opening-layout-0.8.2-verification.json).

- Translated the missed RPG game-over image to "And then it was all over...".
  The English GIF uses outlined GenEi Latin glyphs with the original's measured
  motion and colour effects. The unused matching still image is mapped too;
  original assets and ending script timing remain
  intact. Staged with the other fixes while the user continues playing.
  Native checks confirm visible animation, the original two-second hold and a
  normal return to the title; see the
  [game-over verification](docs/rpg-game-over-effect-0.8.2-verification.json).

- Fixed an RPG choice-input race: clicking while an option is still being drawn
  can resolve its target inside the choice macro instead of the story script,
  producing the microscope's missing-label alert. Mouse and touch input now wait
  for the completed menu; timed battle choices remain available during their
  original countdowns. The fix is staged with the Ending List heading.
- Restored the engine reference needed by RPG choice listeners rebuilt when
  loading a save. This prevents an exception after selecting a restored choice;
  saves are loaded normally without changing their stored bytes.
- Native regression checks pass early mouse/touch input, repeated clicks,
  ready and restored choices, the decline branch, and all five timed battle
  menus with their original countdown cancellation. See the
  [input verification](docs/choice-input-0.8.2-verification.json).

- Translated the missed base Ending List heading to Ending List using outlined
  GenEi glyphs over the original background. Both ED.jpg and ed.jpg map to the
  new vector asset. Native checks cover all 147 entries across three pages and
  forward/back navigation; zero pixels outside the header rectangle change.
- The user chose to keep playing, so the verified header fix is staged under
  work/debug/ending-list-header-0.8.2-staged. Main Steam files and saves remain
  untouched. Portrait-name layout approval is separate and not included in it.

- Audited eight RPG portrait variants: seven contain embedded Japanese labels;
  one Arai portrait is intentionally unnamed. Prepared an isolated native UI
  comparison using horizontal English nameplates, with Me/Me?, Sadao Hino,
  Shoji Arai and Reiko Fukuzawa as the proposed labels. Original PNGs stay intact.
- At the user's request, show the layout preview before applying the fix.
  Main Steam files and saves are unchanged; no release has been created.

## 0.8.1 · 2026-11-12 · Retro Trans Tools integration

- Added an optional standalone installer ZIP with Apply.cmd, Undo.cmd, the
  verified published full delta, bundled decoder and notices. It installs the
  identical English executable without Retro Trans Tools. Its separate checksum
  preserves every previously published asset and canonical Tools checksum.
  Windows PowerShell 5.1 checks pass installation, no-op reapplication, undo with
  newer progress, corrupted-payload rejection and the old-Undo/new-Apply upgrade
  path. The bundled full Xdelta 3.2.0 decoder supports the issued delta's LZMA.
  The downloaded public ZIP and every member checksum match the tested package;
  catalog recheck 43184390496 passes and both live Automatic routes remain
  available. See [standalone verification](docs/standalone-v0.8.1-verification.json).

- Published after Tools 0.5.23. All six public assets match their checked hashes;
  catalog workflow 43181567788 succeeded. Actual public full and upgrade downloads
  produce the same verified executable, and already-current recognition passes.
  [Publication verification](docs/release-v0.8.1-verification.json) records the
  immutable asset hashes and route results. Main Steam remains untouched at 0.8.0.

- Prepared a schema-3 combined-source full patch and an ordinary incremental
  upgrade from the public 0.8.0 executable for Retro Trans Tools 0.5.23. Both
  produce the same verified embedded target; the only game-content change is
  the title-screen version credit. The user explicitly approved pushing and
  publishing Tools 0.5.23 followed by this game release.
- Full delta: 162,330,751 bytes; 0.8.0 upgrade: 246,802 bytes. All 2,009 package
  files were compared, both deltas passed decode round trips, and the actual
  Automatic full/upgrade paths and current-version recognition passed locally.
- Native startup verifies the 0.8.1 credit, proportional font, production-only
  runtime and advancing title music. Main Steam files and user saves are
  untouched. Existing 0.8.0 public downloads and tag remain unchanged.

## Repository documentation · 2026-11-12

- Updated the README and the published v0.8.0 release title and notes to use the full game name: Apathy - Gakkou de Atta Kowai Hanashi - Kiwame.

## Repository artwork · 2026-11-12

- Updated the social preview to display the full title, Apathy - Gakkou de Atta Kowai Hanashi - Kiwame, and saved a separate 1280×640 JPEG below 1 MB.
- Created the Apathy Kiwame GitHub social preview in the requested retro-trans style and exported a 1280×640 JPEG below 1 MB for upload.

## 0.8.0 · 2026-11-12 · first public release

- Published the cumulative English patch and tools as `retro-trans/Apathy-Kiwame`, with the README organized after the SRW-Z project template and this game's actual coverage and limitations.
- Updated the title-screen credit to `v0.8.0`. All translation, artwork, audio, rendering and non-graphic adaptation content is unchanged from verified0.1.24.
- Added a standalone Windows 64-bit patch ZIP for the original Japanese Steam build 10331351. It validates both original inputs, applies a binary delta to a staged executable, verifies every output, retains the original backup and preserves current saves. Undo restores the exact original executable without rolling back progress.
- Preserved unchanged compressed game records in the private build, verified all 2,009 production package files and an exact whole-executable delta decode round trip. Release downloads contain only the delta, patcher, decoder, notices and player instructions; no prepatched game, Japanese script dump, QA runtime or saves.
- Checked native startup, version credit, proportional font and normal audio from the actual installer output. Installation/undo save checks and corrupted-payload rejection pass, including Windows' built-in PowerShell5.1. English exports were regenerated with `strip_jp.py` and verified byte-identical before committing; private source data and game files remain ignored.

## 0.1.24 · 2026-11-12

- Added bottom-right title-screen branding: the current patch version above `github.com/retro-trans`, matching the user's placement reference. The footer sits beside the Official Site button and preserves the original copyright.
- The credit uses the bundled Latin font, follows the title screen's scale, remains visible over hover artwork and hides in gameplay. It accepts no pointer input and stays outside native saved layers. Fresh builds take its version from the central build version.
- Existing generated artwork styles, scenarios, Life adaptation, audio and prior runtime files are unchanged. Local and main Steam deployment preserve user saves independently; no public release is created.
- Verified in the installed Steam title screen. Both main and preview saves remain byte-identical; `work/ui/final-install-audit-0.1.24.json` records final package/save checks. The owned verification instance is closed.

## 0.1.23 · 2026-11-12

- Replaced the61 user-retained Life fields with a clearly labelled, three-page non-graphic English summary. Preserved the marked cabin, mistaken expectation in darkness, unwanted contact, panic, demands to stop, threat and escape. Used the existing neutral black background.
- Preserved all native order names/line positions, non-text commands, canonical story flags and the surrounding English. Suppressed58 placeholder text slots and redundant internal breaks/pauses so only the three summary pages enter the display/backlog.
- Old scene saves are sanitized in memory before rendering, including old menu titles/thumbnails and the transition into the aftermath. Save/Load menu views leave stored slot data untouched; a real private-save test confirms saving one slot preserves an unrelated legacy slot.
- Native tests pass all three pages, three new-page loads, three synthetic legacy loads, transition boundaries, actual Save/Load menus and Skip/Auto. The affectedED116 path reaches its expected ending with210 measured pauses and no clipping. All unrelated package content remains byte-identical to0.1.22.
- User save preservation, rollback archive and main Steam installation are recorded in the final deployment evidence. No public release was requested.
- Installed0.1.23 in main Steam; normal production startup confirms the summary module, English interface/font and music with no debug runtime. Final audit confirms all main and preview saves are byte-identical and only0.1.23 remains in output. Verification instance closed gracefully.

## 0.1.22 · 2026-11-12

- Installed in the main Steam game with all existing saves byte-identical. Normal production startup verifies the English menu, proportional font and advancing unmuted music; debug tools are absent from Steam. The previous package and original stock backup remain available for rollback.

- Completed the local translation:36,145 reviewed English fields, all147 ending titles, remaining graphics and runtime display text. Preserved the user's61-field Japanese exception;140 remaining inventory entries are blank layout. Retained the proportional GenEi font, natural English wrapping, readable backlog and normal-launch audio.
- Final native checks pass all147 revealed/locked labels,14 Ending List hovers, six active title hovers, the complete credit scroll and the opening newspaper. Both pendant views pass hide/show and RAM save/load. Focused Site tests retain the original eight-second reveal under Skip/Auto and verify loading, early/late choices and a choice after reveal.
- A normal launch verifies unmuted advancing music and native decode/play/seek for all16 rebuilt English videos. Encoded video content/timing matches reviewed clips;472 original media files are unchanged. The user confirmed the stamp is a sound effect and both safe ambient tracks contain no understandable words, so no unsupported dialogue captions were added.
- Packaged a verified0.1.22 preview with every0.1.21 user save preserved byte for byte and automated progress excluded. Verified33 reverse Xdelta files and78 removals for rollback; kept ten active archives. No public release was created.


- All eight Summoning Incident choice paths reach their five expected ending codes, with 5,758 newly measured pauses and no clipping. The true ending enters the original 60-second credits sequence; a separate observation records its natural title return after the earlier harness's 45-second limit. Caption timing logs exposed a 55–105ms gap between the nominal timer and native image completion. Captions now start at the following native wait; Cat starts after its final coin frame and clears after the existing black fade. No source waits or image lettering change.
- Eight focused board cases pass with native completion ordering, all six answers, normal/skip cases, bounds checks and post-clear RAM save/load. The native Save button is blocked during answer holds; Load remains available during waits. A real private-slot Load-menu test reproduced an old scene timer advancing the loaded page. The compatibility layer now cancels that pending wait when loading a nonwaiting saved scene. The same real-menu test then keeps the loaded page idle beyond the abandoned timer's deadline. Main/preview user saves remain untouched.
- The user reports no understandable words in the two full-duration ambience listening copies. Separate-channel local recognition adds 20 windows across all four original channels; all 17 hypotheses have invalid out-of-window endpoints. No speech caption is inferred, and both original stereo tracks remain unchanged.

- All 25 cram-school ending codes pass 26 native paths, including both dispatches of the shared ending. The run measures 3,972 new dialogue pauses without clipping, verifies each actual ending jump and flag, and reaches the native title/storyteller stop after every path. Reused checkpoint pauses are recorded separately. The remaining 27 logical choices are being followed through their scenes; these results do not yet certify every branch context or timed interaction.
- Extended the private route checker to explore unvisited native options from hash-bound menu checkpoints. Added command/caption clock observations for the Summoning Incident board; its timing results remain pending. No production files or user saves changed for these tools.
- Reconciled the earlier source-boundary findings with the current combined candidate. Engine strings, remaining ending displays and planned artwork are implemented; native interaction limits stay explicit. All ten active references to the five legacy RPG ending values remain confined to the dormant script, with no literal incoming scenario reference. The ending macro overwrites supplied text from its name lookup. Internal values and dormant routing remain untouched. Added a dry-run-first focused checker for the cram-school voice cue, hidden paper timer and maximum-name narrow-frame save/load; its native results remain pending.
- Extended the Ending List checker for all14 native pointer hover groups in combined draft3. Added a credits checker for all44 reviewed ink rows during the original60-second hold/80-second scroll command, with no timing changes. Both pass syntax/plan checks; native execution remains pending while the choice-path job owns the debugger. Prepared a1.8-second, hash-bound WAV of the safe stamp effect for user listening clarification; no speech caption was guessed.
- The user confirmed the stamp clip is a chime/sound effect. Its original audio remains unchanged, with no invented speech subtitle. A fresh local preview was rebuilt from guarded original Steam archives:1,992 of2,008 package files are byte-identical to the native-tested candidate; the16 different WebM containers have identical encoded packet data, timing and stream parameters. All seven runtime files also match. The fresh build contains no user/QA saves and remains staged privately pending final checks.
- Corrected branch coverage to use the observed native menu stop, option and target rather than planned source IDs. The repeated family question shares two labels/targets with its first-visit menu; warm-state ending tests therefore did not cover the three first-visit fields. The ending-code/dispatch results remain valid. A controlled native branch-entry fixture changes only the private read flag, preserves its existing question and canonical route variables, and checks the first-visit choices. The first fixture cleared the question and exposed an empty-text bounds false alarm; it is retained as failed evidence and excluded from reuse. No production text or logic changed for these harness corrections.
- All77 cram-school logical choices across28 menus now have actual native selection evidence. Combined e/f/h evidence records8,224 new measurements, including one controlled first-visit bootstrap; inherited checkpoint counts remain separate. The three first-visit answers reach native outcomes and the repeat-question flow. Focused timing, maximum-name frames and ordinary save/load checks continue.
- Focused cram-school checks now pass: the source5023 Hello? caption follows the original2.323605-second clip through native time advancement and natural completion, then clears; the hidden-message paper hold measures3,004ms; and three narrow frames pass21 measured pauses and native RAM save/load with12+12-character player names. The first direct-jump fixture lacked a required character, so the corrected checker restores verified native scene context before entry. No production scripts, timers or user saves were changed for these checks.

- Added a native branch runner with verified menu checkpoints, canonical route-variable comparisons and separate initial-story contexts. It records actual ending jumps as well as ending flags, and waits for the native title/storyteller return before restoring a checkpoint. A direct test jump inherited a native stop flag; clearing only that flag restored normal clicking. Its earlier attribution to sound-channel testing was not established. These are isolated test-harness corrections, with no production-script changes.

- Completed all remaining ordinary scenario drafts and exported 36,145 reviewed display fields. Added all 147 ending titles in both displays, replaced 147 locked-title bars with Latin hyphens, and classified 140 blank HTML fields as nonlinguistic layout. The user’s 61 retained Life fields remain unchanged. These counts do not cover every image or runtime-generated word.
- Life now reaches all 13 ending codes, both random locker outcomes, and a maximum-name second-riddle failure: 15 runs measured 2,982 dialogue pauses without clipping. Frozen phase-one inputs preserve the exact hashes behind this evidence before the combined candidate changes.
- Fixed stale sound captions when a native sound channel is reused for an uncaptioned clip. Native regression checks cover all three Life cues, ordinary-load cleanup and channel replacement. Added the independently reviewed, unattributed “Hello?” cue for cram school; its native verification is pending.
- Integrated the English startup window title and five directly visible engine error formats with exact source guards, preserving project/save identifiers and control flow. Added display-only sports/games/girls mapping for the cram-school hobby variable; saved branch values remain unchanged. Native checks remain.
- Coordinated five cram-school script fields with the English misspelled warning prop. The instructor now claims to use easy phonetic spellings while misspelling easy words. The Japanese kanji/hiragana distinction is documented as an adaptation tradeoff.
- Preparing a separate combined debug candidate with all reviewed scripts, ending titles, natural line-flow maps and remaining horizontal choice layouts. Artwork and full route verification remain in progress; Steam and the delivered preview remain 0.1.21.
- The first combined-candidate Revenge Site run reaches ED056 with 463 measured pauses and no clipping. All 147 revealed ending labels and all 147 locked labels fit across the native three-page Ending List. Timed alternatives and remaining route checks continue.
- Original native expression/loader baselines confirm three further source faults. Exact repairs join the malformed cram-school OR operator, point its footprints scene to the existing PNG, and point the Summoning Incident static cue to the existing noise file. Only those three command lines change; source line counts remain intact.
- All four Revenge Site endings now pass native runs, measuring 2,286 pauses without clipping. The no-input first decision takes 8,052ms in the observed native run; the final delayed-choice path is recorded separately. All three opening choices were exercised across these runs.
- Completed seven cram-school artwork fixtures. Original stamp colors and all 7,065 protected Accept-button pixels match exactly. Remaining clipping-edge differences intersect the approved lettering geometry; no pixels wholly outside that geometry changed. Actual story timing remains pending.
- Added a complete English startup notice with a native click-to-continue pause, replacing only its former 1,500ms reading window. The other startup waits remain intact; actual startup verification is pending in the next combined candidate.
- Built combined draft3 with all reviewed scripts, 31 Summoning Incident graphics, seven cram-school graphics and 29 common-art mappings. Static reproduction matches every generated asset and all six new/revised scenario files; 472 original sound, music and video files remain byte-identical.
- Native draft3 checks pass the complete startup pause/title sequence, all 182 new fresh/visited choice variants and 35,331 dialogue/backlog break commands across 29 scenarios. The 7,806 continuous-English wraps agree in dialogue and backlog and each break advances exactly once. A dynamic-name continuation exposed a fixture assumption, which was corrected without changing production text.
- Rechecked all eight retained-range punctuation boundaries in draft3 without displaying retained content. Life's three native speech captions, ordinary-load cleanup and channel reuse also pass in this build. All three canonical hobby values display as sports/games/girls while their branch-state values remain unchanged. Actual old-slot and narrative-path checks remain separate.

- Merged Life's 3,203 reviewed English fields and 3,298 fragments privately. The user requested that the identified passage remain Japanese; all 61 original fields, including its closing fragment, are byte-identical. A metadata-only locator records the exception. Life is not included in 0.1.21.
- Integrated Life's 3,203 English fields and 13 ending titles into an isolated 0.1.22 candidate. All 113 translated Ending List titles pass native text-bound checks. The delivered preview and Steam installation remain 0.1.21 pending complete route checks.
- Added eight English Life graphics. Native lettering fixtures preserve 3,204,490 protected rendered pixels with zero changes. Generated clean plates and exact prompts are recorded; Michiru Furushiba's surname reading remains provisional. Actual title/portrait/hover interactions and the audio-caption audit remain.
- Prepared the Revenge Site glossary with 15 terms and verified existing cast references. Translation proceeds in separately reviewed 80-field slices. Preserve its eight-second decisions, delayed escape choice and source count discrepancies.
- Completed Revenge Site's private draft: 1,453 fields and 1,552 fragments, all 18 joins independently reviewed. Native integration, timed-choice checks and two text-bearing graphics remain.
- Confirmed seven narrow Life grid repairs, correct/wrong answers and retry behavior. A separate original save-state fault now has an English-gated snapshot helper. Native English saves restore the initial clue page, confirmation layout and completed selections; a partial board loads after another attempt and completes the correct branch. The natural cave lead-in also reaches the adapted puzzles and readable clue page.
- Fixed punctuation preservation when loading the retained Japanese passage. Native loading mutates the saved line metadata while restoring layers; the English runtime now decides whether to preserve punctuation before that mutation. Eight synthetic boundary checks pass without reading, displaying or capturing the retained passage.
- Verified 23,291 native break commands across 24 translated scenarios, including 5,159 natural continuations. Each advances exactly once and dialogue/backlog spacing agrees. The 68 commands inside the retained-original scene were excluded before fixture rendering.
- Completed Perfect Score Cram School's private draft: 5,779 fields and 5,893 fragments across 73 slices. Independent review covered all 72 joins and six overlapping drafts, applying 12 exact corrections. All 10,766 source lines remain intact. Its glossary has 53 entries, and the embedded-quotation continuation at1975 has a guarded flow override ready for integration. Graphics, menus, ending titles and native route checks remain.
- The Summoning Incident has a reviewed 59-entry glossary and a fresh 3,358-field source reference; translation is underway. Phone artwork, board captions and typing jokes require coordinated adaptation.
- Added English captions to Life's two faint help calls and the overlapping tape promise. Native checks verify all three captions, unchanged audio durations, natural playback completion, fit above the controls and cleanup on ordinary loading. Source notes and local ASR agree on the spoken words; a hallucinated phrase in the noisy first tape was rejected. Other audio remains under audit.
- Completed six Life ending routes (ED114, ED115 and ED117–120), measuring 1,368 pauses without clipping. All 102 fresh/visited choice variants fit in 36 native fixtures. A test restart exposed that RAM snapshots omit global sound/music aliases; the helpers now complete normal startup before loading fixtures. The corrected ED120 run passes. Remaining endings, alternatives and actual artwork interactions are still pending.
- Drafted the two English Revenge Site images with clipped clean plates. Native visual checks found no remaining original title lettering, and 1,215,983 pixels outside the approved lettering rectangles remain identical. Original monitor, cursor, outer splatter and reflections are preserved. Built-in image generation mode, exact prompts and project-local clean plates are recorded. Story integration and timed-choice checks remain.

## 0.1.21 · 2026-11-11 · local preview

- Added all 3,472 reviewed Hosoda fields and 3,638 English fragments, plus 16 ending titles in both displays. The English corpus now contains 22,108 fields and 100 ending titles. All 44 slices passed accuracy, editorial and proofreading review; independent checks covered the main agent's drafts, all 43 slice joins and exact quiz wording. The 6,843 physical source lines and commands remain intact.
- Reached all 16 endings and completed four lead-in/alternate runs, measuring 4,089 pauses without clipping. All 136 visited/unvisited choice variants and 100 ending-list labels fit. A maximum-name run saved and restored the narrow dialogue panel with identical text and background.
- Added Latin name-challenge input with the opening's 12-character limit, wider fields and canonical-name normalization. Actual typing passed default, maximum-length and wrong-answer cases while retaining the native comparison and branch outcomes.
- Localized three photographed letters and the soldier title card, resolving the first title card's malformed path through the visual map. Audited 58 direct images and ten indirect backgrounds, including all 80 abstract animation frames. Native comparison found zero changes across 778,607 protected pixels. Two generated blank-paper textures and exact prompts are recorded in the artwork provenance file. Kashima, Isamu Hidaka and Eiko Hoshikawa remain explicitly provisional readings.
- Added 850 natural sentence continuations. The native engine checked all 19,894 audited break commands, including 4,443 soft wraps, with exactly one advance each and no errors. Preserved all 442 original music/sound files and all 15,027 packets across the 16 reviewed videos.
- Updated the main Steam game with its current save unchanged and its original runtime, official patch and original backup intact. Retained the previous installed package for rollback. Preserved both preview saves separately and excluded QA progress. Eight verified reverse Xdelta patches restore 0.1.20; ten active archives cover 0.1.11–0.1.20. Only 0.1.21 remains in `work/output`; superseded files remain in the existing debug holding area. No public release was created.

## 0.1.20 · 2026-11-11 · local preview

- Applied the verified build to the user's main Steam installation on request. Kept Steam's own save unchanged, backed up the original executable and publisher patch, retained the original application identity, and excluded the QA runtime. Verified the installed English title menu and normal, unmuted music playback. Source extraction continues using the verified original archives in the backup.
- Audited all 18,604 translated fields across 22 script files for inherited hard line breaks. Replaced 3,593 sentence-continuation breaks across 14 files with natural wrapping; preserved 12,610 speaker, paragraph, sentence-end, staging, and other intentional breaks. Kept translation wording, source rows, script commands, and click pauses unchanged.
- Fixed the reported email passage, its narration, and backlog entry. The native game checked all 16,203 audited break commands and advanced exactly once for each. Reviewed name labels, embedded quotations, capitalized continuations, and split punctuation; hyphens and ellipses join without an extra space.
- Loading an older slot now reflows matching existing text immediately. A native snapshot made with the old hard-break layout restored with all four unnecessary breaks removed from the reported passage. The two opening replays measured 437 pauses without clipping.
- The close-up regression passed another 94 pauses with maximum-length names and native save/load. Preserved both user save files byte for byte. Three verified reverse Xdelta patches restore 0.1.19; the ten active archives now cover 0.1.10–0.1.19. Only 0.1.20 remains in `work/output`; superseded files are held under `work/debug` following the previously recorded deletion-policy rejection. No public release was created.

## 0.1.19 · 2026-11-11 · local preview

- Fixed opening dialogue running below the text area: the reported hallway page now includes the final reply, with its bottom at y=551 against a y=637 limit. Default and maximum-length names passed 272 measured opening pauses without clipping.
- Installed the requested GenEi Latin font with its original license and verified its proportional glyph widths in the native renderer. English dialogue and ending labels now use ASCII ellipses. Restored line breaks and word separation in the backlog, improved its contrast, and verified scrolling and closing it.
- Fixed the debug helper forcing every launch silent. Muting now applies only when the QA launcher requests it; the title and opening music play normally when that flag is absent. Native checks confirmed advancing playback, nonzero volume, and no decoding errors in both tracks.
- Added all 1,933 reviewed fields and 2,030 fragments of Reiko Fukuzawa's water and social-media stories, plus eight ending titles. The preview now contains 18,604 proofread English fields. Added the verified glossary, seven horizontal menu layouts, compact dialogue for the close-ups, and six localized graphics for the phone, title card, and principal's-office sign.
- Corrected the original clinic-background spelling through the visual map. Completed native runs reached all eight endings. Four route runs with the corrected typography measured 1,296 pauses without clipping; native save/load restored the ant close-up, all 38 choice variants and 84 English Ending List entries fit, and all 341,176 protected artwork pixels matched the originals.
- Preserved account handles and photo clues. The original CG2 cropped message retains a clipped English verb ending; CG3–4's inconsistent account labels are documented rather than swapped. Incidental blurred signs remain indistinct.
- Loading an older slot now reapplies the compact layout immediately. The user's existing opening slot passed 21 pauses through the reported hallway page. Preserved both current user save files byte for byte, including slot data, and kept QA progress separately. Carried forward the 16 reviewed videos with 15,027 matching audio/video packets.
- Verified 26 reverse Xdelta patches and nine asset removals to restore 0.1.18. Only 0.1.19 remains in `work/output`; the ten active archives cover 0.1.9 through 0.1.18. The previous full preview and oldest delta are held under `work/debug`, following the earlier deletion-policy rejection. No public release was created.

## 0.1.18 · 2026-11-11 · local preview

- Added all 1,902 reviewed fields and 1,938 English fragments of Akemi Iwashita's corridor and shared-diary stories, plus seven ending titles in both displays. The preview contains 16,655 reviewed English fields.
- Added the Iwashita glossary, horizontal layouts for all 23 choice menus, and compact English dialogue for the two narrow close-ups. All 102 visited/unvisited choice variants fit. Preserved the original diary, letter, and close-up images after checking for readable lettering.
- Reviewed all 24 script slices for accuracy, clarity, voice, and proofreading. Preserved the borrowed player name, unresolved Sano/Nakata identity, and the distinction between a class log and a shared diary. Recorded the apparent source typo at line 3116 and retained the original control logic where comments describe unimplemented behavior.
- Reached all seven endings across nine completed route checks, with 1,455 measured dialogue pauses and no clipping. Maximum-length names fit through the diary ending, native save/load restored the hands close-up, and all 76 translated Ending List entries fit. The fresh build matches the reviewed route scripts and layout files.
- Preserved the existing save byte for byte and carried forward all 16 reviewed videos after matching 15,027 regenerated audio/video packets. Six verified reverse Xdelta patches restore 0.1.17. The ten active archives cover 0.1.8 through 0.1.17; the superseded full preview and oldest delta are held separately under `work/debug`, following the earlier deletion-policy rejection.

## 0.1.17 · 2026-11-11 · local preview

- Added all 1,654 reviewed fields and 1,713 English fragments of Nozomu Kazama's Kokkuri-san route, plus 15 ending titles. The preview contains 14,739 reviewed English fields.
- Added Latin readings to 39 ritual-board frames and 72 timed English answers. Preserved the coin positions, the missing syllables in the burned-paper clue, the Tama/Shii joke, and the incomplete Red She… phrase. Added horizontal layouts for all 31 choice menus and visual breaks after four original speaker labels.
- Played from the opening through the ten-yen detour, the five-hundred-yen reading, and ED025. Focused replays covered all 15 ending codes, the timed choice, three other ten-yen topics, and both default and maximum-length player names. The 22 completed runs measured 1,408 dialogue pauses without clipping.
- Verified all 31 menu layouts and 39 board assets. Coin-center comparison matched 146,414 original pixels. All 69 translated Ending List entries fit. The timed choice advanced after 9.98 seconds, and native save/load restored the English dialogue and annotated background at an ordinary dialogue pause.
- Preserved the existing save and all 16 previously reviewed videos. Seven verified reverse Xdelta patches and 39 asset removals restore 0.1.16. The ten active rollback archives cover 0.1.7 through 0.1.16. The previous full preview and older delta are in separate debug holding folders following the recorded deletion-policy rejection.

## 0.1.16 · 2026-11-11 · local preview

- Added all 1,639 reviewed fields of Shoji Arai's rooftop route and the ED013–020 titles in both displays. The preview contains 13,055 reviewed English fields.
- Added the Arai glossary, English handwriting for both note shots, compact dialogue for the narrow artwork scenes, and horizontal layouts for all 11 choice menus. Preserved the original branch destinations, read-history flags, and random branch probabilities.
- Localized Settings, both mute-button states, the text-speed preview, and Controls. The guide follows the active keyboard and mouse bindings.
- Played from the opening into ED013, ED014, and ED018. Six focused replays covered ED015–017, ED019–020, and the family branch. The nine runs measured 1,329 dialogue pauses without clipping. All eight new Ending List entries fit, and the settings controls and text-speed sample worked through their native controls.
- Preserved the existing save. Seven verified reverse Xdelta patches and ten asset removals restore 0.1.15. The ten active archives cover 0.1.6 through 0.1.15. Filesystem policy blocked recursive deletion, so the previous full preview and the oldest delta are held separately under `work/debug`.

## 0.1.15 · 2026-11-11 · local preview

- Added all 1,785 reviewed fields of Makoto Shindo's playing-card route and the titles for ED002–012 in both displays. The preview contains 11,399 reviewed English fields.
- Localized the storyteller heading, all six names and their hover and completed states, and the three-card prompt. Preserved the eight-second transition into The Game Streamer's Ghost Story.
- Added the remaining 128 timed English chat messages and English lettering to stream clips 5–16. Preserved the clue coordinates, original audio packets, frame counts, silhouette, and closing effect. Localized the dialogue and buttons embedded in the final clip.
- Played from the normal opening through the card timeout and all 16 stream clips to ED100 and the Arai continuation. Focused replays of ED004 and ED008 checked the narrow dialogue box and the existing school hallway used in place of the missing source path. All 46 translated Ending List entries fit.
- Preserved the existing save and archived 0.1.14 as ten verified reverse Xdelta patches with 38 asset removals. The ten active rollback archives cover 0.1.5 through 0.1.14.

## 0.1.14 · 2026-11-11 · local preview

- Added all 1,815 reviewed fields from The Game Streamer's Ghost Story, Mountains of Madness, and Love's Purgatory. The preview contains 9,592 reviewed English fields.
- Fitted all six choice menus for horizontal English and added ED099, ED100, ED113, and ED145 to the ending animations and Ending List.
- Added 31 English graphics, including the title cards, Majiru's business card, the red clue screens, the mountain maps and HUD, and the animated dating-game interface. The original animations and coordinate values carry through the translated scenes.
- Added 56 English messages and the stream banner to the first four videos. The translated videos preserve the original frame counts and audio packets. English chat timings for the remaining clips are prepared for the next pass.
- Played through the three stories in isolated profiles. The first route reached ED100, ED145, and ED113 across 1,163 dialogue and choice pauses. The alternate route reached ED099, ED145, and ED113 across 1,173 pauses. Both runs had zero measured clipping. All four new Ending List entries fit.
- Preserved the existing save and archived 0.1.13 as seven verified reverse Xdelta patches with 35 asset removals. The ten active rollback archives cover 0.1.4 through 0.1.13.

## 0.1.13 · 2026-11-11 · local preview

- Added the remaining 531 battle fields, 378 Fukuzawa fields, 173 exploration-event fields, and eight more ending titles in both displays. The preview contains 7,769 reviewed English fields.
- Added English artwork for the five-years-later card, faculty office sign, and intact mirror. Restored the blank reflection shot by mapping its missing path to the matching window image in the original package.
- Replayed the final fish scene with two twelve-character player names. The repaired image and English menu rendered, ED147 unlocked, and its English title appeared in the Ending List. All 59 measured stops fit in the focused replay.
- Played the Fukuzawa route from the opening through the Broken Mop and Strange Device choices to ED144. Tightened two overflowing pages and replayed the final fight with 184 measured stops and no clipping.
- Fitted all 20 lines of the madness chant and used Georgia to render the accented glyphs. Verified the eight new ending titles in their native animations and the 31 translated entries across all three Ending List pages.
- Carried forward the existing save. Archived 0.1.12 as nine verified reverse Xdelta patches with three asset removals. Moved 0.1.2 into debug holding to retain ten active rollback archives.
- Completed reviewed drafts for all 1,815 fields in `game.ks`. Prepared the title artwork and Majiru's business card for the next build.

## 0.1.12 · 2026-11-11 · local preview

- Added the first 560 battle fields, all 31 battle hints, and the English animation and Ending List titles for ED132–133. The build now includes 6,671 reviewed English fields.
- Verified the Holy Water and possession endings, the timed Shoggoth victory, and Arai's opening combat actions. The four focused runs measured 525 dialogue and choice stops without clipping. Later scenes used isolated progression states after normal initialization.
- Preserved the three-, four-, and five-second battle timers. Corrected an English sentence boundary that the engine's physical-line trimming joined together.
- Rechecked three revised hints through native calls and returns, including their red emphasis. Stressed the Arai dialogue with twelve-character player names.
- Carried forward the existing save. Archived 0.1.11 as six verified reverse Xdelta patches. The active archive contains ten versions, with the oldest delta moved into reversible debug holding.
- Completed reviewed drafts for the remaining 531 battle fields and prepared the later time card, faculty office sign, and intact mirror artwork. Mazaka's full-name romanization remains provisional.

## 0.1.11 · 2026-11-11 · local preview

- Added the remaining 565 exploration fields and the English titles for ED137–139. The build now includes all 1,445 fields in the exploration script and 6,076 reviewed English fields overall.
- Localized all three microscope descriptions while preserving the game's branch values. Added the full-screen Holy Water recipe and corrected the matching notebook copy to “rite of consecration.”
- Verified the gate and forest routes through the blackboard puzzle, the turn limit ending, and Holy Water crafting. Measured 216 dialogue and choice stops without clipping in the focused checks.
- Carried forward the existing save. Archived 0.1.10 as seven verified reverse Xdelta patches with one asset removal and moved the oldest delta out of the ten-version active archive.
- Drafted the first 560 battle script fields and all 31 battle hints.

## 0.1.10 · 2026-11-11 · local preview

- Added 880 reviewed old school building exploration fields and the English titles for ED134–136. The build now includes 5,505 reviewed English fields.
- Localized the Yoshino and Somei envelopes, the Somei notebook inset, both mirror backgrounds, and the music-room chart.
- Verified the cherry-tree photo hotspot and the tape clue using the original 8-, 2-, and 4-minute choices. Corrected the displayed number on both copies of the third time choice.
- Played the entrance from the normal opening and used isolated progression states for the later checks. Verified all three ending unlocks and 247 measured dialogue and choice stops without clipping.
- Carried forward the existing save. Archived 0.1.9 as six verified reverse Xdelta patches with five asset removals.
- Drafted the remaining 565 exploration fields and the separate full-screen Holy Water recipe.

## 0.1.9 · 2026-11-11 · local preview

- Added the final 374 cafeteria fields and localized the animation and Ending List titles for ED068–070. All 2,702 cafeteria script fields are now in English.
- Kept the final branches horizontal and fitted the English dialogue beside the Bavarois Cat door. The original door already carries the name in Latin lettering.
- Playtested the three endings from the opening and measured 2,292 dialogue stops without clipping. Verified the ten-second timeout and the returning player's password in separate runs.
- Carried forward the existing save and archived 0.1.8 as five verified reverse Xdelta patches.
- Drafted 800 more exploration fields for the old school building and English artwork for the envelope clues, mirror signs, and music chart.

## 0.1.8 · 2026-11-11 · local preview

- Added 637 reviewed cafeteria fields through ED067 and localized the animation and Ending List titles for ED065–067. The build contains 4,239 reviewed English fields.
- Fitted the four- and five-option menus and localized the timed password menu, ED065 intertitle, and “30 years later” card.
- Unlocked all three endings from the opening and measured 2,191 dialogue stops without clipping. Replayed ED062 to check the news captions and ED065 to check the revised intertitle.
- Carried forward the existing save and archived 0.1.7 as seven verified reverse Xdelta patches with two asset removals.
- Drafted the final 374 cafeteria fields through ED070 and added glossary entries for the new characters, Bavarois Cat, and the okuri-inu.

## 0.1.7 · 2026-11-11 · local preview

- Added 473 reviewed cafeteria fields covering the paths to ED062, ED063, and ED064. Localized each ending title in the animation and Ending List.
- Translated the two additional choice screens and fitted the English dialogue to the narrow illustration panel on the shared branch.
- Translated the ED062 broadcast headline and report with timed lettering over the original footage.
- Playtested all three paths and verified the ending unlocks and Ending List entries. Carried forward the existing save and archived 0.1.6 as verified reverse Xdelta patches.
- Drafted the next 407 cafeteria fields and the ED065 intertitle. Added glossary entries for the Nyarinians, Sunbaralians, and Mazaka.

## 0.1.6 · 2026-11-11 · local preview

- Added 1,218 reviewed fields of “Human Flesh Cafeteria” through ED061, “The Star of Dinner,” and localized both displays of that ending title.
- Added the cafeteria title card and two horizontal choice screens with five options total. Kept the narrow illustration panel within the game window.
- Played from the opening through the ED061 animation and measured 922 dialogue stops with no clipping.
- Verified the unlocked ED061 Ending List entry in a separate test. Carried forward the existing save and archived 0.1.5 as verified reverse Xdelta patches.
- Drafted 400 more cafeteria fields beyond ED061, including the paths to ED062 and ED063, and an English subtitle draft for the ED062 news segment.

## 0.1.5 · 2026-11-11 · local preview

- Added all 137 reviewed notebook and map fields, bringing the build to 1,897 reviewed English fields.
- Localized the floor plan, gear list and recipe, poem, five rumors, three research memos, the Yoshino and Somei photo captions, and the Holy Water note.
- Added the English Return to Map label and dark outlines around the RPG controls for contrast on light notebook pages.
- Tested notebook navigation, clues, Holy Water acquisition, and return to the story. Carried forward the existing save and archived 0.1.4 as verified reverse Xdelta patches.
- Drafted the first 960 fields of “Human Flesh Cafeteria,” its title card, and glossary entries for Aim and Yukihito Ayanokoji.
- Drafted the first 80 fields of the old school building exploration script and identified the envelope graphic that carries the Yoshino clue.

## 0.1.4 · 2026-11-11 · local preview

- Added all 163 reviewed fields of the old school building introduction, including nine choices, and five shared interface fields.
- Localized both old school building title cards, the Field Notes cover and tooltip, six RPG controls, the two status panels, and 23 location labels.
- Playtested the three branches from the normal opening through their handoffs to the rooftop, entrance, and notebook map. Checked 354 dialogue stops for clipping.
- Carried forward the existing save and archived 0.1.3 as verified reverse Xdelta patches.
- Drafted all 137 notebook and map script fields, the floor plan and equipment page graphics, and the first 480 fields of “Human Flesh Cafeteria.”

## 0.1.3 · 2026-11-11 · local preview

- Added all 526 reviewed fields of “Burying the Lie,” its two English title cards, and both script displays of ED060.
- Kept the burial route horizontal after the ending macro and tightened the route’s dialogue layout to fit its longer pages.
- Played the burial route from the opening to ED060 and checked 385 dialogue stops for clipping. Carried forward the existing save and archived 0.1.2 as verified reverse Xdelta patches.
- Added 131 RPG choice fields to the scenario inventory, bringing it to 36,346 fields. The build includes 1,592 reviewed English fields.
- Drafted the 163-field old school building introduction and the first 160 fields of “Human Flesh Cafeteria.”

## 0.1.2 · 2026-11-11 · local preview

- Added all 414 reviewed fields in the self-help scenario and localized its choice layout, both title cards, and the two script displays of ED071–073.
- Added 25 timed English captions for the self-help cutscene, including the letter and the final book-cover reveal.
- Restored horizontal dialogue after the self-help ending macro resets the game's writing direction.
- Completed first drafts for all 526 fields of “Burying the Lie” and recorded the route's names and terminology.

## 0.1.1 · 2026-11-11 · local preview

- Completed the opening scenario's 602 extractable fields, including its routes into the self-help story, the old school building, the storyteller selection, and the first ending.
- Translated the 40-field old school building prologue and both script displays of the first ending title, “It Ends Today.”
- Added 147 runtime ending titles to the translation inventory. Added glossary entries for the wall newspaper, the self-help book, the manhood pun, and the old school building route title.
- Laid out the final opening choice horizontally and retained the previous build as verified reverse Xdelta patches.

## 0.1.0 · 2026-11-11 · local preview

- Added an isolated Windows test build for Steam build `10331351` that merges the publisher's bundled update before applying English changes.
- Added a sourced glossary for the core cast, the school, and recurring Newspaper Club terms.
- Used the game's existing proportional font with horizontal English dialogue, adjusted tracking and line spacing, and added horizontal choice buttons for three opening choice screens.
- Translated 138 opening script fields and added English name entry, title menu buttons, dialogue controls, and common menu labels.
- Added local debugger controls, screenshots, trace and state inspection, text preview, scene jumps, and guarded scenario reload.
- Inventoried 36,068 extractable fields across 41 scenarios and generated offline machine references. The test build reads the reviewed English files only.
