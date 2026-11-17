# Duo watch-page update from device reports

Two physical-device reports on iOS 27.2 show a 951 × 669 point app window and watch view. Both already reach the screen edge. The right safe inset is 84 points. The previous helper was installed and its native layout hooks were running; the failure was not an unloaded library or an OS-excluded window.

The actual gap is nested inside the side column. `YTWatchNextView` is 388 points wide, but `_watchNextResultsView` is only 304 points wide. The chat panel has the same 84-point subtraction in `_contentContainerView`. The app-owned `_statusBarView` is zero height and cannot be the vertical strip.

## Changes

- Let `YTWatchView.expandedPlayerSize` use the full width in its existing native split calculation. The app's private `yt_safeAreaInsets` getter omits the right inset only during that size query. UIKit safe areas remain unchanged.
- The original sizing code uses a 0.6875 fraction capped by the native minimum feed width. In the supplied geometry, the video width therefore grows from 563 to 647 points, and the right column becomes 304 points wide. The player height comes from the existing native calculation; a cached fixed flexible-player height grows proportionally. No rendering gravity or content mode is changed.
- After `YTWatchNextView.layoutSubviews`, extend only its manually laid-out `_watchNextResultsView` when the missing width exactly matches the measured right safe inset. Invalidate its collection layout so real cells reflow at the new width.
- Extend the native return rectangle of `YTEngagementPanelView.contentViewRectForHeaderFrame:footerFrame:safeX:`. Native code then resizes the chat content container and content view. Header and footer button rectangles remain native and protected by their original safe inset.
- Use scrollable-axis safe-area adjustment for these vertical recommendations/chat collections. This retains vertical inset handling while avoiding another horizontal 84-point inset. Original scroll policy is restored when the view leaves the eligible layout. Caller contentInsets are untouched.

Changes apply only to visible, non-fullscreen watch content in a large landscape window with the measured right-side reserve. Home/browse layout and fullscreen playback use their original behavior. No status indicators are hidden, copied, replaced or covered by a new window. The old test.6 layout helper and diagnostic badge are absent: this package starts from the pinned test.4 base and adds one replacement layout helper.

## Evidence and limits

Native class/ivar metadata and ARM64 disassembly identify the exact feed, panel content-rectangle and video-size methods. [Sanitized measurements and method addresses](../analysis/releases/test7-device-findings.json) preserve the device evidence without account or video content. The expected dimensions describe the native arithmetic applied to those measurements; they are not a captured result from the new IPA.

The build uses Apple's iOS SDK and performs archive CRC and every-member preservation checks. No simulator is run. The updated UI still needs physical-device confirmation. Source and package checks cannot prove the final rendered appearance, server playback or every app feature on the user's device.
