#!/bin/bash
# Run tests
#
# Usage:
#   ./test.sh
#

set -euo pipefail

cd "$(dirname "$0")"

echo "🧪 Running tests..."
echo ""

swift test

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
else
    echo ""
    echo "❌ Tests failed"
    exit 1
fi

