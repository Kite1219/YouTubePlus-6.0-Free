# YouTube Plus 6.0: static compatibility inspection

Downloaded official asset: https://github.com/dayanch96/YTLite/releases/download/v6.0/com.dvntm.ytlite_6.0_iphoneos-arm.deb
SHA-256: 9822234413eeb085faec8f77864360156900bd62f281294b38b05e066777a55d

The package contains a 39,144,352-byte ARM64 Mach-O YTLite.dylib plus YTLite.bundle resources. It is a tweak package, not a complete YouTube application or IPA.

Existing REA 6.4.0 ran using the existing system Node executable. Its Ghidra provider rejected this Mach-O target on Windows. Existing Ghidra 12.1.4 successfully imported and analyzed the binary directly with the existing JDK. No tools were installed or updated.

## Confirmed compiled interfaces

- YTPPivotTabBarController: tab selection, tab geometry, context-menu anchors and previews. Its stored fields include a weak pivotBar reference, itemViews and menuAnchor.
- YTPLiquidGlass::placeTabBar:inPivotBar: at analysis address 0x00192b50.
- YTPLiquidGlass::layoutTabBarInPivotBar: at analysis address 0x00192e48.
- YTPTabHelper: custom pivot renderers, startup-tab selection, pivot-bar discovery and visible tab-bar geometry.
- Objective-C selectors include updateStyleOfTabBar:inPivotBar:, measureTabBar, floatingForced, featuredChannelWatermarkImageView, loadFeaturedChannelWatermark and safeAreaInsets.

## What the recovered code establishes

The controller provides separate handlers for context-menu highlighting and dismissal; both call menuPreviewForInteraction:. The preview code references view bounds, a rounded rectangular UIBezierPath, UIPreviewParameters and UITargetedPreview. This supports rounded tab menu previews.

## Limits

The tab-placement and layout routines decompile into indirect, computed branches. Ghidra reports unrecovered jump tables and several decoding errors. These results do not establish their exact positioning formulas, device checks or fold/unfold behavior. No distinct iPhone Duo detection routine was confirmed. General navigation-layout compatibility is a plausible interpretation, not a demonstrated Duo-specific implementation.

See layout-focused.txt and ghidra-output.txt for raw recovered pseudocode and warnings. No licensing code was modified. Static inspection only; no iOS execution or on-device verification was performed.

A complete installable IPA cannot be reconstructed from this tweak alone. A compatible base YouTube IPA is required for packaging.
