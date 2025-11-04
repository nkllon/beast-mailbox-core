#!/bin/bash
echo "🧹 Cleaning Xcode artifacts before reinstall..."

# Backup customizations
if [ -d ~/Library/Developer/Xcode/UserData ]; then
    echo "📦 Backing up UserData..."
    tar -czf ~/xcode_userdata_backup.tar.gz \
      ~/Library/Developer/Xcode/UserData/KeyBindings \
      ~/Library/Developer/Xcode/UserData/FontAndColorThemes \
      ~/Library/Preferences/com.apple.dt.Xcode.plist 2>/dev/null
    echo "✅ Backup saved to ~/xcode_userdata_backup.tar.gz"
fi

# Clean build caches
echo "🗑️  Removing DerivedData..."
rm -rf ~/Library/Developer/Xcode/DerivedData

echo "🗑️  Removing caches..."
rm -rf ~/Library/Caches/com.apple.dt.Xcode*

echo "🗑️  Removing old AI assistant cache..."
rm -rf ~/Library/Developer/Xcode/UserData/CodingAssistant

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Delete /Applications/Xcode.app (if exists)"
echo "2. Download latest Xcode from App Store"
echo "3. After install, run: cd $(pwd) && xcodegen generate"
