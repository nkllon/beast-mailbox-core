//
//  DashboardView.swift
//  ObservatoryApp
//
//  SwiftUI dashboard for viewing metrics
//

import SwiftUI
import Charts

struct DashboardView: View {
    @EnvironmentObject var monitor: StatusMonitor
    @Environment(\.dismiss) var dismiss
    @State private var metrics: [MetricPoint] = []
    @State private var isLoading = false
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Status Card
                    StatusCard(monitor: monitor)
                    
                    // Metrics Cards
                    if !metrics.isEmpty {
                        MetricsChart(metrics: metrics)
                    }
                    
                    // Last Sync Info
                    if let lastSync = monitor.lastSyncTime {
                        Text("Last Sync: \(lastSync, style: .date) \(lastSync, style: .time)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
            }
            .navigationTitle("Beast Observatory")
            .toolbar {
                ToolbarItem(placement: .automatic) {
                    Button("Done") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .automatic) {
                    Button(action: {
                        monitor.triggerSync()
                    }) {
                        Image(systemName: "arrow.clockwise")
                    }
                    .disabled(monitor.isSyncing)
                }
            }
            .frame(minWidth: 600, minHeight: 400)
        }
        .task {
            await loadMetrics()
        }
    }
    
    private func loadMetrics() async {
        isLoading = true
        // TODO: Load metrics from Prometheus or SonarCloud
        isLoading = false
    }
}

struct StatusCard: View {
    @ObservedObject var monitor: StatusMonitor
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Status")
                .font(.headline)
            
            HStack {
                Image(systemName: monitor.statusIcon)
                    .foregroundColor(monitor.statusColor)
                    .font(.title2)
                
                VStack(alignment: .leading) {
                    Text(monitor.isSyncing ? "Syncing..." : "Ready")
                        .font(.title3)
                    
                    if let error = monitor.lastError {
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.red)
                    }
                }
            }
            
            if let coverage = monitor.coverage {
                Text("Coverage: \(coverage, specifier: "%.1f")%")
                    .font(.caption)
            }
        }
        .padding()
        .background(Color(.controlBackgroundColor))
        .cornerRadius(8)
    }
}

struct MetricsChart: View {
    let metrics: [MetricPoint]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Coverage Trend")
                .font(.headline)
            
            Chart(metrics) { point in
                LineMark(
                    x: .value("Date", point.date),
                    y: .value("Coverage", point.value)
                )
            }
            .frame(height: 200)
        }
        .padding()
        .background(Color(.controlBackgroundColor))
        .cornerRadius(8)
    }
}

struct MetricPoint: Identifiable {
    let id = UUID()
    let date: Date
    let value: Double
}

struct SettingsView: View {
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            Form {
                Section("SonarCloud") {
                    TextField("Project Key", text: .constant("nkllon_beast-mailbox-core"))
                    TextField("Pushgateway URL", text: .constant("http://localhost:9091"))
                }
                
                Section("Sync") {
                    Picker("Interval", selection: .constant(1)) {
                        Text("1 hour").tag(1)
                        Text("6 hours").tag(6)
                        Text("24 hours").tag(24)
                    }
                }
            }
            .navigationTitle("Settings")
            .toolbar {
                ToolbarItem(placement: .automatic) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .frame(width: 500, height: 400)
        }
    }
}

