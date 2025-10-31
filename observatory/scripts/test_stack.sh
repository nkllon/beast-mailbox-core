#!/bin/bash
# Test Observatory stack health and connectivity
#
# Usage:
#   ./scripts/test_stack.sh

set -euo pipefail

cd "$(dirname "$0")/.."

echo "🧪 Testing Observatory stack..."
echo ""

# Check if stack is running
if ! docker compose -f docker/docker-compose.yml ps | grep -q "Up"; then
    echo "❌ ERROR: Stack is not running"
    echo "   Run: ./scripts/setup_local.sh first"
    exit 1
fi

echo "✅ Stack is running"
echo ""

# Test Prometheus
echo "📊 Testing Prometheus..."
PROM_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9090/api/v1/status/config 2>&1 || echo "000")
if [ "$PROM_STATUS" = "200" ]; then
    echo "✅ Prometheus: OK (HTTP $PROM_STATUS)"
    curl -s http://localhost:9090/api/v1/status/config | jq -r '.data.yaml' | head -5 || echo "   Config readable"
else
    echo "❌ Prometheus: FAILED (HTTP $PROM_STATUS)"
fi

# Test Pushgateway
echo ""
echo "📤 Testing Pushgateway..."
PG_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9091/metrics 2>&1 || echo "000")
if [ "$PG_STATUS" = "200" ]; then
    echo "✅ Pushgateway: OK (HTTP $PG_STATUS)"
    METRICS_COUNT=$(curl -s http://localhost:9091/metrics | grep -c "^[^#]" || echo "0")
    echo "   Metrics available: $METRICS_COUNT"
else
    echo "❌ Pushgateway: FAILED (HTTP $PG_STATUS)"
fi

# Test Grafana
echo ""
echo "📈 Testing Grafana..."
GRAF_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health 2>&1 || echo "000")
if [ "$GRAF_STATUS" = "200" ]; then
    echo "✅ Grafana: OK (HTTP $GRAF_STATUS)"
    GRAF_HEALTH=$(curl -s http://localhost:3000/api/health | jq -r '.database' || echo "unknown")
    echo "   Database: $GRAF_HEALTH"
else
    echo "❌ Grafana: FAILED (HTTP $GRAF_STATUS)"
fi

# Test Prometheus scraping Pushgateway
echo ""
echo "🔗 Testing Prometheus → Pushgateway scraping..."
PG_IN_TARGETS=$(curl -s http://localhost:9090/api/v1/targets | jq -r '.data.activeTargets[] | select(.job=="pushgateway") | .health' || echo "unknown")
if [ "$PG_IN_TARGETS" = "up" ]; then
    echo "✅ Prometheus is scraping Pushgateway: UP"
else
    echo "⚠️  Prometheus scraping status: $PG_IN_TARGETS"
fi

# Test push to Pushgateway
echo ""
echo "🧪 Testing metric push to Pushgateway..."
TEST_METRIC="test_metric_$(date +%s) 42"
echo "$TEST_METRIC" | curl -s --data-binary @- http://localhost:9091/metrics/job/test_job/instance/test123 >/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Metric push: SUCCESS"
    # Verify it appears in Prometheus
    sleep 2
    PROM_QUERY=$(curl -s "http://localhost:9090/api/v1/query?query=test_metric" | jq -r '.data.result | length' || echo "0")
    if [ "$PROM_QUERY" != "0" ]; then
        echo "✅ Metric appears in Prometheus query"
    else
        echo "⚠️  Metric not yet in Prometheus (may need to wait for scrape interval)"
    fi
else
    echo "❌ Metric push: FAILED"
fi

echo ""
echo "📋 Service Status Summary:"
docker compose -f docker/docker-compose.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ Test complete!"
echo ""
echo "Service URLs:"
echo "   Prometheus:  http://localhost:9090"
echo "   Grafana:    http://localhost:3000 (admin/admin)"
echo "   Pushgateway: http://localhost:9091"
echo ""

