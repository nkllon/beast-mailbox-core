#!/bin/bash

echo "🔨 Building ObservatoryApp..."

# Clean previous build
swift package clean

# Attempt to build
if swift build; then
    echo "✅ Build successful!"
    echo ""
    echo "To run the app:"
    echo "  swift run ObservatoryApp"
    echo ""
    echo "To build for release:"
    echo "  swift build -c release"
else
    echo "❌ Build failed!"
    echo ""
    echo "Check the error messages above for specific issues."
    exit 1
fi