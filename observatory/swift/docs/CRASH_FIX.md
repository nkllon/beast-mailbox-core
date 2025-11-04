# Crash Fix - NSApp Initialization

**Issue:** Fatal error: Unexpectedly found nil while implicitly unwrapping an Optional value at line 19

**Root Cause:** `NSApp` was being accessed in `init()` before `NSApplication` was fully initialized.

**Fix:**
1. Removed `NSApp.setActivationPolicy(.accessory)` from `App.init()`
2. Moved to `AppDelegate.applicationDidFinishLaunching()` where `NSApp` is guaranteed to be initialized

**Before:**
```swift
init() {
    NSApp.setActivationPolicy(.accessory)  // ❌ NSApp is nil here
}
```

**After:**
```swift
// App struct - no init needed
@main
struct ObservatoryAppApp: App { ... }

// AppDelegate - set policy here
func applicationDidFinishLaunching(_ notification: Notification) {
    NSApp.setActivationPolicy(.accessory)  // ✅ NSApp is initialized here
}
```

**Status:** ✅ Fixed - App should now run without crashing

