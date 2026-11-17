# Youtube Plus 6.0 Free

Personal build based on YouTubePlus 6.0 / YouTube 21.43.5.

Latest update: **test.8 — iPhone Duo comments header**. Gives the normal comments title and filter row the native width they need beside the system indicators. The updated rendering still needs device confirmation.

## Download

[Download the latest IPA](https://github.com/Kite1219/YouTubePlus-6.0-Free/releases/latest) · [test.8 release and validation](https://github.com/Kite1219/YouTubePlus-6.0-Free/releases/tag/v6.0-test.8)

Sign and install it with your usual sideloading setup.

Opening comments now uses the native wider side-panel balance, providing room for the Comments title, information/close controls and Top / Timed / Newest row. Closing comments restores test.7's larger video/recommendations layout. Fullscreen playback and fullscreen comments keep their existing layout. Genuine system indicators stay visible, and the existing edge-to-edge comments body is retained.

Built with Apple's iOS SDK. Archive CRC and independent comparison of every unchanged member passed. Existing background audio, PiP libraries, settings and resources remain byte-identical to test.4. The old layout helper and diagnostic badge are absent. **No simulator run was performed; final rendering still needs physical-device confirmation.** [Comments-header implementation and limits](docs/duo-watch-test8.md) · [Previous edge-to-edge update](docs/duo-watch-test7.md).

Earlier test.5 was reported ineffective; test.6 remains a draft. The [one-tap diagnostic edition](diagnostics/README.md) and its source remain available for future investigation.

## Development

[Development guide](docs/DEVELOPMENT.md) · [Historical app releases](https://github.com/Kite1219/YouTubePlus-6.0-Free/releases)

| Folder | Contents |
| --- | --- |
| [src](src/) | Playback and watch-layout helper sources |
| [diagnostics](diagnostics/) | One-tap layout collector, simulator smoke app and packaging entry point |
| [tests](tests/) | Historical playback and layout fixtures |
| [tools](tools/) | Build, packaging, inspection and historical setup scripts |
| [docs](docs/) | Development guide, PiP notes and historical findings |
| [analysis](analysis/) | Build reports, extracted metadata and audit evidence |
| [third_party](third_party/) | YouPiP license |
| [releases](releases/) | Complete backup file manifest |
| [archive](archive/) | Previous helper revisions and historical tool cache files |

IPAs and the complete binary development backup are stored in GitHub release assets. This repository contains our helper and integration work, **not the original complete YouTube/YouTubePlus application source**.
