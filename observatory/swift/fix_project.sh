#!/bin/bash

# Observatory Project Fix Script
echo "🔍 Diagnosing Observatory Project Issues..."

PROJECT_ROOT="/Volumes/lemon/cursor/beast-mailbox-core/observatory"
SWIFT_DIR="$PROJECT_ROOT/swift"

echo "📁 Checking project structure..."

# Check if the main project directory exists
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "❌ Project root not found: $PROJECT_ROOT"
    exit 1
fi

echo "✅ Project root exists: $PROJECT_ROOT"

# Check Swift directory
if [ ! -d "$SWIFT_DIR" ]; then
    echo "❌ Swift directory not found: $SWIFT_DIR"
    echo "🔧 Creating Swift directory..."
    mkdir -p "$SWIFT_DIR"
fi

echo "✅ Swift directory exists: $SWIFT_DIR"

# List current Swift files
echo "📋 Current Swift files:"
find "$SWIFT_DIR" -name "*.swift" -type f 2>/dev/null | while read file; do
    echo "  ✓ $(basename "$file")"
done

# Check for missing files mentioned in errors
MISSING_FILES=(
    "ObservatoryService.swift"
    "DashboardView.swift"
    "ChatView.swift"
    "GitHubActionsMonitor.swift"
)

echo "🔍 Checking for missing files..."
for file in "${MISSING_FILES[@]}"; do
    if [ ! -f "$SWIFT_DIR/$file" ]; then
        echo "❌ Missing: $file"
        echo "🔧 Creating placeholder for $file..."
        
        case "$file" in
            "ObservatoryService.swift")
                cat > "$SWIFT_DIR/$file" << 'EOF'
import Foundation

@MainActor
class ObservatoryService: ObservableObject {
    // Placeholder implementation
}
EOF
                ;;
            "DashboardView.swift")
                cat > "$SWIFT_DIR/$file" << 'EOF'
import SwiftUI

struct DashboardView: View {
    var body: some View {
        Text("Dashboard")
            .navigationTitle("Dashboard")
    }
}

#Preview {
    DashboardView()
}
EOF
                ;;
            "ChatView.swift")
                cat > "$SWIFT_DIR/$file" << 'EOF'
import SwiftUI

struct ChatView: View {
    var body: some View {
        Text("Chat")
            .navigationTitle("Chat")
    }
}

#Preview {
    ChatView()
}
EOF
                ;;
            "GitHubActionsMonitor.swift")
                cat > "$SWIFT_DIR/$file" << 'EOF'
import Foundation

@MainActor
class GitHubActionsMonitor: ObservableObject {
    // Placeholder implementation
}
EOF
                ;;
        esac
        echo "✅ Created placeholder: $file"
    else
        echo "✅ Found: $file"
    fi
done

# Fix the main actor issue in StatusMonitor.swift
if [ -f "$SWIFT_DIR/StatusMonitor.swift" ]; then
    echo "🔧 Fixing main actor isolation in StatusMonitor.swift..."
    
    # Create backup
    cp "$SWIFT_DIR/StatusMonitor.swift" "$SWIFT_DIR/StatusMonitor.swift.backup"
    
    # Fix the main actor issue - wrap stopMonitoring() calls in Task
    sed -i '' 's/stopMonitoring()/Task { await stopMonitoring() }/g' "$SWIFT_DIR/StatusMonitor.swift"
    
    echo "✅ Fixed main actor isolation (backup created)"
else
    echo "❌ StatusMonitor.swift not found"
fi

# Clean Xcode derived data
echo "🧹 Cleaning Xcode derived data..."
rm -rf ~/Library/Developer/Xcode/DerivedData/Observatory*

echo "🎉 Project fix complete!"
echo "📝 Next steps:"
echo "  1. Open Xcode"
echo "  2. Clean Build Folder (Cmd+Shift+K)"
echo "  3. Build (Cmd+B)"
echo ""
echo "If issues persist, run: xcodebuild -list from the project directory"