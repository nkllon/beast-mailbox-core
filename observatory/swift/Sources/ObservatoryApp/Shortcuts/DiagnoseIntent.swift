//
//  DiagnoseIntent.swift
//  ObservatoryApp
//
//  Apple Shortcuts intent for diagnosing Observatory errors
//  Phase 4: Intelligent Error Diagnosis
//

import AppIntents
import Foundation

struct DiagnoseObservatoryErrorIntent: AppIntent {
    static var title: LocalizedStringResource = "Diagnose Observatory Error"
    static var description = IntentDescription("Analyze Observatory error and suggest fixes")
    static var openAppWhenRun: Bool = false
    
    @Parameter(title: "Error Log", description: "Error log content to analyze")
    var errorLog: String?
    
    func perform() async throws -> some IntentResult & ReturnsValue<String> {
        // Get error log if not provided
        let logContent = errorLog ?? getRecentErrorLog()
        
        // Analyze error (Phase 4 will add AI analysis)
        let analysis = await analyzeError(log: logContent)
        
        return .result(value: analysis.summary)
    }
    
    private func getRecentErrorLog() -> String {
        let errorLogPath = NSString(string: "~/Library/Logs/beast-observatory/sync.error.log").expandingTildeInPath
        
        guard FileManager.default.fileExists(atPath: errorLogPath),
              let content = try? String(contentsOfFile: errorLogPath) else {
            return "No error log found"
        }
        
        // Get last 50 lines
        let lines = content.components(separatedBy: .newlines)
        return lines.suffix(50).joined(separator: "\n")
    }
    
    private func analyzeError(log: String) async -> DiagnosisResult {
        // Phase 4: This will use Apple Intelligence for intelligent analysis
        // For now, simple pattern matching
        
        var cause = "Unknown error"
        var confidence: Double = 0.5
        var suggestedFix = "Check logs for details"
        
        // Pattern matching (will be replaced with AI in Phase 4)
        if log.contains("Pushgateway") && log.contains("unreachable") {
            cause = "Pushgateway unreachable"
            confidence = 0.9
            suggestedFix = "Check if Pushgateway is running: curl http://localhost:9091/metrics"
        } else if log.contains("SonarCloud") && log.contains("timeout") {
            cause = "SonarCloud API timeout"
            confidence = 0.8
            suggestedFix = "Check network connection and SonarCloud API status"
        } else if log.contains("Connection refused") {
            cause = "Connection refused"
            confidence = 0.9
            suggestedFix = "Service may not be running. Check launchctl status."
        }
        
        return DiagnosisResult(
            cause: cause,
            confidence: confidence,
            suggestedFix: suggestedFix,
            errorContext: log.prefix(200).description // First 200 chars
        )
    }
}

// MARK: - Diagnosis Result

struct DiagnosisResult {
    let cause: String
    let confidence: Double
    let suggestedFix: String
    let errorContext: String
    
    var summary: String {
        """
        Cause: \(cause)
        Confidence: \(Int(confidence * 100))%
        
        Suggested Fix:
        \(suggestedFix)
        """
    }
}

