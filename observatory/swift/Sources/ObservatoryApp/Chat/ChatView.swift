//
//  ChatView.swift
//  ObservatoryApp
//
//  Minimal SwiftUI chat interface for Apple Intelligence
//  Inspired by Chatbox/Jan but built natively in SwiftUI
//

import SwiftUI
import AppIntents

struct ChatView: View {
    @StateObject private var chatViewModel = ChatViewModel()
    @State private var messageText: String = ""
    @FocusState private var isInputFocused: Bool
    
    var body: some View {
        VStack(spacing: 0) {
            // Message List
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(chatViewModel.messages) { message in
                            MessageBubble(message: message)
                                .id(message.id)
                        }
                        
                        // Loading indicator
                        if chatViewModel.isLoading {
                            HStack {
                                ProgressView()
                                    .scaleEffect(0.8)
                                Text("Thinking...")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            .padding()
                        }
                    }
                    .padding()
                }
                .onChange(of: chatViewModel.messages.count) { _ in
                    if let lastMessage = chatViewModel.messages.last {
                        withAnimation {
                            proxy.scrollTo(lastMessage.id, anchor: .bottom)
                        }
                    }
                }
            }
            
            Divider()
            
            // Input Area
            HStack(spacing: 12) {
                TextField("Ask Apple Intelligence...", text: $messageText, axis: .vertical)
                    .textFieldStyle(.roundedBorder)
                    .lineLimit(1...10)
                    .focused($isInputFocused)
                    .onSubmit {
                        sendMessage()
                    }
                
                Button(action: sendMessage) {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.title2)
                        .foregroundColor(messageText.isEmpty ? .gray : .blue)
                }
                .disabled(messageText.isEmpty || chatViewModel.isLoading)
            }
            .padding()
        }
        .frame(minWidth: 600, minHeight: 500)
        .navigationTitle("Apple Intelligence Chat")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button("Clear") {
                    chatViewModel.clearMessages()
                }
            }
        }
        .onAppear {
            // Configure window to have proper window controls
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                configureChatWindow()
            }
        }
    }
    
    private func sendMessage() {
        guard !messageText.isEmpty else { return }
        
        let userMessage = messageText
        messageText = ""
        isInputFocused = false
        
        Task {
            await chatViewModel.sendMessage(userMessage)
        }
    }
    
    private func configureChatWindow() {
        // Window is now created externally, no need to configure here
        // This function is kept for backward compatibility but does nothing
    }
}

// MARK: - Message Bubble

struct MessageBubble: View {
    let message: ChatMessage
    
    var body: some View {
        HStack {
            if message.isFromUser {
                Spacer()
            }
            
            VStack(alignment: message.isFromUser ? .trailing : .leading, spacing: 4) {
                Text(message.text)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(
                        message.isFromUser
                            ? Color.blue.opacity(0.1)
                            : Color.gray.opacity(0.1)
                    )
                    .foregroundColor(message.isFromUser ? .blue : .primary)
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                
                Text(message.timestamp, style: .time)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            if !message.isFromUser {
                Spacer()
            }
        }
    }
}

// MARK: - Chat View Model

@MainActor
class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var isLoading: Bool = false
    
    func sendMessage(_ text: String) async {
        // Add user message
        let userMessage = ChatMessage(
            id: UUID(),
            text: text,
            isFromUser: true,
            timestamp: Date()
        )
        messages.append(userMessage)
        isLoading = true
        
        // Send to Apple Intelligence
        do {
            let response = try await AppleIntelligenceChat.shared.query(text)
            
            // Add AI response
            let aiMessage = ChatMessage(
                id: UUID(),
                text: response,
                isFromUser: false,
                timestamp: Date()
            )
            messages.append(aiMessage)
        } catch {
            // Add error message
            let errorMessage = ChatMessage(
                id: UUID(),
                text: "Error: \(error.localizedDescription)",
                isFromUser: false,
                timestamp: Date()
            )
            messages.append(errorMessage)
        }
        
        isLoading = false
    }
    
    func clearMessages() {
        messages.removeAll()
    }
}

// MARK: - Message Model

struct ChatMessage: Identifiable {
    let id: UUID
    let text: String
    let isFromUser: Bool
    let timestamp: Date
}

// MARK: - Apple Intelligence Chat Bridge

actor AppleIntelligenceChat {
    static let shared = AppleIntelligenceChat()
    
    private init() {}
    
    func query(_ text: String) async throws -> String {
        // Bridge to QueryAppleIntelligenceIntent
        // For now, use AppleIntelligenceProcessor directly
        // Future: Use AppIntents when fully implemented
        let response = await AppleIntelligenceProcessor.shared.process(
            query: text,
            context: "",
            type: .general
        )
        return response
    }
}

