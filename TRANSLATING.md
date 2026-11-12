# Editing the translation

Use your own supported Steam game and keep original archives backed up. Source
working files and unpacked assets belong under ignored local directories.

1. Find the scenario and field in `work/translation/en/*.en.json`.
2. Inspect adjacent source context locally, using the approved glossary spellings.
3. Review accuracy, then clarity/voice, then spelling and punctuation. Recheck
   meaning after substantive edits.
4. Preserve one fragment per source fragment, commands, placeholders, source
   positions and deliberate interruptions. Let ordinary English wrap naturally.
5. Preview `tools/strip_jp.py <working.json> --dry-run`, then export without that
   flag. Only rows marked `proofread` are exported.
6. Verify the original SHA-256 and rendering with `tools/scenario.py verify`.
7. Check the changed text in the actual game, including the backlog and relevant
   maximum-width names. A correct JSON structure is not a fit check.

The English overlays are the public editable script. `tools/scenario.py export`
creates a private working file only for a scenario that has no export yet; it
does not manufacture a bilingual replacement for an existing overlay. Keep
Japanese source and bilingual review files private even when contributing a fix.

## Life adaptation

The approved adaptation is `work/translation/en/adaptations/inoti-summary.json`.
It covers61 source fields at3356..3438 and uses three native page pauses. The
other 58 slots contain suppressed placeholders so older save positions remain
compatible. These are adapted source fields, not61 literal translations.

Keep this section non-graphic. Do not include the original explicit passage or
imagery in public issues, commits, screenshots or review artifacts. Preserve its
story context and the stated uncertainties rather than inventing identities.

## Building and assets

The original-source renderer, runtime and UI specifications are public. Some
historical artwork clean plates and native test fixtures are local-only because
they contain game-derived images or source data. Full artwork regeneration from
a checkout therefore needs those locally prepared inputs. The release patch is
the supported way to obtain the tested English artwork from your own game.

The normal Steam distribution is a patched embedded executable. Development
previews use an isolated external `package.nw` and an optional debug runtime.
Never ship that debug runtime, QA saves, browser profiles or complete game data.

Publishing a release requires an explicit project-lead request; local translation
work or a preview build alone does not authorize publication.
