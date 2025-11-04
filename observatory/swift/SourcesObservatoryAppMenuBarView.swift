//
//  MenuBarView.swift
//  ObservatoryApp
//
//  Menu bar popup view
//

import SwiftUI
import AppKit

struct MenuBarView: View {
    @EnvironmentObject var monitor: StatusMonitor
    @StateObject private var actionsMonitor = GitHubActionsMonitor()
    @State private var chatWindow: NSWindow?
    @State private var dashboardWindow: NSWindow?
    @State private var settingsWindow: NSWindow?
    
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
            
            // GitHub Actions Status
            if !actionsMonitor.workflows.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text("GitHub Actions")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    ForEach(actionsMonitor.workflows.prefix(2)) { workflow in
                        HStack {
                            Image(systemName: workflow.icon)
                                .foregroundColor(colorForWorkflowStatus(workflow))
                            Text(workflow.name)
                                .font(.caption)
                            Spacer()
                            Text(workflow.status.rawValue.capitalized)
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            
                            // Trigger button
                            if let workflowId = workflow.workflowId {
                                Button(action: {
                                    Task {
                                        do {
                                            try await actionsMonitor.triggerWorkflow(workflowId: workflowId)
                                        } catch {
                                            print("⚠️  Failed to trigger workflow: \(error)")
                                        }
                                    }
                                }) {
                                    Image(systemName: "arrow.clockwise")
                                        .font(.caption2)
                                }
                                .buttonStyle(.plain)
                                .help("Re-run workflow")
                            }
                        }
                        .onTapGesture {
                            if let url = URL(string: workflow.htmlURL) {
                                NSWorkspace.shared.open(url)
                            }
                        }
                    }
                    
                    if actionsMonitor.workflows.count > 2 {
                        Text("+ \(actionsMonitor.workflows.count - 2) more")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.vertical, 4)
                
                Divider()
            }
            
            // Quick Actions
            Button(action: {
                monitor.triggerSync()
            }) {
                Label("Sync Now", systemImage: "arrow.clockwise")
            }
            .keyboardShortcut("s", modifiers: .command)
            .disabled(monitor.isSyncing)
            
            Button(action: {
                openDashboardWindow()
            }) {
                Label("Open Dashboard", systemImage: "chart.bar")
            }
            .keyboardShortcut("d", modifiers: .command)
            
            Button(action: {
                openChatWindow()
            }) {
                Label("Chat with Apple Intelligence", systemImage: "message.fill")
            }
            .keyboardShortcut("c", modifiers: .command)
            
            Button(action: {
                openLogs()
            }) {
                Label("View Logs", systemImage: "doc.text")
            }
            .keyboardShortcut("l", modifiers: .command)
            
            Divider()
            
            Button(action: {
                openSettingsWindow()
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
        .task {
            await actionsMonitor.fetchWorkflows()
        }
    }
    
    private func openChatWindow() {
        // Close existing window if open
        chatWindow?.close()
        chatWindow = nil
        
        // Create new window
        let chatView = ChatView()
            .frame(minWidth: 600, minHeight: 500)
            .environmentObject(monitor)
        
        let hostingView = NSHostingView(rootView: chatView)
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 600, height: 500),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.contentView = hostingView
        window.center()
        window.title = "Apple Intelligence Chat"
        window.makeKeyAndOrderFront(nil)
        window.isReleasedWhenClosed = false
        
        // Keep reference to prevent deallocation
        chatWindow = window
        
        // Window will be managed - closed windows will be niled on next open
    }
    
    private func openDashboardWindow() {
        // Close existing window if open
        dashboardWindow?.close()
        dashboardWindow = nil
        
        // Create new window
        let dashboardView = DashboardView()
            .environmentObject(monitor)
        
        let hostingView = NSHostingView(rootView: dashboardView)
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 800, height: 600),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.contentView = hostingView
        window.center()
        window.title = "Beast Observatory Dashboard"
        window.makeKeyAndOrderFront(nil)
        window.isReleasedWhenClosed = false
        
        dashboardWindow = window
        
        NotificationCenter.default.addObserver(
            forName: NSWindow.willCloseNotification,
            object: window,
            queue: .main
        ) { _ in
            // Window closed, will be handled by next open call
        }
    }
    
    private func openSettingsWindow() {
        // Close existing window if open
        settingsWindow?.close()
        settingsWindow = nil
        
        // Create new window
        let settingsView = SettingsView()
        
        let hostingView = NSHostingView(rootView: settingsView)
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 500, height: 400),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.contentView = hostingView
        window.center()
        window.title = "Settings"
        window.makeKeyAndOrderFront(nil)
        window.isReleasedWhenClosed = false
        
        settingsWindow = window
        
        NotificationCenter.default.addObserver(
            forName: NSWindow.willCloseNotification,
            object: window,
            queue: .main
        ) { _ in
            // Window closed, will be handled by next open call
        }
    }
    
    private func openLogs() {
        let logPath = NSString(string: "~/Library/Logs/beast-observatory/sync.log").expandingTildeInPath
        let fileURL = URL(fileURLWithPath: logPath)
        
        // Use modern API instead of deprecated openFile(_:withApplication:)
        if let textEditURL = NSWorkspace.shared.urlForApplication(withBundleIdentifier: "com.apple.TextEdit") {
            let config = NSWorkspace.OpenConfiguration()
            NSWorkspace.shared.open([fileURL], withApplicationAt: textEditURL, configuration: config) { _, error in
                if let error = error {
                    print("⚠️  Failed to open logs: \(error)")
                }
            }
        } else {
            // Fallback: open with default application
            NSWorkspace.shared.open(fileURL)
        }
    }
    
    private func colorForWorkflowStatus(_ workflow: GitHubActionsMonitor.WorkflowStatus) -> Color {
        switch workflow.status {
        case .queued:
            return .gray
        case .inProgress:
            return .blue
        case .completed:
            switch workflow.conclusion {
            case .success:
                return .green
            case .failure:
                return .red
            case .cancelled:
                return .orange
            case .skipped:
                return .gray
            case .none:
                return .gray
            }
        }
    }
}