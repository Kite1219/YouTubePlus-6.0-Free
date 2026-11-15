# YouTubePlus Personal 6.0-test.1

Separate unsigned personal test build based on the supplied YouTube 21.43.5 / YouTubePlus 6.0 IPA. The original customer IPA is unchanged.

## Changes
- The shared eligibility routine at 0xc24bc now returns true. Boolean and integer feature preferences continue to read their saved values, rather than being disabled by missing membership credentials.
- The credential lookup at 0xc1bd8 now returns nil. No membership JWT/device credential is loaded through that routine.
- The membership fetch-token client at 0xc4b48 now returns nil without entering its network path.
- The FeaturesNotActivated / Access.LogIn reminder routine at 0xcac80 returns immediately.
- The membership settings section no longer populates status, login, or device-management controls, and its header is cleared. Section allocation and existing ownership/release operations are retained.

The original third-party gate describes account, tier, app-registration, and device-limit failures. The personal build avoids this local eligibility requirement and its associated UI, rather than rewriting server responses or creating a subscription. Official YouTube login and Premium logic were not patched.

## Evidence
- The original routines were inspected with the already installed Ghidra engine. REA's Windows provider rejected Mach-O, Hopper is unsupported on Windows, and IDA is not configured. No tools were installed, and unsupported tools were not represented as used.
- Static tracing decoded deviceId, jwt, accessExpiry, FeaturesNotActivated, Access.LogIn, and the membership fetch-token URL from the original binary. No requests were made to that service.
- The final instructions and return values were independently disassembled/decompiled by Ghidra: patched-verification.txt. The original Ghidra project was opened read-only for that verification.
- Eight bounded offline preference-getter cases passed, including saved false and numeric values remaining intact: preference-verification.json. External calls were mocked; this is not device execution.
- ZIP integrity passed; every retained member matches the source byte for byte except YTLite.dylib. Stale signing files were removed for re-signing.
- Exact input/output hashes and every changed byte are recorded in personal-build.json. build_personal.py reproduces the package from the exact input hash.

## Installation and limits
Sign YouTubePlus-Personal-6.0-test.1-unsigned.ipa using your usual sideloading tool. This is a device-test build, not a runtime-verified release: launch, settings, playback, downloads, and both iPhone/iPad still need to be exercised on actual devices. The binary is obfuscated, so additional integrity checks or access paths may remain outside the inspected paths. No claim is made that all server-backed functionality becomes available offline.
