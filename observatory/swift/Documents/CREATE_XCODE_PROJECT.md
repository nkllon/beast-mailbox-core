# Create Xcode Project - Step by Step

**The .xcodeproj was corrupted. Here's how to create a proper one!**

---

## Option 1: Open Swift Package in Xcode (Easiest) ✅

**I just opened Package.swift in Xcode for you!**

Xcode can work with Swift Packages directly, but for App Store submission, we need a real Xcode project.

**What Xcode should show:**
- Package.swift in Navigator
- Sources/ObservatoryApp/ folder with Swift files
- Can build and run from here

**Next Steps:**
1. In Xcode: File > New > Project
2. Choose: **macOS > App**
3. Name: **ObservatoryApp**
4. Bundle ID: **com.nkllon.ObservatoryApp**
5. Interface: **SwiftUI**
6. Save to: `observatory/swift/Xcode/` (or wherever you prefer)

---

## Option 2: Create New Xcode Project Manually

### Step 1: Create New Project

1. **In Xcode:** File > New > Project
2. **Choose:** macOS > App
3. **Configure:**
   - Product Name: `ObservatoryApp`
   - Team: Your Apple Developer Team
   - Organization Identifier: `com.nkllon`
   - Bundle Identifier: `com.nkllon.ObservatoryApp` (auto-filled)
   - Interface: **SwiftUI**
   - Language: **Swift**
   - Storage: None (or Core Data if you want, but we don't need it)
4. **Save Location:** `observatory/swift/Xcode/` (or create new folder)
5. **Click:** Create

### Step 2: Delete Default Files

Xcode creates default files we don't need:
- Delete `ContentView.swift` (we have our own)
- Delete `ObservatoryAppApp.swift` (we'll copy ours)
- Keep `Info.plist` (we'll update it)

### Step 3: Copy Our Swift Files

**In Finder:**
```bash
cd observatory/swift
# Copy all Swift files to Xcode project
cp -r Sources/ObservatoryApp/* Xcode/ObservatoryApp/
```

**Or in Xcode:**
1. Right-click project in Navigator
2. Add Files to "ObservatoryApp"...
3. Navigate to `Sources/ObservatoryApp/`
4. Select all Swift files
5. Make sure "Copy items if needed" is checked
6. Click "Add"

### Step 4: Update Info.plist

**Copy our Info.plist:**
```bash
cp observatory/swift/Info.plist Xcode/ObservatoryApp/Info.plist
```

**Or in Xcode:**
- Replace the Info.plist with ours (from `observatory/swift/Info.plist`)

### Step 5: Configure Target

**Select project in Navigator, then target "ObservatoryApp":**

**General Tab:**
- Display Name: **Beast Observatory**
- Bundle Identifier: `com.nkllon.ObservatoryApp`
- Version: **1.0**
- Build: **1**
- Minimum Deployments: **macOS 15.0**

**Signing & Capabilities Tab:**
- Team: Select your Apple Developer Team
- Enable "Automatically manage signing"
- Bundle ID: `com.nkllon.ObservatoryApp`

**Add Capabilities:**
- Click **+ Capability** button
- Add: **App Sandbox**
  - Enable: Outgoing Connections (Client)
- Add: **User Notifications** (if available)

**Build Phases Tab:**
- Link Binary With Libraries > **+**
- Add: **AppIntents.framework**
- Add: **UserNotifications.framework**

### Step 6: Build & Test

1. **Product > Clean Build Folder** (⇧⌘K)
2. **Product > Build** (⌘B)
3. **Check for errors** - fix any issues
4. **Product > Run** (⌘R)
5. **Test app** - menu bar, chat, dashboard

---

## Option 3: Use Xcode's "Create App" from Package

**If Xcode has this feature (newer versions):**

1. Right-click `Package.swift` in Navigator
2. Choose: **Create App**
3. Follow prompts to create app target
4. Configure signing
5. Build & run

**Note:** This might not be available in all Xcode versions.

---

## Recommended: Option 2 (Create New Project Manually)

**Why:**
- ✅ Full control over project structure
- ✅ Works with all Xcode versions
- ✅ Clean project setup
- ✅ App Store submission ready

**Time:** ~15-20 minutes

---

## Quick Checklist After Creating Project

- [ ] Project created with correct Bundle ID
- [ ] All Swift files copied to project
- [ ] Info.plist updated
- [ ] Target settings configured (macOS 15.0)
- [ ] Signing configured (team selected)
- [ ] Capabilities added (App Sandbox, Notifications)
- [ ] Frameworks linked (AppIntents, UserNotifications)
- [ ] Build succeeds (no errors)
- [ ] App runs and works

---

## If You Run Into Issues

### Issue: "No such module 'AppIntents'"
**Fix:** Build Phases > Link Binary With Libraries > Add AppIntents.framework

### Issue: Code Signing Failed
**Fix:** Signing & Capabilities > Select Team > Enable "Automatically manage signing"

### Issue: Files Not Found
**Fix:** Make sure all Swift files are in project Navigator (drag them in if missing)

---

**Status:** Xcode is open with Package.swift - Create new project using Option 2 above!

