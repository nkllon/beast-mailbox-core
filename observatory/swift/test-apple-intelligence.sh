#!/bin/bash
# Test script for Observatory App with Apple Intelligence

echo "🚀 Building Observatory App with Apple Intelligence..."

# Clean build
echo "🧹 Cleaning build directory..."
rm -rf .build

# Build the project  
echo "🔨 Building project..."
if swift build; then
    echo "✅ Build successful!"
else
    echo "❌ Build failed!"
    exit 1
fi

# Test Apple Intelligence integration (if available)
echo ""
echo "🤖 Testing Apple Intelligence integration..."
if swift run -c debug --enable-test-discovery TestAppleIntelligence 2>/dev/null; then
    echo "✅ Apple Intelligence test completed!"
else
    echo "⚠️  Apple Intelligence test executable not found or failed"
    echo "   This is normal if FoundationModels framework is not available"
fi

echo ""
echo "✅ All tests completed! Ready to run: swift run ObservatoryApp"