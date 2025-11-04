//
//  ChatView.swift
//  ObservatoryApp
//
//  Apple Intelligence Chat Interface
//

import SwiftUI

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
        
        // Simulate Apple Intelligence response
        // In a real implementation, this would use actual Apple Intelligence APIs
        let response = generateIntelligentResponse(for: text)
        
        // Add AI response
        let aiMessage = ChatMessage(
            id: UUID(),
            text: response,
            isFromUser: false,
            timestamp: Date()
        )
        messages.append(aiMessage)
        
        isLoading = false
    }
    
    func clearMessages() {
        messages.removeAll()
    }
    
    private func generateIntelligentResponse(for query: String) -> String {
        let lowercaseQuery = query.lowercased()
        
        // Detect query type and provide appropriate response
        if lowercaseQuery.contains("error") || lowercaseQuery.contains("bug") {
            return """
            I can help you debug that issue! Common Swift/macOS debugging steps:
            
            1. **Check the full error message** for specific details
            2. **Review the stack trace** to identify the source
            3. **Use breakpoints** to inspect variable states
            4. **Add logging** with `print()` or `OSLog`
            
            Could you share the specific error message you're seeing?
            """
        } else if lowercaseQuery.contains("code") && lowercaseQuery.contains("review") {
            return """
            I'd be happy to review your code! For the best analysis, please share:
            
            • Your Swift code snippet
            • Any specific concerns you have
            • The context (what the code is supposed to do)
            
            I can help with:
            - Bug identification
            - Performance improvements  
            - Swift best practices
            - Apple framework usage
            """
        } else if lowercaseQuery.contains("architecture") || lowercaseQuery.contains("design") {
            return """
            For macOS app architecture, I recommend:
            
            **Patterns:**
            • MVVM with SwiftUI for clean separation
            • Repository pattern for data access
            • Dependency injection for testability
            
            **Frameworks:**
            • SwiftUI + Combine for reactive UI
            • Core Data for persistence
            • OSLog for structured logging
            
            What specific architectural challenge are you facing?
            """
        } else {
            return """
            I'm here to help with your Apple development questions! I can assist with:
            
            • Swift programming and best practices
            • SwiftUI and AppKit development
            • macOS app architecture
            • Debugging and performance optimization
            • Apple framework integration
            
            What would you like to know more about?
            """
        }
    }
}

// MARK: - Message Model

struct ChatMessage: Identifiable {
    let id: UUID
    let text: String
    let isFromUser: Bool
    let timestamp: Date
}