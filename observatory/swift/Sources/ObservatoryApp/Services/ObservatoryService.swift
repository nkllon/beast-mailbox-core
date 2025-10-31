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
    
    var errorDescription: String? {
        switch self {
        case .serviceUnavailable:
            return "Observatory service is not available"
        case .syncFailed(let code):
            return "Sync failed with exit code \(code)"
        case .invalidResponse:
            return "Invalid response from service"
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
                logger.warning("HTTP API failed, falling back to log file: \(error.localizedDescription)")
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
                logger.warning("HTTP API failed, falling back to process: \(error.localizedDescription)")
            }
        }
        
        // Option B: Direct process execution
        guard FileManager.default.fileExists(atPath: syncServicePath) else {
            throw ObservatoryError.serviceUnavailable
        }
        
        let process = Process()
        process.executableURL = URL(fileURLWithPath: syncServicePath)
        process.arguments = ["--one-shot"] // If Python service supports this
        
        try process.run()
        process.waitUntilExit()
        
        guard process.terminationStatus == 0 else {
            throw ObservatoryError.syncFailed(process.terminationStatus)
        }
        
        logger.info("Sync triggered via process")
    }
    
    // MARK: - Metrics
    
    func getMetrics() async throws -> [String: Any] {
        // Query Prometheus or SonarCloud API
        // For now, placeholder
        return [:]
    }
}

