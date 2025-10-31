//
//  SimpleHTTPServer.swift
//  ObservatoryApp
//
//  Simple HTTP server for exposing Apple Intelligence queries as REST API
//  Allows Python agents to query Apple Intelligence programmatically
//

import Foundation
import Network
import OSLog

class SimpleHTTPServer {
    private let port: UInt16
    private var listener: NWListener?
    private let logger = Logger(subsystem: "com.nkllon.ObservatoryApp", category: "HTTPServer")
    private let queue = DispatchQueue(label: "http-server")
    
    init(port: UInt16 = 8081) {
        self.port = port
    }
    
    func start() throws {
        guard listener == nil else {
            logger.warning("Server already running")
            return
        }
        
        let parameters = NWParameters.tcp
        let portEndpoint = NWEndpoint.Port(rawValue: port)!
        listener = try NWListener(using: parameters, on: portEndpoint)
        
        listener?.newConnectionHandler = { [weak self] connection in
            self?.handleConnection(connection)
        }
        
        listener?.start(queue: queue)
        logger.info("✅ Apple Intelligence HTTP server started on port \(port)")
    }
    
    func stop() {
        listener?.cancel()
        listener = nil
        logger.info("Apple Intelligence HTTP server stopped")
    }
    
    private func handleConnection(_ connection: NWConnection) {
        connection.start(queue: queue)
        
        connection.receive(minimumIncompleteLength: 1, maximumLength: 65536) { [weak self] data, _, isComplete, error in
            if let error = error {
                self?.logger.error("Connection error: \(error)")
                connection.cancel()
                return
            }
            
            if let data = data, !data.isEmpty {
                self?.handleRequest(data: data, connection: connection)
            }
            
            if !isComplete {
                connection.receive(minimumIncompleteLength: 1, maximumLength: 65536) { _, _, _, _ in }
            }
        }
    }
    
    private func handleRequest(data: Data, connection: NWConnection) {
        guard let requestString = String(data: data, encoding: .utf8) else {
            sendResponse(connection: connection, status: 400, body: "Invalid request")
            return
        }
        
        logger.debug("Received request: \(requestString.prefix(200))")
        
        let response = processRequest(requestString)
        sendResponse(connection: connection, status: response.status, body: response.body, headers: response.headers)
    }
    
    private func processRequest(_ requestString: String) -> ServerHTTPResponse {
        let lines = requestString.components(separatedBy: .newlines)
        guard let firstLine = lines.first else {
            return ServerHTTPResponse(status: 400, body: "Invalid request")
        }
        
        let parts = firstLine.split(separator: " ")
        guard parts.count >= 2 else {
            return ServerHTTPResponse(status: 400, body: "Invalid request")
        }
        
        let method = String(parts[0])
        let path = String(parts[1])
        
        // Extract body if present
        let bodyStart = requestString.range(of: "\r\n\r\n")
        let body = bodyStart != nil ? String(requestString[bodyStart!.upperBound...]) : ""
        
        switch (method, path) {
        case ("POST", "/query"):
            return handleQuery(body: body)
        case ("POST", "/review"):
            return handleCodeReview(body: body)
        case ("POST", "/diagnose"):
            return handleErrorDiagnosis(body: body)
        case ("GET", "/health"):
            return ServerHTTPResponse(status: 200, body: "OK")
        default:
            return ServerHTTPResponse(status: 404, body: "Not Found")
        }
    }
    
    private func handleQuery(body: String) -> ServerHTTPResponse {
        guard let jsonData = body.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
              let query = json["query"] as? String else {
            return ServerHTTPResponse(status: 400, body: "Missing 'query' parameter")
        }
        
        let context = json["context"] as? String
        let queryType = json["query_type"] as? String ?? "general"
        
        // For now, return placeholder
        // Future: Integrate with Apple Intelligence AppIntents
        let response = """
        {
            "response": "Apple Intelligence response for: \(query)",
            "query_type": "\(queryType)",
            "status": "processed"
        }
        """
        
        return ServerHTTPResponse(
            status: 200,
            body: response,
            headers: ["Content-Type": "application/json"]
        )
    }
    
    private func handleCodeReview(body: String) -> ServerHTTPResponse {
        // TODO: Implement code review
        return ServerHTTPResponse(status: 501, body: "Not implemented")
    }
    
    private func handleErrorDiagnosis(body: String) -> ServerHTTPResponse {
        // TODO: Implement error diagnosis
        return ServerHTTPResponse(status: 501, body: "Not implemented")
    }
    
    private func sendResponse(connection: NWConnection, status: Int, body: String, headers: [String: String] = [:]) {
        let statusText = HTTPStatusText(status: status)
        var response = "HTTP/1.1 \(status) \(statusText)\r\n"
        
        for (key, value) in headers {
            response += "\(key): \(value)\r\n"
        }
        
        response += "Content-Length: \(body.utf8.count)\r\n"
        response += "\r\n"
        response += body
        
        guard let responseData = response.data(using: .utf8) else {
            logger.error("Failed to encode response")
            return
        }
        
        connection.send(content: responseData, completion: .contentProcessed { error in
            if let error = error {
                self.logger.error("Failed to send response: \(error)")
            }
            connection.cancel()
        })
    }
}

struct ServerHTTPResponse {
    let status: Int
    let body: String
    let headers: [String: String]
}

func HTTPStatusText(status: Int) -> String {
    switch status {
    case 200: return "OK"
    case 400: return "Bad Request"
    case 404: return "Not Found"
    case 501: return "Not Implemented"
    default: return "Unknown"
    }
}

