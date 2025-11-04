# Xcode Reinstall Guide - Get Latest Version

## Current Situation
- Xcode needs to be reinstalled (retiring current instance)
- Need latest Xcode for macOS 26 SDK support
- Project is set up for macOS 15.0+ deployment target

## Recommended Approach

### Option 1: App Store (Recommended for Stable)
1. **Backup first** (if you customized):
   ```bash
   tar -czf ~/xcode_backup.tar.gz \
     ~/Library/Preferences/com.apple.dt.Xcode.plist \
     ~/Library/Developer/Xcode/UserData/KeyBindings \
     ~/Library/Developer/Xcode/UserData/FontAndColorThemes
   ```

2. **Delete current Xcode:**
   ```bash
   sudo rm -rf /Applications/Xcode.app
   ```

3. **Clean up artifacts:**
   ```bash
   rm -rf ~/Library/Developer/Xcode/DerivedData
   rm -rf ~/Library/Caches/com.apple.dt.Xcode*
   rm -rf ~/Library/Developer/Xcode/UserData/CodingAssistant  # 21GB old AI cache
   ```

4. **Download from App Store:**
   - Open App Store app
   - Search "Xcode"
   - Click "Get" or "Update" (if already installed)
   - Wait for download (~12GB)

5. **Install & Configure:**
   - Open Xcode from Applications
   - Accept license: `sudo xcodebuild -license accept`
   - Install additional components (prompted)

### Option 2: Developer Portal (Latest Beta/RC)
1. **Go to:** https://developer.apple.com/download/all/
2. **Download:** Latest Xcode (requires Apple ID login)
3. **Extract and move to Applications:**
   ```bash
   # Xcode downloads as .xip file
   xip -x ~/Downloads/Xcode*.xip
   mv Xcode.app /Applications/
   ```

4. **Verify and accept license:**
   ```bash
   sudo xcodebuild -license accept
   ```

### After Reinstall

1. **Set Command Line Tools:**
   ```bash
   sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
   ```

2. **Verify installation:**
   ```bash
   xcodebuild -version
   swift --version
   ```

3. **Regenerate ObservatoryApp project:**
   ```bash
   cd observatory/swift
   xcodegen generate
   ```

4. **Open in Xcode:**
   ```bash
   open ObservatoryApp.xcodeproj
   ```

## Quick Cleanup Script

Save this as `clean_xcode.sh`:

```bash
#!/bin/bash
echo "🧹 Cleaning Xcode artifacts before reinstall..."

# Backup customizations
if [ -d ~/Library/Developer/Xcode/UserData ]; then
    echo "📦 Backing up UserData..."
    tar -czf ~/xcode_userdata_backup.tar.gz \
      ~/Library/Developer/Xcode/UserData/KeyBindings \
      ~/Library/Developer/Xcode/UserData/FontAndColorThemes \
      ~/Library/Preferences/com.apple.dt.Xcode.plist 2>/dev/null
fi

# Clean build caches
echo "🗑️  Removing DerivedData..."
rm -rf ~/Library/Developer/Xcode/DerivedData

echo "🗑️  Removing caches..."
rm -rf ~/Library/Caches/com.apple.dt.Xcode*

echo "🗑️  Removing old AI assistant cache (21GB)..."
rm -rf ~/Library/Developer/Xcode/UserData/CodingAssistant

echo "✅ Cleanup complete!"
echo ""
echo "Next steps:"
echo "1. Delete /Applications/Xcode.app"
echo "2. Download latest from App Store or developer portal"
echo "3. Run: cd observatory/swift && xcodegen generate"
```

## Verification Checklist

After reinstall:
- [ ] `xcodebuild -version` shows latest version
- [ ] `swift --version` works
- [ ] `xcodegen generate` creates project successfully
- [ ] Xcode opens `ObservatoryApp.xcodeproj` without errors
- [ ] Project shows macOS 15.0+ deployment target
- [ ] Build succeeds (even with empty source files initially)

## Notes

- **Command Line Tools** are separate - won't be affected
- **project.yml** has all settings - project regenerates cleanly
- **All docs** in `observatory/swift/docs/` - ready for reference
- **21GB CodingAssistant** - safe to delete (old AI cache, switching to Claude anyway)
