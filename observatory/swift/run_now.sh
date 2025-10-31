#!/bin/bash
# Run ObservatoryApp locally - TODAY!
# Usage: ./run_now.sh

set -e

cd "$(dirname "$0")"

echo "🚀 Running Beast Observatory App..."
echo ""

# Build first
echo "🔨 Building..."
swift build -c release || {
    echo "⚠️  Release build failed, trying debug..."
    swift build
}

echo ""
echo "✅ Build complete!"
echo ""
echo "🎯 Launching app..."
echo "   Look for menu bar icon (top right of menu bar)"
echo "   Click icon → Menu opens"
echo "   Press ⌘C → Chat with Apple Intelligence opens!"
echo ""

# Run the app
swift run ObservatoryApp

