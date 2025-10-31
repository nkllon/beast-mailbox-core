//
//  SyncIntent.swift
//  ObservatoryApp
//
//  Apple Shortcuts intent for triggering Observatory sync
//

import AppIntents
import Foundation

struct TriggerObservatorySyncIntent: AppIntent {
    static var title: LocalizedStringResource = "Trigger Observatory Sync"
    static var description = IntentDescription("Manually trigger a sync of SonarCloud metrics to Prometheus")
    static var openAppWhenRun: Bool = false
    
    func perform() async throws -> some IntentResult & ReturnsValue<Bool> {
        do {
            try await ObservatoryService.shared.triggerSync()
            return .result(value: true)
        } catch {
            throw error
        }
    }
}

