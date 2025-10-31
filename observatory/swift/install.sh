#!/bin/bash
# Install ObservatoryApp to Applications
#
# Usage:
#   ./install.sh
#

set -euo pipefail

cd "$(dirname "$0")"

echo "📦 Building release version..."
swift build -c release

EXECUTABLE=".build/release/ObservatoryApp"
APP_NAME="ObservatoryApp"
APP_DIR="$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Create .app bundle structure
echo "📱 Creating app bundle..."
rm -rf "$APP_DIR"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

# Copy executable
cp "$EXECUTABLE" "$MACOS_DIR/$APP_NAME"
chmod +x "$MACOS_DIR/$APP_NAME"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.nkllon.ObservatoryApp</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>15.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
EOF

# Install to Applications
INSTALL_DIR="$HOME/Applications"
echo "📥 Installing to $INSTALL_DIR..."

if [ -d "$INSTALL_DIR" ]; then
    cp -r "$APP_DIR" "$INSTALL_DIR/"
    echo "✅ Installed to $INSTALL_DIR/$APP_DIR"
    echo ""
    echo "To run:"
    echo "   open $INSTALL_DIR/$APP_DIR"
else
    echo "⚠️  Applications directory not found, app bundle created: $APP_DIR"
    echo "   Copy manually: cp -r $APP_DIR $INSTALL_DIR/"
fi

