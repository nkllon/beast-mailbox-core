//
//  TestAppleIntelligence.swift
//  ObservatoryApp
//
//  Simple test script to verify Apple Intelligence integration
//

import Foundation
import FoundationModels

@main
struct TestAppleIntelligence {
    static func main() async {
        print("🤖 Testing Apple Intelligence Integration...")
        
        let model = SystemLanguageModel.default
        
        // Check availability
        print("\n📱 Checking Apple Intelligence availability...")
        switch model.availability {
        case .available:
            print("✅ Apple Intelligence is available!")
            await testAppleIntelligence()
        case .unavailable(.deviceNotEligible):
            print("❌ Device not eligible for Apple Intelligence")
        case .unavailable(.appleIntelligenceNotEnabled):
            print("⚠️  Apple Intelligence not enabled - please enable in System Settings")
        case .unavailable(.modelNotReady):
            print("⏳ Apple Intelligence model is downloading or not ready")
        case .unavailable(let reason):
            print("❌ Apple Intelligence unavailable: \(reason)")
        }
    }
    
    static func testAppleIntelligence() async {
        print("\n🧠 Testing Apple Intelligence responses...")
        
        do {
            // Test basic functionality
            let instructions = """
            You are a helpful assistant for Apple developers.
            Provide brief, accurate responses about Swift and Apple development.
            """
            
            let session = LanguageModelSession(instructions: instructions)
            
            let testQuery = "What's the difference between @State and @StateObject in SwiftUI?"
            print("Query: \(testQuery)")
            
            let response = try await session.respond(to: testQuery)
            print("\n🎯 Apple Intelligence Response:")
            print(response.content)
            
            print("\n✅ Apple Intelligence integration test completed successfully!")
            
        } catch {
            print("❌ Test failed: \(error)")
        }
    }
}