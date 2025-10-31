#!/bin/bash
# Complete App Store submission script
# Usage: ./submit_to_appstore.sh
#
# Loads credentials from ~/.env
# Set up your credentials there first (see .env.example)

set -euo pipefail

# Try to extract Team ID and Apple ID from Xcode first
extract_xcode_credentials() {
    # Try to get Team ID from Xcode project
    if [ -f "${PROJECT_NAME}.xcodeproj/project.pbxproj" ]; then
        XCODE_TEAM_ID=$(grep -m 1 "DEVELOPMENT_TEAM" "${PROJECT_NAME}.xcodeproj/project.pbxproj" 2>/dev/null | \
            sed -E 's/.*DEVELOPMENT_TEAM = ([^;]*).*/\1/' | tr -d ' ' | tr -d '"')
        if [ -n "$XCODE_TEAM_ID" ] && [ "$XCODE_TEAM_ID" != "" ]; then
            if [ -z "${TEAM_ID:-}" ]; then
                TEAM_ID="$XCODE_TEAM_ID"
                echo "📋 Using Team ID from Xcode project: $TEAM_ID"
            fi
        fi
    fi
    
    # Try to get Apple ID from Xcode preferences (simpler - just use what's in accounts)
    # Xcode stores this, but it's complex to extract. Better to rely on user setting it.
}

# Extract from Xcode if available
extract_xcode_credentials

# Load credentials from home directory .env file (overrides Xcode values if set)
if [ -f "$HOME/.env" ]; then
    echo "📋 Loading credentials from ~/.env..."
    source "$HOME/.env"
else
    echo "⚠️  Note: ~/.env not found (optional - Xcode handles signing)"
    echo "   Create it if you need App-Specific Password or API Key for CLI"
    echo "   See .env.example for template"
fi

# Configuration (loaded from ~/.env or defaults)
PROJECT_NAME="${PROJECT_NAME:-ObservatoryApp}"
SCHEME="${SCHEME:-ObservatoryApp}"
BUNDLE_ID="${BUNDLE_ID:-com.nkllon.ObservatoryApp}"
TEAM_ID="${TEAM_ID:-}"
APPLE_ID="${APPLE_ID:-}"
APP_STORE_PASSWORD="${APP_STORE_PASSWORD:-}"
API_KEY_ID="${API_KEY_ID:-}"
API_ISSUER_ID="${API_ISSUER_ID:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
BUILD_DIR="./build"
ARCHIVE_PATH="$BUILD_DIR/${PROJECT_NAME}.xcarchive"
EXPORT_PATH="$BUILD_DIR/export"

# Check if Xcode project exists
if [ ! -f "${PROJECT_NAME}.xcodeproj/project.pbxproj" ]; then
    echo -e "${RED}❌ Error: ${PROJECT_NAME}.xcodeproj not found!${NC}"
    echo "   Create Xcode project first (see CREATE_XCODE_PROJECT.md)"
    exit 1
fi

# Check required environment variables
if [ -z "$TEAM_ID" ]; then
    echo -e "${YELLOW}⚠️  Warning: TEAM_ID not set${NC}"
    echo "   Set it via: export TEAM_ID=\"YOUR_TEAM_ID\""
fi

if [ -z "$APPLE_ID" ] && [ -z "$API_KEY_ID" ]; then
    echo -e "${YELLOW}⚠️  Warning: Authentication not configured${NC}"
    echo "   Set APPLE_ID and APP_STORE_PASSWORD, or API_KEY_ID and API_ISSUER_ID"
fi

# Functions
log_step() {
    echo -e "${GREEN}$1${NC}"
}

log_error() {
    echo -e "${RED}❌ Error: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  Warning: $1${NC}"
}

# Step 1: Clean
log_step "🧹 Step 1: Cleaning build directory..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
mkdir -p "$EXPORT_PATH"

# Step 2: Clean Xcode project
log_step "🧹 Step 2: Cleaning Xcode project..."
xcodebuild clean \
    -project "${PROJECT_NAME}.xcodeproj" \
    -scheme "$SCHEME" \
    -configuration Release || log_warning "Clean may have failed (this is OK)"

# Step 3: Build
log_step "🔨 Step 3: Building for Release..."
xcodebuild build \
    -project "${PROJECT_NAME}.xcodeproj" \
    -scheme "$SCHEME" \
    -configuration Release \
    -arch arm64 \
    -arch x86_64 \
    -derivedDataPath "$BUILD_DIR" \
    CODE_SIGN_IDENTITY="Apple Development" \
    CODE_SIGN_STYLE="Automatic" \
    DEVELOPMENT_TEAM="$TEAM_ID" || {
    log_error "Build failed"
    exit 1
}

log_step "✅ Build successful"

# Step 4: Archive
log_step "📦 Step 4: Creating archive..."
xcodebuild archive \
    -project "${PROJECT_NAME}.xcodeproj" \
    -scheme "$SCHEME" \
    -configuration Release \
    -archivePath "$ARCHIVE_PATH" \
    -derivedDataPath "$BUILD_DIR" \
    CODE_SIGN_IDENTITY="Apple Development" \
    CODE_SIGN_STYLE="Automatic" \
    DEVELOPMENT_TEAM="$TEAM_ID" || {
    log_error "Archive failed"
    exit 1
}

if [ ! -d "$ARCHIVE_PATH" ]; then
    log_error "Archive not created"
    exit 1
fi

log_step "✅ Archive created: $ARCHIVE_PATH"

# Step 5: Export
log_step "📤 Step 5: Exporting archive..."
cat > "$BUILD_DIR/ExportOptions.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
    <key>teamID</key>
    <string>$TEAM_ID</string>
    <key>signingStyle</key>
    <string>automatic</string>
    <key>uploadBitcode</key>
    <false/>
    <key>uploadSymbols</key>
    <true/>
    <key>compileBitcode</key>
    <false/>
    <key>destination</key>
    <string>export</string>
    <key>stripSwiftSymbols</key>
    <true/>
</dict>
</plist>
EOF

xcodebuild -exportArchive \
    -archivePath "$ARCHIVE_PATH" \
    -exportPath "$EXPORT_PATH" \
    -exportOptionsPlist "$BUILD_DIR/ExportOptions.plist" || {
    log_error "Export failed"
    exit 1
}

# Find exported app or pkg
EXPORTED_FILE=""
if [ -f "$EXPORT_PATH/${PROJECT_NAME}.pkg" ]; then
    EXPORTED_FILE="$EXPORT_PATH/${PROJECT_NAME}.pkg"
elif [ -f "$EXPORT_PATH/${PROJECT_NAME}.app" ]; then
    EXPORTED_FILE="$EXPORT_PATH/${PROJECT_NAME}.app"
elif [ -f "$EXPORT_PATH/${PROJECT_NAME}.zip" ]; then
    EXPORTED_FILE="$EXPORT_PATH/${PROJECT_NAME}.zip"
else
    log_error "Exported file not found in $EXPORT_PATH"
    ls -la "$EXPORT_PATH"
    exit 1
fi

log_step "✅ Export successful: $EXPORTED_FILE"

# Step 6: Validate (optional but recommended)
if [ -n "$API_KEY_ID" ] && [ -n "$API_ISSUER_ID" ]; then
    log_step "✅ Step 6: Validating with API Key..."
    xcrun altool --validate-app \
        -f "$EXPORTED_FILE" \
        -t macos \
        --apiKey "$API_KEY_ID" \
        --apiIssuer "$API_ISSUER_ID" || {
        log_error "Validation failed"
        exit 1
    }
elif [ -n "$APPLE_ID" ] && [ -n "$APP_STORE_PASSWORD" ]; then
    log_step "✅ Step 6: Validating with App-Specific Password..."
    xcrun altool --validate-app \
        -f "$EXPORTED_FILE" \
        -t macos \
        -u "$APPLE_ID" \
        -p "$APP_STORE_PASSWORD" || {
        log_error "Validation failed"
        exit 1
    }
else
    log_warning "Skipping validation (no credentials provided)"
fi

log_step "✅ Validation successful"

# Step 7: Upload
if [ -n "$API_KEY_ID" ] && [ -n "$API_ISSUER_ID" ]; then
    log_step "🚀 Step 7: Uploading to App Store Connect (API Key)..."
    xcrun altool --upload-app \
        -f "$EXPORTED_FILE" \
        -t macos \
        --apiKey "$API_KEY_ID" \
        --apiIssuer "$API_ISSUER_ID" || {
        log_error "Upload failed"
        exit 1
    }
elif [ -n "$APPLE_ID" ] && [ -n "$APP_STORE_PASSWORD" ]; then
    log_step "🚀 Step 7: Uploading to App Store Connect (App-Specific Password)..."
    xcrun altool --upload-app \
        -f "$EXPORTED_FILE" \
        -t macos \
        -u "$APPLE_ID" \
        -p "$APP_STORE_PASSWORD" || {
        log_error "Upload failed"
        exit 1
    }
else
    log_error "Cannot upload: No credentials provided"
    log_warning "Archive ready at: $ARCHIVE_PATH"
    log_warning "Exported app ready at: $EXPORTED_FILE"
    log_warning "Upload manually or set credentials and run again"
    exit 1
fi

log_step "✅ Upload complete!"
echo ""
echo -e "${GREEN}🎉 Success! Check App Store Connect for processing status.${NC}"
echo ""
echo "Next steps:"
echo "  1. Go to App Store Connect > My Apps > ObservatoryApp"
echo "  2. Wait for processing (usually 15-30 minutes)"
echo "  3. Select build in Version > Build"
echo "  4. Submit for Review"
echo ""

