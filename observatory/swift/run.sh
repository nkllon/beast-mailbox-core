#!/bin/bash
# Run ObservatoryApp (builds first if needed)
#
# Usage:
#   ./run.sh [debug|release]
#

set -euo pipefail

cd "$(dirname "$0")"

BUILD_TYPE="${1:-debug}"

# Build first
./build.sh "$BUILD_TYPE"

# Run
if [ "$BUILD_TYPE" = "release" ]; then
    EXECUTABLE=".build/release/ObservatoryApp"
else
    EXECUTABLE=".build/debug/ObservatoryApp"
fi

echo "🚀 Running ObservatoryApp..."
echo ""

"$EXECUTABLE"

