#!/bin/bash
# Run Observatory sync service
#
# Usage:
#   ./scripts/run_sync_service.sh
#
# Environment variables (see sync_service.py for full list):
#   SONARCLOUD_PROJECT_KEY - SonarCloud project key
#   SONARCLOUD_TOKEN - SonarCloud API token
#   PROMETHEUS_PUSHGATEWAY_URL - Pushgateway URL
#   SYNC_INTERVAL_HOURS - Sync interval (default: 1)

set -euo pipefail

cd "$(dirname "$0")/.."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 not found"
    exit 1
fi

# Check dependencies
if ! python3 -c "import aiohttp" 2>/dev/null; then
    echo "⚠️  Installing aiohttp..."
    pip3 install aiohttp || {
        echo "❌ ERROR: Failed to install aiohttp"
        exit 1
    }
fi

# Set defaults
export SONARCLOUD_PROJECT_KEY="${SONARCLOUD_PROJECT_KEY:-nkllon_beast-mailbox-core}"
export PROMETHEUS_PUSHGATEWAY_URL="${PROMETHEUS_PUSHGATEWAY_URL:-http://localhost:9091}"
export SYNC_INTERVAL_HOURS="${SYNC_INTERVAL_HOURS:-1}"
export GIT_BRANCH="${GIT_BRANCH:-main}"

# Get version from pyproject.toml if available
if [ -f "../../pyproject.toml" ]; then
    VERSION=$(grep '^version = ' ../../pyproject.toml | cut -d'"' -f2 || echo "unknown")
    export PACKAGE_VERSION="$VERSION"
fi

echo "🚀 Starting Observatory sync service..."
echo "   Project: $SONARCLOUD_PROJECT_KEY"
echo "   Pushgateway: $PROMETHEUS_PUSHGATEWAY_URL"
echo "   Interval: ${SYNC_INTERVAL_HOURS} hour(s)"
echo ""

# Add src to path (handle unset PYTHONPATH)
export PYTHONPATH="$(pwd)/src:$(pwd)/../../src:${PYTHONPATH:-}"

# Run sync service
python3 src/sync_service.py

