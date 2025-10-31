//
//  StatusMonitor.swift
//  ObservatoryApp
//
//  Monitors Observatory sync service status
//

import SwiftUI
import Combine
import OSLog
import UserNotifications

@MainActor
class StatusMonitor: ObservableObject {
    @Published var lastSyncTime: Date?
    @Published var isSyncing: Bool = false
    @Published var lastError: String?
    @Published var coverage: Double?
    @Published var bugs: Int?
    
    private let service = ObservatoryService.shared
    private var updateTimer: Timer?
    private let logger = Logger(subsystem: "com.nkllon.ObservatoryApp", category: "StatusMonitor")
    
    var statusIcon: String {
        if isSyncing {
            return "arrow.triangle.2.circlepath"
        } else if lastError != nil {
            return "exclamationmark.triangle.fill"
        } else if lastSyncTime != nil {
            return "checkmark.circle.fill"
        } else {
            return "questionmark.circle"
        }
    }
    
    var statusColor: Color {
        if isSyncing {
            return .blue
        } else if lastError != nil {
            return .red
        } else if lastSyncTime != nil {
            return .green
        } else {
            return .gray
        }
    }
    
    var lastSyncTimeString: String {
        guard let lastSync = lastSyncTime else {
            return "Never"
        }
        
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: lastSync, relativeTo: Date())
    }
    
    init() {
        updateStatus()
        startPeriodicUpdates()
    }
    
    deinit {
        updateTimer?.invalidate()
    }
    
    func updateStatus() {
        Task {
            do {
                let status = try await service.getStatus()
                self.lastSyncTime = status.lastSyncTime
                self.lastError = status.lastError
                self.coverage = status.coverage
                self.bugs = status.bugs
                self.isSyncing = status.isSyncing
                
                logger.info("Status updated: lastSync=\(status.lastSyncTime?.description ?? "nil"), error=\(status.lastError ?? "none")")
            } catch {
                logger.error("Failed to update status: \(error.localizedDescription)")
                self.lastError = "Failed to check status: \(error.localizedDescription)"
            }
        }
    }
    
    func triggerSync() {
        guard !isSyncing else { return }
        
        isSyncing = true
        lastError = nil
        
        Task {
            do {
                try await service.triggerSync()
                // Wait a moment, then refresh status
                try await Task.sleep(nanoseconds: 2_000_000_000) // 2 seconds
                updateStatus()
            } catch {
                lastError = error.localizedDescription
                logger.error("Sync failed: \(error.localizedDescription)")
            }
            isSyncing = false
        }
    }
    
    private func startPeriodicUpdates() {
        updateTimer = Timer.scheduledTimer(withTimeInterval: 60.0, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.updateStatus()
            }
        }
    }
}

