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

// MARK: - Service Factory

class ObservatoryServiceFactory {
    static func createService() -> ObservatoryServicing {
        let mode = ProcessInfo.processInfo.environment["OBS_SYNC_MODE"] ?? "process"
        let endpoint = ProcessInfo.processInfo.environment["OBS_SYNC_ENDPOINT"] ?? "http://localhost:8080"
        
        switch mode.lowercased() {
        case "http":
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
    
    // Monitoring endpoints (for future Prometheus integration)
    static let prometheusEndpoint = ProcessInfo.processInfo.environment["PROMETHEUS_ENDPOINT"] ?? "http://prometheus.nkllon.com"
    static let grafanaEndpoint = ProcessInfo.processInfo.environment["GRAFANA_ENDPOINT"] ?? "http://grafana.nkllon.com"
    static let observatoryEndpoint = ProcessInfo.processInfo.environment["OBSERVATORY_ENDPOINT"] ?? "http://observatory.nkllon.com"
}