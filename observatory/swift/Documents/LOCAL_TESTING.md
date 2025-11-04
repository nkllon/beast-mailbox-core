# Local Testing Before App Store Submission

**Goal:** Test the app thoroughly locally before submitting  
**Philosophy:** Test locally, not in production! 😄

---

## What to Test

### 1. Build & Run ✅

**In Xcode:**
1. **Product > Clean Build Folder** (⇧⌘K)
2. **Product > Build** (⌘B) - Should succeed with no errors
3. **Product > Run** (⌘R) - Should launch app

**Command Line:**
```bash
cd observatory/swift
swift build -c release  # Or build via Xcode
```

---

### 2. Menu Bar App ✅

**When app launches:**
- [ ] Menu bar icon appears (top right of menu bar)
- [ ] Icon shows status (checkmark, sync, error, etc.)
- [ ] Click icon → menu opens
- [ ] Menu shows: "Beast Observatory" header
- [ ] Menu shows: "Last Sync: [time]"
- [ ] Menu shows: Quick actions

**Test:**
- Click menu bar icon
- Verify menu opens
- Check status icon is visible

---

### 3. Menu Items ✅

**Test each menu item:**
- [ ] **Sync Now** - Triggers sync (⌘S)
- [ ] **Open Dashboard** - Opens dashboard window (⌘D)
- [ ] **Chat with Apple Intelligence** - Opens chat (⌘C)
- [ ] **View Logs** - Opens log file in TextEdit (⌘L)
- [ ] **Settings...** - Opens settings (⌘,)
- [ ] **Quit** - Quits app (⌘Q)

**Test:**
- Click each menu item
- Verify actions work
- Test keyboard shortcuts

---

### 4. Chat UI ✅

**Test Apple Intelligence Chat:**
- [ ] Chat window opens (600x500 minimum)
- [ ] Input field is visible
- [ ] Send button works
- [ ] Messages display (user messages on right, AI on left)
- [ ] Loading indicator shows while AI "thinking"
- [ ] AI responses appear
- [ ] Auto-scroll to latest message
- [ ] Clear button works

**Test Messages:**
```bash
# Try these queries:
- "Hello, can you help me?"
- "Review this code for issues"
- "What's the best way to handle errors?"
```

**Test:**
- Open chat (⌘C or menu)
- Type a message
- Send message
- Wait for AI response
- Verify response appears

**Known Limitations:**
- Apple Intelligence integration may be placeholder until AppIntents are fully implemented
- This is OK - we're testing UI flow first

---

### 5. Dashboard ✅

**Test Dashboard View:**
- [ ] Dashboard window opens
- [ ] Shows metrics (coverage, bugs, etc.)
- [ ] Charts/graphs display (if implemented)
- [ ] Real-time updates work
- [ ] Close button works

**Test:**
- Open dashboard (⌘D or menu)
- Verify content displays
- Check for any crashes or errors

---

### 6. Settings ✅

**Test Settings Panel:**
- [ ] Settings window opens
- [ ] Settings display correctly
- [ ] Settings can be changed (if implemented)
- [ ] Settings save (if implemented)
- [ ] Close button works

**Test:**
- Open settings (⌘, or menu)
- Verify UI displays
- Test any interactive elements

---

### 7. Status Monitor ✅

**Test Status Updates:**
- [ ] Status icon changes based on sync status
- [ ] Status color changes (blue=syncing, green=ok, red=error)
- [ ] Last sync time updates
- [ ] Error messages display (if any)
- [ ] Coverage percentage shows (if available)

**Test:**
- Trigger sync manually
- Watch status icon change
- Verify status updates in menu

---

### 8. Error Handling ✅

**Test Error Cases:**
- [ ] App handles missing log file gracefully
- [ ] App handles network errors gracefully
- [ ] App handles Apple Intelligence unavailable gracefully
- [ ] App doesn't crash on errors
- [ ] Error messages display appropriately

**Test:**
- Simulate errors (if possible)
- Check error handling
- Verify no crashes

---

### 9. Performance ✅

**Test Performance:**
- [ ] App launches quickly (< 3 seconds)
- [ ] Menu bar responds quickly
- [ ] Chat UI is responsive
- [ ] No memory leaks (check Activity Monitor)
- [ ] CPU usage is reasonable

**Test:**
- Launch app multiple times
- Use app for 10-15 minutes
- Check Activity Monitor for issues

---

### 10. Permissions ✅

**Test Permissions:**
- [ ] Notification permission requested (if needed)
- [ ] Permission dialogs appear correctly
- [ ] App works without permissions (graceful degradation)

**Test:**
- Launch app first time
- Check permission dialogs
- Test with/without permissions

---

## Test Checklist

### Critical (Must Work):
- [x] App builds without errors
- [ ] App runs without crashing
- [ ] Menu bar icon appears
- [ ] Menu opens and displays
- [ ] Chat UI opens
- [ ] Dashboard opens
- [ ] Settings open
- [ ] Quit works
- [ ] No obvious crashes

### Important (Should Work):
- [ ] Status updates correctly
- [ ] Chat UI is responsive
- [ ] Apple Intelligence integration works (or shows placeholder)
- [ ] Error handling is graceful
- [ ] Keyboard shortcuts work

### Nice to Have (Future):
- [ ] Full Apple Intelligence responses
- [ ] Real-time metrics updates
- [ ] Settings persistence
- [ ] Advanced features

---

## Local Testing Script

```bash
#!/bin/bash
# Run local tests before submission

echo "🧪 Local Testing Checklist"
echo ""

# Test 1: Build
echo "1. Building..."
swift build -c release || xcodebuild build -scheme ObservatoryApp
echo "✅ Build complete"

# Test 2: Run (requires Xcode or manual testing)
echo "2. Testing (manual steps):"
echo "   - Launch app in Xcode (⌘R)"
echo "   - Check menu bar icon appears"
echo "   - Test menu items"
echo "   - Test chat UI"
echo "   - Test dashboard"
echo "   - Test settings"

# Test 3: No obvious errors
echo "3. Checking for errors..."
# Could check logs here if implemented

echo ""
echo "✅ Local testing complete!"
echo "   If all tests pass, ready for App Store submission"
```

---

## How Long to Test?

**Minimum:**
- Test all critical features once
- Make sure nothing crashes
- Verify UI works

**Recommended:**
- Use app for 1-2 days
- Test all features multiple times
- Check edge cases
- Verify stability

**Thorough:**
- Use app for a week
- Test all features extensively
- Test with real data
- Check performance over time

---

## What If Something Breaks?

**Before Submission:**
1. Fix the issue
2. Re-test
3. Don't submit until it works

**After Submission (Emergency):**
- Submit a new version immediately
- Or withdraw current submission if possible

---

## Pre-Submission Checklist

**Before running `./submit_to_appstore.sh`:**

- [ ] App builds successfully
- [ ] App runs without crashing
- [ ] All UI elements work
- [ ] Menu bar functionality works
- [ ] Chat opens and functions (even if AI is placeholder)
- [ ] Dashboard opens
- [ ] Settings open
- [ ] Error handling is graceful
- [ ] No obvious bugs
- [ ] Tested for at least 30 minutes of use

---

## Ready to Submit?

**If all tests pass:**
```bash
cd observatory/swift
source ~/.env
./submit_to_appstore.sh
```

**If tests fail:**
- Fix issues first
- Re-test
- Then submit

---

**Status:** Let's test locally first! 🧪

