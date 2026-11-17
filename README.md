# Youtube Plus 6.0 Free

Personal build based on YouTubePlus 6.0 / YouTube 21.43.5.

Latest update: **test.7 — iPhone Duo watch-page content and larger video**. Built from the two reports copied from the affected physical device. The updated rendering still needs device confirmation.

## Download

[Download the latest IPA](https://github.com/Kite1219/YouTubePlus-6.0-Free/releases/latest) · [test.7 release and validation](https://github.com/Kite1219/YouTubePlus-6.0-Free/releases/tag/v6.0-test.7)

Sign and install it with your usual sideloading setup.

The device reports identified an 84-point gap inside recommendations and chat even though the app window already fills the screen. This update corrects those inner views and lets the native video sizing calculation reuse the recovered space. For the supplied layout, the calculated video width grows from 563 to 647 points, with a 304-point side column. Video aspect ratio is preserved and genuine system indicators remain visible; chat header/footer buttons retain their native safe placement.

Built with Apple's iOS SDK. Archive CRC and independent comparison of every unchanged member passed. Existing background audio, PiP libraries, settings and resources remain byte-identical to test.4. The old layout helper and diagnostic badge are absent. **No simulator run was performed, and calculated target dimensions are not a captured result from the new IPA.** [Implementation, device evidence and limits](docs/duo-watch-test7.md).

Earlier test.5 was reported ineffective; test.6 remains a draft. The [one-tap diagnostic edition](diagnostics/README.md) and its source remain available for future investigation.

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
