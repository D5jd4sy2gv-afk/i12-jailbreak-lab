# i12 Jailbreak Lab — iOS app shell V0.9

Target: iPhone 12 (`iPhone13,2`, A14/T8101), iOS 27.0 build `24A437`.

## Included
- Native SwiftUI dashboard.
- Runtime device identifier, iOS version and `kern.osversion` build detection.
- Evidence-oriented compatibility display.
- Read-only safety boundary.
- Previous Python research utilities and evidence notes at the package root.

## Build an IPA
This source project must be opened and built on macOS with Xcode. This environment cannot sign an iOS app or produce a valid installable IPA.

1. Open `i12_Jailbreak_Lab.xcodeproj` in Xcode on a Mac.
2. Select the `i12_Jailbreak_Lab` target and choose your Apple development Team under Signing & Capabilities.
3. Keep Bundle Identifier `com.research.i12jailbreaklab` (or change it to one registered to your team).
4. Select Any iOS Device (arm64), Product > Archive, then Distribute App > Development or Ad Hoc.
5. Xcode exports a signed IPA according to the selected distribution method.

## Important
- This is a research/diagnostic shell, not a jailbreak.
- It does not exploit, patch, elevate privileges, bypass code signing, disable protections, or modify device data.
- The current public evidence snapshot does not establish a reproducible full jailbreak for the exact A14 / 24A437 target.
- A matching device/build is not proof of exploit compatibility.
