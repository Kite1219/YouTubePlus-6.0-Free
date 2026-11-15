# Personal test.4: manual-only PiP correction

The user confirmed test.3 background audio works, but its PiP button does nothing and swiping Home still starts PiP. Test.4 changes only PersonalPlayback.dylib inside that app package. The working background-playability function source is asserted identical to test.3 during packaging.

## Concrete compatibility finding
Exact Objective-C metadata extracted from the supplied YouTube 21.43.5 main executable shows YTPlayerPIPController implements `appWillResignActive` with type `v16@0:8`. The copied YouPiP source's automatic-entry guard hooks `appWillResignActive:` (one argument). They are different Objective-C selectors. The old colon selector does not intercept this current callback.

The current binary also contains YTPlayerPIPController.maybeTogglePictureInPicture, ML controller activation, the AVKit controller ivar, and the expected playback/PiP chain. Metadata is retained in youtube-21.43.5-player-objc.json. The actual view-controller parent chain on the user's phone was not observed.

## Changes
- Hook the current no-argument resign callback. In button-only mode, it prevents that callback from initiating PiP.
- Guard the AVKit automatic-inline/background setters and inline-auto getter in the same mode. Explicitly prime the AVKit controller after underlying player activation.
- Keep background audio independent of these PiP gates.
- Locate the PiP controller with bounded parent/responder walking, rather than assuming a single fixed parent relationship.
- On a manual tap, stop an already active AVKit PiP session. Otherwise, request AVKit start only when the platform reports it possible. If AVKit has not been prepared, invoke the existing player activation method first. Do not double-toggle a pending/already-started session. Keep guarded fallback paths for absent methods.
- Do not force canEnablePictureInPicture or platform isPictureInPicturePossible to true.
- One-time PiP-only migration resets manual button on, unrestricted activation off, legacy mode off. It does not overwrite the already working background-audio setting. Subsequent user choices are preserved.
- Store the most recent manual action path as PersonalPlaybackLastPiPResult in standard preferences. It contains a status string, no video/account data. A recorded request does not mean the OS actually entered PiP.

## Verification
28 tests execute the production Rust logic compiled for Windows against mocked Objective-C/UIKit/dispatch. They cover the exact current callback selector, Home without auto-start, preserving an already manually-started session, automatic setter suppression, explicit unrestricted-mode pass-through, ready/not-ready/absent AVKit, one-time migration, nested/cyclic parent chains, manual stop, and fallbacks. See native-host-tests-test4.json and test_manual_pip.py.

ARM64 compilation passed with the installed compiler/linker. Packaging checks compare every member with test.3 and allow only PersonalPlayback.dylib to change; CRC integrity is checked. Existing SideStore-compatible archive metadata is preserved.

No iPhone/iPad execution occurred here. These are corrected code paths with stronger regression coverage, not a claim of flawless on-device PiP. Test the button on a regular playing video, then test Home with PiP inactive, and Home after explicitly starting PiP.

## Preservation and rebuild
Original free and 6.0 IPAs, test.3 helper source/binary, metadata, test scripts, and previous reports are kept. Rebuild the ARM64 helper with the existing build-native.ps1, then run package_manual_fix.py. That script can regenerate the intermediate base using the retained prior package scripts when old IPAs have been cleaned up.
