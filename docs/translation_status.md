# English translation status

## Current public release: 0.8.2

Published on 2026-11-14 after the user's explicit release request. The original
combined-source patch and direct upgrades from public English 0.8.0 and 0.8.1
produce the same 2,014-file embedded package. A standalone Apply.cmd ZIP uses
the same full delta. The shared Tools catalog recognizes 0.8.2 as Latest.

This update adds a 500 ms choice input delay, RPG choice-race protection,
pause-aware English flow/spacing and legacy-save display repairs, horizontal
opening text, the Ending List mouse-out fix, original-style English game-over
animation, an improved notebook cover, the complete Latin credit roll, and the
English scrolling letter over original footage/audio. Six credited spellings
remain provisional with user approval; the Life adaptation is unchanged.
The portrait-name experiment is excluded. Main Steam files and saves remain
unchanged by publication. See [release notes](RELEASE-v0.8.2.md) and
[verification](release-v0.8.2-verification.json).

## First public release:0.8.0

Version0.8.0 publishes the cumulative translation under `retro-trans/Apathy-Kiwame`, with a standalone Windows patch for the original Japanese Steam build10331351. It changes only version metadata from verified0.1.24. All content coverage below still applies:36,145 ordinary translated fields,61 adapted source fields,140 blank layout entries and no unknown inventory gaps.

The binary release uses both original files as its verified source. Its embedded target has2,009 verified package files and no QA runtime. Exact delta decoding, native startup/font/audio/title credit, source/payload checks, save preservation and undo were tested on an isolated copy, including Windows PowerShell5.1. The download contains the delta, installer/decoder and notices, not the prepatched game. `docs/release-v0.8.0.json` records supported input and target hashes.

Historical development versions and their notes follow. AI review passes are not counted as complete human proofreading; wider playtesting and human corrections remain welcome.

## Earlier local builds

## Current build:0.1.24

The title screen now shows `v0.1.24` above `github.com/retro-trans` at the bottom right, beside the original Official Site control. It uses the bundled Latin font, stays visible over title hover artwork, hides in gameplay and reappears without duplication on return. The footer accepts no pointer input and is outside native saved layers. Fresh builds take the version from `tools/steam_game.py`.

Only title-credit styling, metadata and loader wiring differ from verified0.1.23. All scenarios, the Life non-graphic adaptation, original media and earlier runtimes are byte-identical; existing generated artwork CSS is preserved verbatim after the new scoped rules. `work/ui/title-credit-0.1.24-b.json` records native bounds and transitions. Local and Steam package/save verification are recorded in the0.1.24 proof files. The0.1.23 content coverage below still applies.

## Previous content update

## Content coverage inherited from0.1.23

The61 previously retained Japanese fields in Life have been replaced, at the user's request, with a clearly labelled three-page non-graphic English summary. It preserves Moriyama's expectation on entering the marked cabin, his mistaken assumption in the darkness, unwanted contact, panic, demands to stop, threat and escape. The other person's identity/gender is not invented. The summary uses a neutral black background and rejoins the existing English aftermath.

Coverage is36,145 translated fields plus61 adapted source fields, with140 blank HTML layout entries: all36,346 known fields are accounted for, with zero retained-Japanese scenario fields and zero unknown gaps. The61 adapted fields comprise three displayed summaries and58 invisible runtime-suppressed placeholders retaining native save positions. They are not61 individual literal translations.

Native checks confirm the original order names/line positions, exactly three clean pages/backlog entries, new-page save/load, synthetic legacy-save sanitization before rendering, old title/thumbnail suppression in menus only, actual file-backed Save/Load and preservation of an unrelated old slot. Skip and Auto both traverse the three pages and rejoin3456. The affectedED116 route reaches its expected ending with210 measured pauses and no clipping. Scope and final hashes are recorded in `work/ui/verified_0.1.23.json`; unrelated content is byte-identical to verified0.1.22.

The local preview is `work/output/kiwame-0.1.23`. Preview saves and main Steam saves were preserved separately, byte for byte; automated QA progress is excluded. Four verified reverse Xdelta files plus one removal restore0.1.22, with ten active rollback archives. Steam installation is recorded in `work/ui/steam-install-0.1.23.json`. No public release was requested.

Normal installed startup verifies the production summary module, three pages, legacy-load coverage through3454, proportional Latin font and advancing unmuted music. Both main save files remain byte-identical after verification. `work/ui/final-install-audit-0.1.23.json` also checks both package manifests and preview saves. The owned verification instance is closed; launch through Steam normally.

## Historical0.1.22 and earlier status

The preserved-Japanese decision and pending checks below belong to their named versions and are superseded by0.1.23 where applicable.

## Current Steam installation and local preview: 0.1.22

All ordinary scenario text is translated and reviewed: 36,145 English fields in29 exports. All36,346 inventoried fields are accounted for:61 Life fields remain original Japanese at the user's request, and140 entries are blank HTML layout. All147 ending titles and147 locked placeholders are in English/Latin typography. The glossary, GenEi proportional font and debug tools are included. No public release has been requested.

The final candidate passed native checks for all25 cram-school endings (26 paths), all5 Summoning Incident endings (8 paths), all4 Revenge Site endings and all13 Life ending codes. Cram-school coverage includes all77 logical choices; focused checks cover maximum-name narrow frames, audio and paper timing. These are route/component checks, not every combination of story flags.

All147 revealed and147 locked Ending List labels fit;14 real pointer hovers and the six active title hovers work. The original storyteller title control is commented out. All44 credit rows enter the viewport before the natural title return. Normal opening choices reach the translated newspaper, whose native hide/show preserves position. Both Life pendant views preserve their images/text through native hide/show and RAM save/load.

The native flow matrix covers35,331 commands and7,806 natural continuations, with matching backlog spacing and one advance per command. All61 retained fields stay byte-identical and their68 break commands are excluded from fixtures. All472 original media files remain unchanged. The two safe ambience tracks and stamp effect require no extra speech captions based on source review and the user's listening responses; no claim is made of human audition of every music file.

Final timing checks cover all six completion-bound board answers, original holds/black fade, native Save/Load availability and post-clear restoration. A real private-slot test reproduced and fixed an abandoned wait callback advancing a loaded page. Revenge Site also passes8.5-second load/choice cancellation checks, early/late selection, the original8-second reveal under Skip/Auto and an original choice after the third appears. Normal-launch title music advances unmuted at nonzero volume; all16 rebuilt English videos pass native decode/play/seek checks and have identical encoded content/timing to reviewed media.

`work/ui/verified_0.1.22.json` binds the delivered preview and evidence. Every preview save was copied byte for byte from0.1.21, independently of Steam saves; automated QA progress was excluded. Only0.1.22 remains under `work/output`;33 verified reverse Xdelta files and78 removals restore0.1.21, with ten active rollback archives. Steam is also updated to0.1.22. Its normal startup reaches the English title with no debug script, a proportional KiwameLatin font and unmuted advancing music. Both main saves remain byte-identical after that check; Steam and preview saves were preserved independently. Deployment and final checks are recorded in `work/ui/steam-install-0.1.22.json`, `work/ui/steam-0.1.22-startup-b.json` and `work/ui/final-install-audit-0.1.22.json`. The verification instance was closed gracefully, so Steam can launch the game normally.

## Historical build and candidate notes

The notes below describe the versions named in each paragraph. The current status above supersedes their pending-check lists.

| Area | Status in local 0.1.21 |
| --- | --- |
| Scenario text | 22,108 proofread fields out of 36,346 known fields across 41 scenarios. Includes the opening, self-help route, burial route, Human Flesh Cafeteria, Makoto Shindo's playing-card route, Shoji Arai's rooftop route, Nozomu Kazama's Kokkuri-san route, Akemi Iwashita's corridor and shared-diary stories, Reiko Fukuzawa's water and social-media stories, Tomoharu Hosoda's Sambra tea and soldier stories, the three stories in `game.ks`, and the old school building routes and events. |
| Choices | Opening, self-help, cafeteria, Shindo, Arai, Kazama, Iwashita, Fukuzawa, Hosoda, the three game stories, and old school building choices and combat menus |
| Interface | Title menu labels, Settings, Controls, name entry and confirmation, dialogue buttons, common engine menus, the storyteller menu, Shindo's card prompt, RPG status panels, 23 old school building location labels, and the notebook pages and controls |
| Endings | 100 English titles in both script displays for ED001–055, ED060–073, ED099–100, ED106–113, and ED127–147. The runtime title inventory includes all 147 endings. |
| Cutscenes | English title cards and translated cutscene lettering for the covered routes, including Arai's handwritten note, Kazama's 39 annotated board frames and 72 timed answers, six Fukuzawa graphics, 31 game-story graphics, and all 16 streamer videos with 184 timed chat messages. |
| Glossary | Core cast and terms plus dedicated files for the self-help, burial, old school building, cafeteria, Shindo, Arai, Kazama, Iwashita, Fukuzawa, game streamer, Mountains of Madness, and Love's Purgatory routes. |
| Font | Bundled GenEi LateGo P v2 for proportional English dialogue, backlog, and horizontal choices, with its original license. Compact pages use 22px text and 27px line height, including restored older slots. English script ellipses use ASCII `...`; sentence continuations wrap naturally instead of retaining Japanese layout breaks. The madness chant retains Georgia. |
| Offline references | 36,068 draft field records, including 100 with an empty fragment. Drafts mistranslate names and lose context around scripted line breaks. Kept separately under `work/source/drafts/10331351`. |

The extractor inventories prose, speaker labels, known display-tag parameters, and the runtime ending-title table. The RPG audit added 131 choices displayed through the game's custom choice macro. The remaining audit includes other RPG text produced by script code, the title-screen logo and credit, story-specific graphics, and text in videos. The translated opening still needs English lettering for the newspaper masthead and feature headline in `op/壁新聞.jpg`. The Japanese scenario labels, paths, flags and nonvisual variables stay in the locally rebuilt game because it uses them to navigate and save.

Hosoda's complete route is included in the preview and main Steam game at 0.1.21. Sixteen ending runs and four additional routes measured 4,089 pauses without clipping. All 136 choice variants, 100 ending-list labels, Latin name input, artwork and narrow-panel save/load passed. The native line-break matrix checked all 19,894 commands. Review notes and explicitly provisional name readings are in `docs/hosoda_review.md`.

The isolated Life phase-one candidate contains 3,203 reviewed English fields and 113 ending titles. It reaches all 13 Life ending codes, both random locker outcomes and a maximum-name second-riddle failure: 15 runs measured 2,982 pauses without clipping. All 102 choice variants, eight graphic fixtures, natural cave lead-in, clue/confirmation save/load, three speech captions, load cleanup and channel reuse pass their focused checks. At the user's request, 61 fields remain byte-identical original Japanese, identified only by locators. Its evidence and inputs are frozen under `work/debug/inoti-candidate1-verification-inputs`; the combined candidate requires new evidence for changed files. Pendant and Ending List interactions and unvisited alternative dialogue remain to be checked. Neither candidate is installed over 0.1.21.

All ordinary scenario drafts are reviewed and exported: Revenge Site has 1,453 fields, Perfect Score Cram School has 5,779, and The Summoning Incident has 3,358. Independent reviews cover all their slice joins and the cram-school overlapping drafts. Current exports contain 36,145 fields, including all 147 revealed ending titles in both displays and 147 Latin locked-title placeholders. Of the 36,346 inventoried fields, the remaining 201 consist of 61 user-retained Life fields and 140 blank HTML layout fields. The whole-game audit also identified the startup window title, five engine error formats, a dynamically displayed hobby and remaining photographic lettering. These are being integrated and checked in a separate combined candidate. Menus, timed decisions, artwork, audio and ending routes still require native verification; field completion alone does not establish full translation.

Combined draft3 now includes those exports, all remaining planned photographic lettering and 29 common-art mappings. Its English startup notice stays readable until clicked, and normal initialization reaches the English title menu. All 182 new choice variants and 35,331 break commands pass native checks; the latter includes 7,806 natural wraps with matching backlog spacing. The three hobby values display in English without changing their canonical branch state. Life's retained-range punctuation guards, three speech captions, load cleanup and sound-channel reuse pass again. Static reproduction matches the generated assets, and 472 original media files remain byte-identical. The combined build is still private: full cram-school/Summoning Incident routes, timed-answer and other interaction checks, save/load, production audio, final packaging and the closed-game Steam update remain.

The cram-school ending proof now reaches all25 codes through26 native paths, including both ED079 dispatches, and measures3,972 new pauses without clipping. Additional logical choices are undergoing native exploration; inherited checkpoint measurements remain separate. The updated boundary dispositions are in `work/source/whole-game-boundary-status-current.json`. They account for the implemented engine/title/artwork findings and classify the five dormant RPG values without changing canonical save state.

A fresh local preview is staged at `work/debug/kiwame-0.1.22-preview-stage1`. Its1,992 nonvideo package files and all seven runtime files match the tested combined candidate byte for byte. The16 rebuilt English WebM containers differ, but all encoded packet contents, order, timestamps, duration and stream parameters match. `work/ui/fresh-preview-stage1-summary.json` binds the comparison evidence. This does not certify the pending normal-audio launch, user-save preservation, final packaging or Steam upgrade. The user listened to the safe stamp effect and confirmed it is a chime/sound effect, so no speech subtitle is added.

## Opening review

Accuracy review covered all 138 translated fields. An independent check covered the first 80 consecutive fields and read into the neighboring branches. It caught Asahina's club role (`102`), the permission to speak up (`113`), Hino's choice of Sakagami (`134–135`), the narrator's uncertainty (`197`), Hino's appeal to seniority (`225–226`), the transition into the next branch (`245`), and the distinction between the favor and the pitch meeting (`264–265`). The third first-screen choice (`161`, `163`) keeps the person who learned the secret unspecified. Hino's seniority is carried through the register and narration. The English release uses given-name-first full names, while the entry screen preserves the original order of the family and given name fields.

The editorial pass checked character voice across the first scene and its continuations. It kept Hino's pigeon comparison (`290–291`) and replaced a repeated explanation of risk with a sentence that continues across the two existing text segments (`302–303`). Proofreading checked the revised wording, glossary spelling, all 138 field IDs, inline substitutions and repeated choices against the English build input.

In-game QA followed the opening through the first choice and selected “Sure. What is it?” to reach the wall-newspaper choice. The resulting screenshots and measured control bounds are in `work/ui`. The active opening scenario reloaded at its first choice with the same 2,049 interpreter orders.

For 0.1.1, translators worked through the remaining 464 opening fields in contiguous slices, checked the speaker and branch context, and preserved every inline fragment. Accuracy fixes include Kurata's first mention of an unnamed visitor (`764–765`), the `[l]` pause in Kazama's rebuke (`1085`), and Hino's ambiguous final line (`1181`, `1183`) which echoes ED001. The editorial pass kept Hino's stutter (`461–464`), differentiated the storytellers' voices, and retained the bawdy double meaning in Hino's “manhood” joke (`394–396`). Shindo speaks for the group when he says they went to look at the paper (`913–914`). Their arrival together supports that reading. Proofreading checked matching dialogue quotation marks across the merged slices and both variants of each choice.

The 40-field RPG prologue keeps the contrast between Hino's confidence about the daytime visit and his fear of entering after dark. All opening and prologue fields were exported from the bilingual working files with the source digests and fragment counts verified.

Playtesting reached the self-help route, the old school building prologue, and the storyteller choice through the opening's normal controls. The 218-character demolition passage fit with the preceding lines on-screen. A separate jump to ED001 verified the English ending animation. The complete path from the storyteller choice to the ending still needs a confirmed playthrough. `work/ui/verified_0.1.1.json` identifies the captures.

The previous preview's save was copied byte for byte into 0.1.1. Six verified reverse Xdelta patches under `work/patches/kiwame-0.1.0` restore the older build from 0.1.1. The older test folder was moved out of `work/output` into `work/debug/retired-0.1.0`.

## Self-help route review

Accuracy, editorial, and proofreading passes covered all 414 fields and their neighboring context. Revisions preserve the difference between what Sakagami observes and what he infers about Hino (`91`, `99`), the daydream's three timed fragments (`288`), the book's recurring “nothing” motif (`363–369`, `397–398`, `523`), and the specific person Hino means in the last branch (`863`). The compiled script retains all 465 fragments and 910 source lines. Pohe stays ungendered and the route glossary records provisional spellings where the source lacks a confirmed Latin form.

The video track keeps the handwritten letter and book-cover art visible with English captions. The adaptation from “self-help” to “self-harm” carries the Japanese wordplay into the title reveal and ED071. In-game checks reached the route through the normal opening choice, verified the title card and two horizontal choices, and confirmed that the long page at `104` fit. The game loaded all 25 video captions and showed the first letter caption and last book-cover caption at their respective timestamps.

Playtesting advanced past the movie into the continuation at `761`. Separate debug jumps verified the ED071, ED072, and ED073 animations. A continuous playthrough into both alternate final endings remains to be verified. `work/ui/verified_0.1.2.json` identifies the captures.

The 0.1.1 save was copied and checked byte for byte. Seven verified reverse Xdelta patches under `work/patches/kiwame-0.1.1` and the manifest's three asset removals restore the older preview from 0.1.2. The older test folder was moved out of `work/output` into `work/debug/retired-0.1.1`.

## Burial route review

Accuracy, editorial review, and proofreading covered all 526 fields of “Burying the Lie” (`maisou.ks`). The English script preserves all 559 fragments and 986 physical lines. The review clarified why Kurata suspects Kawano (`134–135`), specified the coffin's viewing window (`380`), kept the uncertainty around the movement of an eyelid (`429`), and checked speaker attribution and Hino's change in register in the mortuary (`438–449`). The glossary records the reading Takashi Kawano and distinguishes the mortuary, funeral hall, and crematorium. The English title cards retain the cross and headstone motif and the red accent on the second card.

The playthrough started at the game's title screen, took the third opening choice, and reached ED060. The first pass found 32 stops with text taller than the message area. The route now uses the native proportional font at 22 pixels with tighter line spacing. The final pass measured 385 dialogue stops with no clipping. The tallest page measured 562 pixels in a 627-pixel message area. `work/ui/verified_0.1.3.json` identifies the captures.

The 0.1.2 save was copied and checked byte for byte. Seven verified reverse Xdelta patches under `work/patches/kiwame-0.1.2` and the manifest's two asset removals restore the older preview from 0.1.3. The older test folder was moved out of `work/output` into `work/debug/retired-0.1.2`.

## Old school building introduction review

Accuracy, editorial review, and proofreading covered all 163 fields of `rpg/rpg00.ks` and all five display fields in the shared RPG macro. The renderer preserves 187 introduction fragments and 595 physical lines. Hino explains that one key on Iwayama's ring should open anything on campus (`81–85`). The first choice prompt now leads naturally into three past-tense options (`114–118`). The translation preserves the interruption around Hino's name (`245`), the uncertain figure in the camera (`250–254`), and the embedded player name on the Field Notes acquisition message (`500`).

Both route title cards, the Field Notes cover, the six RPG buttons, and all 23 location labels have English assets. The status panels retain the original icons and use English names and `HP` labels. The player panel formats the saved given and family names for display. Room labels use `1F`, `2F`, and `3F` to keep floor information in the original image bounds.

Three playthroughs entered through the normal opening and took each of the three exterior choices. The photo branch reached the rooftop scene, the wait branch reached the entrance, and the search branch reached the notebook map. All 354 measured dialogue stops fit, including waits inside the RPG line-break macro. The smallest measured margin above the bottom edge was 21 pixels. `work/ui/verified_0.1.4.json` identifies the captures and choice bounds.

The 0.1.3 save was copied and checked byte for byte. Five verified reverse Xdelta patches under `work/patches/kiwame-0.1.3` and the manifest's 38 asset removals restore 0.1.3 from 0.1.4. The older test folder was moved out of `work/output` into `work/debug/retired-0.1.3`.

## Old school building notebook review

Accuracy, editorial review, and proofreading covered all 137 fields of `rpg/map.ks`. The compiled script preserves 165 fragments, 1,027 source lines, and all control tags. The character dialogue keeps Yoshino and Somei separate until Hino joins them (`117–121`). The five rumors refer to physical locations arranged in a pentagram (`189`). The cursed tape's melody still comes from the western sky (`621`). The short incantation at `910` keeps Sakagami's stumbles, while the Holy Water graphic uses the full incantation. The phrase after the incantation on that graphic is rendered as “rite of parting.”

The notebook pages use English lettering over the original diagram or blank ruled pages. The rumor headings and notes sit over their original interactive regions. The photo annotations keep the photographs and the research memo keeps the three original musical notes, which are part of a later puzzle. The poem uses Erich Zann's surname and the Shining Trapezohedron spelling from Lovecraft's texts. [The Music of Erich Zann](https://www.hplovecraft.com/writings/texts/fiction/mez.aspx) · [The Haunter of the Dark](https://www.hplovecraft.com/writings/texts/fiction/hd.aspx)

The playtest opened the notebook from the normal photo branch and clicked the recipe and poem. Later pages used progression flags set in the isolated test copy. The test found all five rumor hotspots, opened the Devil's Melody reply, obtained Holy Water, and closed the notebook to resume the story. Separate in-game checks confirmed the revised spacing on the rumor page and Holy Water note. `work/ui/verified_0.1.5.json` records the captures and clickable bounds.

The 0.1.4 save was copied and checked byte for byte. Fifteen verified reverse Xdelta patches under `work/patches/kiwame-0.1.4` and the manifest's 12 asset removals restore 0.1.4 from 0.1.5. The older test folder was moved out of `work/output` into `work/debug/retired-0.1.4`.

## Human Flesh Cafeteria review

Accuracy review, editorial review, and proofreading covered the first 1,218 fields of `jinniku.ks`, through the ED061 jump. The renderer preserves 1,274 fragments and the 5,042-line script structure. The 10 choice fields include the two display variants of each of five choices. The review kept Pohe's sex unspecified, distinguished the male calico reveal from earlier dialogue, and kept Sakagami's initial misunderstanding of Aim. “You're the star today” appears at `1012` and `1951` to echo “The Star of Dinner.” The ending title uses the same wording in the animation and Ending List.

The first ED061 playthrough entered the cafeteria by declining twice in the opening. Both choice screens appeared horizontally, and the normal choices reached the ending animation. All 922 measured dialogue stops fit. The tallest page reached 562 pixels in a 627-pixel message area. The narrow illustration panel measured 247 pixels wide with a 10-pixel left offset, and its final page reached 156 pixels. The other choice destinations lead to branches still in translation.

The first pass sampled the ending flag before the five-second animation finished. A separate in-game test ran the ED061 sequence through the unlock and verified “ED061: The Star of Dinner” on the second Ending List page. `work/ui/verified_0.1.6.json` records the captures, choice bounds, and panel measurement.

The 0.1.5 save was copied and checked byte for byte. Six verified reverse Xdelta patches under `work/patches/kiwame-0.1.5` and the manifest's one asset removal restore 0.1.5 from 0.1.6. The older test folder was moved out of `work/output` into `work/debug/retired-0.1.5`.

For 0.1.7, accuracy review, editorial review, and proofreading covered 473 more fields. The English script now covers 1,691 fields and 1,771 fragments through ED064. The render check compared the original and compiled scripts and found all control tags and non-text arguments intact. The fake newspaper headline and its accusation stay distinct from Sakagami's hypothetical headline. The Cat Man's verdict (`2745`) echoes “Eaten with Relish.” ED064 uses the wording of the game's player-facing title table.

Playtests declined the meal, then took the revenge, press, and investigation branches through ED062, ED063, and ED064. The runs measured 2,043 dialogue stops, counting the shared opening in each run. None clipped. The shared narrow panel at `2218` used 243 of its 627 available vertical pixels. Both videos played and all three endings unlocked and appeared in English on the second Ending List page.

The ED062 news clip uses the original footage and a timed overlay that covers the Japanese headline and report. An isolated replay of the ED062 branch verified both caption changes, the removal of the overlay at the end, and the return to the Ending List. `work/ui/verified_0.1.7.json` records the captures and bounds.

The 0.1.6 save was copied and checked byte for byte. Seven verified reverse Xdelta patches under `work/patches/kiwame-0.1.6` and the manifest's one asset removal restore 0.1.6 from 0.1.7. The older test folder was moved out of `work/output` into `work/debug/retired-0.1.6`.

For 0.1.8, accuracy review, editorial review, and proofreading covered another 637 cafeteria fields. The compiled script has 2,328 translated fields and 2,429 translated fragments across the original 5,042 lines. The glossary records Reo Togashi and Genzo Kuroki using the readings given in the game. The timed password uses the same words in dialogue and on the menu. Its first-time and repeat destinations and its original ten-second timeout remain distinct in the script.

Normal playthroughs unlocked ED065, ED066, and ED067 and verified each title in the animation and Ending List. The three runs measured 2,191 dialogue stops without clipping, including the shared sections. The four-option alien menu and five-option suspect menu fit above the dialogue controls. The timed menu accepted the first-time password and the “30 years later” card appeared in English. The repeat and timeout branches lead into the remaining cafeteria material.

A repeat playthrough of ED062 verified all three news cues after the shared caption code changed. The first ED065 run showed the new intertitle, but its black backing covered part of the fading planet. A separate scene replay verified the narrower backing during the fade and title hold, its removal at the end, and the return to the Ending List. `work/ui/verified_0.1.8.json` records the captures and bounds.

The 0.1.7 save was copied and checked byte for byte. Seven verified reverse Xdelta patches under `work/patches/kiwame-0.1.7` and the manifest's two asset removals restore 0.1.7 from 0.1.8. The older test folder was moved out of `work/output` into `work/debug/retired-0.1.7`.

For 0.1.9, accuracy review, editorial review, and proofreading covered the final 374 cafeteria fields. The compiled script now has all 2,702 fields and 2,814 fragments across the original 5,042 lines. The ending titles use “Cannibal Buddies,” “At the Famed Bavarois Cat,” and “We Are the Okuri-inu.” The door art already spells out Bavarois Cat. The final branch keeps the identity and sex of the white Shiba Inu unspecified.

Three runs from the opening unlocked ED068, ED069, and ED070 and verified their English animation and Ending List titles. The runs measured 2,292 dialogue stops with no clipping. The narrow panel beside the door measured 287 pixels wide and used 330 of its 627 available vertical pixels. The long menu description at `4701` used 272 pixels in the full-width panel. ED068's normal run let the ten-second password timer expire. A separate replay initialized the route with the repeat-choice flag set and selected the same password as ED067. The game took the ED068 branch immediately. `work/ui/verified_0.1.9.json` records the captures and measurements.

The 0.1.8 save was copied and checked byte for byte. Five verified reverse Xdelta patches under `work/patches/kiwame-0.1.8` restore 0.1.8 from 0.1.9. The older test folder was moved out of `work/output` into `work/debug/retired-0.1.8`.

## Old school building exploration review

Accuracy review, editorial review, and proofreading covered the first 880 of 1,445 exploration fields (`rpg/stage.ks`). The compiled script preserves 1,018 English fragments and all non-display arguments across the original 5,115 lines. The Yoshino and Somei artwork keeps the two names distinct, and the notebook includes the localized Somei inset. The mirror signs keep the original panels and the music chart keeps its original symbols and coordinates.

The normal entrance playthrough reached the shoe lockers and opened the Yoshino envelope. An isolated test set the later progression flags and reached the Somei envelope from Room 3-A's locker hotspot, selected the cherry-tree photo, and opened the corresponding notebook inset. The music-room test used the original half-, quarter-, and eighth-note hotspots, selected the Zann cassette, and read the translated clue in the original 8-, 2-, and 4-minute order. Both copies of the misnumbered third choice display “3. 8 minutes in.” The game's vignette still covers part of the chart's right-hand reference column, outside the three interactive rows.

Three ending checks entered through the normal opening and used isolated progression states to reach the later events. The exit, mirror, and cassette choices unlocked “Nightfall,” “The Last Light,” and “The Devil's Melody” and showed the corresponding entries on the third Ending List page. The focused tests measured 247 dialogue and choice stops without clipping. `work/ui/verified_0.1.10.json` records the captures, bounds, and scope of the checks.

The 0.1.9 save was copied and checked byte for byte. Six verified reverse Xdelta patches under `work/patches/kiwame-0.1.9` and the manifest's five asset removals restore 0.1.9 from 0.1.10. The older test folder was moved out of `work/output` into `work/debug/retired-0.1.9`.

For 0.1.11, accuracy review, editorial review, and proofreading covered the final 565 exploration fields. The full 1,445-field script renders across 5,115 lines with 1,670 translated fragments. The microscope uses English text for the three displayed values, while the original keys still govern the lens and blackboard branches. The full-screen Holy Water insert uses the same instructions as the notebook copy, with “rite of consecration” for the handwritten `聖別の儀`.

The four focused checks entered through the normal opening and set later progression flags in isolated copies. The three magnification choices displayed the expected English views while retaining their original branch values. Drawing the pentagram and using the microscope unlocked “Lost Time” through the gate and “Dreamworld Tour” through the forest. The science lab model consumed the last turn and unlocked “The Silver Key Beyond Time and Space.” The library and notebook both displayed the translated recipe, and the native crafting control granted Holy Water. The checks measured 216 dialogue and choice stops without clipping. `work/ui/verified_0.1.11.json` records the scope, bounds, and captures.

The 0.1.10 save was copied and checked byte for byte. Seven verified reverse Xdelta patches under `work/patches/kiwame-0.1.10` and one asset removal restore 0.1.10 from 0.1.11. The older test folder was moved to `work/debug/retired-0.1.10`. The active archive contains ten versions. The oldest delta is held separately at `work/debug/retired-patch-0.1.0` after filesystem policy blocked deletion.

## Old school building battle review

Accuracy review, editorial review, and proofreading covered the first 560 of 1,091 battle fields (`rpg/batoru.ks`), with 699 English fragments across the original 3,440 lines. All 31 battle hints (`rpg/comment.ks`) are translated across 55 fragments, preserving the 13 red highlight spans and the original 113 lines. An independent review checked every hint and all twelve caller groups. Three wording corrections were then verified through native calls and returns in an isolated fixture.

Four focused runs initialized through the normal opening and set later progression flags in isolated copies. The Hino fight closed Sakagami's eyes three times and verified the native menu change, Holy Water use, ED133 unlock, and English Ending List entry. The possession path verified the giant KILL overlay, the red hint, ED132 unlock, and English Ending List entry. The Shoggoth run used all five timed menus, verified the unchanged three-, four-, and five-second limits, consumed the 500-yen coin, won with the spray, and returned to exploration. The Arai check used twelve-character family and given names, cast Flesh Ward, contacted Mazaka, verified the native HP restoration and removal of the consumed contact option, then threw the field notes and reached the third combat turn.

The four runs measured 525 dialogue and choice stops without clipping. Their tightest pages reached 633 pixels against the 654-pixel control boundary. The three corrected hint checks reached 609 pixels or less. The parser trims spaces between physical script lines, so a narrow runtime adjustment restores the English sentence boundary at battle line 1540. A clean replay verified the rendered space. `work/ui/verified_0.1.12.json` records the scope, bounds, timers, and captures. Mazaka's full-name spelling, “Mazaka Reteranikasennisehi Muzonno,” is a provisional romanization.

The 0.1.11 save was copied and checked byte for byte. Six verified reverse Xdelta patches under `work/patches/kiwame-0.1.11` restore 0.1.11 from 0.1.12. The previous full output is held at `work/debug/retired-0.1.11`. The active delta archive contains ten versions, 0.1.2 through 0.1.11. The older 0.1.0 and 0.1.1 deltas remain in separate reversible debug holding after filesystem policy blocked deletion.

## Late battle and Fukuzawa review

Version 0.1.13 contains all 1,091 battle fields and 1,304 fragments across the original 3,440 lines. It also contains all 378 Fukuzawa fields and 173 optional event fields, which render with 494 and 222 English fragments across the original 1,428 and 576 lines. Accuracy review, editorial review, and proofreading preceded the English-only exports.

The five-years-later card, faculty office sign, and intact mirror appeared in their ending scenes. The build maps the missing reflection path to the matching window image in the original package. The ED147 replay verified the restored image and English sign, the space between twelve-character player names, the second fish-speech option, and the ending unlock. It measured 59 stops without clipping. `work/ui/verified_0.1.13-fish.json` records the comparison and Ending List entry.

The Fukuzawa playthrough took the native choices from the opening through ED144, with driver resumptions at existing stops. It checked the Dream of Doom blackboard clue, the first-floor restroom, the two Stalker encounters, the Broken Mop and the Strange Device. Two pages reached 666 pixels against the 654-pixel dialogue limit. The edited pages fit in a 184-stop replay of the entrance fight and final sequence. The tightened blade and device descriptions retain the original action and imagery.

The Arai madness replay measured 146 dialogue and choice stops without clipping. The chant spans 20 lines at a 32-pixel pitch, with its final line ending at y682 on the 690-pixel canvas. Georgia renders the accented letters that were blank in the first run. Focused scenes verified ED130 and ED140–143. ED143 inherits the RPG message settings from the preceding fight, so its replay restores the RPG spacing before measuring. All 31 translated Ending List entries fit their columns across the three pages, including eight titles that wrap onto two lines. `work/ui/verified_0.1.13.json` records the runs, bounds, and captures.

The 0.1.12 save was copied and checked byte for byte. Nine verified reverse Xdelta patches and three asset removals restore 0.1.12 from 0.1.13. The ten active archives cover 0.1.3 through 0.1.12. The older deltas are held under `work/debug`.

Ruberaize is a provisional romanization. The glossary distinguishes the Occult Society from the Occult Club and records the source references for the recurring room, curse, and yokai names.

The source battle script has several logic inconsistencies that are retained during translation. These include the flash flag, Resurrection's equality expressions, hint dispatch and ordering, a locker/desk mismatch, and literal Sakagami names in otherwise customizable-name dialogue. The optional events compare Classroom 3-C against a differently capitalized ID and use Arai's progression for some Fukuzawa hints. The Fukuzawa mental recovery message is followed by sprite changes without a numeric MP update in that block. These source behaviors need focused checks when the corresponding paths are tested.

## The Game Streamer's Ghost Story, Mountains of Madness, and Love's Purgatory

All 1,815 fields of `game.ks` completed accuracy review, editorial review, and proofreading. All 1,906 English fragments render across the original 4,551 lines with the controls, timings, player-name substitutions, and repeated choice targets preserved. The English-only export is `work/translation/en/game.en.json`.

The static graphics cover both streamer titles, Majiru's business card, the Criminal Kids title, the stream banners and red clue labels, the mountain title, maps, HUD, production credit and newspaper headline, and the Love's Purgatory titles and dating-game screens. The dating overlays keep the source GIFs and cursor animation. The original mountain artwork's blurred upper credits and newspaper body remain in place. The mountain map follows the labels visible in the artwork, including McKinley and Other.

The first four stream clips use the original footage with 56 English messages, the translated banner, and the original audio packets. Frame-by-frame review supplied 184 English chat cues across the 16 clips, including repetitions and messages missing from the scenario notes. Clips 5–16 retain the original Japanese footage in 0.1.14. Draft renders cover the red clue typing, silhouette, closing mask, and embedded dialogue and buttons in clip 16. `work/ui/game-stream-clues.json` and the clip notes record the original coordinates, reveal timings, and effects. The replay checks started at the three-story sequence with isolated progression flags. `work/ui/0.1.14-game-first.json` and `work/ui/0.1.14-game-localized.json` record the routes and layout checks.

The 0.1.14 builder generates the English stream WebM files from the installed Steam footage. This step uses FFmpeg with `drawtext`, `libvpx`, and the Windows Arial Bold font. The prepared preview includes the generated videos and runs from `kiwame.exe`. Seven verified reverse Xdelta patches restore 0.1.13, and the carried-forward save matches the old save byte for byte.

## Makoto Shindo's playing-card route

The accuracy, editorial, and proofreading passes covered 1,785 fields and 1,798 fragments across 3,514 physical lines. All 37 paired choice labels match their corresponding read-history variants. The translation preserves the two choices numbered 2 at lines 410–418 and the original history-flag mismatch at line 1877. `work/glossary/shindo.json` records the verified name readings, the Devil's Deck, the Demon Realm, and the title choice for My Savior. The festival photo has a partly readable stall sign that remains in the visual audit.

The 0.1.15 preview adds 26 graphics for the storyteller menu and card prompt. The normal opening reached the two Shindo playing-card menus and continued into the streamer story through the original eight-second card timeout. It played all 16 English videos, reached the ED100 animation, and continued into Arai's dialogue. The run measured 528 dialogue and choice pauses without clipping. A duplicate screenshot filename stopped the automated driver during the ending, and a follow-up state check confirmed the native transition. The driver now captures each ending once. The evidence is in `work/ui/0.1.15-game-native-entry.json` and `work/ui/0.1.15-game-native-entry-follow-through.json`.

Focused replays checked 79 pauses through ED008 and 60 through ED004 with no clipping. ED008 uses the game's first school hallway image because the script's requested hallway path is absent. ED004 uses the compact English layout for the narrow apparition scene. The storyteller menu and all 46 translated Ending List entries fit in the measured captures. Full playthroughs of the other Shindo branches remain to be checked.

All 16 localized videos match the source frame counts and audio packets. The red labels type in alongside the original changing numbers. The silhouette, closing mask, and final red interruption remain visible, including the transition effects around the localized dialogue. The build regenerates the videos from the Steam assets using FFmpeg and Windows Arial Bold, Consolas Bold, and Georgia. The ready build's decoded videos match the reviewed renders.

The 0.1.14 save was copied and checked byte for byte. Ten verified reverse Xdelta patches under `work/patches/kiwame-0.1.14` and the manifest's 38 asset removals restore the previous preview. The ten active archives cover 0.1.5 through 0.1.14.

## Shoji Arai's rooftop route

The accuracy, editorial, and proofreading passes covered all 1,639 fields of `arai.ks` across its 3,180 physical lines. They preserved the switch between Arai's account and the people he quotes, the delayed names in the rooftop branches, and the ties between the repeated dialogue. The final join review checked the four shared ending speeches that continue into the storyteller epilogues. Hosoda's surname joke uses “narrow field” to carry the wordplay into English. “Dragged Down by Love” (ED018) carries the double meaning of a fatal fall and the possibility of one person taking the other along.

The note has English handwriting in both original shots, with the blur retained in the second. The note and friend scenes use the compact message layout. All 11 choice menus use horizontal labels and retain their original targets and history flags. The source's all-storytellers epilogue checks a different Iwashita flag from the one set by `iwashita.ks`, which can select a fallback epilogue.

Settings keeps the three sliders, music and effects mute states, and the text-speed preview. The Controls guide reflects the game's active keyboard and mouse bindings. The original guide lists a C shortcut whose implementation is commented out.

The opening playthroughs reached ED013, ED014, and ED018. Six focused replays covered ED015–017, ED019–020, and the Kojiyama family scene. The nine completed runs measured 1,329 dialogue pauses without clipping and checked all 11 menus. The two random outcomes were tested by overriding the roll in the isolated QA process. The game scripts retain the original probabilities. All eight Ending List rows fit, including the two-line entry ending at y675. The first direct jumps into the random endings left the QA click layer hidden, so the driver was corrected and the tests rerun. `work/ui/verified_0.1.16.json` records the completed checks and their captures.

The clean builder's 16 regenerated videos matched every audio and video packet, timestamp, duration, and flag in 0.1.15. The ready preview carries forward the existing clip files. The copied save matches the previous preview byte for byte. Seven verified reverse Xdelta patches and ten asset removals restore 0.1.15. The ten active archives cover 0.1.6 through 0.1.15. Recursive deletion was blocked by filesystem policy, so the prior full build and the 0.1.5 delta were moved into separate debug holding folders.

## Nozomu Kazama's Kokkuri-san route

All 1,654 fields and 1,713 fragments completed accuracy review, editorial review, and proofreading. The renderer preserves all 5,907 physical lines and the original controls. The staged Tama/Shii answer keeps the obscene misunderstanding before the soul revelation. The incomplete “Red She…” title and answer lead into the fragmented sheep chant. The unnamed child stays gender-neutral. “Adding Kazama to Injury” carries ED025's proverb substitution, while “Fatso” carries Kazama's deliberately wrong name for Hosoda.

The 39 board frames retain the handwritten Japanese syllabary and add Latin readings at the measured positions. English answers appear after the final coin movement. The five missing readings in the burned-paper clue remain missing, with “I'm coming.” revealed during its original hold. Four original speaker labels run into the following speech without a break, so the English renderer supplies that visual break. The source scripts retain their original tags.

The normal opening reached Kazama, took the ten-yen detour, returned with a five-hundred-yen coin, and completed a reading through ED025. Focused replays covered all 15 ending codes, the timed identity question, the three other ten-yen topics, and the closing line with its missing break. A twelve-character family name and given name fit through the full warning branch. The native snapshot and load path restored the same English dialogue and annotated background at an ordinary dialogue pause, then continued into ED025. The 22 completed runs measured 1,408 dialogue pauses without clipping.

All 31 menu layouts fit through the native parser and choice renderer. All 39 board assets rendered, and 146,414 coin-center pixels matched the original photographs. All 69 translated Ending List entries fit across the three pages. The identity choice advanced automatically after 9.98 seconds. The timed warning retained its 16 inline pauses of 300 milliseconds and both complete English messages. `work/ui/verified_0.1.17.json` records the completed checks.

An early driver omitted the invitation menu and was corrected before the complete replay. The card-capture driver was also corrected to identify endings by code as the animated text changes. The first attempted save fixture took a snapshot during a timed reveal, where the stock Save button is disabled. The unnecessary caption-load hook was removed, and the supported dialogue save/load path passed. The launcher now waits for late child processes when stopping an isolated preview.

Several source effects exist only in comments, including the bucket impact, the burned-name effect, the random monsters at the window, and the ten-yen coin's erratic motion. Their surrounding English dialogue is translated. The actual source branches and asset commands are preserved.

The ready 0.1.17 save matches 0.1.16 byte for byte. All 16 regenerated videos matched the previous 15,027 audio/video packets, timestamps, durations, and flags, and the preview carries forward the existing clip files. Seven verified reverse Xdelta patches and 39 asset removals restore 0.1.16. The ten active archives cover 0.1.7 through 0.1.16. The superseded full preview and oldest delta are held separately under `work/debug` after the earlier deletion-policy rejection.

## Akemi Iwashita's corridor and shared-diary stories

All 1,902 fields and 1,938 fragments completed accuracy review, editorial review, and proofreading across 24 slices. The final 142 fields also received an independent review, which restored the player's explicit perception of the handwriting and clarified seeing the approaching girl's face. The exact renderer preserves the original controls and all 3,790 physical lines. `work/ui/iwashita-review.json` records the review decisions.

The glossary fixes Akiko Sano and Yoko Nakata and distinguishes classroom duty, the class log, and the shared diary. The English keeps Iwashita's borrowed player name, direct threats, and switches between the supposed boy and the listener. The source's unusual “forgot you'd written” wording remains distinct from forgetting to write. The apparent returning-from-home typo at line 3116 is interpreted as coming home from the scene's routine and room context. Sano and Nakata's identity remains unresolved, and the final disappearance does not acquire a permanent fate.

All 23 menus use horizontal English positions. Both visited and unvisited forms rendered through the native parser: 46 menu states and 102 choice labels. The hands and neck close-ups use a 312-pixel panel at the original right boundary, with compact horizontal dialogue. The skeleton scene retains the full-width panel. The diary, class log, letter, and three close-ups contain no readable narrative lettering to replace; the class log's dates are intentionally defocused. `work/ui/iwashita-layout.json` records the image inspection and geometry.

The normal opening reached Iwashita, descended the stairs twice, continued along the corridor, helped the girl, and reached ED046. Focused replays reached ED047–050. Native save/load restored the close-up's English dialogue and background at a supported dialogue pause. The ED044 diary replay checked the classroom-duty description, letter, diary entries, and funeral passage without measured clipping. The seven titles in both displays are A Shared Diary in Heaven, The Shadow of Regret, A Corpse’s Cry, Lying Is the First Step to Execution, Eternal Atonement, The Promise, and The Spirits’ Test.

Several source comments describe behavior absent from the actual code, including resetting the point score at line 1645 and showing or removing Nakata at lines 3444 and 3470. The original controls remain intact. An early diary test removed a portrait before the native hide command; the test setup was corrected. Another driver plan omitted the diary-reaction menu after the refusal branch; the plan was corrected before the completed replay.

The completed checks include all seven ending codes across nine route runs, with 1,455 measured dialogue pauses and no clipping. The refusal and acceptance paths both continued through the diary-reaction menu into ED045. Twelve-character given and family names fit through the full diary ending. The freshly rebuilt preview passed native save/load in the hands close-up, and all 76 translated Ending List entries fit across three pages. `work/ui/verified_0.1.18.json` identifies the completed evidence; aborted setup attempts and superseded duplicate runs are excluded from its totals.

The ready 0.1.18 save matches 0.1.17 byte for byte. All 16 regenerated videos matched the previous 15,027 audio/video packets, timestamps, durations, and flags; the ready preview carries the previous clip files. Six verified reverse Xdelta patches restore 0.1.17, with no added assets to remove. The ten active archives cover 0.1.8 through 0.1.17. Only 0.1.18 remains in `work/output`; the superseded full preview and oldest delta are held separately under `work/debug`, following the earlier deletion-policy rejection. The ready executable reached its title screen, then the existing save was restored and checked again.

## Fukuzawa review and opening regressions

Accuracy, editorial review, and proofreading covered all 1,933 fields, 2,030 fragments, and 3,856 physical lines of `fukuzawa.ks` in 25 contiguous slices. An independent review checked the 173 fields handled by the main agent. The glossary locks Reiko Fukuzawa, Shigeko Ohara, Naoko Shita, Yoshiko Tamai, and the fictional Poetter service. It distinguishes a water tank from a reservoir and preserves uncertain diagnoses, motives, identities, and fates. Source anomalies and editorial decisions are recorded in `work/ui/fukuzawa-review.json`.

The route has seven horizontal menu layouts, 38 visited/unvisited labels, compact close-up dialogue, six localized graphics, and eight translated ending titles. The clinic's original misspelled folder reference is resolved through the visual map. The phone lettering preserves account handles, avatars, photos, and the hand-shaped shadow. Native image checks matched all 341,176 protected pixels exactly. The cropped CG2 message stays incomplete; the conflicting labels on CG3–4 and unreadable incidental signs remain as in the original.

Completed native runs reached ED051–055 and ED127–129. After the typography correction, four route runs measured 1,296 pauses without clipping, all 14 menu states and 84 English Ending List entries fit, and native save/load restored the ant close-up. Earlier checks cover the other ending branches; the final report distinguishes evidence collected before and after the typography change.

The reported opening overflow was caused by retaining the original 38px line spacing. Default and maximum-length names passed 272 opening pauses after the fix. The hallway page includes the previously hidden final reply and ends at y=551, inside its y=637 limit. A native load of the user's existing slot at line 755 adopted the compact layout immediately and passed another 21 pauses through that page. The backlog now records the script's line breaks, retaining spaces and speaker separation. Native checks also verified scrolling and closing it. Details and evidence are in `docs/english_typography.md` and `work/ui/verified_0.1.19.json`.

The debug runtime previously muted every media playback, including ordinary launches. Only automated QA launches request that mute now. With the request absent, the title and opening music played unmuted, at nonzero volume, with advancing playback time and no decoder errors. All 82 music files and 360 effects match the original game. The hallway scene deliberately fades the music out before the reported conversation. Both current user save files, including the existing slot data, are preserved unchanged; QA progress is kept separately.

Only 0.1.19 remains in `work/output`. Its 26 verified reverse Xdelta patches and nine asset removals restore 0.1.18; the ten active archives cover 0.1.9–0.1.18. The superseded full preview and oldest delta are held under `work/debug` following the previously recorded deletion-policy rejection. No public release was created.

## Natural wrapping in 0.1.20

The inherited hard breaks in the reported email passage split “didn't send / that email,” “showing it / to me,” and “looked / at each other.” The reflow audit checked all 18,604 English fields in 22 script files and found 3,593 continuation breaks across 14 files. Those now wrap to the available width. The other 12,610 breaks retain speaker labels, paragraphs, sentence boundaries, explicit staging, and other layout. Translation wording, source rows, and scenario files are unchanged; every original pause remains.

The native engine checked all 16,203 audited break commands with matching text and backlog output, and exactly one interpreter advance per command. The reported passage passed a normal replay and a native load of the old hard-break layout. These checks measured 437 opening pauses without clipping; a narrow close-up with maximum-length names passed 94 more pauses and native save/load. The audit and evidence are indexed by `work/ui/verified_0.1.20.json`.

Both user save files are preserved unchanged. Only 0.1.20 remains in `work/output`. Three verified reverse Xdelta patches restore 0.1.19, and the ten active archives cover 0.1.10–0.1.19. Superseded files are held under `work/debug` following the earlier deletion-policy rejection. No public release was created.

## Continuing the translation

1. Export a scenario with `py -3.11 tools/scenario.py export --scenario op.ks --dry-run`, then run without `--dry-run` to write a private reference. Use the original script and adjacent rows to determine who is speaking and why. Use the offline draft only as a reference.
2. Keep one entry per original field. For lines with inline controls, write one English fragment per listed source fragment and retain the control order. Record unresolved referents and route-specific glossary changes.
3. Review accuracy, edit for voice and clarity, then proofread. For a bilingual working JSON, add `en` and `status: "proofread"` under each approved row. Use `tools/strip_jp.py --dry-run` with the working file, then run it without `--dry-run` to export only the proofread English fields.
4. Run `py -3.11 tools/scenario.py verify`, refresh the isolated copy, and check the actual rendered page and branches. Record the coverage and build changes in the changelog.

Offline draft reference used Helsinki-NLP OPUS-MT Japanese to English, packaged for CTranslate2 by [Playto](https://huggingface.co/playto-mt/opus-mt-ja-en-ct2). Game text was processed locally.
