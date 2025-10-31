//
//  ChatWindowModifier.swift
//  ObservatoryApp
//
//  Modifier to fix sheet window behavior in MenuBarExtra
//

import SwiftUI
import AppKit

struct ChatWindowModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(ChatWindowAccessor())
    }
}

struct ChatWindowAccessor: NSViewRepresentable {
    func makeNSView(context: Context) -> NSView {
        let view = NSView()
        DispatchQueue.main.async {
            // Find the sheet window
            if let window = NSApplication.shared.windows.first(where: { 
                $0.isVisible && $0.title.contains("Chat") || $0.contentView?.subviews.contains(where: { type(of: $0).description().contains("Chat") }) == true
            }) {
                // Configure window to stay open
                window.collectionBehavior = [.stationary, .fullScreenAuxiliary]
                window.level = .floating
                window.isReleasedWhenClosed = false
                window.makeKeyAndOrderFront(nil)
                window.acceptsMouseMovedEvents = true
            }
            
            // Also try to find by iterating all windows
            for window in NSApplication.shared.windows {
                if window.isVisible && window.contentView != nil {
                    window.collectionBehavior = [.stationary]
                    window.isReleasedWhenClosed = false
                }
            }
        }
        return view
    }
    
    func updateNSView(_ nsView: NSView, context: Context) {
        // Update window settings if needed
        DispatchQueue.main.async {
            for window in NSApplication.shared.windows {
                if window.isVisible {
                    window.collectionBehavior = [.stationary]
                    window.isReleasedWhenClosed = false
                }
            }
        }
    }
}

extension View {
    func chatWindowFix() -> some View {
        modifier(ChatWindowModifier())
    }
}

