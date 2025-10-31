#!/bin/bash
# Install Beast Observatory sync service as macOS launchd daemon
#
# Usage:
#   ./scripts/install_sync_service_macos.sh
#
# Requirements:
#   - macOS (Darwin)
#   - beast-observatory installed (pip install beast-observatory)
#   - LaunchAgent directory exists (~/Library/LaunchAgents)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OBSERVATORY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PLIST_NAME="com.nkllon.beast-observatory-sync.plist"
PLIST_SOURCE="$SCRIPT_DIR/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

# Check macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "❌ ERROR: This script is for macOS only"
    echo "   Current OS: $(uname)"
    exit 1
fi

echo "🍎 Installing Beast Observatory sync service for macOS..."
echo ""

# Check if beast-observatory is installed
if ! command -v beast-observatory-sync &> /dev/null; then
    echo "⚠️  WARNING: beast-observatory-sync not found in PATH"
    echo "   Install with: pip install beast-observatory"
    echo "   Or update plist ProgramArguments to use python3 directly"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create LaunchAgents directory if missing
mkdir -p "$HOME/Library/LaunchAgents"
echo "✅ LaunchAgents directory ready"

# Create log directory
mkdir -p "$HOME/Library/Logs/beast-observatory"
echo "✅ Log directory ready"

# Update plist with actual paths
if [[ -f "$PLIST_SOURCE" ]]; then
    # Use current user's home and observatory directory
    sed -e "s|/Users/lou|$HOME|g" \
        -e "s|/Volumes/lemon/cursor/beast-mailbox-core|$OBSERVATORY_DIR/..|g" \
        "$PLIST_SOURCE" > "$PLIST_DEST"
    echo "✅ Plist created: $PLIST_DEST"
else
    echo "❌ ERROR: Plist template not found: $PLIST_SOURCE"
    exit 1
fi

# Check if already loaded
if launchctl list | grep -q "$PLIST_NAME"; then
    echo "⚠️  Service already loaded, unloading first..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
fi

# Load service
echo ""
echo "📦 Loading service..."
launchctl load "$PLIST_DEST"
echo "✅ Service loaded"

# Start service
echo ""
echo "🚀 Starting service..."
launchctl start "$PLIST_NAME"
echo "✅ Service started"

echo ""
echo "📊 Service Status:"
launchctl list | grep "$PLIST_NAME" || echo "   Service may still be starting..."

echo ""
echo "📋 Useful Commands:"
echo "   Check status:  launchctl list | grep beast-observatory"
echo "   View logs:     tail -f ~/Library/Logs/beast-observatory/sync.log"
echo "   Stop service:  launchctl stop $PLIST_NAME"
echo "   Start service: launchctl start $PLIST_NAME"
echo "   Unload:        launchctl unload $PLIST_DEST"
echo "   Reload:        launchctl unload $PLIST_DEST && launchctl load $PLIST_DEST"
echo ""
echo "✅ Installation complete!"

