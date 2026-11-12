First public English patch for **Apathy Kiwame**, Japanese Steam edition
(app 2283710, build 10331351).

### Download and install

Download **Apathy-Kiwame-English-v0.8.0.zip**, extract the entire ZIP, close the
game, and run **Apply.cmd**. The included Windows 64-bit installer finds the Steam
folder, verifies both original files, keeps an original backup and preserves
existing saves. No Python or separate patching program is required.

Use **Undo.cmd** to restore the original executable while keeping current saves.
The ZIP contains a binary patch and tools, **not a prepatched game**. You need
your own supported original installation. Read **README-v0.8.0.txt** and keep
checksum checks enabled; **SHA256SUMS.txt** verifies the release downloads.

### Included

- 36,145 ordinary translated fields and all 147 ending titles.
- English interface, choices, story lettering and 16 translated streamer videos.
- GenEi proportional Latin text, natural wrapping and readable backlog.
- Source-supported audio captions; normal music/effects remain enabled.
- A labelled, three-page non-graphic summary for 61 Life source fields. These are
  adapted rather than individually translated.
- `v0.8.0` and the retro-trans credit on the title screen.

### Verification and limitations

The binary delta was decoded and checked against the complete target executable;
all 2,009 production package files were checked. The actual installer output booted
with the expected title, font, audio and production modules. Installation and undo
preserve saves; corrupted payloads are rejected before mutation. Windows'
built-in PowerShell 5.1 was tested. No QA runtime, test progress, original archives
or Japanese script dump is included in the downloads.

This is an **AI-produced, AI-reviewed translation**. It is not a claim of complete
human proofreading or playtesting of every story-flag combination. Human review,
corrections and bug reports are welcome. The repository README describes coverage,
the adaptation and the contribution workflow.

GenEi and Xdelta notices/licenses are included. Please keep this fan patch free
and do not sell prepatched game copies or gate the download behind payment.
