import SwiftUI

struct MenuBarView: View {
    @StateObject private var statusMonitor = StatusMonitor()
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: statusMonitor.isActive ? "circle.fill" : "circle")
                    .foregroundColor(statusMonitor.isActive ? .green : .gray)
                
                Text(statusMonitor.status)
                    .font(.headline)
            }
            
            Divider()
            
            VStack(alignment: .leading, spacing: 4) {
                Text("Last Updated:")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text(statusMonitor.lastUpdated, style: .time)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Divider()
            
            Button("Refresh Status") {
                statusMonitor.forceUpdate()
            }
            
            Button("Quit") {
                NSApplication.shared.terminate(nil)
            }
        }
        .padding()
        .frame(minWidth: 200)
    }
}

#Preview {
    MenuBarView()
}