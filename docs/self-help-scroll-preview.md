# Self-Help scrolling letter · 0.8.2 preview

This movie was prepared as a local preview and is included in 0.8.2 after the
user requested publication. The main Steam installation, original assets and
user saves remain unchanged by release preparation.

The 24 reviewed letter cues from `work/translation/en/media/self-help.vtt` are
reflowed into 45 English lines, with all 428 words retained. The only text
normalization is the project's ASCII `...` convention. Segoe Print supplies
Latin handwriting for the rendered movie; the font is not a distributed asset.

The original 960 × 690 montage supplies every background frame. A numerical
motion mask follows the baked Japanese lettering at 51.6 pixels per second.
Spatial video inpainting restores the covered pixels from the surrounding
background in the same frame, avoiding color leakage across the montage's
crossfades. Pixels hidden by the source lettering must therefore be
reconstructed. Some small restoration artifacts can remain. Original footage outside the mask is
retained before video encoding. No generated replacement backgrounds are used.

Paragraph positions follow the original 66-pixel line grid. English wraps
within each paragraph's space, with the original scrolling speed, montage
transitions and final letter fade. The final photograph of the physical book
remains original and receives the existing English title caption from 110 to
121 seconds. The letter itself has no duplicate bottom subtitles.

The WebM copies the original Vorbis packets. Verification compares every audio
packet hash and timestamp, and requires 3,149 video frames at 25 fps and a
125.963-second duration. The MP4 viewing copy re-encodes audio for playback
compatibility; use the WebM when checking the exact original soundtrack.

Regeneration uses `tools/self_help_scroll.py` with FFmpeg 9, fontTools and the
OpenCV/NumPy versions in `tools/requirements-rpg-effect.txt`. The default command
is a read-only plan. `--output` writes a new mask; `--restore --mask ... --output
...` restores a video; `--render --mask ... --restored ... --output ...` writes
the English movie. Existing output files are never replaced. Native
decode/seek checks use `tools/check-self-help-scroll.mjs` in the isolated, muted
QA copy.

Review: the previously reviewed translation is reused without substantive
changes; the complete normalized English text is checked for omission or
duplication. Editorial and proofreading checks cover the paragraph flow,
natural wrapping and the first, middle and final lines. Visual review samples
the paper, clubroom, classroom, dog, street, sky and final book photograph.
