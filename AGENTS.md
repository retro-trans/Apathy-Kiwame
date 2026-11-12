** Organize folder like this **
work - work folder
    output - contains the file for testing (iso, zip, etc...)
    glossary - contains the one or many json files for glossary
    ui - contains screenshot of actual UI element ingame with label on screenshot if possible, contains files (json,py,...) describe the coordinate, width and height, id and other attributes
    translation/<language code> - contains the target translation of ui element or dialogues or anything that need translation
docs - documents
tools - any tools help with translation
incoming - outside files that need agent to look into

** SOME RULES **
- Avoid contains extensive Japanese scripts (UI elements is fine)
- Identified each build with version 0.x.y (start at 0.1.0)
- Always write change log
- If user told you to remember anything write it down here, make sure to ask user if the new one conflict with old one
- Be conscious of subscription limit before creating sub-agents
- When using emulator turn the volume down to zero
- For console game: make sure the patch only modify things around real hardware boundary, if not sure document any change that could break the game when running on real hardware
- Keep only latest version output, the other versions keep as xdelta (dcp for dreamcast) but only at most 10 recent version

** REMEMBER **
- The user also approved adding an optional standalone installer ZIP to the existing 0.8.1 release on 2026-11-12. Keep both the shared Tools route and the Apply.cmd ZIP available; preserve the existing published patches, canonical checksums and executable identity.
- The user explicitly approved pushing and publishing Retro Trans Tools 0.5.23 with combined-source support, followed by Apathy 0.8.1 and live catalog verification, on 2026-11-12. Preserve the issued 0.8.0 downloads/tag, unrelated work, original files and all user saves. Future releases still need explicit approval.
- In the Life route, the user explicitly superseded the original-Japanese exception on2026-11-12: use a non-graphic English summary, preserve as much story context as possible, and install it in main Steam. The61 locators in `work/ui/inoti-original-language-exception.json` now identify the adapted section; `work/translation/en/adaptations/inoti-summary.json` defines its three pages. Keep source order positions/save compatibility and neutral background; sanitize legacy saved scene text/thumbnails in memory without rewriting user save bytes. Never reproduce graphic sexual content involving a minor in chat, screenshots or review artifacts.
- The user also plays the patched main Steam copy at `M:/Steam/steamapps/common/Apathy_kiwame`. Its installation marker records the version and original-file backup. Preserve Steam's own saves separately from preview saves.
- Let continuous English prose wrap naturally instead of copying Japanese mid-sentence hard breaks. Preserve speaker labels, paragraphs, explicit staging and pause commands. Regenerate and check `tools/text_flow.py` when translated text changes.
- Use Latin typography for English dialogue and UI, with ASCII `...` for ellipses in translated script text. Keep normal test-build audio enabled; mute only automated QA launches.
- When updating a local build, preserve every user `*.sav` file byte for byte, including slot data as well as system settings. Exclude progress created by automated QA.
- Follow the editorial-pass workflow in `BASE_RULES.md` for translated scripts: accuracy review, editorial review for clarity and character voice, then final proofreading.
- Build debug tool using `debug_tools_guide.md`
- Do not create or publish a GitHub release until the user explicitly requests a release for that build. Translation and local builds do not imply release permission.
- Japanese script text must never be committed to git. Keeping it in local working files is fine: `.gitignore` covers `work/source/` and the translation working files. Commit only the `*.en.json` copies written by `tools/strip_jp.py` (run it before committing). Names and UI terms in Japanese are allowed.
