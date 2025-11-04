//
//  StatusMonitor.swift
//  ObservatoryApp
//
//  Created on October 31, 2025.
//

import Foundation

/// StatusMonitor provides real-time monitoring of system status and health metrics
@MainActor
class StatusMonitor: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isMonitoring: Bool = false
    @Published var currentStatus: SystemStatus = .unknown
    @Published var lastUpdateTime: Date?
    @Published var errorCount: Int = 0
    
    // MARK: - Private Properties
    
    private var monitoringTimer: Timer?
    private let updateInterval: TimeInterval = 5.0 // 5 seconds
    private var statusCheckers: [StatusChecker] = []
    
    // MARK: - Initialization
    
    init() {
        setupStatusCheckers()
    }
    
    deinit {
        stopMonitoring()
    }
    
    // MARK: - Public Methods
    
    /// Starts the status monitoring process
    func startMonitoring() {
        guard !isMonitoring else { return }
        
        isMonitoring = true
        currentStatus = .monitoring
        
        // Start the monitoring timer
        monitoringTimer = Timer.scheduledTimer(withTimeInterval: updateInterval, repeats: true) { [weak self] _ in
            Task { @MainActor in
                await self?.performStatusCheck()
            }
        }
        
        // Perform initial status check
        Task {
            await performStatusCheck()
        }
    }
    
    /// Stops the status monitoring process
    func stopMonitoring() {
        guard isMonitoring else { return }
        
        isMonitoring = false
        monitoringTimer?.invalidate()
        monitoringTimer = nil
        currentStatus = .stopped
    }
    
    /// Performs a manual status check
    func performManualCheck() async {
        await performStatusCheck()
    }
    
    /// Resets the error count
    func resetErrorCount() {
        errorCount = 0
    }
    
    // MARK: - Private Methods
    
    private func setupStatusCheckers() {
        statusCheckers = [
            NetworkStatusChecker(),
            DatabaseStatusChecker(),
            ServiceStatusChecker()
        ]
    }
    
    private func performStatusCheck() async {
        var allHealthy = true
        var errors = 0
        
        for checker in statusCheckers {
            do {
                let isHealthy = try await checker.checkStatus()
                if !isHealthy {
                    allHealthy = false
                    errors += 1
                }
            } catch {
                allHealthy = false
                errors += 1
                print("Status check error: \(error)")
            }
        }
        
        // Update status based on checks
        if allHealthy {
            currentStatus = .healthy
        } else if errors < statusCheckers.count {
            currentStatus = .degraded
        } else {
            currentStatus = .unhealthy
        }
        
        errorCount = errors
        lastUpdateTime = Date()
    }
}

// MARK: - Supporting Types

enum SystemStatus: String, CaseIterable {
    case unknown = "Unknown"
    case monitoring = "Monitoring"
    case healthy = "Healthy"
    case degraded = "Degraded"
    case unhealthy = "Unhealthy"
    case stopped = "Stopped"
    
    var color: String {
        switch self {
        case .unknown, .stopped:
            return "gray"
        case .monitoring:
            return "blue"
        case .healthy:
            return "green"
        case .degraded:
            return "yellow"
        case .unhealthy:
            return "red"
        }
    }
}

// MARK: - Status Checker Protocol

protocol StatusChecker {
    func checkStatus() async throws -> Bool
}

// MARK: - Concrete Status Checkers

struct NetworkStatusChecker: StatusChecker {
    func checkStatus() async throws -> Bool {
        // Simulate network connectivity check
        try await Task.sleep(nanoseconds: 100_000_000) // 0.1 seconds
        return true // In real implementation, check actual network status
    }
}

struct DatabaseStatusChecker: StatusChecker {
    func checkStatus() async throws -> Bool {
        // Simulate database connectivity check
        try await Task.sleep(nanoseconds: 150_000_000) // 0.15 seconds
        return true // In real implementation, ping database
    }
}

struct ServiceStatusChecker: StatusChecker {
    func checkStatus() async throws -> Bool {
        // Simulate service health check
        try await Task.sleep(nanoseconds: 200_000_000) // 0.2 seconds
        return Bool.random() // Simulate occasional service issues
    }
}