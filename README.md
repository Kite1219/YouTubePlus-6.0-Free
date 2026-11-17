# Youtube Plus 6.0 Free

Personal build based on YouTubePlus 6.0 / YouTube 21.43.5.

**iPhone Duo watch-page strip: unresolved on the reported device.** Test.5 was reported ineffective. Test.6 is retained as a draft and is not a confirmed fix.

## One-tap layout diagnostics

[Download the diagnostic IPA](https://github.com/Kite1219/YouTubePlus-6.0-Free/releases/download/layout-diagnostics.1/YouTubePlus-6.0-Diagnostics-1.ipa) · [Release and validation reports](https://github.com/Kite1219/YouTubePlus-6.0-Free/releases/tag/layout-diagnostics.1)

Sign and install it with your usual sideloading setup. Open the affected video page, tap the purple **Copy diagnostics** button near the bottom-left edge, and paste the report into the chat. Nothing is uploaded automatically.

This edition measures the actual app window, status-area geometry, view hierarchy, clipping, constraints, safe areas and native layout calls. It excludes view text, account details, credentials, chat messages, screenshots, video URLs and network logs. Existing test.6 playback, PiP and layout-library bytes are preserved.

The collector passed 12 smoke checks on the iPhone Duo simulator's outer display, including one-tap clipboard capture and privacy exclusions. Archive CRC and independent member comparisons also passed. **The simulator smoke app tests the collector, not the complete YouTube IPA or the unfolded watch-page fix.** A report from the affected device is needed for that diagnosis. [Source, usage and limitations](diagnostics/README.md).

## Development

[Development guide](docs/DEVELOPMENT.md) · [Historical app releases](https://github.com/Kite1219/YouTubePlus-6.0-Free/releases)

| Folder | Contents |
| --- | --- |
| [src](src/) | Playback and watch-layout helper sources |
| [diagnostics](diagnostics/) | One-tap layout collector, simulator smoke app and packaging entry point |
| [tests](tests/) | Playback and layout regression fixtures |
| [tools](tools/) | Build, packaging, inspection and historical setup scripts |
| [docs](docs/) | Development guide, PiP notes and historical findings |
| [analysis](analysis/) | Build reports, extracted metadata and audit evidence |
| [third_party](third_party/) | YouPiP license |
| [releases](releases/) | Complete backup file manifest |
| [archive](archive/) | Previous helper revisions and historical tool cache files |

IPAs and the complete binary development backup are stored in GitHub release assets. This repository contains our helper and integration work, **not the original complete YouTube/YouTubePlus application source**.
