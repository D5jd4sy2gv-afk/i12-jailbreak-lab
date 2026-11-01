#!/usr/bin/env python3
"""Evidence ledger for iPhone 12 / iOS 27 jailbreak research.
Read-only; makes no device changes and does not run exploits.
"""
from __future__ import annotations
import argparse, json
from datetime import date

VERSION = "1.4"
TARGET = {"model": "iPhone 12", "product_type": "iPhone13,2", "chip": "A14 Bionic", "platform": "t8101", "ios": "27.0", "build": "24A437"}
EVIDENCE = [
 {"id":"E01", "topic":"Calif Hexacon demo", "status":"CONFIRMED_DEMO", "confidence":"HIGH", "detail":"A public untethered root demo was reported on iPhone 18 Pro running iOS 27.0.1. The researchers have not published a public end-user tool or technical exploit chain in the cited reporting.", "url":"https://decrypt.co/381177/hackers-jailbreak-iphone-18-pro-survives-reboot"},
 {"id":"E02", "topic":"A14 / iPhone 12 compatibility", "status":"NOT_ESTABLISHED", "confidence":"HIGH", "detail":"The iPhone 18 Pro demonstration does not establish compatibility with iPhone 12 / A14 or build 24A437. No reproducible A14 test is identified by the cited report.", "url":"https://www.iclarified.com/102876/untethered-ios-2701-jailbreak-demonstrated-on-iphone-18-pro-video"},
 {"id":"E03", "topic":"Liter8", "status":"NOT_COMPATIBLE_BY_STATED_SCOPE", "confidence":"HIGH", "detail":"The project explicitly targets iPhone 11 (n104ap); it does not claim iPhone 12 / A14 support.", "url":"https://github.com/Xplo8E/Liter8"},
 {"id":"E04", "topic":"iOS 27.0 signing", "status":"UNSIGNED_REPORTED", "confidence":"HIGH", "detail":"Third-party firmware catalogs report build 24A437 as unsigned. Do not assume it can be restored or downgraded to; check Apple's current signing status before any restore.", "url":"https://ipsw.me/iPhone13,2/"},
 {"id":"E05", "topic":"iOS 27.2 security fixes", "status":"REPORTED_PATCH_RELEASE", "confidence":"MEDIUM", "detail":"A community fact-check tracker reports iOS 27.2 shipped 2026-10-27 and fixed several Calif-credited vulnerabilities. This is a secondary tracker, not proof of the exact exploit chain or A14 applicability.", "url":"https://github.com/iMaxTomas/ios27-jb-tracker"},
]

def build_report():
    return {
      "tool_version": VERSION,
      "checked_date": date.today().isoformat(),
      "target": TARGET,
      "overall": "NO_PUBLIC_REPRODUCIBLE_A14_FULL_JAILBREAK_ESTABLISHED",
      "evidence": EVIDENCE,
      "requirements_for_claiming_compatibility": [
        "A public technical write-up or source identifying the vulnerability chain.",
        "A reproducible test on iPhone13,2 / A14, not merely a newer iPhone model.",
        "Exact iOS build coverage including 24A437.",
        "Evidence for each required privilege and platform-mitigation bypass.",
        "A reviewed recovery procedure and clear tethered/untethered behavior."
      ],
      "safety": [
        "This program only prints a research evidence report; it does not contact or modify an iPhone.",
        "Do not restore to an unsigned IPSW or install unknown jailbreak profiles/IPAs.",
        "A demo on another model/build is not proof of A14 compatibility."
      ]
    }

def main():
    p=argparse.ArgumentParser(description="Print evidence status for iPhone 12 / iOS 27.0 jailbreak research")
    p.add_argument('--json', action='store_true')
    a=p.parse_args(); r=build_report()
    if a.json: print(json.dumps(r,ensure_ascii=False,indent=2)); return
    print(f"i12 Jailbreak Lab v{VERSION} — evidence report")
    print("Target:", " / ".join(TARGET[k] for k in ("model","chip","ios","build")))
    print("Overall:",r['overall'])
    for e in EVIDENCE: print(f"\n[{e['status']}] {e['topic']} ({e['confidence']})\n{e['detail']}\n{e['url']}")
    print("\nNo exploit is run and no device is modified.")
if __name__=='__main__': main()
