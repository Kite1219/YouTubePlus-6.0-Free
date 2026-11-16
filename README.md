# Youtube Plus 6.0 Free

**iPhone Duo watch-page strip: unresolved on the reported device.** Test.5 was reported ineffective. Test.6 is held as a draft: compilation and package verification passed, but UI validation did not complete and no physical-device result is confirmed.

Personal build based on YouTubePlus 6.0 / YouTube 21.43.5.

[Download the latest IPA](https://github.com/Kite1219/YouTubePlus-6.0-Free/releases/latest) · [Development guide](docs/DEVELOPMENT.md)

Latest package: **test.5 — iPhone Duo watch-page layout**. Uses native screen-edge extension for recommendations and chat panels while retaining system indicators. The existing background audio and manual PiP helper are unchanged. [Implementation and limitations](docs/duo-watch-test5.md).

Apple-SDK compilation, 18 UIKit simulator-surrogate checks, package CRC and member-preservation checks passed. **Physical-device rendering and PiP remain unverified.** The fixture does not run the full YouTube app.

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
