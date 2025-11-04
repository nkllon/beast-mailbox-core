//
//  PerformanceMonitor.swift
//  ObservatoryApp
//
//  Performance monitoring for LLM operations
//  Helps prevent Xcode hangs and CPU spikes
//

import Foundation
import OSLog

actor PerformanceMonitor {
    static let shared = PerformanceMonitor()
    
    private let logger = Logger(subsystem: "com.nkllon.ObservatoryApp", category: "Performance")
    private var operationStartTimes: [String: Date] = [:]
    private var operationTimeouts: [String: TimeInterval] = [:]
    
    private init() {}
    
    // MARK: - Operation Tracking
    
    func startOperation(_ operationId: String, timeout: TimeInterval = 30.0) {
        operationStartTimes[operationId] = Date()
        operationTimeouts[operationId] = timeout
        logger.info("Started operation: \(operationId) with timeout: \(timeout)s")
    }
    
    func endOperation(_ operationId: String) -> TimeInterval? {
        guard let startTime = operationStartTimes[operationId] else {
            logger.warning("No start time found for operation: \(operationId)")
            return nil
        }
        
        let duration = Date().timeIntervalSince(startTime)
        operationStartTimes.removeValue(forKey: operationId)
        operationTimeouts.removeValue(forKey: operationId)
        
        logger.info("Completed operation: \(operationId) in \(String(format: "%.3f", duration))s")
        
        if duration > 10.0 {
            logger.warning("Long-running operation detected: \(operationId) took \(String(format: "%.3f", duration))s")
        }
        
        return duration
    }
    
    func checkForTimeouts() -> [String] {
        let now = Date()
        var timedOutOperations: [String] = []
        
        for (operationId, startTime) in operationStartTimes {
            guard let timeout = operationTimeouts[operationId] else { continue }
            
            if now.timeIntervalSince(startTime) > timeout {
                timedOutOperations.append(operationId)
                logger.error("Operation timeout: \(operationId)")
            }
        }
        
        // Clean up timed out operations
        for operationId in timedOutOperations {
            operationStartTimes.removeValue(forKey: operationId)
            operationTimeouts.removeValue(forKey: operationId)
        }
        
        return timedOutOperations
    }
    
    // MARK: - Memory Monitoring
    
    func logMemoryUsage() {
        let info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4
        
        let kerr: kern_return_t = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_,
                         task_flavor_t(MACH_TASK_BASIC_INFO),
                         $0,
                         &count)
            }
        }
        
        if kerr == KERN_SUCCESS {
            let memoryMB = Double(info.resident_size) / 1024.0 / 1024.0
            logger.info("Memory usage: \(String(format: "%.1f", memoryMB)) MB")
            
            if memoryMB > 500.0 {
                logger.warning("High memory usage detected: \(String(format: "%.1f", memoryMB)) MB")
            }
        }
    }
}

// MARK: - Performance Helper Extensions

extension Task where Success == Void, Failure == Never {
    /// Creates a task with automatic timeout and performance monitoring
    static func withPerformanceMonitoring(
        operationId: String,
        timeout: TimeInterval = 30.0,
        @_implicitSelfCapture operation: @escaping @Sendable () async -> Void
    ) -> Task<Void, Never> {
        return Task {
            await PerformanceMonitor.shared.startOperation(operationId, timeout: timeout)
            
            await withTaskGroup(of: Void.self) { group in
                // Main operation
                group.addTask {
                    await operation()
                }
                
                // Timeout monitoring
                group.addTask {
                    try? await Task.sleep(nanoseconds: UInt64(timeout * 1_000_000_000))
                    let timedOut = await PerformanceMonitor.shared.checkForTimeouts()
                    if timedOut.contains(operationId) {
                        // Cancel the group if we timed out
                        group.cancelAll()
                    }
                }
                
                await group.next()
                group.cancelAll()
            }
            
            await PerformanceMonitor.shared.endOperation(operationId)
        }
    }
}

// MARK: - Safe String Processing

struct SafeStringBuilder {
    private var components: [String] = []
    private let maxLength: Int
    
    init(maxLength: Int = 10000) {
        self.maxLength = maxLength
    }
    
    mutating func append(_ string: String) -> Bool {
        let currentLength = components.reduce(0) { $0 + $1.count }
        
        if currentLength + string.count > maxLength {
            return false // Would exceed max length
        }
        
        components.append(string)
        return true
    }
    
    func build() -> String {
        return components.joined()
    }
    
    var currentLength: Int {
        return components.reduce(0) { $0 + $1.count }
    }
}