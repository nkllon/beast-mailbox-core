#!/bin/bash
# Setup Observatory stack locally on Herbert
#
# Usage:
#   ./scripts/setup_local.sh

set -euo pipefail

cd "$(dirname "$0")/.."

echo "🚀 Setting up Observatory stack locally..."
echo ""

# Check Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ ERROR: Docker is not running"
    echo "   Please start Docker and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Create config directories if missing
mkdir -p configs/prometheus
mkdir -p configs/grafana/provisioning/{datasources,dashboards}
mkdir -p docker/volumes

# Verify config files exist
if [ ! -f "configs/prometheus/prometheus.yml" ]; then
    echo "⚠️  Warning: prometheus.yml not found, using default"
fi

if [ ! -f "configs/grafana/provisioning/datasources/prometheus.yml" ]; then
    echo "⚠️  Warning: Grafana datasource config not found, using default"
fi

echo "✅ Configuration directories ready"
echo ""

# Boot stack
echo "📦 Starting Observatory stack..."
cd docker

if docker compose ps | grep -q "Up"; then
    echo "⚠️  Stack is already running"
    echo "   Use: docker compose restart"
else
    docker compose up -d
    echo "✅ Stack started"
fi

echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "🌐 Service URLs:"
echo "   Prometheus:  http://localhost:9090"
echo "   Grafana:    http://localhost:3000 (admin/admin)"
echo "   Pushgateway: http://localhost:9091"
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Verify Prometheus: curl http://localhost:9090/api/v1/status/config"
echo "  2. Verify Grafana: curl http://localhost:3000/api/health"
echo "  3. Verify Pushgateway: curl http://localhost:9091/metrics"
echo ""

