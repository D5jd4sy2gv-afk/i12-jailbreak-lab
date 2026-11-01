#!/usr/bin/env python3
"""Validate the dated, read-only jailbreak evidence ledger."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_TARGET = {"product_type": "iPhone13,2", "chip": "A14 Bionic", "ios": "27.0", "build": "24A437"}
VALID_CONFIDENCE = {"high", "medium", "low"}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", nargs="?", default="evidence_database.json")
    args = parser.parse_args()
    data = json.loads(Path(args.database).read_text(encoding="utf-8"))
    errors = []
    if data.get("schema_version") != 1: errors.append("unsupported schema_version")
    if data.get("target") != REQUIRED_TARGET: errors.append("target does not match the configured iPhone 12 target")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries: errors.append("entries must be a non-empty list")
    seen = set()
    for i, item in enumerate(entries if isinstance(entries, list) else []):
        for key in ("id", "name", "status", "confidence", "detail", "url", "checked"):
            if not item.get(key): errors.append(f"entry[{i}] missing {key}")
        if item.get("id") in seen: errors.append(f"duplicate id: {item.get('id')}")
        seen.add(item.get("id"))
        if item.get("confidence") not in VALID_CONFIDENCE: errors.append(f"entry[{i}] invalid confidence")
        parsed = urlparse(item.get("url", ""))
        if parsed.scheme != "https" or not parsed.netloc: errors.append(f"entry[{i}] URL must be HTTPS")
    if errors:
        print("Evidence database: INVALID")
        for error in errors: print(f"- {error}")
        return 1
    print(f"Evidence database: OK ({len(entries)} entries; snapshot {data['snapshot_date']})")
    print(f"Target: {data['target']['product_type']} / {data['target']['chip']} / iOS {data['target']['ios']} ({data['target']['build']})")
    print(f"Assessment: {data['overall_assessment']}")
    print("Reminder: another device/build's successful test is not evidence for this exact target.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
