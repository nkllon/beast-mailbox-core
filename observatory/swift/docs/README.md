# Beast Observatory - Swift Native App (Command Line Setup)

**Status:** Ready for Command Line Development  
**Target:** macOS 15.0+ (Sequoia / Tahoe 26.0.1+)  
**No Xcode Required!** Uses Swift Package Manager (SPM)

---

## Quick Start (Command Line Only)

### 1. Verify Swift is Installed

```bash
swift --version
# Should show: Swift version 5.9+ for macOS 15.0+
```

### 2. Build

```bash
cd observatory/swift
swift build
```

### 3. Run

```bash
swift run ObservatoryApp
```

**Or use the helper scripts:**

```bash
# Build
./build.sh

# Run (builds first if needed)
./run.sh

# Build release version
./build.sh release

# Run release version
./run.sh release

# Install to Applications
./install.sh

# Run tests
./test.sh
```

---

## Project Structure (SPM)

```
swift/
├── Package.swift              # Swift Package Manager manifest
├── Sources/
│   └── ObservatoryApp/
│       ├── main.swift         # Main app entry
│       ├── MenuBar/           # Menu bar components
│       │   ├── MenuBarView.swift
│       │   ├── StatusMonitor.swift
│       │   └── DashboardView.swift
│       └── Services/           # Service integration
│           └── ObservatoryService.swift
├── Tests/
│   └── ObservatoryAppTests/   # Unit tests
├── build.sh                   # Build script
├── run.sh                     # Run script
├── install.sh                 # Install script
└── test.sh                    # Test script
```

---

## Development Workflow

### Daily Development

```bash
# Make changes to .swift files
vim Sources/ObservatoryApp/MenuBar/MenuBarView.swift

# Build and run
./run.sh

# The app appears in menu bar!
```

### Testing

```bash
# Run tests
./test.sh

# Or directly
swift test
```

### Release Build

```bash
# Build optimized release
swift build -c release

# Install to Applications
./install.sh

# Run installed app
open ~/Applications/ObservatoryApp.app
```

---

## Adding New Files

### Add a New Swift File

```bash
# Create file
cat > Sources/ObservatoryApp/NewFeature.swift <<'EOF'
import SwiftUI

struct NewFeature: View {
    var body: some View {
        Text("New Feature")
    }
}
EOF

# Rebuild (Swift automatically picks it up)
swift build
```

### Add a New Test

```bash
# Create test file
cat > Tests/ObservatoryAppTests/NewFeatureTests.swift <<'EOF'
import XCTest
@testable import ObservatoryApp

final class NewFeatureTests: XCTestCase {
    func testExample() {
        XCTAssertTrue(true)
    }
}
EOF

# Run tests
swift test
```

---

## Troubleshooting

### "Swift not found"

```bash
# Install Xcode Command Line Tools (no full Xcode needed)
xcode-select --install
```

### "Unsupported macOS version"

**Package.swift requires macOS 15.0+**. If you need to support older versions:

```swift
// Edit Package.swift, change:
platforms: [
    .macOS(.v13) // Or whatever version you need
]
```

### "Build errors"

```bash
# Clean build
rm -rf .build
swift build

# Check for syntax errors
swift build --verbose
```

### "App doesn't appear in menu bar"

- Check Console.app for errors
- Verify executable runs: `swift run ObservatoryApp`
- Check permissions: App needs accessibility permissions for menu bar

---

## Dependencies

**No external dependencies!** Uses only built-in frameworks:
- SwiftUI
- AppKit
- Foundation
- AppIntents (for Shortcuts - Phase 2)
- NaturalLanguage (for NLP - Phase 3)
- Vision (for image analysis - Phase 7)

---

## Implementation Phases

**See:** `ImplementationPlan.md`

**Current:** Phase 1 (Foundation)  
**Next:** Phase 2 (Shortcuts Integration)

---

## Command Line vs Xcode

**Why SPM (Command Line)?**
- ✅ No Xcode required
- ✅ Faster builds
- ✅ Works in CI/CD
- ✅ Better for automation
- ✅ Works with any editor (vim, Cursor, VS Code)

**When to use Xcode:**
- Visual debugging (breakpoints, step-through)
- Interface Builder (if using XIBs)
- App Store submission workflow
- Code signing GUI

**You can still use Xcode if needed:**
```bash
# Open package in Xcode
open Package.swift

# Xcode will open the package
# You get all Xcode features while still using SPM
```

---

## Next Steps

1. **Build:** `swift build`
2. **Run:** `swift run ObservatoryApp`
3. **Develop:** Edit `.swift` files, rebuild, test
4. **Implement Phases:** See `ImplementationPlan.md`

---

**Status:** ✅ Ready for command-line development!
