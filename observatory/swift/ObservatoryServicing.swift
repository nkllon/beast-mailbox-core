//
//  ObservatoryServicing.swift
//  ObservatoryApp
//
//  Protocol abstraction for Observatory sync services
//  Supports local process, HTTP API, and Redis-based implementations
//

import Foundation

// MARK: - Service Protocol

protocol ObservatoryServicing {
    func triggerSync(timeout: TimeInterval) async throws
    func getStatus() async throws -> SyncStatus
    func getLastSyncTime() async throws -> Date?
}

// MARK: - Shared Types

struct SyncStatus: Codable {
    let lastSyncTime: Date?
    let lastError: String?
    let isSyncing: Bool
    let coverage: Double?
    let bugs: Int?
    let vulnerabilities: Int?
    let codeSmells: Int?
    
    // Additional metrics for infrastructure integration
    let metricsCollectedAt: Date?
    let syncDuration: TimeInterval?
    let syncSource: String? // "process", "http", "redis"
}

enum ObservatoryError: LocalizedError {
    case serviceUnavailable
    case syncFailed(Int32)
    case invalidResponse
    case timeout
    case connectionFailed(String)
    case authenticationFailed
    case configurationError(String)
    
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
        case .connectionFailed(let details):
            return "Connection failed: \(details)"
        case .authenticationFailed:
            return "Authentication failed"
        case .configurationError(let details):
            return "Configuration error: \(details)"
        }
    }
    
    var recoverySuggestion: String? {
        switch self {
        case .serviceUnavailable:
            return "Check that the Observatory service is running and accessible"
        case .syncFailed:
            return "Check the Observatory logs for detailed error information"
        case .invalidResponse:
            return "Verify the Observatory service API version is compatible"
        case .timeout:
            return "Try increasing the timeout or check if the sync process is stuck"
        case .connectionFailed:
            return "Check network connectivity and service endpoint configuration"
        case .authenticationFailed:
            return "Verify credentials and authentication configuration"
        case .configurationError:
            return "Check environment variables and service configuration"
        }
    }
}

// MARK: - Service Factory

class ObservatoryServiceFactory {
    static func createService() -> ObservatoryServicing {
        let mode = ProcessInfo.processInfo.environment["OBS_SYNC_MODE"] ?? "process"
        
        switch mode.lowercased() {
        case "http":
            let endpoint = ProcessInfo.processInfo.environment["OBS_SYNC_ENDPOINT"] ?? "http://localhost:8080"
            return HTTPObservatoryService(baseURL: URL(string: endpoint)!)
        case "redis":
            let redisHost = ProcessInfo.processInfo.environment["REDIS_HOST"] ?? "localhost"
            let redisPort = Int(ProcessInfo.processInfo.environment["REDIS_PORT"] ?? "6379") ?? 6379
            return RedisObservatoryService(host: redisHost, port: redisPort)
        case "process":
            fallthrough
        default:
            return ProcessObservatoryService()
        }
    }
}

// MARK: - Service Configuration

struct ObservatoryServiceConfig {
    // Process mode
    static let defaultSyncBinaryPath = "/usr/local/bin/beast-observatory-sync"
    static let defaultLogPath = "~/Library/Logs/beast-observatory/sync.log"
    static let defaultErrorLogPath = "~/Library/Logs/beast-observatory/sync.error.log"
    
    // HTTP mode  
    static let defaultHTTPEndpoint = "http://localhost:8080"
    
    // Redis mode
    static let defaultRedisHost = "localhost"
    static let defaultRedisPort = 6379
    static let syncTriggerKey = "observatory:sync:trigger"
    static let syncStatusKey = "observatory:sync:status"
    
    // Timeouts
    static let defaultSyncTimeout: TimeInterval = 60.0
    static let defaultHTTPTimeout: TimeInterval = 30.0
    
    // Infrastructure endpoints (vonnegut lab instance)
    static let prometheusEndpoint = ProcessInfo.processInfo.environment["PROMETHEUS_ENDPOINT"] ?? "https://prometheus.nkllon.com"
    static let grafanaEndpoint = ProcessInfo.processInfo.environment["GRAFANA_ENDPOINT"] ?? "https://grafana.nkllon.com"
    static let observatoryEndpoint = ProcessInfo.processInfo.environment["OBSERVATORY_ENDPOINT"] ?? "https://observatory.nkllon.com"
    
    // Local development (herbert/Docker Desktop)
    static let localPrometheusEndpoint = "http://localhost:9090"
    static let localGrafanaEndpoint = "http://localhost:3000"
    static let localObservatoryEndpoint = "http://localhost:8080"
    static let localRedisEndpoint = "redis://localhost:6379"
}