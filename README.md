# i12 Jailbreak Lab — V1.4

**Target profile:** iPhone 12 (`iPhone13,2`) · A14 Bionic · iOS 27.0 · build `24A437`

V1.4 is a **read-only research and diagnostics toolkit**, not a jailbreak installer. It does not run exploits, gain root, bypass platform mitigations, patch the kernel, install profiles, alter security settings, or write to the device.

## V1.4 changes

- Removed the `BuildManifest.plist` / IPSW import feature completely.
- Removed the IPSW analyzer source from this release; there is no manifest picker, import path, parser, or multi-gigabyte IPSW workflow.
- Replaced the previous concept icon with the exact user-supplied purple waveform artwork. Added a 1024×1024 PNG and an iOS `AppIcon.appiconset` ready for an Xcode asset catalog.
- Kept device/build identification, public compatibility evidence review, and lightweight firmware-catalog metadata lookup.
- Added regression tests for the device audit, evidence report, and firmware metadata lookup.

## Included files

| File | Purpose |
|---|---|
| `i12_jb_audit.py` | Manual device/build audit; optionally reads a paired device through `ideviceinfo` |
| `research_status.py` | Prints a structured evidence ledger and safety notes |
| `firmware_catalog.py` | Looks up firmware metadata only; never downloads firmware binaries |
| `assets/AppIcon.svg` | Scalable wrapper preserving the supplied icon artwork |
| `assets/AppIcon-1024.png` | 1024×1024 app icon PNG |
| `assets/AppIcon.appiconset/` | iOS universal AppIcon asset catalog |
| `tests/` | Offline unit tests |

There is deliberately **no** `ipsw_analyzer.py` in V1.4.

## Quick start

Requires Python 3.9+. No third-party Python packages are needed.

Audit the configured target profile:

```bash
python3 i12_jb_audit.py --product-type iPhone13,2 --ios-version 27.0 --build 24A437
```

Export the audit as JSON:

```bash
python3 i12_jb_audit.py --product-type iPhone13,2 --ios-version 27.0 --build 24A437 --json
```

Print the research evidence ledger:

```bash
python3 research_status.py
python3 research_status.py --json
```

Check firmware catalog metadata (network required; metadata response only):

```bash
python3 firmware_catalog.py
python3 firmware_catalog.py --json
```

Run offline tests:

```bash
python3 -m unittest discover -s tests -v
```

## Device connection

On macOS/Linux, install `libimobiledevice`, connect and unlock the iPhone, pair it with the computer, then run `python3 i12_jb_audit.py` without manual identity arguments. If device access is unavailable, the tool asks for explicit CLI identifiers or reports unknown values. The project does not attempt to bypass pairing or device protections.

## Evidence interpretation

A matching model/version/build tuple only confirms that the supplied identifiers match this research profile. It is **not** a jailbreak-availability signal. A firmware catalog's signing flag is third-party metadata and can change; verify signing status with Apple/Finder before any restore. Do not restore or erase a daily-use device to test research code.

The current evidence ledger does not establish a public, reproducible full jailbreak for iPhone 12 / A14 / iOS 27.0 build 24A437. Demonstrations on other devices or builds are not proof of compatibility. Recheck primary sources before relying on any status because projects and firmware signing can change.

## Exit codes (`i12_jb_audit.py`)

- `0`: exact target tuple matched (not a jailbreak signal).
- `1`: supplied/read identity does not match the exact target tuple.
- `2`: no device identity found.

## Safety boundary

This release is limited to read-only identification, metadata lookup, and evidence reporting. It does not contain jailbreak payloads or instructions for exploiting the device.
