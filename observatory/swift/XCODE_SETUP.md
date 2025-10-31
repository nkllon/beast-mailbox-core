# Xcode Project Setup for App Store Submission

**Goal:** Create Xcode project from Swift Package for App Store submission

---

## Option 1: Create New Xcode Project (Recommended)

Since we have a Swift Package, easiest is to create Xcode project manually:

### Steps:

1. **Open Xcode**
   ```bash
   open -a Xcode
   ```

2. **Create New Project**
   - File > New > Project
   - Choose: **macOS > App**
   - Product Name: `ObservatoryApp`
   - Team: Your Apple Developer Team
   - Organization Identifier: `com.nkllon`
   - Interface: **SwiftUI**
   - Language: **Swift**
   - Save Location: `observatory/swift/Xcode/`

3. **Copy Source Files**
   ```bash
   # Copy our Swift files into Xcode project
   cp -r Sources/ObservatoryApp/* Xcode/ObservatoryApp/
   ```

4. **Configure Project**
   - Target > General:
     - Minimum Deployments: **macOS 15.0**
     - Bundle Identifier: `com.nkllon.ObservatoryApp`
   
   - Target > Signing & Capabilities:
     - Select Team
     - Enable "Automatically manage signing"
     - Add Capabilities:
       - ✅ App Sandbox
       - ✅ Outgoing Connections (Client)
       - ✅ User Notifications

5. **Add AppIntents Framework**
   - Target > Build Phases > Link Binary With Libraries
   - Add: `AppIntents.framework`

6. **Build & Test**
   ```bash
   # In Xcode
   Product > Build (⌘B)
   Product > Run (⌘R)
   ```

---

## Option 2: Generate Xcode Project from Package

**Note:** `swift package generate-xcodeproj` is deprecated. Use SwiftUI in Xcode directly.

Instead, open Package.swift in Xcode:

```bash
cd observatory/swift
open Package.swift
```

Then Xcode will open the package. But for App Store submission, you still need a proper app project.

---

## Option 3: Create App Target in Package (Swift 5.9+)

We can add an app target to Package.swift:

```swift
.target(
    name: "ObservatoryApp",
    dependencies: [],
    path: "Sources/ObservatoryApp",
    exclude: [],
    sources: ["ObservatoryAppApp.swift"]
)
```

But App Store still prefers Xcode project format.

---

## Recommended: Option 1 (Create New Xcode Project)

**Why:**
- ✅ Full Xcode integration
- ✅ App Store submission ready
- ✅ Code signing configured
- ✅ Archive & distribution workflows
- ✅ App Store Connect integration

**Steps:**
1. Create new Xcode project
2. Copy our Swift files
3. Configure signing
4. Build & archive
5. Submit to App Store

---

## App Store Submission Checklist

- [ ] Xcode project created
- [ ] All source files copied
- [ ] Bundle identifier set: `com.nkllon.ObservatoryApp`
- [ ] Version: 1.0.0 (or higher)
- [ ] Build number: 1
- [ ] Minimum macOS: 15.0
- [ ] Code signing configured
- [ ] App icon added (can use SF Symbols initially)
- [ ] Info.plist configured
- [ ] Build succeeds
- [ ] Archive created
- [ ] App Store Connect listing created
- [ ] Screenshots prepared
- [ ] Description written
- [ ] Privacy policy URL (if needed)
- [ ] Submit for review

---

**Status:** Ready to create Xcode project for App Store submission

