# Xcode Project Setup - Step by Step

**Goal:** Get ObservatoryApp ready for App Store submission in Xcode

---

## Quick Start

### Option 1: Open Swift Package in Xcode (Recommended)

```bash
cd observatory/swift
./open_in_xcode.sh
```

This will open Xcode with the Swift Package. Then:

1. **In Xcode:**
   - Wait for indexing to complete
   - Product > Scheme > ObservatoryApp (should be selected)
   - Product > Build (⌘B) to test build
   - Product > Run (⌘R) to test run

2. **For App Store Submission:**
   - File > New > Project > macOS > App
   - Name: **ObservatoryApp**
   - Bundle ID: **com.nkllon.ObservatoryApp**
   - Interface: **SwiftUI**
   - Language: **Swift**
   - Location: `observatory/swift/Xcode/`
   - Copy Swift files from `Sources/ObservatoryApp/` into new project
   - Configure signing in target settings

---

### Option 2: Create New Xcode Project Manually

1. **Open Xcode:**
   ```bash
   open -a Xcode
   ```

2. **Create New Project:**
   - File > New > Project
   - Choose: **macOS > App**
   - Product Name: `ObservatoryApp`
   - Team: Your Apple Developer Team
   - Organization Identifier: `com.nkllon`
   - Bundle Identifier: `com.nkllon.ObservatoryApp`
   - Interface: **SwiftUI**
   - Language: **Swift**
   - Save Location: `observatory/swift/Xcode/`

3. **Copy Swift Files:**
   ```bash
   # Copy all Swift files into Xcode project
   cp -r Sources/ObservatoryApp/* Xcode/ObservatoryApp/
   ```

4. **Add to Xcode Project:**
   - In Xcode: Right-click project > Add Files to "ObservatoryApp"
   - Select all Swift files
   - Make sure "Copy items if needed" is checked
   - Click "Add"

---

## Configure Project for App Store

### 1. General Settings

In Xcode, select project target:

- **Display Name:** Beast Observatory
- **Bundle Identifier:** com.nkllon.ObservatoryApp
- **Version:** 1.0
- **Build:** 1
- **Minimum Deployments:** macOS 15.0

### 2. Signing & Capabilities

- **Team:** Select your Apple Developer Team
- **Automatically manage signing:** ✅ Checked
- **Bundle Identifier:** com.nkllon.ObservatoryApp

**Add Capabilities:**
- ✅ App Sandbox
  - Outgoing Connections (Client)
  - User Notifications

### 3. Info.plist

We've created `Info.plist` with:
- Bundle identifier
- Display name
- Version
- Minimum macOS version (15.0)
- Permission descriptions

**In Xcode:**
- Drag `Info.plist` into project
- Or Xcode will auto-generate one (use ours as reference)

### 4. Add Frameworks

**Build Phases > Link Binary With Libraries:**
- ✅ AppIntents.framework (for Apple Intelligence)
- ✅ UserNotifications.framework (for notifications)
- ✅ Foundation.framework (automatically added)
- ✅ SwiftUI.framework (automatically added)
- ✅ AppKit.framework (automatically added)

---

## Build & Test

### 1. Build

```bash
# In Xcode:
Product > Build (⌘B)
```

**Or command line:**
```bash
cd observatory/swift
xcodebuild -scheme ObservatoryApp -configuration Debug build
```

### 2. Run

```bash
# In Xcode:
Product > Run (⌘R)
```

**Or command line:**
```bash
xcodebuild -scheme ObservatoryApp -configuration Debug run
```

### 3. Test Features

- ✅ Menu bar icon appears
- ✅ Click menu bar → menu opens
- ✅ "Chat with Apple Intelligence" → opens chat
- ✅ Chat works (sends to Apple Intelligence)
- ✅ Dashboard opens
- ✅ Settings opens

---

## Archive for App Store

### 1. Set Build Configuration

- Product > Scheme > Edit Scheme
- Archive > Build Configuration: **Release**

### 2. Clean Build

```bash
Product > Clean Build Folder (⇧⌘K)
```

### 3. Archive

```bash
Product > Archive
```

Wait for build to complete...

### 4. Distribute

1. Window > Organizer (opens automatically)
2. Select archive
3. Click **Distribute App**
4. Choose **App Store Connect**
5. Follow prompts:
   - Upload: ✅
   - App Thinning: ✅ All compatible device variants
   - Upload your app's symbols: ✅ (recommended)
6. Click **Upload**
7. Wait for upload to complete

---

## App Store Connect

### 1. Create App Listing

In App Store Connect:
1. My Apps > **+** > New App
2. Platform: **macOS**
3. Name: **Beast Observatory**
4. Primary Language: **English (U.S.)**
5. Bundle ID: **com.nkllon.ObservatoryApp** (select from dropdown)
6. SKU: `observatory-app-001`
7. Click **Create**

### 2. Fill App Information

**App Information:**
- Category: **Developer Tools** > **Utilities**
- Age Rating: **4+** (Developer Tools)
- Copyright: Your copyright

**Pricing:**
- Price: **Free** (or your price)

**Description:**
```
Monitor code quality metrics with native macOS integration.

Features:
• Real-time quality metrics dashboard
• Chat with Apple Intelligence for code review and advice
• Menu bar status indicator
• Native macOS notifications
• Shortcuts integration (Siri support)

Perfect for developers who want quality metrics at their fingertips.
```

**Keywords:**
```
developer tools, code quality, metrics, monitoring, Apple Intelligence, chat
```

**Support URL:**
- Your support URL (if you have one)

**Marketing URL:**
- Your website (optional)

### 3. Screenshots

**Required Screenshots:**
1. Menu bar with status
2. Chat interface with Apple Intelligence
3. Dashboard view
4. Settings panel

**How to Capture:**
```bash
# In Xcode Simulator or running app:
# Device > Screenshots > Capture Screenshot (⌘S)
# Or: Screenshot app (⇧⌘3)
```

**Sizes Needed:**
- 1280 x 800 (minimum)
- 1440 x 900 (recommended)
- 2880 x 1800 (Retina)

### 4. Version Information

**Version:** 1.0  
**Build:** 1  
**What's New in This Version:**
```
Initial release of Beast Observatory.

Features:
• Native macOS menu bar app
• Chat with Apple Intelligence for code review
• Quality metrics dashboard
• Shortcuts integration (Siri support)
```

### 5. Submit for Review

1. In App Store Connect > App Information
2. **Build** section > Select your uploaded archive
3. Click **Submit for Review**
4. Add notes if needed:
   ```
   This app uses Apple Intelligence via AppIntents for on-device AI assistance.
   Requires macOS 15.0+ for Apple Intelligence support.
   ```
5. Click **Submit**

---

## What to Check in Xcode

### ✅ Code Compiles
- No errors
- No warnings (or acceptable warnings)

### ✅ App Runs
- Menu bar icon appears
- Chat opens and works
- Dashboard displays
- No crashes

### ✅ Signing Configured
- Team selected
- Bundle ID set
- Code signing works

### ✅ Deployment Target
- macOS 15.0 minimum

### ✅ Info.plist Complete
- Display name
- Bundle ID
- Version
- Permissions

---

## Common Issues & Fixes

### Issue: "No such module 'AppIntents'"
**Fix:** Add AppIntents framework in Build Phases > Link Binary With Libraries

### Issue: Code Signing Failed
**Fix:** 
- Check Apple Developer account has active membership
- Verify bundle ID matches App Store Connect
- Try cleaning build folder (⇧⌘K)

### Issue: Archive Not Appearing in Organizer
**Fix:** 
- Make sure build succeeded (no errors)
- Check Product > Archive menu (should be enabled)
- Try Product > Clean Build Folder first

### Issue: Upload Fails
**Fix:**
- Check internet connection
- Verify Apple ID has App Store Connect access
- Try exporting instead of uploading (for testing)

---

## Timeline

**Total Time:** ~1 hour

- Open in Xcode: 5 min
- Configure project: 10 min
- Build & test: 10 min
- Archive: 5 min
- App Store Connect: 15 min
- Submit: 5 min

---

**Status:** Ready to open in Xcode! Run `./open_in_xcode.sh` to get started.

