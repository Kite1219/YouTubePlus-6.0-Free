# YouTubePlus custom subscription gate — static inspection

## Target
IPA: YouTubePlus_6.0_YouTube_21.43.5_official.ipa
App bundle: com.google.ios.youtube; version 21.43.5.
Analyzed embedded Frameworks/YTLite.dylib: 38,955,408 bytes.
SHA-256: aec278e47289639a7dc8b22cc4257df9b9f75336d6e187dd82da0d981c1ae59c

## Confirmed observations
The IPA contains a distinct third-party subscription interface. English resources in Payload/YouTube.app/YTLite.bundle/en.lproj/Localizable.strings include:
- FeaturesNotActivated: You are not logged in. To access YouTube Plus features, please log in to an account with an active subscription.
- Access.Active: Active
- Access.InsufficientPlan: Subscription level is too low
- Access.DeviceNotRegistered: Device is not linked
- Access.DeviceLimit: Device limit reached
- Access.NotFound: Account not found
- Access.AppNotFound: App is not registered
- Access.AccountRequired: Account required
- Access.Status: Subscription status
- Access.SignInAgain: Sign in again
- Access.RequestError: Request error

Objective-C metadata identifies YTPSettingsBuilder methods patreonSection: at 0x34b160, patreonStatusCell at 0x34bcdc, and patreonButtonCellWithType:model: at 0x34c1c4. Targeted decompilation reaches section/cell construction and conditional button presentation in this region.

The DVNPatreonContext category implements presentationAnchorForWebAuthenticationSession: at 0xc3590. Its recovered body obtains the view's window for the authentication presentation anchor. This identifies web-authentication presentation support; it does not establish the authentication provider or entitlement validation protocol.

## Interpretation
The resources describe an account-based membership system with subscription tiers, app registration, and linked-device limits. This is separate from the official YouTube Premium interface. The Patreon-named code is a useful implementation clue, not proof that Patreon itself performs all validation.

## Limits
The inspected routines use encoded strings and indirect control-flow dispatch. Recovering UI routines does not prove that every displayed status is enforced by a server or that the entire app is blocked rather than selected features. Exact backend URLs, response validation, token storage/signatures, expiration behavior, offline grace, and the final feature-enforcement call sites remain unverified. No claim of a complete security audit or a recovered original source tree is made.

## Evidence and preservation
See access-localization.json, objc.json, categories.json, decompile-output.txt, and blocks-output.txt in this directory. These results concern the exact embedded dylib above, not the different standalone .deb inspected previously.
The IPA was not modified. No activation endpoints were called, no accounts were accessed, and no subscription checks were patched.
