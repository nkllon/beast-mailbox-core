#!/bin/bash
# Build ObservatoryApp from command line
#
# Usage:
#   ./build.sh [debug|release]
#

set -euo pipefail

cd "$(dirname "$0")"

BUILD_TYPE="${1:-debug}"
BUILD_DIR=".build"

echo "🔨 Building ObservatoryApp ($BUILD_TYPE mode)..."
echo ""

# Build
if [ "$BUILD_TYPE" = "release" ]; then
    swift build -c release
    EXECUTABLE=".build/release/ObservatoryApp"
else
    swift build
    EXECUTABLE=".build/debug/ObservatoryApp"
fi

if [ -f "$EXECUTABLE" ]; then
    echo ""
    echo "✅ Build successful!"
    echo "   Executable: $EXECUTABLE"
    echo ""
    echo "To run:"
    echo "   $EXECUTABLE"
    echo ""
    echo "Or install to Applications:"
    echo "   ./install.sh"
else
    echo "❌ Build failed - executable not found"
    exit 1
fi

