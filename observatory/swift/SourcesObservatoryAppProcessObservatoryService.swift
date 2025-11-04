//
//  ProcessObservatoryService.swift
//  ObservatoryApp
//
//  Process-based Observatory service implementation
//  Executes local observatory sync binary
//

import Foundation
import OSLog

class ProcessObservatoryService: ObservatoryServicing {
    private let logger = Logger(subsystem: "com.nkllon.ObservatoryApp", category: "ProcessService")
    private let syncServicePath: String
    private let logPath: String
    private let errorLogPath: String
    
    init(
        syncServicePath: String = ObservatoryServiceConfig.defaultSyncBinaryPath,
        logPath: String = ObservatoryServiceConfig.defaultLogPath,
        errorLogPath: String = ObservatoryServiceConfig.defaultErrorLogPath
    ) {
        self.syncServicePath = syncServicePath
        self.logPath = logPath
        self.errorLogPath = errorLogPath
        
        logger.info("ProcessObservatoryService initialized with binary: \(syncServicePath)")
    }
    
    func triggerSync(timeout: TimeInterval = ObservatoryServiceConfig.defaultSyncTimeout) async throws {
        guard FileManager.default.fileExists(atPath: syncServicePath) else {
            logger.error("Sync binary not found at path: \(syncServicePath)")
            throw ObservatoryError.serviceUnavailable
        }
        
        logger.info("Triggering sync via process: \(syncServicePath)")
        
        return try await withCheckedThrowingContinuation { continuation in
            let process = Process()
            process.executableURL = URL(fileURLWithPath: syncServicePath)
            process.arguments = ["--one-shot"]
            
            var hasResumed = false
            
            process.terminationHandler = { process in
                guard !hasResumed else { return }
                hasResumed = true
                
                if process.terminationStatus == 0 {
                    self.logger.info("Sync process completed successfully")
                    continuation.resume()
                } else {
                    self.logger.error("Sync process failed with exit code: \(process.terminationStatus)")
                    continuation.resume(throwing: ObservatoryError.syncFailed(process.terminationStatus))
                }
            }
            
            do {
                try process.run()
                
                // Set up timeout
                DispatchQueue.global().asyncAfter(deadline: .now() + timeout) {
                    if process.isRunning && !hasResumed {
                        hasResumed = true
                        self.logger.warning("Sync process timed out after \(timeout) seconds")
                        process.terminate()
                        continuation.resume(throwing: ObservatoryError.timeout)
                    }
                }
            } catch {
                guard !hasResumed else { return }
                hasResumed = true
                self.logger.error("Failed to start sync process: \(error.localizedDescription)")
                continuation.resume(throwing: error)
            }
        }
    }
    
    func getStatus() async throws -> SyncStatus {
        return try await getStatusFromLogFile()
    }
    
    func getLastSyncTime() async throws -> Date? {
        let status = try await getStatus()
        return status.lastSyncTime
    }
    
    // MARK: - Private Methods
    
    private func getStatusFromLogFile() async throws -> SyncStatus {
        let expandedLogPath = NSString(string: logPath).expandingTildeInPath
        
        guard FileManager.default.fileExists(atPath: expandedLogPath) else {
            logger.debug("Log file not found at path: \(expandedLogPath)")
            return SyncStatus(
                lastSyncTime: nil,
                lastError: nil,
                isSyncing: false,
                coverage: nil,
                bugs: nil,
                vulnerabilities: nil,
                codeSmells: nil,
                metricsCollectedAt: nil,
                syncDuration: nil,
                syncSource: "process"
            )
        }
        
        // Get last modification time (proxy for last sync)
        let attributes = try FileManager.default.attributesOfItem(atPath: expandedLogPath)
        let modificationDate = attributes[.modificationDate] as? Date
        
        // Read last error from error log
        let expandedErrorLogPath = NSString(string: errorLogPath).expandingTildeInPath
        var lastError: String? = nil
        
        if FileManager.default.fileExists(atPath: expandedErrorLogPath),
           let errorContent = try? String(contentsOfFile: expandedErrorLogPath),
           let lastLine = errorContent.components(separatedBy: .newlines).last(where: { 
               !$0.isEmpty && ($0.contains("ERROR") || $0.contains("error")) 
           }) {
            lastError = lastLine.trimmingCharacters(in: .whitespaces)
        }
        
        logger.debug("Status from log file: lastSync=\(modificationDate?.description ?? "nil"), error=\(lastError ?? "none")")
        
        return SyncStatus(
            lastSyncTime: modificationDate,
            lastError: lastError,
            isSyncing: false, // Can't determine from log file
            coverage: nil,
            bugs: nil,
            vulnerabilities: nil,
            codeSmells: nil,
            metricsCollectedAt: modificationDate,
            syncDuration: nil,
            syncSource: "process"
        )
    }
}