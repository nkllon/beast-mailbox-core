//
//  ShortcutsIntent.swift
//  Beast Observatory Shortcuts Integration
//
//  Apple Shortcuts App integration for voice control and automation
//

import AppIntents
import Foundation

// MARK: - Check Observatory Status Intent

struct CheckObservatoryStatusIntent: AppIntent {
    static var title: LocalizedStringResource = "Check Beast Observatory Status"
    static var description = IntentDescription("Check the current status of Beast Observatory sync service")
    static var openAppWhenRun: Bool = false
    
    func perform() async throws -> some IntentResult & ReturnsValue<String> {
        let status = await ObservatoryStatusProvider.shared.getStatus()
        return .result(value: status.message)
    }
}

// MARK: - Trigger Sync Intent

struct TriggerSyncIntent: AppIntent {
    static var title: LocalizedStringResource = "Trigger Observatory Sync"
    static var description = IntentDescription("Manually trigger a sync of SonarCloud metrics to Prometheus")
    static var openAppWhenRun: Bool = false
    
    func perform() async throws -> some IntentResult & ReturnsValue<Bool> {
        do {
            try await ObservatoryService.shared.syncNow()
            return .result(value: true)
        } catch {
            throw error
        }
    }
}

// MARK: - Get Coverage Intent

struct GetCoverageIntent: AppIntent {
    static var title: LocalizedStringResource = "Get Code Coverage"
    static var description = IntentDescription("Get the current code coverage percentage")
    
    @Parameter(title: "Project")
    var project: String?
    
    func perform() async throws -> some IntentResult & ReturnsValue<Double> {
        let projectKey = project ?? "nkllon_beast-mailbox-core"
        let coverage = try await MetricsProvider.shared.getCoverage(project: projectKey)
        return .result(value: coverage)
    }
}

// MARK: - Status Provider

class ObservatoryStatusProvider {
    static let shared = ObservatoryStatusProvider()
    
    struct Status {
        let isRunning: Bool
        let lastSync: Date?
        let lastError: String?
        
        var message: String {
            if let error = lastError {
                return "Observatory sync failed: \(error)"
            } else if let lastSync = lastSync {
                let formatter = RelativeDateTimeFormatter()
                return "Last sync: \(formatter.localizedString(for: lastSync, relativeTo: Date()))"
            } else {
                return "Observatory status: \(isRunning ? "Running" : "Not running")"
            }
        }
    }
    
    func getStatus() async -> Status {
        // Check if service is running
        let isRunning = checkServiceRunning()
        
        // Get last sync time
        let lastSync = ObservatoryService.shared.getLastSyncTime()
        
        // Check for errors in log
        let lastError = checkLastError()
        
        return Status(isRunning: isRunning, lastSync: lastSync, lastError: lastError)
    }
    
    private func checkServiceRunning() -> Bool {
        // Check launchctl status
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/bin/launchctl")
        process.arguments = ["list", "com.nkllon.beast-observatory-sync"]
        
        do {
            try process.run()
            process.waitUntilExit()
            return process.terminationStatus == 0
        } catch {
            return false
        }
    }
    
    private func checkLastError() -> String? {
        let logPath = NSString(string: "~/Library/Logs/beast-observatory/sync.error.log").expandingTildeInPath
        guard let logContent = try? String(contentsOfFile: logPath) else {
            return nil
        }
        
        // Extract last error from log
        let lines = logContent.components(separatedBy: .newlines).reversed()
        for line in lines.prefix(20) {
            if line.lowercased().contains("error") || line.contains("ERROR") {
                return line.trimmingCharacters(in: .whitespaces)
            }
        }
        
        return nil
    }
}

// MARK: - Metrics Provider

class MetricsProvider {
    static let shared = MetricsProvider()
    
    func getCoverage(project: String) async throws -> Double {
        // Query Prometheus or SonarCloud API
        // For now, return a placeholder
        return 89.5
    }
}

