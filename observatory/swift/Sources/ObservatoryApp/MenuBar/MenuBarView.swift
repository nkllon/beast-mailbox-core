//
//  MenuBarView.swift
//  ObservatoryApp
//
//  Menu bar popup view
//

import SwiftUI

struct MenuBarView: View {
    @EnvironmentObject var monitor: StatusMonitor
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
                
                Text("Last Sync: \(monitor.lastSyncTimeString)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                if let coverage = monitor.coverage {
                    Text("Coverage: \(coverage, specifier: "%.1f")%")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                if let error = monitor.lastError {
                    Text("Error: \(error)")
                        .font(.caption)
                        .foregroundColor(.red)
                        .lineLimit(2)
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
            .disabled(monitor.isSyncing)
            
            Button(action: {
                showingDashboard = true
            }) {
                Label("Open Dashboard", systemImage: "chart.bar")
            }
            .keyboardShortcut("d", modifiers: .command)
            
            Button(action: {
                openLogs()
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
        .frame(width: 300)
        .sheet(isPresented: $showingDashboard) {
            DashboardView()
                .environmentObject(monitor)
        }
        .sheet(isPresented: $showingSettings) {
            SettingsView()
        }
    }
    
    private func openLogs() {
        let logPath = NSString(string: "~/Library/Logs/beast-observatory/sync.log").expandingTildeInPath
        NSWorkspace.shared.openFile(logPath, withApplication: "TextEdit")
    }
}

