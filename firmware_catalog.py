#!/usr/bin/env python3
"""Read-only firmware metadata lookup; never downloads IPSW binaries."""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEVICE = "iPhone13,2"
TARGET_VERSION = "27.0"
TARGET_BUILD = "24A437"
SOURCES = (
    ("ipsw.info", f"https://ipsw.info/api/v1/firmware/{DEVICE}/{TARGET_BUILD}"),
    ("ipsw.me", f"https://api.ipsw.me/v4/device/{DEVICE}?type=ipsw"),
)
TIMEOUT = 12

def _get_json(url: str):
    req = Request(url, headers={"Accept": "application/json", "User-Agent": "i12-jailbreak-lab/1.4 (metadata-only)"})
    with urlopen(req, timeout=TIMEOUT) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        if int(response.headers.get("Content-Length", "0") or 0) > 2_000_000:
            raise RuntimeError("Response too large; refusing metadata payload")
        data = response.read(2_000_001)
        if len(data) > 2_000_000:
            raise RuntimeError("Response too large; refusing metadata payload")
        return json.loads(data.decode("utf-8"))

def _normalise(entry: dict, source: str) -> dict:
    return {
        "device": entry.get("identifier") or DEVICE,
        "version": entry.get("version"),
        "build": entry.get("buildid") or entry.get("build"),
        "signed": entry.get("signed") if isinstance(entry.get("signed"), bool) else None,
        "file_size_bytes": entry.get("filesize") or entry.get("size"),
        "release_date": entry.get("releasedate") or entry.get("releasedate"),
        "source": source,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "binary_downloaded": False,
    }

def lookup(fetch=_get_json) -> dict:
    errors = []
    for source, url in SOURCES:
        try:
            payload = fetch(url)
            if isinstance(payload, dict) and isinstance(payload.get("firmwares"), list):
                entries = payload["firmwares"]
            elif isinstance(payload, list):
                entries = payload
            elif isinstance(payload, dict):
                entries = [payload]
            else:
                raise ValueError("Unexpected API response format")
            match = next((x for x in entries if isinstance(x, dict) and
                          (x.get("buildid") or x.get("build")) == TARGET_BUILD), None)
            if match is None:
                return {"status": "not_found", "target": {"device": DEVICE, "version": TARGET_VERSION, "build": TARGET_BUILD},
                        "source": source, "message": "Catalog did not return the requested build. This is not proof that the build never existed."}
            result = _normalise(match, source)
            result["target_version_match"] = result["version"] == TARGET_VERSION
            result["target_build_match"] = result["build"] == TARGET_BUILD
            result["status"] = "found"
            result["interpretation"] = "Signing status is third-party catalog metadata; verify with Apple's signing service before any restore."
            return result
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, RuntimeError) as exc:
            errors.append(f"{source}: {type(exc).__name__}: {exc}")
    return {"status": "unavailable", "target": {"device": DEVICE, "version": TARGET_VERSION, "build": TARGET_BUILD},
            "errors": errors, "binary_downloaded": False,
            "message": "Firmware metadata services are unavailable. No firmware file was requested or downloaded."}

def main():
    p = argparse.ArgumentParser(description="Look up iPhone 12 firmware metadata without downloading IPSW")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    report = lookup()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("i12 Jailbreak Lab v1.4 — firmware metadata only")
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "found" else 2

if __name__ == "__main__":
    sys.exit(main())
