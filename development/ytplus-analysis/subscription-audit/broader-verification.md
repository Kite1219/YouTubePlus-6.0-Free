# YouTubePlus Personal test.2: broader verification

## Result
Test.2 is a device-test build, not a fully verified release. The settings/access correction has stronger independent evidence now. No further IPA changes were made during this review.

The first build left an access-state byte check in both feature preference readers. A nonzero byte makes saved enabled/nonzero preferences act disabled/zero. Ghidra's independent machine-code emulator reproduced that failure and verified test.2's correction. This supports the incomplete subscription-removal patch as a likely explanation of the reported switches-on/features-off behavior. The byte's actual state on the user's phone was not observed, so it does not prove that every symptom has the same cause.

## Checks completed
- Independently emulated actual ARM64 instructions in Ghidra, rather than relying solely on the custom Python interpreter. All 32 cases passed: test.1 vs test.2, Boolean vs integer settings, access-state byte clear vs set, and saved values 0, 1, 37, and -1. Calls to Foundation were explicitly mocked. Keys, stack restoration, and callee-saved registers were checked. See independent-emulation.txt.
- Verified the final IPA hash is still 2dcf2a5a2a4ac678b85fc935510e40a58ef19b32fdf38db11b4f935773b83f0a.
- Inspected 11 embedded ARM64 binaries and their load commands. The main executable directly loads YTLite.dylib. No unresolved bundled dependency was found in the checked paths. Swift runtime dependencies refer to the system /usr/lib/swift path; their presence on a specific phone was not inspected.
- The main executable and inspected binaries have no active encryption flag. ZIP integrity passed. Previous member-by-member verification established that retained files other than YTLite.dylib match the original; signing records are omitted for re-signing.
- Info.plist declares audio background mode, iPhone and iPad families, and minimum iOS 17. These declarations do not prove working background playback or layouts.
- Mapped 253 direct calls to the Boolean feature reader and 75 to the integer reader. Bounded reverse tracing reaches player, feed, Shorts, and download settings. Indirect Objective-C dispatch is not fully covered by this graph. See feature-getter-coverage.json.
- Inspected the PiP-related player methods. Tracing reaches UIKit/Objective-C calls requiring real player objects. It was deliberately stopped at unmodeled calls, not represented as a successful PiP test. No separate YouPiP artifact is packaged.

## Feature coverage
| Feature area | What is established here | What is still unverified |
|---|---|---|
| Feature switches and numeric settings | Corrected machine-code readers preserve saved values with either access-state byte value | Real Foundation persistence, every individual key, save/import/reset behavior |
| Background audio | Audio mode declared; relevant setting and player code present | Home gesture, screen lock, Control Center, interruption/resume, device-specific behavior |
| PiP | Setting, overlay toggle code, and PiP controller code present | Button rendering, manual activation, automatic PiP preference, supported content and actual controller eligibility |
| Player controls, speed, loop, captions, quality | Related methods and setting-read call paths are present | Rendering, gestures, setting effects and compatibility for every video type |
| Feed/ad filtering | Filtering methods and Boolean preference paths present | Current YouTube ad formats, feed variants and server experiments |
| Shorts/interface/tab customizations | Code/resources retained; relevant preference-reader callers present | Every layout variant, Shorts interaction and iPad/iPhone Duo layout |
| Downloads/conversion | Downloader/task code and embedded conversion libraries retained | Real URL extraction, audio tracks, codecs, permissions, queue/resume and background completion |
| SponsorBlock | Integration code/resources retained | API responses, actual segment skipping and submission behavior |
| Official account/playback | Main executable retained byte for byte | Login, casting, DRM/content-specific playback, notifications and signer's entitlements |
| Subscription UI/reminders | Exact changed instructions independently verified | Every possible obfuscated integrity/licensing path and remote-only functionality |

## Device validation needed
The user has not installed test.2 yet. The shortest useful test is: install over test.1 using the same signing identity/bundle ID where possible, completely close/reopen the app, start a regular video, and lock the screen. Then test one obvious display option and the PiP button. Downloads, SponsorBlock, and iPad behavior need their own device checks. Do not infer that all features work from a passing binary/package audit.

The IPA remains unsigned and was not uploaded or published. The original input IPA is preserved.
