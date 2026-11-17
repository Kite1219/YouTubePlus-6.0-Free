# Comments header on the normal Duo watch page

The supplied screenshots confirm that test.7's recommendations layout works with comments closed. They also show the normal comments title truncated and the filter row clipped. The fullscreen comments screenshot has adequate room and must keep its existing layout.

The native expanded-player calculation enforces a minimum feed width of 304 points in the measured 951-point window. Test.7 reclaims the 84-point horizontal reserve when calculating the video width, leaving a 304-point side column. The native panel then subtracts the reserve for its header controls, leaving only 220 points for the comments title, information/close buttons and filter row. Extending the body alone cannot give that header enough space.

## Scoped repair

When the top engagement panel has the app's native `engagement-panel-comments-section` identifier, use the original expanded-player size in the eligible, non-fullscreen landscape watch layout. This restores the native wider panel/header balance: in the retained geometry the side panel is 388 points wide, with 304 points available for the native header after the system reserve. The video uses the native size while comments are open. The existing body extension remains active, so the comments body still reaches the app window edge.

When comments close, test.7's larger video sizing is used again. Other panel identifiers retain test.7 behavior. Fullscreen fails the existing eligibility gate and uses the original native calculation, as before.

The helper matches the native identifier, never the visible or localized title text. It only inspects the top panel's UIKit wrappers and stops before collection content. Native container layout/add/remove callbacks request a parent layout when the comments panel changes. Original callbacks are forwarded once. This uses native sizing and reflow without altering header fonts, button hit targets, filter models, clipping or real system indicators. No polling timer is added.

## Verification and limits

Native metadata confirms the identifier comparison, top-navigation getter and container layout signatures. The literal panel identifier is present in the exact app binary. Runtime checks verify method encodings before adding callbacks. The build uses Apple's SDK and verifies the archive CRC, exact main-executable load-command change, and every other archive member against the hash-pinned test.4 base.

No simulator is run. The expected widths come from the supplied device geometry and the inspected native sizing code; they are not a captured result from this update. Final rendering and interaction still need physical-device confirmation.
