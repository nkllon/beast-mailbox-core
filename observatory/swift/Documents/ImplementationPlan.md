# Apple Intelligence Integration - Implementation Plan

**Project:** Beast Observatory Native macOS App  
**Target:** macOS 15.0+ (Sequoia / Tahoe 26.0.1+)  
**Date:** 2025-10-31

---

## Project Setup

### Step 1: Create Xcode Project

```bash
# Open Xcode
open -a Xcode

# Or use command line:
mkdir -p observatory/swift/ObservatoryApp
cd observatory/swift/ObservatoryApp
```

**In Xcode:**
1. File > New > Project
2. Choose: **macOS > App**
3. Configure:
   - **Product Name:** `ObservatoryApp`
   - **Team:** Your Apple Developer Team (or Personal Team)
   - **Organization Identifier:** `com.nkllon`
   - **Interface:** SwiftUI
   - **Language:** Swift
   - **Uncheck:** "Use Core Data", "Include Tests" (we'll add later)
4. **Save Location:** `observatory/swift/ObservatoryApp`
5. Click **Create**

### Step 2: Configure Project Settings

**Target:** ObservatoryApp

**General Tab:**
- **Minimum Deployments:** macOS 15.0
- **Bundle Identifier:** `com.nkllon.ObservatoryApp`
- **App Category:** Utilities

**Signing & Capabilities:**
1. **Enable Signing** (Personal Team or Developer Team)
2. **Add Capabilities:**
   - ✅ App Sandbox
   - ✅ App Groups (optional, for shared data)
   - ✅ Network Client (for API calls)
   - ✅ User Notifications
   - ✅ Background Modes → Remote notifications

**Info.plist:**
- Add `NSAppleEventsUsageDescription`: "ObservatoryApp needs access to automate sync tasks"
- Add `NSUserNotificationsUsageDescription`: "ObservatoryApp sends notifications for sync status"

### Step 3: Add Source Files

**File Structure:**
```
ObservatoryApp/
├── ObservatoryAppApp.swift          # Main app entry
├── MenuBar/
│   ├── MenuBarView.swift
│   ├── StatusMonitor.swift
│   └── DashboardView.swift
├── Intelligence/
│   ├── NaturalLanguageQueries.swift
│   ├── ErrorDiagnosis.swift
│   ├── PredictiveMonitoring.swift
│   └── VisualUnderstanding.swift
├── Shortcuts/
│   ├── StatusIntent.swift
│   ├── SyncIntent.swift
│   ├── DiagnoseIntent.swift
│   └── QueryIntent.swift
├── Services/
│   ├── ObservatoryService.swift
│   ├── MetricsService.swift
│   └── NotificationService.swift
└── Models/
    ├── SyncStatus.swift
    ├── Metrics.swift
    └── Diagnosis.swift
```

**In Xcode:**
1. Right-click project > New Group > Name: `MenuBar`
2. Right-click project > New Group > Name: `Intelligence`
3. Right-click project > New Group > Name: `Shortcuts`
4. Right-click project > New Group > Name: `Services`
5. Right-click project > New Group > Name: `Models`

---

## Implementation Phases

### Phase 1: Foundation (Week 1) ⭐⭐⭐⭐⭐
**Priority:** Critical - Foundation for everything else

**Tasks:**
1. ✅ Create Xcode project
2. ✅ Set up project structure
3. ✅ Configure capabilities and signing
4. ✅ Create basic MenuBar app (StatusMonitor)
5. ✅ Connect to Python service (HTTP API or Process)
6. ✅ Basic status display

**Deliverables:**
- Menu bar app shows sync status
- Click menu bar → shows last sync time
- Basic error display

**Code Files:**
- `ObservatoryAppApp.swift`
- `MenuBar/MenuBarView.swift`
- `MenuBar/StatusMonitor.swift`
- `Services/ObservatoryService.swift`

---

### Phase 2: Shortcuts Integration (Week 2) ⭐⭐⭐⭐⭐
**Priority:** High - Uniquely Apple, high delight factor

**Tasks:**
1. ✅ Add AppIntents framework
2. ✅ Create status query intent
3. ✅ Create sync trigger intent
4. ✅ Test with Siri
5. ✅ Test with Shortcuts app

**Deliverables:**
- "Hey Siri, check Observatory status" works
- "Hey Siri, trigger Observatory sync" works
- Shortcuts app integration

**Code Files:**
- `Shortcuts/StatusIntent.swift`
- `Shortcuts/SyncIntent.swift`
- `Intelligence/NaturalLanguageQueries.swift`

---

### Phase 3: Natural Language Queries (Week 3) ⭐⭐⭐⭐⭐
**Priority:** Very High - Conversational interface

**Tasks:**
1. ✅ Integrate NaturalLanguage framework
2. ✅ Create query parser
3. ✅ Implement status queries ("What's the sync status?")
4. ✅ Implement metric queries ("What's the code coverage?")
5. ✅ Implement trend queries ("Show me coverage trend")

**Deliverables:**
- Natural language query intent
- Conversational responses
- Works via Siri and Shortcuts

**Code Files:**
- `Intelligence/NaturalLanguageQueries.swift`
- `Shortcuts/QueryIntent.swift`
- `Services/MetricsService.swift`

---

### Phase 4: Intelligent Error Diagnosis (Week 4) ⭐⭐⭐⭐⭐
**Priority:** Very High - Proactive problem solving

**Tasks:**
1. ✅ Integrate error analysis
2. ✅ Create error pattern recognition
3. ✅ Implement diagnosis intent
4. ✅ Generate suggested fixes
5. ✅ Test with real error logs

**Deliverables:**
- "Why did sync fail?" → AI explains
- Suggested fixes automatically generated
- Context-aware error analysis

**Code Files:**
- `Intelligence/ErrorDiagnosis.swift`
- `Shortcuts/DiagnoseIntent.swift`
- `Models/Diagnosis.swift`

---

### Phase 5: Smart Notifications (Week 5) ⭐⭐⭐⭐
**Priority:** High - Reduces notification fatigue

**Tasks:**
1. ✅ Integrate UserNotifications framework
2. ✅ Implement notification prioritization
3. ✅ Group related notifications
4. ✅ Create notification summaries
5. ✅ Test with sync events

**Deliverables:**
- Notifications grouped intelligently
- Priority-based interruption levels
- Actionable notification buttons

**Code Files:**
- `Services/NotificationService.swift`
- `Intelligence/NotificationPrioritization.swift`

---

### Phase 6: Predictive Monitoring (Week 6) ⭐⭐⭐⭐⭐
**Priority:** Very High - Proactive monitoring

**Tasks:**
1. ✅ Analyze historical metrics
2. ✅ Implement trend analysis
3. ✅ Create prediction model
4. ✅ Generate predictions ("Coverage will drop in 2 days")
5. ✅ Alert on predicted issues

**Deliverables:**
- Predictive health monitoring
- Proactive alerts
- Trend analysis

**Code Files:**
- `Intelligence/PredictiveMonitoring.swift`
- `Services/MetricsService.swift` (extend)

---

### Phase 7: Visual Understanding (Week 7) ⭐⭐⭐⭐⭐
**Priority:** High - Unique capability

**Tasks:**
1. ✅ Integrate Vision framework
2. ✅ Implement screenshot analysis
3. ✅ Create dashboard image parser
4. ✅ Extract metrics from images
5. ✅ Test with Grafana screenshots

**Deliverables:**
- Screenshot analysis works
- Extract metrics from dashboards
- Visual error detection

**Code Files:**
- `Intelligence/VisualUnderstanding.swift`
- `Shortcuts/AnalyzeImageIntent.swift`

---

### Phase 8: SwiftUI Dashboard (Week 8) ⭐⭐⭐⭐⭐
**Priority:** High - Visual polish

**Tasks:**
1. ✅ Create SwiftUI dashboard
2. ✅ Integrate Charts framework
3. ✅ Real-time metric updates
4. ✅ Interactive charts
5. ✅ Keyboard shortcuts

**Deliverables:**
- Beautiful native dashboard
- Real-time updates
- Professional UI

**Code Files:**
- `MenuBar/DashboardView.swift`
- `MenuBar/ChartsView.swift`

---

## Quick Start: Phase 1 Implementation

### 1. Create Basic Menu Bar App

**Replace `ObservatoryAppApp.swift`:**
```swift
import SwiftUI

@main
struct ObservatoryAppApp: App {
    @StateObject private var statusMonitor = StatusMonitor()
    
    var body: some Scene {
        MenuBarExtra {
            MenuBarView()
                .environmentObject(statusMonitor)
        } label: {
            Image(systemName: statusMonitor.statusIcon)
                .foregroundColor(statusMonitor.statusColor)
        }
    }
}
```

**Create `MenuBar/StatusMonitor.swift`:**
```swift
import SwiftUI
import Combine

@MainActor
class StatusMonitor: ObservableObject {
    @Published var lastSyncTime: Date?
    @Published var isSyncing: Bool = false
    @Published var lastError: String?
    
    var statusIcon: String {
        if isSyncing { return "arrow.triangle.2.circlepath" }
        if lastError != nil { return "exclamationmark.triangle.fill" }
        return "checkmark.circle.fill"
    }
    
    var statusColor: Color {
        if isSyncing { return .blue }
        if lastError != nil { return .red }
        return .green
    }
    
    func updateStatus() {
        // TODO: Connect to Python service
    }
}
```

**Create `MenuBar/MenuBarView.swift`:**
```swift
import SwiftUI

struct MenuBarView: View {
    @EnvironmentObject var monitor: StatusMonitor
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: monitor.statusIcon)
                    .foregroundColor(monitor.statusColor)
                Text("Beast Observatory")
                    .font(.headline)
            }
            
            if let lastSync = monitor.lastSyncTime {
                Text("Last Sync: \(lastSync, style: .relative)")
                    .font(.caption)
            }
            
            Divider()
            
            Button("Sync Now") {
                // TODO: Trigger sync
            }
            
            Button("Open Dashboard") {
                // TODO: Show dashboard
            }
            
            Button("Quit") {
                NSApplication.shared.terminate(nil)
            }
        }
        .padding()
        .frame(width: 280)
    }
}
```

### 2. Connect to Python Service

**Option A: HTTP API (Recommended)**
```swift
// Create local HTTP server in Python sync service
// Then call from Swift:
class ObservatoryService {
    let baseURL = URL(string: "http://localhost:8080")!
    
    func getStatus() async throws -> SyncStatus {
        let url = baseURL.appendingPathComponent("status")
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(SyncStatus.self, from: data)
    }
    
    func triggerSync() async throws {
        let url = baseURL.appendingPathComponent("sync")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        _ = try await URLSession.shared.data(for: request)
    }
}
```

**Option B: Process Call**
```swift
// Call Python script directly
class ObservatoryService {
    func triggerSync() async throws {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/local/bin/beast-observatory-sync")
        process.arguments = ["--one-shot"]
        
        try process.run()
        process.waitUntilExit()
        
        guard process.terminationStatus == 0 else {
            throw ObservatoryError.syncFailed(process.terminationStatus)
        }
    }
}
```

---

## Testing Strategy

### Unit Tests
```swift
// ObservatoryAppTests/
import XCTest
@testable import ObservatoryApp

class StatusMonitorTests: XCTestCase {
    func testStatusIcon() {
        let monitor = StatusMonitor()
        monitor.isSyncing = true
        XCTAssertEqual(monitor.statusIcon, "arrow.triangle.2.circlepath")
    }
}
```

### Integration Tests
- Test Shortcuts intents with Siri
- Test menu bar interactions
- Test notification delivery
- Test Python service connection

### UI Tests
- Test menu bar app launch
- Test dashboard interactions
- Test notification actions

---

## Dependencies

**Frameworks:**
- SwiftUI (UI)
- AppIntents (Shortcuts)
- NaturalLanguage (Natural language queries)
- Vision (Visual understanding)
- UserNotifications (Notifications)
- Charts (Dashboard)

**External:**
- Python sync service (HTTP API or process)

---

## Build & Run

```bash
# Build
cd observatory/swift/ObservatoryApp
xcodebuild -scheme ObservatoryApp -configuration Release

# Run
open build/Release/ObservatoryApp.app

# Or in Xcode:
# Product > Run (Cmd+R)
```

---

## Deployment

### App Store Distribution
1. Archive in Xcode (Product > Archive)
2. Upload to App Store Connect
3. Submit for review

### Direct Distribution
1. Build release (`xcodebuild -archivePath`)
2. Export signed app
3. Distribute `.app` bundle

### Homebrew Cask
```ruby
cask 'observatory-app' do
  version '1.0.0'
  sha256 '...'
  
  url "https://github.com/nkllon/beast-observatory/releases/download/v#{version}/ObservatoryApp-#{version}.dmg"
  name 'Observatory App'
  homepage 'https://github.com/nkllon/beast-observatory'
  
  app 'ObservatoryApp.app'
end
```

---

## Success Criteria

**Phase 1 Complete When:**
- ✅ Menu bar app runs and shows status
- ✅ Can trigger sync from menu bar
- ✅ Status updates correctly

**Phase 2 Complete When:**
- ✅ "Hey Siri, check Observatory status" works
- ✅ Shortcuts app shows intents

**All Phases Complete When:**
- ✅ All 8 phases implemented
- ✅ Tests passing
- ✅ App Store ready (or distributed)

---

## Next Steps

1. **Create Xcode Project** (Step 1 above)
2. **Implement Phase 1** (Basic menu bar app)
3. **Test Python Service Connection**
4. **Iterate through phases** (2-8)
5. **Test with Siri**
6. **Deploy**

---

**Status:** Implementation plan ready - begin with Phase 1

