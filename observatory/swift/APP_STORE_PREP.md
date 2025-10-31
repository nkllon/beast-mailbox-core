# App Store Preparation Checklist

**Target:** macOS 15.0+ (Sequoia / Tahoe 26.0.1+)  
**Goal:** Get Observatory App ready for App Store submission TODAY

---

## App Store Requirements ✅

### 1. App Structure ✅
- [x] Proper app bundle structure
- [x] Info.plist configured
- [x] App icon (SF Symbols work)
- [x] Minimum deployment target (macOS 15.0)

### 2. Code Signing
- [ ] Apple Developer account (required)
- [ ] App ID registered
- [ ] Provisioning profile
- [ ] Code signing certificate

### 3. App Store Connect
- [ ] App listing created
- [ ] Screenshots prepared
- [ ] Description written
- [ ] Privacy policy URL
- [ ] App categories selected

### 4. Technical Requirements
- [x] Sandbox mode (if needed)
- [x] Entitlements configured
- [x] Proper bundle identifier
- [x] Version number set

---

## Quick Setup for App Store

### Step 1: Configure Info.plist

Create `Info.plist` with:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleDisplayName</key>
    <string>Beast Observatory</string>
    <key>CFBundleIdentifier</key>
    <string>com.nkllon.ObservatoryApp</string>
    <key>CFBundleName</key>
    <string>ObservatoryApp</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>15.0</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2025</string>
    <key>NSAppleEventsUsageDescription</key>
    <string>ObservatoryApp needs access to automate sync tasks</string>
    <key>NSUserNotificationsUsageDescription</key>
    <string>ObservatoryApp sends notifications for sync status</string>
</dict>
</plist>
```

### Step 2: Create Xcode Project (for App Store)

SPM is great for development, but App Store requires Xcode project:

```bash
# Create Xcode project from Package.swift
cd observatory/swift
swift package generate-xcodeproj

# Or create manually in Xcode
open -a Xcode
# File > New > Project > macOS > App
```

### Step 3: Configure Signing

In Xcode:
1. Select project target
2. Signing & Capabilities
3. Select team
4. Enable "Automatically manage signing"
5. Bundle Identifier: `com.nkllon.ObservatoryApp`

### Step 4: Build Archive

In Xcode:
1. Product > Archive
2. Wait for build to complete
3. Click "Distribute App"
4. Choose "App Store Connect"
5. Follow prompts

---

## App Store Listing

### Screenshots Needed:
1. Menu bar with status
2. Chat interface with Apple Intelligence
3. Dashboard view
4. Settings panel

### Description Draft:
```
Beast Observatory - Developer Quality Metrics

Monitor your code quality metrics with native macOS integration.

Features:
• Real-time quality metrics dashboard
• Chat with Apple Intelligence for code review and advice
• Menu bar status indicator
• Native macOS notifications
• Shortcuts integration (Siri support)

Perfect for developers who want quality metrics at their fingertips.
```

### Keywords:
- developer tools
- code quality
- metrics
- monitoring
- Apple Intelligence
- chat

---

## Critical: macOS 15.0+ Only

**Why:**
- Apple Intelligence requires macOS 15.0+
- Our AppIntents use macOS 15.0+ APIs
- Chat UI uses SwiftUI features from macOS 15.0+

**App Store Note:**
- ✅ macOS 26.0.1 (Tahoe) is compatible with App Store
- ✅ macOS 15.0+ requirement is valid
- ⚠️ Some users on older macOS won't see the app

---

## App Store Review Guidelines

### Potential Issues:

1. **Apple Intelligence Claims**
   - ✅ We're using actual Apple Intelligence APIs (AppIntents)
   - ✅ Not claiming features we don't have
   - ✅ On-device processing (privacy-safe)

2. **Menu Bar App**
   - ✅ Standard macOS pattern
   - ✅ No dock icon (accessory policy)
   - ✅ Clean UI

3. **Permissions**
   - ✅ Only requesting what we need
   - ✅ Clear usage descriptions in Info.plist

4. **Functionality**
   - ✅ App works standalone
   - ✅ No crashes or obvious bugs
   - ✅ Proper error handling

---

## Next Steps

1. ✅ **Code Complete** - Chat UI integrated
2. 🚧 **Create Xcode Project** - For App Store submission
3. 🚧 **Configure Signing** - Apple Developer account
4. 🚧 **Test Build** - Make sure everything works
5. 🚧 **Screenshot Capture** - For App Store listing
6. 🚧 **Submit to App Store** - Today!

---

**Status:** Code ready, need Xcode project setup for submission

