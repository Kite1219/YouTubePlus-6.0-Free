# YouTubePlus Personal test.2 — settings enabled but features inactive

## Diagnosis
The first personal build changed the credential-eligibility routine but left two further checks intact. Both the Boolean preference getter (0xc1ddc) and integer preference getter (0xc2aa4) also read a separate access-error byte at 0x2363040. When that byte is set, the getters return disabled/zero values despite saved settings being enabled.

Offline instruction tracing reproduced this test.1 behavior. This is a concrete failure path consistent with the screenshots, not an observation of the user's phone memory. The first test's mocked-external-call checks covered only the clear error flag and therefore missed this state. They were insufficient to establish on-device functionality.

## Correction
Test.2 retains the previous personal-build changes and changes the two access-error reads in the feature getters to a local zero (0xc23e0 and 0xc3110). The saved Boolean/integer preference is still used; features are not all forced on. Account tokens and server responses are not fabricated.

## Checks
- Sixteen bounded offline cases reproduce the previous error and verify that test.2 keeps saved false/true and numeric values with the error flag both clear and set: access-error-regression.json.
- The new instruction values are read from the actual rebuilt library in those cases.
- Package ZIP integrity and member-by-member verification passed. Every retained file is unchanged except YTLite.dylib; stale signing files are omitted for re-signing.
- Original customer IPA preserved. Full hashes and patches: personal-build-test2.json.
- Still not iPhone/iPad runtime tested. PiP provider availability and YouTube-specific eligibility are separate from this setting-read fix.

## GitHub research
The current upstream README confirms YouTube 21.43.5 / YouTubePlus 6.0 as tested, so the version number alone is not evidence of incompatibility:
https://github.com/dayanch96/YTLite/blob/main/README.md

The README identifies YouPiP as an optional separate integration providing native YouTube PiP. No separate YouPiP library was present in the supplied/personal IPA. Internal AVPictureInPictureController support and the YTPlus overlay-button setting do not by themselves establish complete native-player PiP support.

YouPiP issue 139 reports activation/button failures on YouTube 21.33.6. The maintainer says version 1.12.14 fixed the Use PiP Button setting issue; the reporter subsequently says activation still fails on their device. This is related evidence, not proof of an exact match or a universal fix for this IPA:
https://github.com/PoomSmart/YouPiP/issues/139

YTLite issue 478 concerns overlapping feed audio, not all settings being ignored. It was traced to DontEatMyContent and should not be presented as a matching fix:
https://github.com/dayanch96/YTLite/issues/478

## Device validation
Sign and install test.2 over test.1 using the same bundle ID/signing identity to preserve settings where supported. Fully close/reopen it. First test Background playback with a regular video by locking the screen, then test an obvious local display setting and the PiP button. PiP activation remains unverified. Do not treat package/static checks as evidence of device success.
