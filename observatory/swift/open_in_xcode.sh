#!/bin/bash
# Open Swift Package in Xcode for App Store submission

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Opening ObservatoryApp in Xcode..."
echo ""

# Open Package.swift in Xcode (creates project automatically)
open -a Xcode Package.swift

echo ""
echo "✅ Xcode should now be opening..."
echo ""
echo "📋 Next steps in Xcode:"
echo "   1. Wait for Xcode to open and index the project"
echo "   2. Product > Scheme > ObservatoryApp (select executable)"
echo "   3. For App Store submission:"
echo "      - File > New > Project > macOS > App"
echo "      - Name: ObservatoryApp"
echo "      - Bundle ID: com.nkllon.ObservatoryApp"
echo "      - Copy Swift files from Sources/ObservatoryApp/"
echo "      - Configure signing in target settings"
echo ""
echo "   OR use Xcode's 'Create App' from Swift Package:"
echo "   - Right-click Package.swift > Create App"
echo ""

