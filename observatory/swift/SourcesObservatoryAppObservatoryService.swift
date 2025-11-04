//
//  ObservatoryService.swift
//  ObservatoryApp
//
//  Service for interacting with Observatory Python sync service
//

import Foundation
import OSLog

struct SyncStatus: Codable {
    let lastSyncTime: Date?
    let lastError: String?
    let isSyncing: Bool
    let coverage: Double?
    let bugs: Int?
    let vulnerabilities: Int?
    let codeSmells: Int?
}

enum ObservatoryError: LocalizedError {
    case serviceUnavailable
    case syncFailed(Int32)
    case invalidResponse
    case timeout
    
    var errorDescription: String? {
        switch self {
        case .serviceUnavailable:
            return "Observatory service is not available"
        case .syncFailed(let code):
            return "Sync failed with exit code \(code)"
        case .invalidResponse:
            return "Invalid response from service"
        case .timeout:
            return "Sync timed out after 60 seconds"
        }
    }
}

class ObservatoryService {
    static let shared = ObservatoryService()
    
    private let logger = Logger(subsystem: "com.nkllon.ObservatoryApp", category: "ObservatoryService")
    
    // Option A: HTTP API (if Python service exposes HTTP)
    private let apiBaseURL = URL(string: "http://localhost:8080")
    
    // Option B: Direct process execution
    private let syncServicePath = "/usr/local/bin/beast-observatory-sync"
    
    private init() {}
    
    // MARK: - Status
    
    func getStatus() async throws -> SyncStatus {
        // Try HTTP API first (if available)
        if let url = apiBaseURL?.appendingPathComponent("status") {
            do {
                let (data, _) = try await URLSession.shared.data(from: url)
                let status = try JSONDecoder().decode(SyncStatus.self, from: data)
                return status
            } catch {
                // Service not running is expected - silently fall back to log file
                // Only log if it's not a connection error
                if !error.localizedDescription.contains("Could not connect") &&
                   !error.localizedDescription.contains("Connection refused") {
                    logger.debug("HTTP API unavailable, using log file: \(error.localizedDescription)")
                }
            }
        }
        
        // Fallback: Read from log file
        return try await getStatusFromLogFile()
    }
    
    private func getStatusFromLogFile() async throws -> SyncStatus {
        let logPath = NSString(string: "~/Library/Logs/beast-observatory/sync.log").expandingTildeInPath
        
        guard FileManager.default.fileExists(atPath: logPath) else {
            return SyncStatus(
                lastSyncTime: nil,
                lastError: nil,
                isSyncing: false,
                coverage: nil,
                bugs: nil,
                vulnerabilities: nil,
                codeSmells: nil
            )
        }
        
        // Get last modification time (proxy for last sync)
        let attributes = try FileManager.default.attributesOfItem(atPath: logPath)
        let modificationDate = attributes[.modificationDate] as? Date
        
        // Read last error from error log
        let errorLogPath = NSString(string: "~/Library/Logs/beast-observatory/sync.error.log").expandingTildeInPath
        var lastError: String? = nil
        
        if FileManager.default.fileExists(atPath: errorLogPath),
           let errorContent = try? String(contentsOfFile: errorLogPath),
           let lastLine = errorContent.components(separatedBy: .newlines).last(where: { !$0.isEmpty && ($0.contains("ERROR") || $0.contains("error")) }) {
            lastError = lastLine.trimmingCharacters(in: .whitespaces)
        }
        
        return SyncStatus(
            lastSyncTime: modificationDate,
            lastError: lastError,
            isSyncing: false, // Can't determine from log file
            coverage: nil,
            bugs: nil,
            vulnerabilities: nil,
            codeSmells: nil
        )
    }
    
    // MARK: - Sync
    
    func triggerSync() async throws {
        // Option A: HTTP API
        if let url = apiBaseURL?.appendingPathComponent("sync") {
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            
            do {
                let (_, response) = try await URLSession.shared.data(for: request)
                if let httpResponse = response as? HTTPURLResponse,
                   httpResponse.statusCode == 200 {
                    logger.info("Sync triggered via HTTP API")
                    return
                }
            } catch {
                // Service not running is expected - silently fall back to process
                if !error.localizedDescription.contains("Could not connect") &&
                   !error.localizedDescription.contains("Connection refused") {
                    logger.debug("HTTP API unavailable, using process: \(error.localizedDescription)")
                }
            }
        }
        
        // Option B: Direct process execution with timeout
        try await triggerSyncViaProcess()
    }
    
    private func triggerSyncViaProcess() async throws {
        guard FileManager.default.fileExists(atPath: syncServicePath) else {
            throw ObservatoryError.serviceUnavailable
        }
        
        return try await withCheckedThrowingContinuation { continuation in
            let process = Process()
            process.executableURL = URL(fileURLWithPath: syncServicePath)
            process.arguments = ["--one-shot"]
            
            process.terminationHandler = { process in
                if process.terminationStatus == 0 {
                    continuation.resume()
                } else {
                    continuation.resume(throwing: ObservatoryError.syncFailed(process.terminationStatus))
                }
            }
            
            do {
                try process.run()
                
                // Set up timeout
                DispatchQueue.global().asyncAfter(deadline: .now() + 60.0) {
                    if process.isRunning {
                        process.terminate()
                        continuation.resume(throwing: ObservatoryError.timeout)
                    }
                }
            } catch {
                continuation.resume(throwing: error)
            }
        }
    }
    
    // MARK: - Metrics
    
    func getMetrics() async throws -> [String: Any] {
        // Query Prometheus or SonarCloud API
        // For now, placeholder
        return [:]
    }
}