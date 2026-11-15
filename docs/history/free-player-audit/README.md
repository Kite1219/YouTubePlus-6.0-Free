# YouTubePlus Personal 6.0 test.3 — free-build playback integration

## Inputs preserved
- Exact user-selected free build: C:/Users/Kiet/Desktop/Apps/IPAs/21.13.6_YouTubePlus_5.2b4.ipa
- Original 6.0/YouTube 21.43.5 IPA remains under ytplus-analysis.
- All previous patch scripts, traces, reports, extracted original and patched code remain available.

## What changed
The selected free IPA contains YouPiP.dylib and YouPiP.bundle, including a separate YouPiP settings section. The supplied 6.0 IPA did not contain them. Test.3 copies that installed component and its full resources into the personal 6.0 build; it does not replace 6.0 with the old YTLite binary.

The YouPiP binary is preserved except for normalizing its library install name to @rpath/YouPiP.dylib. Its original SHA-256 and the integrated SHA-256 are recorded in integration-build.json. Its MIT license is included in the app resources and this audit directory.

A small native PersonalPlayback helper restores the free 5.2b4 background-playability hooks on YTIPlayabilityStatus and MLVideo. It reads the same backgroundPlayback setting directly from NSUserDefaults, independently of the 6.0 membership preference reader.

On its first launch only, it enables YouPiP and its manual overlay button, disables Unrestricted PiP Activation and Legacy PiP, enables background audio, and marks that migration complete. Later user changes are preserved.

## Conflict handling
- The existing 6.0 PlayerManager PiP veto is neutralized while YouPiP is enabled; its original behavior remains available when YouPiP is disabled.
- The old 6.0 PiP overlay button is disabled by its preference and hidden after the normal button update. The copied YouPiP button is a separate component and is not the hidden legacy button.
- The English legacy-toggle description points to the YouPiP settings section to avoid confusing the two controls.
- Manual button activation checks for the newer maybeTogglePictureInPicture method. It preserves YouPiP's FromUser flag and invokes the player's own method. It does not force canEnablePictureInPicture to true. Missing methods, missing ivars, or a missing exported flag fall back to the copied handler.
- The helper loads before YouPiP; callback integration is queued onto the main queue so the copied component initializes first. This load/dispatch arrangement is checked statically; real dyld/UIKit behavior still needs device validation.

## Verification
- 12 tests execute the production Rust hook code compiled for Windows with mocked Objective-C/UIKit/dispatch. They cover background preference changes, one-time migration, preserving later choices, manual activation exactly once, missing-method/ivar/flag fallbacks, disabling YouPiP, and hiding only the legacy button after its original update. See native-host-tests.json and test_playback.py.
- ARM64 helper compilation passed using the already installed Rust/linker toolchain.
- ZIP CRC and member-by-member verification passed. Original members are unchanged except main executable load commands and the English legacy PiP label. The personal 6.0 dylib remains identical to test.2.
- Copied resource bytes match the free IPA; the newly included license is additional.
- Dependency/header inspection found 13 ARM64 binaries, no unresolved bundled dependencies, no active encryption flags, and audio background mode declared. System Swift libraries are runtime-provided and were not checked on the phone.
- Fresh ZIP metadata and executable permissions use the packaging approach that the user confirmed SideStore accepted.

These checks do not establish that playback, PiP activation, or the settings UI work on an actual iPhone/iPad. This remains a private device-test build. The former assertion that the settings-reader correction alone would solve background/PiP behavior was not established by device testing; the user subsequently reported both still failed.

## Expected settings after first launch
YouTube settings > YouPiP:
- Enabled: on
- Use PiP Button: on
- Unrestricted PiP Activation: off
- Legacy PiP: off

YouTubePlus > Player > Background playback: on.

Completely close/reopen after installation. Test a regular video: leaving the app should retain audio without automatically opening a PiP window; pressing the YouPiP overlay button should request PiP. Actual results are still pending.

## Rebuild
From the project workspace, compile PersonalPlayback.rs with the existing twitch-integration/native-audit/build-native.ps1 script, then run package_integrated.py using the installed Python. If the intermediate test.2 IPA has been cleaned up, package_integrated.py regenerates it from the retained original and prior patch/repack scripts. No tool downloads are required.

## Upstream references
https://github.com/PoomSmart/YouPiP
https://github.com/PoomSmart/YouPiP/blob/main/Tweak.x
https://github.com/dayanch96/YTLite/blob/v5.2b4/YTLite.x
https://github.com/PoomSmart/YouPiP/blob/main/LICENSE
