# Youtube Plus 6.0 Free

Personal build based on YouTubePlus 6.0 / YouTube 21.43.5.

Latest downloadable build: **test.7 — iPhone Duo edge-to-edge content and larger video**.

**Known issue:** the normal comments-panel header can truncate. Test.8 was removed after it was reported ineffective.

## Download

[Download test.7](https://github.com/Kite1219/YouTubePlus-6.0-Free/releases/tag/v6.0-test.7) · [Latest release](https://github.com/Kite1219/YouTubePlus-6.0-Free/releases/latest)

Sign and install it with your usual sideloading setup.

Test.7 restores edge-to-edge recommendations and chat content, with a larger video using the recovered space. The normal comments-header issue remains unresolved. [Implementation and limits](docs/duo-watch-test7.md).

Build and archive checks passed; no simulator run was performed for test.7. The [withdrawn test.8 findings](docs/duo-watch-test8.md) and source history are retained for future development.

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
