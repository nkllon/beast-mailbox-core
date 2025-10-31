#!/bin/bash
# Setup Swift Package Manager project structure
#
# Usage:
#   ./setup.sh
#

set -euo pipefail

cd "$(dirname "$0")"

echo "📦 Setting up Swift Package Manager project..."
echo ""

# Create directories
mkdir -p Sources/ObservatoryApp/MenuBar
mkdir -p Sources/ObservatoryApp/Services
mkdir -p Sources/ObservatoryApp/Intelligence
mkdir -p Sources/ObservatoryApp/Shortcuts
mkdir -p Tests/ObservatoryAppTests

# Move files if they exist in wrong location
if [ -f "ObservatoryAppApp.swift" ] && [ ! -f "Sources/ObservatoryApp/main.swift" ]; then
    echo "Moving ObservatoryAppApp.swift to main.swift..."
    mv ObservatoryAppApp.swift Sources/ObservatoryApp/main.swift
fi

if [ -d "MenuBar" ] && [ ! -d "Sources/ObservatoryApp/MenuBar" ]; then
    echo "Moving MenuBar files..."
    cp -r MenuBar/* Sources/ObservatoryApp/MenuBar/ 2>/dev/null || true
fi

if [ -d "Services" ] && [ ! -d "Sources/ObservatoryApp/Services" ]; then
    echo "Moving Services files..."
    cp -r Services/* Sources/ObservatoryApp/Services/ 2>/dev/null || true
fi

# Verify Package.swift exists
if [ ! -f "Package.swift" ]; then
    echo "❌ ERROR: Package.swift not found"
    exit 1
fi

# Validate package
echo "Validating package..."
swift package describe 2>&1 | head -5 || {
    echo "⚠️  Package validation failed - may need to fix Package.swift"
}

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Review Sources/ObservatoryApp/ structure"
echo "  2. Build: swift build"
echo "  3. Run: swift run ObservatoryApp"
echo ""

