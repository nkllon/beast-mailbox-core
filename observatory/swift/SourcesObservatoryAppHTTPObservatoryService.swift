//
//  HTTPObservatoryService.swift
//  ObservatoryApp
//
//  HTTP-based Observatory service implementation
//  Connects to containerized Observatory API
//

import Foundation
import OSLog

class HTTPObservatoryService: ObservatoryServicing {
    private let baseURL: URL
    private let session: URLSession
    private let logger = Logger(subsystem: "com.nkllon.ObservatoryApp", category: "HTTPService")
    
    init(baseURL: URL) {
        self.baseURL = baseURL
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = ObservatoryServiceConfig.defaultHTTPTimeout
        config.timeoutIntervalForResource = ObservatoryServiceConfig.defaultHTTPTimeout
        self.session = URLSession(configuration: config)
        
        logger.info("HTTPObservatoryService initialized with endpoint: \(baseURL.absoluteString)")
    }
    
    func triggerSync(timeout: TimeInterval = ObservatoryServiceConfig.defaultSyncTimeout) async throws {
        let url = baseURL.appendingPathComponent("api/v1/sync")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Include timeout in request body
        let requestBody = ["timeout": timeout]
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        logger.info("Triggering sync via HTTP API: \(url.absoluteString)")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw ObservatoryError.invalidResponse
        }
        
        guard 200...299 ~= httpResponse.statusCode else {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            logger.error("Sync API returned \(httpResponse.statusCode): \(errorMessage)")
            throw ObservatoryError.syncFailed(Int32(httpResponse.statusCode))
        }
        
        logger.info("Sync triggered successfully via HTTP API")
    }
    
    func getStatus() async throws -> SyncStatus {
        let url = baseURL.appendingPathComponent("api/v1/status")
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        logger.debug("Fetching status from HTTP API: \(url.absoluteString)")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw ObservatoryError.invalidResponse
        }
        
        guard 200...299 ~= httpResponse.statusCode else {
            logger.warning("Status API returned \(httpResponse.statusCode), using fallback")
            // Fall back to empty status rather than failing
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
        
        do {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            let status = try decoder.decode(SyncStatus.self, from: data)
            logger.debug("Status fetched successfully from HTTP API")
            return status
        } catch {
            logger.error("Failed to decode status response: \(error.localizedDescription)")
            throw ObservatoryError.invalidResponse
        }
    }
    
    func getLastSyncTime() async throws -> Date? {
        let status = try await getStatus()
        return status.lastSyncTime
    }
}