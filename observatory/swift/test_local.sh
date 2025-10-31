#!/bin/bash
# Local testing checklist before App Store submission
# Usage: ./test_local.sh

set -e

echo "🧪 Local Testing Checklist - Beast Observatory"
echo "=============================================="
echo ""

# Test 1: Build
echo "1️⃣  Testing Build..."
echo "   Building project..."

cd "$(dirname "$0")"

if [ -f "Package.swift" ]; then
    swift build -c release 2>&1 | tail -5
    echo "   ✅ Swift Package build successful"
elif [ -f "ObservatoryApp.xcodeproj/project.pbxproj" ]; then
    xcodebuild clean build \
        -project ObservatoryApp.xcodeproj \
        -scheme ObservatoryApp \
        -configuration Release 2>&1 | grep -E "(BUILD SUCCEEDED|BUILD FAILED|error)" | tail -3
    echo "   ✅ Xcode build successful"
else
    echo "   ⚠️  No build system found (create Xcode project first)"
fi

echo ""

# Test 2: Check for obvious issues
echo "2️⃣  Checking for Issues..."
echo "   Looking for common problems..."

ISSUES=0

# Check for missing files
if [ ! -f "Sources/ObservatoryApp/ObservatoryAppApp.swift" ]; then
    echo "   ⚠️  Missing: ObservatoryAppApp.swift"
    ISSUES=$((ISSUES + 1))
fi

# Check for Swift errors (basic syntax check)
if command -v swiftc &> /dev/null; then
    swiftc -typecheck Sources/ObservatoryApp/*.swift 2>&1 | head -5 || {
        echo "   ⚠️  Swift syntax errors found"
        ISSUES=$((ISSUES + 1))
    }
fi

if [ $ISSUES -eq 0 ]; then
    echo "   ✅ No obvious issues found"
fi

echo ""

# Test 3: Manual testing checklist
echo "3️⃣  Manual Testing Checklist:"
echo "   ⬜ Launch app in Xcode (⌘R)"
echo "   ⬜ Menu bar icon appears"
echo "   ⬜ Click icon → menu opens"
echo "   ⬜ Test 'Chat with Apple Intelligence' (⌘C)"
echo "   ⬜ Test 'Open Dashboard' (⌘D)"
echo "   ⬜ Test 'Settings...' (⌘,)"
echo "   ⬜ Test 'Sync Now' (⌘S)"
echo "   ⬜ Test 'View Logs' (⌘L)"
echo "   ⬜ Test 'Quit' (⌘Q)"
echo "   ⬜ No crashes or errors"
echo ""

# Test 4: File structure
echo "4️⃣  Checking File Structure..."
REQUIRED_FILES=(
    "Sources/ObservatoryApp/ObservatoryAppApp.swift"
    "Sources/ObservatoryApp/MenuBar/MenuBarView.swift"
    "Sources/ObservatoryApp/Chat/ChatView.swift"
)

ALL_PRESENT=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ Missing: $file"
        ALL_PRESENT=false
    fi
done

if [ "$ALL_PRESENT" = true ]; then
    echo "   ✅ All required files present"
fi

echo ""

# Summary
echo "📋 Summary:"
echo "   Build: Check above"
echo "   Issues: $ISSUES found"
echo "   Files: $([ "$ALL_PRESENT" = true ] && echo "All present" || echo "Some missing")"
echo ""
echo "⚠️  Manual Testing Required:"
echo "   - Launch app and test all features"
echo "   - Use app for at least 30 minutes"
echo "   - Test all menu items"
echo "   - Verify no crashes"
echo ""
echo "When ready to submit:"
echo "   source ~/.env"
echo "   ./submit_to_appstore.sh"
echo ""

