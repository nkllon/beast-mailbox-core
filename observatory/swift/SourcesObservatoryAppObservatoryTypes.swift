//
//  ObservatoryTypes.swift
//  ObservatoryApp
//
//  Shared types and errors for Observatory services
//

import Foundation

// MARK: - Sync Status

struct SyncStatus: Codable {
    let lastSyncTime: Date?
    let lastError: String?
    let isSyncing: Bool
    let coverage: Double?
    let bugs: Int?
    let vulnerabilities: Int?
    let codeSmells: Int?
    
    // Additional metrics for Prometheus integration
    let metricsCollectedAt: Date?
    let syncDuration: TimeInterval?
    let syncSource: String? // "process", "http", "redis"
}

// MARK: - Observatory Errors

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

// MARK: - Service Info

struct ServiceInfo {
    let mode: ServiceMode
    let endpoint: String?
    let isAvailable: Bool
    let lastHealthCheck: Date?
    
    enum ServiceMode: String, CaseIterable {
        case process = "process"
        case http = "http" 
        case redis = "redis"
        
        var displayName: String {
            switch self {
            case .process: return "Local Process"
            case .http: return "HTTP API"
            case .redis: return "Redis Pub/Sub"
            }
        }
    }
}