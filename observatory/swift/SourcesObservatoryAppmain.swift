//
//  main.swift
//  ObservatoryApp
//
//  Entry point for Observatory App
//

import SwiftUI

@main
struct ObservatoryApp: App {
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