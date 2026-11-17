# One-tap layout diagnostics

This is a diagnostic edition of YouTubePlus 6.0, based on the exact retained test.6 IPA (SHA-256 `db62288f7fb34509f7395e6848001b0aa123418dc370cf98ab1e564c75fce09f`). A separate iOS app cannot inspect YouTube's view hierarchy, so the collector is injected into the app being diagnosed. Existing playback, PiP and layout-helper bytes are preserved.

## Use

1. Sign and install the diagnostic IPA with the same sideloading setup you already use.
2. Open the video page where the strip is visible. A purple **Copy diagnostics** button appears near the bottom-left safe edge.
3. Tap once, then paste the copied report into the chat. There is no separate export, login or upload step.

The collector copies current window/view/constraint/layer data plus a short in-memory geometry history. You may visit Home, the affected video and fullscreen before copying if you want those transitions included; a report from the affected page alone is sufficient to start.

## Recorded data

- Actual foreground scenes and owning windows, window/screen coordinate rectangles, screen association, status-manager geometry and size classes.
- View hierarchy, frames/bounds, converted window rectangles, original safe areas/margins, transforms, opacity/colors, clipping, masks and presentation-layer differences.
- Active constraint owners/items, Auto Layout attributes/constants/multipliers/priorities and guide frames.
- Controller hierarchy and native watch/player wrapper references and layout flags.
- Loaded app-library names and SDK linkage, exact native layout-method signatures and implementation owners.
- Read-only compact/regular/outer layout call counts and before/after rectangles; the existing layout helper's current eligibility result when its verified exported function is present.
- Available reserved-region metadata and safe, small display-setting boolean/enum preferences.

Text input, collection/table cell internals and the diagnostic badge are pruned. Limits (650 view nodes, 1,600 constraints, bounded layer depth/history) prevent unbounded reports; `truncated` reports whether a limit was reached. Nonfinite values are serialized as null.

## Privacy and behavior

The collector does not read label text, accessibility identifiers, accounts, cookies, tokens, video URLs, screenshots or network logs. No report is uploaded automatically. Copying happens only after the user's tap. Reports remain in memory and on the clipboard. The badge is a subview of the actual app window; it does not create a high-level window or cover/recreate system indicators.

Layout observation hooks forward the original methods exactly once and do not set content frames, constraints or safe areas. The existing test.6 layout helper remains unchanged, so this records the failing build's actual behavior. This is a diagnostic tool, not a claimed strip fix.

## Build and verification

Workflow: **Build one-tap layout diagnostics**. It uses the preinstalled Xcode 27 runner, tests one-tap capture/privacy in an iPhone Duo simulator, then adds `LayoutDiagnostics.dylib` to the pinned test.6 IPA. Packaging verifies ZIP CRC and every unchanged member, including existing playback/PiP/layout libraries and Info.plist. The IPA is unsigned and needs the user's normal re-signing process.

The simulator smoke app verifies the diagnostic tool itself on the Duo simulator's outer display; both simulated displays are captured separately. It does not claim to run the complete YouTube IPA or verify the unfolded watch-page fix. The actual on-device report is needed to locate the strip.
