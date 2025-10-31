//
//  MenuBarApp.swift
//  Beast Observatory Menu Bar
//
//  Native macOS menu bar application for Beast Observatory
//  Provides status indicator and quick actions
//

import SwiftUI
import AppKit

@main
struct ObservatoryMenuBar: App {
    @StateObject private var syncMonitor = SyncStatusMonitor()
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        MenuBarExtra {
            MenuBarView()
                .environmentObject(syncMonitor)
        } label: {
            Image(systemName: syncMonitor.statusIcon)
                .foregroundColor(syncMonitor.statusColor)
        }
        .menuBarExtraStyle(.window)
    }
}

// MARK: - App Delegate

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Hide dock icon (menu bar only)
        NSApp.setActivationPolicy(.accessory)
        
        // Request notification permissions
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound]) { granted, error in
            if granted {
                print("✅ Notification permission granted")
            }
        }
    }
}

// MARK: - Menu Bar View

struct MenuBarView: View {
    @EnvironmentObject var monitor: SyncStatusMonitor
    @State private var showingDashboard = false
    @State private var showingSettings = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Status Section
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Image(systemName: monitor.statusIcon)
                        .foregroundColor(monitor.statusColor)
                    Text("Beast Observatory")
                        .font(.headline)
                }
                
                Text("Last Sync: \(monitor.lastSyncTime)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                if let error = monitor.lastError {
                    Text("Error: \(error)")
                        .font(.caption)
                        .foregroundColor(.red)
                }
            }
            .padding(.vertical, 4)
            
            Divider()
            
            // Quick Actions
            Button(action: {
                monitor.triggerSync()
            }) {
                Label("Sync Now", systemImage: "arrow.clockwise")
            }
            .keyboardShortcut("s", modifiers: .command)
            
            Button(action: {
                showingDashboard = true
            }) {
                Label("Open Dashboard", systemImage: "chart.bar")
            }
            .keyboardShortcut("d", modifiers: .command)
            
            Button(action: {
                showingLogs()
            }) {
                Label("View Logs", systemImage: "doc.text")
            }
            .keyboardShortcut("l", modifiers: .command)
            
            Divider()
            
            Button(action: {
                showingSettings = true
            }) {
                Label("Settings...", systemImage: "gearshape")
            }
            .keyboardShortcut(",", modifiers: .command)
            
            Divider()
            
            Button("Quit") {
                NSApplication.shared.terminate(nil)
            }
            .keyboardShortcut("q", modifiers: .command)
        }
        .padding()
        .frame(width: 280)
        .sheet(isPresented: $showingDashboard) {
            DashboardView()
                .environmentObject(monitor)
        }
        .sheet(isPresented: $showingSettings) {
            SettingsView()
        }
    }
    
    private func showingLogs() {
        let logPath = "~/Library/Logs/beast-observatory/sync.log"
        NSWorkspace.shared.openFile((logPath as NSString).expandingTildeInPath)
    }
}

// MARK: - Sync Status Monitor

@MainActor
class SyncStatusMonitor: ObservableObject {
    @Published var lastSyncTime: String = "Never"
    @Published var lastError: String? = nil
    @Published var isSyncing: Bool = false
    
    var statusIcon: String {
        if isSyncing {
            return "arrow.triangle.2.circlepath"
        } else if lastError != nil {
            return "exclamationmark.triangle.fill"
        } else {
            return "checkmark.circle.fill"
        }
    }
    
    var statusColor: Color {
        if isSyncing {
            return .blue
        } else if lastError != nil {
            return .red
        } else {
            return .green
        }
    }
    
    init() {
        updateStatus()
        startMonitoring()
    }
    
    func triggerSync() {
        Task {
            isSyncing = true
            do {
                // Call sync service
                try await ObservatoryService.shared.syncNow()
                lastSyncTime = "Just now"
                lastError = nil
                sendNotification(title: "Sync Complete", body: "Metrics synced successfully")
            } catch {
                lastError = error.localizedDescription
                sendNotification(title: "Sync Failed", body: error.localizedDescription)
            }
            isSyncing = false
        }
    }
    
    private func updateStatus() {
        // Read from log file or service status
        if let lastSync = ObservatoryService.shared.getLastSyncTime() {
            let formatter = RelativeDateTimeFormatter()
            lastSyncTime = formatter.localizedString(for: lastSync, relativeTo: Date())
        }
    }
    
    private func startMonitoring() {
        Timer.scheduledTimer(withTimeInterval: 60, repeats: true) { _ in
            Task { @MainActor in
                self.updateStatus()
            }
        }
    }
    
    private func sendNotification(title: String, body: String) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        
        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: nil
        )
        
        UNUserNotificationCenter.current().add(request)
    }
}

// MARK: - Observatory Service

class ObservatoryService {
    static let shared = ObservatoryService()
    
    private init() {}
    
    func syncNow() async throws {
        // Call Python sync service via local HTTP API or process
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/local/bin/beast-observatory-sync")
        process.arguments = ["--one-shot"]
        
        try process.run()
        process.waitUntilExit()
        
        guard process.terminationStatus == 0 else {
            throw ObservatoryError.syncFailed(process.terminationStatus)
        }
    }
    
    func getLastSyncTime() -> Date? {
        // Read from log file or status file
        let logPath = NSString(string: "~/Library/Logs/beast-observatory/sync.log").expandingTildeInPath
        if let attributes = try? FileManager.default.attributesOfItem(atPath: logPath),
           let modificationDate = attributes[.modificationDate] as? Date {
            return modificationDate
        }
        return nil
    }
}

enum ObservatoryError: LocalizedError {
    case syncFailed(Int32)
    
    var errorDescription: String? {
        switch self {
        case .syncFailed(let code):
            return "Sync failed with exit code \(code)"
        }
    }
}

