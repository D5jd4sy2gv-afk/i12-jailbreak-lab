# i12 Jailbreak Lab V1.2 — iPhone read-only research app

**Target:** iPhone 12 (`iPhone13,2`, A14 Bionic), iOS 27.0 build `24A437`.

## Included
- `i12_Jailbreak_Lab.xcodeproj/` — SwiftUI iOS app project.
- `i12_Jailbreak_Lab/Sources/` — device/build detection, firmware manifest import, evidence ledger, and report sharing.
- `evidence_database.json` — dated, source-linked public evidence snapshot.
- `evidence_audit.py` — validates the evidence ledger schema, target identity, HTTPS links, and confidence labels.
- `i12_jb_audit.py` — read-only compatibility audit.
- `ipsw_analyzer.py` — read-only IPSW manifest and bounded Mach-O metadata inspection.
- `research_status.py` and `TARGET_STATUS.md` — research notes.

## V1.2 changes
1. Adds an in-app evidence ledger with source URLs, confidence labels, device scope, and checked date.
2. Separates exact-device evidence from results on iPhone 11/A13; no cross-device compatibility inference.
3. Adds a dated firmware-signing caution and current firmware index reference.
4. Includes a machine-readable JSON evidence database for external review.

## Firmware manifest import
The app imports an extracted `BuildManifest.plist`, not a full IPSW. Transfer that single plist to the iPhone and select it in the app. This checks firmware metadata only; it does not test exploits or prove jailbreak compatibility.

## Build an IPA on macOS
This is **source code, not a compiled or signed IPA**. Open `i12_Jailbreak_Lab.xcodeproj` in Xcode on macOS, select your own Team in Signing & Capabilities, and build/archive for your device. A valid signing identity and provisioning profile are required. This project cannot bypass Apple's code-signing requirements.

## Python tools
Requires Python 3.9+.
```bash
python3 i12_jb_audit.py --product-type iPhone13,2 --ios-version 27.0 --build 24A437
python3 i12_jb_audit.py --product-type iPhone13,2 --ios-version 27.0 --build 24A437 --json
python3 research_status.py
python3 evidence_audit.py
python3 ipsw_analyzer.py /path/to/firmware.ipsw
```

## Evidence snapshot — 2026-11-01
The Liter8 repository says it builds/boots custom iOS 27 on iPhone 11 (`n104ap`) and explicitly limits its tested claim to that device; iPhone 11 Pro/Pro Max are experimental and unverified. The 24A437 row for iPhone 11 cannot be applied to iPhone 12/A14. The public material reviewed here does not establish a reproducible full jailbreak for `iPhone13,2 / A14 / 24A437`. A third-party firmware catalog reports 24A437 unsigned; do not attempt restore/downgrade based on this project. Check Apple's current signing state before any restore.

Sources: [Liter8](https://github.com/Xplo8E/Liter8), [iPhone 12 firmware details](https://www.applefirmwares.com/firmware/iPhone13%2C2/27.0), [The Apple Wiki iOS 27.x firmware index](https://theapplewiki.com/wiki/Firmware/iPhone/27.x).

## Safety
Read-only only. No exploit execution, privilege escalation, kernel patching, boot-chain modification, restore, or device writes are included. Back up your device and do not install unknown profiles, certificates, or IPA files.

## GitHub 云端构建 IPA

仓库已提供 `.github/workflows/build-unsigned-ipa.yml`。将项目完整上传到 GitHub 后，在 Actions 中运行 **Build unsigned iOS IPA**，从 Artifacts 下载未签名 IPA，再使用易签和你自己的合法签名凭据签名。详细步骤见 `GITHUB_ACTIONS_BUILD_CN.md`。

注意：Actions 生成的是未签名 IPA；签名与安装仍需使用匹配的证书/描述文件完成。本项目为只读诊断工具，不是越狱载荷。
