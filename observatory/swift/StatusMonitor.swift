import Foundation
import Combine

@MainActor
class StatusMonitor: ObservableObject {
    @Published var isActive: Bool = false
    @Published var status: String = "Inactive"
    @Published var lastUpdated: Date = Date()
    
    private var timer: Timer?
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        setupMonitoring()
    }
    
    deinit {
        stopMonitoring()
    }
    
    private func setupMonitoring() {
        // Start monitoring with a timer that updates every 5 seconds
        timer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.updateStatus()
            }
        }
    }
    
    private func updateStatus() {
        // Update the status - customize this based on what you want to monitor
        lastUpdated = Date()
        
        // Example: Random status for demonstration
        let statuses = ["Active", "Inactive", "Processing", "Idle"]
        status = statuses.randomElement() ?? "Unknown"
        isActive = status == "Active" || status == "Processing"
    }
    
    func startMonitoring() {
        guard timer == nil else { return }
        setupMonitoring()
    }
    
    func stopMonitoring() {
        timer?.invalidate()
        timer = nil
    }
    
    func forceUpdate() {
        updateStatus()
    }
}