#!/usr/bin/env python3
"""Read-only compatibility auditor for iPhone 12 / iOS 27 research.

This utility identifies a device/build and compares it with public project
support statements. It does not exploit, patch, restore, or modify a device.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

VERSION = "1.4"
TARGET_PRODUCT = "iPhone13,2"
TARGET_IOS = "27.0"
TARGET_BUILD = "24A437"

DEVICE_MAP = {
    TARGET_PRODUCT: {"name": "iPhone 12", "chip": "A14 Bionic", "board": "D53gAP"},
    "iPhone13,1": {"name": "iPhone 12 mini", "chip": "A14 Bionic", "board": "D52gAP"},
    "iPhone13,3": {"name": "iPhone 12 Pro", "chip": "A14 Bionic", "board": "D53pAP"},
    "iPhone13,4": {"name": "iPhone 12 Pro Max", "chip": "A14 Bionic", "board": "D54pAP"},
}

SOURCES = {
    "liter8": "https://github.com/Xplo8E/Liter8",
    "liter8_iphone12_issue": "https://github.com/Xplo8E/Liter8/issues/29",
    "usbliter8_patchfinder": "https://github.com/Trussh/usbliter8",
    "usbliter8_secure_rom": "https://github.com/JoshAtticus/usbliter8",
    "dopamine": "https://theapplewiki.com/wiki/Dopamine",
    "ppl_sptm": "https://theapplewiki.com/wiki/PPL/SPTM_Bypasses",
    "chollima": "https://theapplewiki.com/wiki/Chollima",
    "apple_security": "https://support.apple.com/en-ca/100100",
    "firmware_signing": "https://ipsw.me/iPhone13,2/",
}


@dataclass
class DeviceInfo:
    product_type: str
    product_version: str
    build_version: str
    device_name: str
    chip: str
    board: str


def idevice_value(key: str) -> Optional[str]:
    """Read a single identifier from a USB-paired device, if available."""
    if not shutil.which("ideviceinfo"):
        return None
    try:
        result = subprocess.run(
            ["ideviceinfo", "-k", key], check=True, capture_output=True,
            text=True, timeout=8,
        )
        return result.stdout.strip() or None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None


def collect_device(args: argparse.Namespace) -> DeviceInfo:
    product_type = args.product_type or idevice_value("ProductType") or "unknown"
    product_version = args.ios_version or idevice_value("ProductVersion") or "unknown"
    build_version = args.build or idevice_value("BuildVersion") or "unknown"
    known = DEVICE_MAP.get(product_type, {})
    return DeviceInfo(
        product_type=product_type,
        product_version=product_version,
        build_version=build_version,
        device_name=known.get("name", "Unknown device"),
        chip=known.get("chip", "Unknown chip"),
        board=known.get("board", "Unknown board"),
    )


def assess(info: DeviceInfo) -> dict:
    model_match = info.product_type == TARGET_PRODUCT
    os_match = info.product_version == TARGET_IOS and info.build_version == TARGET_BUILD
    exact_target = model_match and os_match

    checks = [
        {
            "project": "Liter8",
            "status": "NOT_SUPPORTED_FOR_IPHONE_12",
            "confidence": "HIGH — explicit project scope",
            "reason": (
                "The README says iPhone 11 / n104ap only. Its 24A437 row is an "
                "iPhone 11 result; iPhone 12/A14 is not listed."
            ),
            "source": SOURCES["liter8"],
        },
        {
            "project": "Liter8 iPhone 12 support issue",
            "status": "NO_MAINTAINER_COMPATIBILITY_CONFIRMATION",
            "confidence": "HIGH — issue is a request, not a support statement",
            "reason": (
                "The issue asks whether iPhone 12 mini/A14 support can be added; "
                "it is not evidence that A14 support exists."
            ),
            "source": SOURCES["liter8_iphone12_issue"],
        },
        {
            "project": "Trussh/usbliter8 patchfinder",
            "status": "OUTSIDE_STATED_A12_A13_DEVICE_SCOPE",
            "confidence": "HIGH — README lists tested A12/A13 devices",
            "reason": (
                "The tested-device table lists A12/A13 devices, including iOS 27.0 beta, "
                "but does not list A14 or iPhone 12. A beta test on A13 is not an A14 result."
            ),
            "source": SOURCES["usbliter8_patchfinder"],
        },
        {
            "project": "JoshAtticus/usbliter8 SecureROM exploit",
            "status": "A14_NOT_IN_STATED_SOC_SUPPORT",
            "confidence": "HIGH — explicit A12/A13 scope",
            "reason": (
                "The project describes support for A12/A13 SoCs (and theoretical A12X/Z); "
                "A14 is not in its stated support."
            ),
            "source": SOURCES["usbliter8_secure_rom"],
        },
        {
            "project": "Dopamine",
            "status": "NO_PUBLIC_IOS_27_A14_RELEASE_CONFIRMED",
            "confidence": "MEDIUM — public release-history check",
            "reason": (
                "The reviewed public release information does not list a reproducible "
                "iPhone 12/A14/iOS 27.0 release."
            ),
            "source": SOURCES["dopamine"],
        },
        {
            "project": "Calif / Chollima",
            "status": "DEMO_NOT_DEVICE_COMPATIBILITY_PROOF",
            "confidence": "HIGH — different device, no public tool",
            "reason": (
                "The public demonstration was on iPhone 18 Pro / iOS 27.0.1. "
                "No public release or iPhone 12/A14 compatibility proof is established."
            ),
            "source": SOURCES["chollima"],
        },
    ]

    return {
        "target_match": exact_target,
        "device_model_match": model_match,
        "os_build_match": os_match,
        "overall": "NO_VERIFIED_PUBLIC_FULL_JAILBREAK_FOR_THIS_TARGET",
        "protection_assessment": {
            "status": "REQUIRES_BUILD_SPECIFIC_TECHNICAL_VALIDATION",
            "note": (
                "Do not infer a complete A14 chain from a generic PPL/SPTM label. "
                "A valid claim must identify the exact hardware, firmware build, "
                "kernel/boot components, mitigations bypassed, and reproducible test."
            ),
            "source": SOURCES["ppl_sptm"],
        },
        "firmware_note": {
            "status": "UNSIGNED_AT_LAST_CHECK",
            "note": (
                "Third-party firmware catalogs reported 24A437 as unsigned. "
                "Signing status changes; verify with Apple/Finder before any restore. "
                "Do not restore or erase a daily-use device to test a research tool."
            ),
            "source": SOURCES["firmware_signing"],
        },
        "next_research_steps": [
            "Find an A14-specific exploit with a public technical write-up and reproducible test.",
            "Require explicit testing on iPhone13,2 and build 24A437, not only A13 or iPhone 18.",
            "Verify each required kernel and platform mitigation bypass separately.",
            "Keep all analysis read-only until the full chain and recovery path are independently reviewed.",
        ],
        "checks": checks,
        "sources": SOURCES,
    }


def print_report(info: DeviceInfo, result: dict) -> None:
    print("=" * 76)
    print(f"i12 Jailbreak Lab v{VERSION} — read-only compatibility audit")
    print("=" * 76)
    print(f"Model       : {info.device_name} ({info.product_type})")
    print(f"Chip        : {info.chip}")
    print(f"Board       : {info.board}")
    print(f"iOS         : {info.product_version}")
    print(f"Build       : {info.build_version}")
    print("-" * 76)
    print(f"Exact target: {'YES' if result['target_match'] else 'NO'}")
    print(f"Overall     : {result['overall']}")
    print("\nProject checks:")
    for item in result["checks"]:
        print(f"\n[{item['status']}] {item['project']}")
        print(f"  Confidence: {item['confidence']}")
        print(f"  {item['reason']}")
        print(f"  Source: {item['source']}")
    print("\nProtection assessment:")
    protection = result["protection_assessment"]
    print(f"  [{protection['status']}] {protection['note']}")
    firmware = result["firmware_note"]
    print(f"\nFirmware note: [{firmware['status']}] {firmware['note']}")
    print("\nSafety: read-only; no exploit, patch, restore, or device write is performed.")
    print("=" * 76)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only jailbreak compatibility auditor for iPhone 12 / iOS 27.0."
    )
    parser.add_argument("--product-type", help="Example: iPhone13,2")
    parser.add_argument("--ios-version", help="Example: 27.0")
    parser.add_argument("--build", help="Example: 24A437")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    parser.add_argument("--sources", action="store_true", help="Print source index")
    args = parser.parse_args()

    if args.sources:
        print(json.dumps(SOURCES, ensure_ascii=False, indent=2))
        return 0

    info = collect_device(args)
    result = assess(info)
    payload = {"tool_version": VERSION, "device": asdict(info), "assessment": result}

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_report(info, result)

    if info.product_type == "unknown":
        return 2
    return 0 if result["target_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
