//
//  MenuBarApp.swift
//  Beast Observatory Menu Bar
//
//  Native macOS menu bar application for Beast Observatory
//  Provides status indicator and quick actions
//

import SwiftUI
import AppKit
import UserNotifications

@main
struct ObservatoryMenuBar: App {
    @StateObject private var syncMonitor = StatusMonitor()
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