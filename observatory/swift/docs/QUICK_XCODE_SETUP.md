# Quick Xcode Setup - 5 Minutes

**Xcode Package.swift is open! Now let's create a real Xcode project for App Store.**

---

## 🚀 Quick Steps (5 minutes)

### 1. Create New Project (1 min)

**In Xcode (currently open):**
1. **File > New > Project** (⌘⇧N)
2. **macOS > App** → Next
3. **Product Name:** `ObservatoryApp`
4. **Team:** Your Apple Developer Team
5. **Organization Identifier:** `com.nkllon`
6. **Bundle Identifier:** `com.nkllon.ObservatoryApp` (auto)
7. **Interface:** SwiftUI → Next
8. **Save Location:** `observatory/swift/Xcode/` → Create

### 2. Add Swift Files (2 min)

**In Xcode:**
1. **Right-click** `ObservatoryApp` folder in Navigator
2. **Add Files to "ObservatoryApp"...**
3. Navigate to: `observatory/swift/Sources/ObservatoryApp/`
4. **Select ALL Swift files:**
   - `ObservatoryAppApp.swift`
   - `MenuBar/` folder (all files)
   - `Chat/` folder (all files)
   - `Intelligence/` folder (all files)
   - `Services/` folder (all files)
   - `Shortcuts/` folder (all files)
5. **Options:**
   - ✅ Copy items if needed
   - ✅ Create groups (not folder references)
   - ✅ Add to targets: ObservatoryApp
6. **Add**

### 3. Configure Target (1 min)

**Select project → Target "ObservatoryApp":**

**General:**
- Display Name: `Beast Observatory`
- Version: `1.0`
- Minimum Deployments: `macOS 15.0`

**Signing & Capabilities:**
- Team: Your team
- ✅ Automatically manage signing
- **+ Capability** → App Sandbox
  - ✅ Outgoing Connections (Client)

**Build Phases:**
- Link Binary With Libraries → **+**
- Add: `AppIntents.framework`
- Add: `UserNotifications.framework`

### 4. Replace Info.plist (30 sec)

**Delete default Info.plist, copy ours:**
```bash
# In Terminal
cd observatory/swift
cp Info.plist Xcode/ObservatoryApp/Info.plist
```

**Or manually copy contents from `Info.plist` in repo.**

### 5. Build & Test (1 min)

**Product > Build (⌘B)** - Should succeed!

**Product > Run (⌘R)** - App should launch!

---

## ✅ Verify Everything Works

- [ ] Menu bar icon appears
- [ ] Click menu → menu opens
- [ ] "Chat with Apple Intelligence" → chat opens
- [ ] Dashboard opens
- [ ] Settings opens
- [ ] No crashes

---

## 📦 Ready for Archive?

**If everything works:**
1. **Product > Clean Build Folder** (⇧⌘K)
2. **Product > Scheme > Edit Scheme**
   - Archive > Build Configuration: **Release**
3. **Product > Archive**
4. **Distribute App** → App Store Connect
5. **Submit!** 🚀

---

**Total Time:** ~5 minutes to create project, then archive & submit!

