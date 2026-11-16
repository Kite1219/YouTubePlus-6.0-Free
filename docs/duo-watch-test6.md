# Test.6: repair measured watch-container geometry

The user confirmed test.5 did not change the visible strip. Its checks validated a surrogate, not the real app's layout. Test.5 depended on physical phone idiom and a substantial `UIWindow.safeAreaInsets.right`; neither is sufficient to describe the watch view. The exact on-device cause could not be established from screenshots alone. The user declined a separate diagnostic installation, so this update performs its measurements inside the normal layout helper without asking for another report.

## Verified native implementation

Static inspection of the pinned main executable confirms:

- `YTWatchView.layoutSubviews_regular`: `v16@0:8`, implementation `0x101563af0`.
- `YTWatchView.watchNextSafeAreaInsets`: returns `UIEdgeInsets`, implementation `0x101567ecc`.
- The regular layout uses that private inset getter when calculating the feed's trailing extent.
- The watch view owns `_watchNextWrapperView` and `_engagementPanelView`; `YTWatchLayerView` has an app-owned `_statusBarView` placeholder.
- The main executable already reports an SDK linkage of 27.1. No SDK metadata is edited or represented as a genuine rebuild of YouTube.

The old flag-only library is excluded by building directly from the unchanged test.4 base. The replacement hooks the verified regular-layout method and its private inset getter. Only while the regular layout calculates content frames, its trailing column inset is removed. `UIView.safeAreaInsets` and the host getter outside that call retain their original values for foreground controls.

## Actual window and constraints

The helper uses the affected view's own window, verifies foreground/large-landscape geometry, and examines the current converted bounds. It does not select an arbitrary scene or use `UIScreen.main.bounds`. Measured narrow trailing gaps in the known outer watch containers, feed wrapper and engagement panel are expanded to the window's right edge while retaining their left and vertical placement.

For manually positioned views, the helper changes the frame during the native layout lifecycle. For Auto Layout views it displaces only identified external equal leading/trailing/left/right/center-X/width constraints against the owning parent or safe-area guide, then retains dedicated horizontal edge constraints. Vertical and internal controls/rendering constraints are preserved. Unknown constraint ownership is skipped. Constraints are idempotent and rebuilt on reparenting. Original geometry is restored on leaving the applicable mode where still valid. There are no recursive `layoutIfNeeded` calls in production.

Only an empty, app-owned status placeholder that actually matches a full-height narrow trailing strip can have its opaque background cleared, with its previous appearance restored outside that condition. Genuine system indicator views are never hidden, recreated or covered. No global clipping or safe-area override is installed; video fit/fill behavior is untouched.

The last meaningful before/after geometry, ancestor clipping/masks, controller classes, size classes and constraint attributes are recorded locally in `YouTubePlusWatchGeometry` preferences. This contains no account details, video URLs, view text or chat messages. No user action is required and nothing is uploaded by the app.

## Validation and limits

The UIKit surrogate now reproduces a distinction test.5 missed: **window right inset 0, watch inset 84**. It checks actual before/after view rectangles, the native getter outside layout, measured outer viewport repair, preserved vertical/internal constraints, idempotence and reparenting. It is still not the complete YouTube application or a physical Duo test.

If the system gives the application a window that excludes the status area, the code cannot draw outside that window. It will not use larger negative insets, cover system UI, or claim that such a restriction has been fixed. The physical-device rendering result remains unverified until the user runs the updated app.
