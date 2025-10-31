#!/bin/bash
# Push quality metrics to Prometheus Pushgateway
#
# Usage:
#   ./scripts/push_metrics_to_prometheus.sh
#
# Environment variables:
#   PROMETHEUS_PUSHGATEWAY_URL - Pushgateway endpoint (required)
#   PROMETHEUS_PUSHGATEWAY_AUTH - Basic auth credentials (user:pass, optional)
#   BRANCH - Git branch name
#   VERSION - Package version
#   COMMIT - Git commit SHA
#   WORKFLOW_RUN_ID - GitHub Actions run ID

set -euo pipefail

# Default values
PUSHGATEWAY_URL="${PROMETHEUS_PUSHGATEWAY_URL:-}"
PUSHGATEWAY_AUTH="${PROMETHEUS_PUSHGATEWAY_AUTH:-}"
BRANCH="${BRANCH:-main}"
VERSION="${VERSION:-unknown}"
COMMIT="${COMMIT:-unknown}"
WORKFLOW_RUN_ID="${WORKFLOW_RUN_ID:-unknown}"
WORKFLOW_NAME="${WORKFLOW_NAME:-unknown}"
WORKFLOW_STATUS="${WORKFLOW_STATUS:-unknown}"
INSTANCE="${INSTANCE:-${VERSION}-${COMMIT:0:8}}"

# Metrics file (will be generated if not provided)
METRICS_FILE="${METRICS_FILE:-/tmp/metrics.prom}"

# Check if Pushgateway URL is configured
if [ -z "$PUSHGATEWAY_URL" ]; then
    echo "⚠️  PROMETHEUS_PUSHGATEWAY_URL not configured, skipping metric push"
    echo "   Set PROMETHEUS_PUSHGATEWAY_URL to enable Prometheus export"
    exit 0
fi

# Validate Pushgateway URL format
if [[ ! "$PUSHGATEWAY_URL" =~ ^https?:// ]]; then
    echo "❌ ERROR: PROMETHEUS_PUSHGATEWAY_URL must be a valid HTTP(S) URL"
    exit 1
fi

# Prepare curl command with authentication if provided
CURL_CMD="curl -X PUT"
if [ -n "$PUSHGATEWAY_AUTH" ]; then
    CURL_CMD="$CURL_CMD --user \"$PUSHGATEWAY_AUTH\""
fi

# Pushgateway endpoint
# Format: PUT /metrics/job/{job_name}/instance/{instance}/branch/{branch}
PUSH_URL="${PUSHGATEWAY_URL%/}/metrics/job/beast-mailbox-core/instance/${INSTANCE}/branch/${BRANCH}/version/${VERSION}"

echo "📊 Pushing metrics to Prometheus Pushgateway..."
echo "   URL: $PUSH_URL"
echo "   Job: beast-mailbox-core"
echo "   Instance: $INSTANCE"
echo "   Branch: $BRANCH"
echo "   Version: $VERSION"

# Push metrics
if [ -f "$METRICS_FILE" ]; then
    RESPONSE=$(eval "$CURL_CMD --data-binary @${METRICS_FILE} --write-out '%{http_code}' --silent --output /dev/null ${PUSH_URL}")
    
    if [ "$RESPONSE" = "200" ]; then
        echo "✅ Metrics pushed successfully (HTTP $RESPONSE)"
    else
        echo "❌ Failed to push metrics (HTTP $RESPONSE)"
        echo "   Response: $RESPONSE"
        exit 1
    fi
else
    echo "❌ ERROR: Metrics file not found: $METRICS_FILE"
    exit 1
fi

echo "✅ Metrics export complete"

