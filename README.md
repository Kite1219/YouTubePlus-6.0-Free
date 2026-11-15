# Youtube Plus 6.0 Free

Private personal build based on YouTubePlus 6.0 / YouTube 21.43.5.

[Download the latest IPA](https://github.com/Kite1219/YouTubePlus-6.0-Free/releases/latest) · [Development guide](docs/DEVELOPMENT.md)

Latest package: **test.4 — Manual PiP**. Preserves background audio and corrects manual PiP activation and automatic-entry guards. Package checks and 28 mocked host tests passed; on-device PiP remains unverified.

## Project layout

| Folder | Contents |
| --- | --- |
| [src](src/) | Current PersonalPlayback helper source |
| [tests](tests/) | Playback regression tests and generated host fixture |
| [tools](tools/) | Workspace setup and historical build, packaging and inspection scripts |
| [docs](docs/) | Development guide, PiP notes and historical findings |
| [analysis](analysis/) | Build reports, extracted metadata and audit evidence |
| [third_party](third_party/) | YouPiP license |
| [releases](releases/) | Complete backup file manifest |
| [archive](archive/) | Previous helper revision and historical tool cache files |

The IPA and complete binary development backup remain in the private release assets. This repository contains our helper and integration work, **not the original complete YouTube/YouTubePlus application source**.
