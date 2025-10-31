//
//  ObservatoryAppApp.swift
//  ObservatoryApp
//
//  App structure for SwiftUI
//

import SwiftUI
import AppKit
import UserNotifications
import AppKit
import UserNotifications

@main
struct ObservatoryAppApp: App {
    @StateObject private var statusMonitor = StatusMonitor()
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    init() {
        // Hide dock icon (menu bar only app)
        NSApp.setActivationPolicy(.accessory)
    }
    
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
    func applicationDidFinishLaunching(_ notification: Notification) {
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
}

