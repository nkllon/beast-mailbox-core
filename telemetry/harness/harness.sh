#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE="docker compose -f \"$ROOT_DIR/docker-compose.yml\""
ARTIFACT="$ROOT_DIR/harness.json"

usage() {
  cat <<EOF
Usage: $(basename "$0") <start|stop|status>

start   Launch Prometheus (20090), Grafana (20300), and Pushgateway (20637)
stop    Stop and remove harness containers
status  Show running state and active endpoints
EOF
}

write_status() {
  cat <<EOF >"$ARTIFACT"
{
  "prometheus": "http://localhost:20090",
  "grafana": "http://localhost:20300",
  "pushgateway": "http://localhost:20637"
}
EOF
}

case "${1:-}" in
  start)
    eval "$COMPOSE up -d"
    write_status
    echo "Telemetry harness started. Endpoints recorded in $ARTIFACT"
    ;;
  stop)
    if [ -f "$ARTIFACT" ]; then rm -f "$ARTIFACT"; fi
    eval "$COMPOSE down"
    echo "Telemetry harness stopped."
    ;;
  status)
    eval "$COMPOSE ps"
    if [ -f "$ARTIFACT" ]; then
      echo "Configured endpoints:"
      cat "$ARTIFACT"
    else
      echo "No harness.json found; run start to create." >&2
    fi
    ;;
  *)
    usage
    exit 1
    ;;
 esac
