//
//  WindowAccessor.swift
//  ObservatoryApp
//
//  Helper to keep sheet window open and focusable
//

import SwiftUI
import AppKit

struct WindowAccessor: NSViewRepresentable {
    func makeNSView(context: Context) -> NSView {
        let view = NSView()
        DispatchQueue.main.async {
            if let window = view.window {
                window.collectionBehavior = [.stationary, .fullScreenAuxiliary]
                window.level = .floating
                window.makeKeyAndOrderFront(nil)
                window.isReleasedWhenClosed = false
            }
        }
        return view
    }
    
    func updateNSView(_ nsView: NSView, context: Context) {}
}

