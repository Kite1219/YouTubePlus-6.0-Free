# Test.5: native watch-page edge extension

The supplied screenshots show an inset recommendations/chat column on the normal watch page, while Home and fullscreen already draw as expected. Static inspection of the supplied YouTube 21.43.5 executable found separate native screen-edge extension flags for the watch-next wrapper and engagement-panel container. In `YTWatchView.layoutSubviews_regular`, these control adding the trailing safe-area amount back to the content container's width. The native code also retains the extension amount for descendant layout. This is a plausible app-side source of the strip; screenshots and static inspection do not prove the physical device's window geometry.

The helper enables only those two existing BOOL fields while laying out a visible, expanded watch view on a large landscape phone with a substantial right safe inset. UIKit's safe-area values and system status indicators are unchanged. Original field values are restored when leaving that geometry, entering fullscreen, hiding the watch view, or using a miniplayer. Portrait, ordinary phones, tablets, and RTL are left untouched. Unknown host fields/types or selectors cause a no-op. No global safe-area, status visibility, window, cropping, or aspect-ratio overrides are installed.

Apple explains that [safeAreaInsets](https://developer.apple.com/documentation/uikit/uiview/safeareainsets) account for system and ancestor bars. The safe area is retained so important controls can remain clear of the genuine indicators. The patch uses the host's own distinction between edge-extending content and safe control placement.

## Validation and limits

The workflow compiles against Apple's SDK, exercises the production hook with a surrogate host on an iPhone UIKit simulator, and compares every package member against the pinned test.4 base. The existing `PersonalPlayback.dylib`, YouPiP library, original Info.plist and all resources are preserved byte-for-byte. Only a load command in the main executable and a new `DuoWatchLayout.dylib` are needed. The existing code signature becomes invalid and the IPA must be re-signed using the user's normal sideloading setup.

The simulator fixture is not YouTube or an iPhone Duo. No physical-device watch-page capture or indicator overlap check can be performed here. If the OS supplies a window that excludes the status region, these flags cannot draw outside that window; the patch deliberately does not modify system status windows. On-device verification is required before claiming the strip is eliminated. Some content remains legitimately black, including video aspect-fit letterboxing.

## Build

Run the **Build Duo watch layout** workflow. It downloads the checksum-pinned test.4 base, runs the UIKit fixture, compiles the separate helper, and uploads the resulting package/validation artifact. Package script: `tools/package_duo.py`. Helper: `src/DuoWatchLayout.m`. This workflow does not publish automatically; release publication follows artifact verification.
