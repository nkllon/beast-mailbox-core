# macOS App Store Submission - Command Line Procedure

**Goal:** Submit macOS app to App Store entirely via command line  
**Target:** ObservatoryApp (Beast Observatory)  
**Date:** 2025-10-31  
**Status:** Reusable procedure for future submissions

---

## Overview

**Complete command-line workflow:**
1. Build project (xcodebuild)
2. Archive app (xcodebuild archive)
3. Export archive (xcodebuild -exportArchive)
4. Validate & upload (xcrun altool / xcodebuild -upload)

**Time:** ~10-15 minutes from build to submission

---

## Prerequisites

### 1. Apple Developer Account

```bash
# Verify you're signed in
xcrun altool --list-providers

# Or check certificates
security find-identity -v -p codesigning
```

### 2. App Store Connect API Key

**Create in App Store Connect:**
1. Users and Access > Keys > App Store Connect API
2. Generate API Key
3. Download `.p8` key file
4. Save Key ID and Issuer ID

**Or use App-Specific Password:**
```bash
# Generate in appleid.apple.com > App-Specific Passwords
export APP_STORE_PASSWORD="your-app-specific-password"
export APPLE_ID="your-apple-id@example.com"
```

### 3. Bundle Identifier & App Store Connect Listing

- Bundle ID must exist in App Store Connect
- App listing created in App Store Connect
- Version matches what you're submitting

---

## Step 1: Build Project

### Option A: Build from Swift Package (Current Setup)

```bash
cd observatory/swift

# Clean build
swift package clean
swift package reset

# Build for release
swift build -c release

# Verify build succeeded
if [ $? -eq 0 ]; then
    echo "✅ Build successful"
else
    echo "❌ Build failed"
    exit 1
fi
```

### Option B: Build from Xcode Project

```bash
# If you have Xcode project
xcodebuild clean \
    -project ObservatoryApp.xcodeproj \
    -scheme ObservatoryApp \
    -configuration Release

xcodebuild build \
    -project ObservatoryApp.xcodeproj \
    -scheme ObservatoryApp \
    -configuration Release \
    -arch arm64 \
    -arch x86_64 \
    -derivedDataPath ./build
```

---

## Step 2: Create Archive

### Option A: Archive from Xcode Project

```bash
cd observatory/swift

# Archive
xcodebuild archive \
    -project ObservatoryApp.xcodeproj \
    -scheme ObservatoryApp \
    -configuration Release \
    -archivePath ./build/ObservatoryApp.xcarchive \
    -derivedDataPath ./build \
    CODE_SIGN_IDENTITY="Apple Development" \
    CODE_SIGN_STYLE="Automatic" \
    DEVELOPMENT_TEAM="YOUR_TEAM_ID"

# Verify archive created
if [ -d "./build/ObservatoryApp.xcarchive" ]; then
    echo "✅ Archive created: ./build/ObservatoryApp.xcarchive"
else
    echo "❌ Archive failed"
    exit 1
fi
```

### Option B: Archive from Package (Requires App Target)

**If using Swift Package with app target:**

```bash
xcodebuild archive \
    -scheme ObservatoryApp \
    -destination "generic/platform=macOS" \
    -archivePath ./build/ObservatoryApp.xcarchive \
    SKIP_INSTALL=NO \
    BUILD_LIBRARY_FOR_DISTRIBUTION=YES
```

**Note:** For App Store submission, you typically need an Xcode project, not just a Swift Package. However, you can create one programmatically or use Xcode GUI once.

---

## Step 3: Export Archive

### Export for App Store

```bash
# Create ExportOptions.plist
cat > ExportOptions.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
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

# Export archive
xcodebuild -exportArchive \
    -archivePath ./build/ObservatoryApp.xcarchive \
    -exportPath ./build/export \
    -exportOptionsPlist ExportOptions.plist

# Verify export
if [ -f "./build/export/ObservatoryApp.pkg" ] || [ -f "./build/export/ObservatoryApp.app" ]; then
    echo "✅ Export successful"
else
    echo "❌ Export failed"
    exit 1
fi
```

---

## Step 4: Validate Archive

### Validate Before Upload

```bash
# Using xcodebuild (recommended)
xcodebuild -validateApp \
    -archivePath ./build/ObservatoryApp.xcarchive \
    -exportPath ./build/export \
    -exportOptionsPlist ExportOptions.plist

# Or using xcrun altool (legacy, but works)
xcrun altool --validate-app \
    -f ./build/export/ObservatoryApp.pkg \
    -t macos \
    -u "$APPLE_ID" \
    -p "$APP_STORE_PASSWORD"
```

**For API Key:**
```bash
xcrun altool --validate-app \
    -f ./build/export/ObservatoryApp.pkg \
    -t macos \
    --apiKey "$API_KEY_ID" \
    --apiIssuer "$API_ISSUER_ID"
```

---

## Step 5: Upload to App Store Connect

### Upload Using xcodebuild

```bash
xcodebuild -uploadApp \
    -archivePath ./build/ObservatoryApp.xcarchive \
    -exportPath ./build/export \
    -exportOptionsPlist ExportOptions.plist \
    -username "$APPLE_ID" \
    -password "$APP_STORE_PASSWORD"
```

### Upload Using xcrun altool

```bash
# Using App-Specific Password
xcrun altool --upload-app \
    -f ./build/export/ObservatoryApp.pkg \
    -t macos \
    -u "$APPLE_ID" \
    -p "$APP_STORE_PASSWORD"

# Using API Key
xcrun altool --upload-app \
    -f ./build/export/ObservatoryApp.pkg \
    -t macos \
    --apiKey "$API_KEY_ID" \
    --apiIssuer "$API_ISSUER_ID"
```

### Upload Using Transporter (GUI Alternative)

```bash
# Install Transporter from Mac App Store first
open -a Transporter

# Or upload via command line
xcrun altool --upload-app -f ./build/export/ObservatoryApp.pkg -t macos
```

---

## Complete Automation Script

Creating `submit_to_appstore.sh` with all steps:

```bash
#!/bin/bash
# Complete App Store submission script
# Usage: ./submit_to_appstore.sh

set -euo pipefail

# Configuration
PROJECT_NAME="ObservatoryApp"
SCHEME="ObservatoryApp"
BUNDLE_ID="com.nkllon.ObservatoryApp"
TEAM_ID="${TEAM_ID:-}"  # Set via env var
APPLE_ID="${APPLE_ID:-}"  # Set via env var
APP_STORE_PASSWORD="${APP_STORE_PASSWORD:-}"  # Set via env var
API_KEY_ID="${API_KEY_ID:-}"  # Optional: API Key ID
API_ISSUER_ID="${API_ISSUER_ID:-}"  # Optional: API Issuer ID

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
BUILD_DIR="./build"
ARCHIVE_PATH="$BUILD_DIR/${PROJECT_NAME}.xcarchive"
EXPORT_PATH="$BUILD_DIR/export"

# Clean up
echo "🧹 Cleaning..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
mkdir -p "$EXPORT_PATH"

# Step 1: Build
echo "🔨 Building..."
xcodebuild clean \
    -project "${PROJECT_NAME}.xcodeproj" \
    -scheme "$SCHEME" \
    -configuration Release

xcodebuild build \
    -project "${PROJECT_NAME}.xcodeproj" \
    -scheme "$SCHEME" \
    -configuration Release \
    -arch arm64 \
    -arch x86_64 \
    -derivedDataPath "$BUILD_DIR"

# Step 2: Archive
echo "📦 Creating archive..."
xcodebuild archive \
    -project "${PROJECT_NAME}.xcodeproj" \
    -scheme "$SCHEME" \
    -configuration Release \
    -archivePath "$ARCHIVE_PATH" \
    -derivedDataPath "$BUILD_DIR" \
    CODE_SIGN_IDENTITY="Apple Development" \
    CODE_SIGN_STYLE="Automatic" \
    DEVELOPMENT_TEAM="$TEAM_ID"

# Step 3: Export
echo "📤 Exporting..."
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
    -exportOptionsPlist "$BUILD_DIR/ExportOptions.plist"

# Step 4: Validate
echo "✅ Validating..."
if [ -n "$API_KEY_ID" ] && [ -n "$API_ISSUER_ID" ]; then
    # Use API Key
    xcrun altool --validate-app \
        -f "$EXPORT_PATH/${PROJECT_NAME}.pkg" \
        -t macos \
        --apiKey "$API_KEY_ID" \
        --apiIssuer "$API_ISSUER_ID"
else
    # Use App-Specific Password
    xcrun altool --validate-app \
        -f "$EXPORT_PATH/${PROJECT_NAME}.pkg" \
        -t macos \
        -u "$APPLE_ID" \
        -p "$APP_STORE_PASSWORD"
fi

# Step 5: Upload
echo "🚀 Uploading to App Store Connect..."
if [ -n "$API_KEY_ID" ] && [ -n "$API_ISSUER_ID" ]; then
    # Use API Key
    xcrun altool --upload-app \
        -f "$EXPORT_PATH/${PROJECT_NAME}.pkg" \
        -t macos \
        --apiKey "$API_KEY_ID" \
        --apiIssuer "$API_ISSUER_ID"
else
    # Use App-Specific Password
    xcrun altool --upload-app \
        -f "$EXPORT_PATH/${PROJECT_NAME}.pkg" \
        -t macos \
        -u "$APPLE_ID" \
        -p "$APP_STORE_PASSWORD"
fi

echo "✅ Upload complete! Check App Store Connect for processing status."
```

---

## Quick Reference Commands

### Build & Archive

```bash
# Clean
xcodebuild clean -project App.xcodeproj -scheme App

# Build
xcodebuild build -project App.xcodeproj -scheme App -configuration Release

# Archive
xcodebuild archive -project App.xcodeproj -scheme App -archivePath App.xcarchive
```

### Export

```bash
# Export for App Store
xcodebuild -exportArchive \
    -archivePath App.xcarchive \
    -exportPath ./export \
    -exportOptionsPlist ExportOptions.plist
```

### Validate & Upload

```bash
# Validate
xcrun altool --validate-app -f App.pkg -t macos -u user@example.com -p password

# Upload
xcrun altool --upload-app -f App.pkg -t macos -u user@example.com -p password
```

---

## Environment Variables

Create `.env` file (don't commit):

```bash
# .env (add to .gitignore)
export TEAM_ID="YOUR_TEAM_ID"
export APPLE_ID="your-apple-id@example.com"
export APP_STORE_PASSWORD="your-app-specific-password"

# Or use API Key
export API_KEY_ID="your-api-key-id"
export API_ISSUER_ID="your-issuer-id"
```

**Source before running:**
```bash
source .env
./submit_to_appstore.sh
```

---

## Troubleshooting

### Issue: Code Signing Failed
```bash
# Check certificates
security find-identity -v -p codesigning

# Check team ID
xcodebuild -showBuildSettings -project App.xcodeproj | grep DEVELOPMENT_TEAM
```

### Issue: Archive Failed
```bash
# Check scheme exists
xcodebuild -list -project App.xcodeproj

# Verify target
xcodebuild -target App -showBuildSettings
```

### Issue: Upload Failed
```bash
# Check App Store Connect status
# Verify bundle ID exists in App Store Connect
# Check version matches
```

---

## Next Steps After Upload

1. **App Store Connect:**
   - Go to My Apps > ObservatoryApp
   - Processing status shows "Processing" → "Ready to Submit"
   - Select build in Version > Build
   - Submit for Review

2. **Monitor:**
   - Check App Store Connect for processing
   - Usually takes 15-30 minutes
   - Check email for status updates

---

**Status:** Complete command-line procedure documented and script ready!

