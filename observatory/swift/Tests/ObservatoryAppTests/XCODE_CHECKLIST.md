# Xcode Inspection Checklist

**Now that Xcode is open, let's verify everything is ready for App Store submission!**

---

## 🔍 What to Check in Xcode

### 1. Project Structure ✅

**In Navigator (left sidebar):**
- ✅ All Swift files are present:
  - `ObservatoryAppApp.swift`
  - `MenuBar/` folder:
    - `MenuBarView.swift`
    - `StatusMonitor.swift`
    - `DashboardView.swift`
  - `Chat/` folder:
    - `ChatView.swift`
  - `Intelligence/` folder:
    - `AppleIntelligenceAgent.swift`
  - `Services/` folder:
    - `SimpleHTTPServer.swift`
    - `ObservatoryService.swift`
  - `Shortcuts/` folder:
    - `StatusIntent.swift`
    - `SyncIntent.swift`
    - `DiagnoseIntent.swift`

**If files are missing:**
- Drag them from `Sources/ObservatoryApp/` into Xcode project
- Make sure "Copy items if needed" is checked

---

### 2. Target Settings ⚙️

**Select project in Navigator, then select target "ObservatoryApp":**

#### General Tab:
- ✅ **Display Name:** Beast Observatory
- ✅ **Bundle Identifier:** `com.nkllon.ObservatoryApp`
- ✅ **Version:** 1.0
- ✅ **Build:** 1
- ✅ **Minimum Deployments:** macOS 15.0

#### Signing & Capabilities Tab:
- ✅ **Team:** Your Apple Developer Team (selected)
- ✅ **Automatically manage signing:** Checked
- ✅ **Bundle Identifier:** `com.nkllon.ObservatoryApp`

**Capabilities Added:**
- ✅ App Sandbox
  - ✅ Outgoing Connections (Client)
  - ✅ User Notifications (if available)

#### Build Phases Tab:
**Link Binary With Libraries:**
- ✅ AppIntents.framework
- ✅ UserNotifications.framework
- ✅ Foundation.framework (usually auto-added)
- ✅ SwiftUI.framework (usually auto-added)
- ✅ AppKit.framework (usually auto-added)

**If AppIntents is missing:**
- Click **+** button
- Search for "AppIntents"
- Add it

---

### 3. Info.plist 📋

**Check if Info.plist exists:**
- Should be in project navigator
- If missing, we created `Info.plist` in the repo

**Verify contents:**
- Bundle identifier matches
- Display name: "Beast Observatory"
- Minimum macOS version: 15.0
- Permission descriptions present

---

### 4. Build Configuration 🔨

**Check Build Settings:**
- **Product > Scheme > Edit Scheme**
- **Archive > Build Configuration:** Release
- **Run > Build Configuration:** Debug (for testing)

**Verify:**
- No build errors
- Warnings are acceptable (or fix them)

---

### 5. Test Build ✅

**In Xcode:**
1. **Product > Clean Build Folder** (⇧⌘K)
2. **Product > Build** (⌘B)
3. **Check for errors:**
   - ✅ No red errors
   - ⚠️ Warnings OK (or fix them)

**If errors occur:**
- Check missing imports
- Verify frameworks are linked
- Check Info.plist

---

### 6. Test Run 🚀

**In Xcode:**
1. **Product > Run** (⌘R)
2. **Check:**
   - ✅ Menu bar icon appears
   - ✅ Click menu bar → menu opens
   - ✅ "Chat with Apple Intelligence" works
   - ✅ Chat window opens
   - ✅ Dashboard opens
   - ✅ Settings opens
   - ✅ No crashes

**If app doesn't run:**
- Check signing (must have team selected)
- Check bundle identifier
- Check minimum macOS version

---

### 7. Archive for App Store 📦

**Before archiving:**
1. **Product > Scheme > Edit Scheme**
2. **Archive > Build Configuration:** Release
3. **Product > Clean Build Folder** (⇧⌘K)

**Create Archive:**
1. **Product > Archive**
2. Wait for build...
3. Organizer window opens automatically
4. Verify archive appears

**If archive fails:**
- Check signing (must have valid Apple Developer account)
- Check bundle identifier matches App Store Connect
- Verify no build errors

---

## 🐛 Common Issues & Fixes

### Issue: "No such module 'AppIntents'"
**Fix:**
- Build Phases > Link Binary With Libraries > **+**
- Add `AppIntents.framework`

### Issue: Code Signing Failed
**Fix:**
- Signing & Capabilities > Select your Team
- Enable "Automatically manage signing"
- Verify bundle ID: `com.nkllon.ObservatoryApp`

### Issue: Minimum Deployment Target
**Fix:**
- General > Minimum Deployments > **macOS 15.0**

### Issue: App Crashes on Launch
**Fix:**
- Check Console.app for crash logs
- Verify Info.plist has all required keys
- Check permission descriptions are present

### Issue: Chat Doesn't Work
**Fix:**
- Verify `QueryAppleIntelligenceIntent` is included
- Check `AppleIntelligenceAgent.swift` is in project
- Verify AppIntents framework is linked

---

## 📸 Screenshots (For App Store)

**While app is running, capture:**

1. **Menu Bar:**
   - Menu bar icon visible
   - Click to show menu
   - Screenshot: ⌘⇧3 or Device > Screenshot

2. **Chat Window:**
   - Open chat (⌘C or menu)
   - Show conversation with Apple Intelligence
   - Screenshot

3. **Dashboard:**
   - Open dashboard
   - Show metrics
   - Screenshot

4. **Settings:**
   - Open settings
   - Screenshot

**Screenshot sizes needed:**
- 1280 x 800 (minimum)
- 1440 x 900 (recommended)
- 2880 x 1800 (Retina, optional)

---

## ✅ Pre-Submission Checklist

Before submitting to App Store:

- [ ] All Swift files in project
- [ ] Build succeeds (no errors)
- [ ] App runs without crashes
- [ ] Menu bar works
- [ ] Chat opens and works
- [ ] Dashboard opens
- [ ] Settings opens
- [ ] Signing configured (team selected)
- [ ] Bundle ID: `com.nkllon.ObservatoryApp`
- [ ] Version: 1.0
- [ ] Build: 1
- [ ] Minimum macOS: 15.0
- [ ] Info.plist configured
- [ ] AppIntents framework linked
- [ ] Archive created successfully
- [ ] Screenshots captured

---

## 🚀 Next Steps

1. ✅ **Check all items above**
2. 🚧 **Fix any issues found**
3. 🚧 **Create archive** (Product > Archive)
4. 🚧 **Upload to App Store Connect**
5. 🚧 **Create App Store listing**
6. 🚧 **Submit for review**

---

**Status:** Xcode is open - let's verify everything is ready!

