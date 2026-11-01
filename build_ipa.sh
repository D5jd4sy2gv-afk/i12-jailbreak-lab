#!/bin/bash
set -euo pipefail

# Build a signed IPA on macOS with Xcode. This script does not modify an iPhone.
# Usage: ./build_ipa.sh [TEAM_ID] [BUNDLE_ID]
TEAM_ID="${1:-${DEVELOPMENT_TEAM:-}}"
BUNDLE_ID="${2:-com.research.i12jailbreaklab}"
PROJECT="i12_Jailbreak_Lab.xcodeproj"
SCHEME="i12_Jailbreak_Lab"
OUT="$(pwd)/build-ipa"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "ERROR: IPA compilation/signing requires macOS and Xcode."
  exit 2
fi
if ! command -v xcodebuild >/dev/null 2>&1; then
  echo "ERROR: Xcode command-line tools are not installed."
  exit 2
fi
if [[ -z "$TEAM_ID" ]]; then
  echo "Usage: $0 YOUR_10_CHARACTER_TEAM_ID [BUNDLE_ID]"
  echo "Or set DEVELOPMENT_TEAM in the environment."
  exit 2
fi

mkdir -p "$OUT"
cat > "$OUT/ExportOptions.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>method</key><string>ad-hoc</string>
  <key>teamID</key><string>${TEAM_ID}</string>
  <key>signingStyle</key><string>automatic</string>
  <key>stripSwiftSymbols</key><true/>
  <key>compileBitcode</key><false/>
  <key>destination</key><string>export</string>
</dict></plist>
PLIST

xcodebuild -project "$PROJECT" -scheme "$SCHEME" \
  -configuration Release -destination 'generic/platform=iOS' \
  -archivePath "$OUT/${SCHEME}.xcarchive" \
  PRODUCT_BUNDLE_IDENTIFIER="$BUNDLE_ID" \
  DEVELOPMENT_TEAM="$TEAM_ID" \
  CODE_SIGN_STYLE=Automatic archive

xcodebuild -exportArchive \
  -archivePath "$OUT/${SCHEME}.xcarchive" \
  -exportPath "$OUT/export" \
  -exportOptionsPlist "$OUT/ExportOptions.plist"

IPA=$(find "$OUT/export" -maxdepth 1 -name '*.ipa' -print -quit)
if [[ -z "$IPA" ]]; then
  echo "ERROR: Xcode finished without producing an IPA."
  exit 3
fi
/usr/bin/codesign -dv --verbose=2 "$OUT/${SCHEME}.xcarchive/Products/Applications/${SCHEME}.app" 2>&1 | head -20 || true
echo "IPA ready: $IPA"
