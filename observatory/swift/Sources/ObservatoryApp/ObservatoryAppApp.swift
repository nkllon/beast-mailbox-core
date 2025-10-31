//
//  ObservatoryAppApp.swift
//  ObservatoryApp
//
//  App structure for SwiftUI
//

import SwiftUI
import AppKit
import UserNotifications

@main
struct ObservatoryAppApp: App {
    @StateObject private var statusMonitor = StatusMonitor()
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        MenuBarExtra {
            MenuBarView()
                .environmentObject(statusMonitor)
        } label: {
            Image(systemName: statusMonitor.statusIcon)
                .foregroundColor(statusMonitor.statusColor)
        }
        .menuBarExtraStyle(.window)
    }
}

// MARK: - App Delegate

class AppDelegate: NSObject, NSApplicationDelegate {
    private var intelligenceServer: SimpleHTTPServer?
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Hide dock icon (menu bar only app)
        NSApp.setActivationPolicy(.accessory)
        
        // Start Apple Intelligence HTTP server (for Python agents)
        startIntelligenceServer()
        
        // Request notification permissions
        Task {
            do {
                let center = UNUserNotificationCenter.current()
                let granted = try await center.requestAuthorization(options: [.alert, .sound, .badge])
                if granted {
                    print("✅ Notification permission granted")
                }
            } catch {
                print("⚠️  Notification permission error: \(error)")
            }
        }
    }
    
    private func startIntelligenceServer() {
        let server = SimpleHTTPServer(port: 8081)
        do {
            try server.start()
            intelligenceServer = server
            print("✅ Apple Intelligence HTTP server started on port 8081")
            print("   Python agents can query at: http://localhost:8081/query")
        } catch {
            print("⚠️  Failed to start intelligence server: \(error)")
        }
    }
}

