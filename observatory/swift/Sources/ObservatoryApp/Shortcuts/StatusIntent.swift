//
//  StatusIntent.swift
//  ObservatoryApp
//
//  Apple Shortcuts intent for checking Observatory status
//

import AppIntents
import Foundation

struct CheckObservatoryStatusIntent: AppIntent {
    static var title: LocalizedStringResource = "Check Beast Observatory Status"
    static var description = IntentDescription("Check the current status of Beast Observatory sync service")
    static var openAppWhenRun: Bool = false
    
    func perform() async throws -> some IntentResult & ReturnsValue<String> {
        let status = await ObservatoryStatusProvider.shared.getStatus()
        return .result(value: status.message)
    }
}

// MARK: - Status Provider

actor ObservatoryStatusProvider {
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
                formatter.unitsStyle = .abbreviated
                return "Last sync: \(formatter.localizedString(for: lastSync, relativeTo: Date()))"
            } else if isRunning {
                return "Observatory sync service is running"
            } else {
                return "Observatory sync service is not running"
            }
        }
    }
    
    func getStatus() async -> Status {
        // Check if service is running (launchctl)
        let isRunning = await checkServiceRunning()
        
        // Get last sync time from log file
        let lastSync = getLastSyncTime()
        
        // Check for errors
        let lastError = getLastError()
        
        return Status(isRunning: isRunning, lastSync: lastSync, lastError: lastError)
    }
    
    private func checkServiceRunning() async -> Bool {
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
    
    private func getLastSyncTime() -> Date? {
        let logPath = NSString(string: "~/Library/Logs/beast-observatory/sync.log").expandingTildeInPath
        
        guard FileManager.default.fileExists(atPath: logPath) else {
            return nil
        }
        
        do {
            let attributes = try FileManager.default.attributesOfItem(atPath: logPath)
            return attributes[.modificationDate] as? Date
        } catch {
            return nil
        }
    }
    
    private func getLastError() -> String? {
        let errorLogPath = NSString(string: "~/Library/Logs/beast-observatory/sync.error.log").expandingTildeInPath
        
        guard FileManager.default.fileExists(atPath: errorLogPath),
              let errorContent = try? String(contentsOfFile: errorLogPath) else {
            return nil
        }
        
        // Extract last error from log
        let lines = errorContent.components(separatedBy: .newlines).reversed()
        for line in lines.prefix(20) {
            if line.lowercased().contains("error") || line.contains("ERROR") {
                return line.trimmingCharacters(in: .whitespaces)
            }
        }
        
        return nil
    }
}

