#!/bin/bash
# Discover Observatory stack on Vonnegut
#
# Usage:
#   ./scripts/discover_vonnegut.sh
#
# Environment variables:
#   VONNEGUT_HOST - Hostname or IP (default: vonnegut)
#   SSH_USER - SSH user (default: root)
#   OUTPUT_DIR - Output directory (default: docs/discovery)

set -euo pipefail

VONNEGUT_HOST="${VONNEGUT_HOST:-vonnegut}"
SSH_USER="${SSH_USER:-root}"
OUTPUT_DIR="${OUTPUT_DIR:-docs/discovery}"

echo "🔍 Discovering Observatory stack on $VONNEGUT_HOST..."
echo "   User: $SSH_USER"
echo "   Output: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run remote command and save output
run_and_save() {
    local description="$1"
    local command="$2"
    local output_file="$3"
    
    echo -e "${YELLOW}📋 $description${NC}"
    ssh "$SSH_USER@$VONNEGUT_HOST" "$command" > "$output_file" 2>&1 || {
        echo "⚠️  Warning: Command failed or returned no output"
        echo "" > "$output_file"
    }
    echo -e "${GREEN}✅ Saved to $output_file${NC}"
    echo ""
}

# 1. List all running containers
run_and_save \
    "Listing all running containers" \
    "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}\t{{.Command}}'" \
    "$OUTPUT_DIR/containers.txt"

# 2. Get detailed container information
run_and_save \
    "Getting detailed container configurations" \
    "docker ps -q | xargs -I {} docker inspect {} | jq '[.[] | {Name: .Name, Image: .Config.Image, Env: .Config.Env, Mounts: .Mounts, Networks: .NetworkSettings.Networks, Ports: .NetworkSettings.Ports, Cmd: .Config.Cmd, Args: .Config.Args}]'" \
    "$OUTPUT_DIR/containers_detailed.json"

# 3. Find Docker Compose files
run_and_save \
    "Finding Docker Compose files" \
    "find / -name docker-compose.yml -o -name docker-compose.yaml 2>/dev/null | head -20" \
    "$OUTPUT_DIR/docker_compose_files.txt"

# 4. Get Docker Compose file contents (if found)
if ssh "$SSH_USER@$VONNEGUT_HOST" "test -f /path/to/docker-compose.yml 2>/dev/null" 2>/dev/null; then
    COMPOSE_FILE=$(ssh "$SSH_USER@$VONNEGUT_HOST" "find / -name docker-compose.yml 2>/dev/null | head -1")
    if [ -n "$COMPOSE_FILE" ]; then
        run_and_save \
            "Getting Docker Compose configuration" \
            "cat $COMPOSE_FILE" \
            "$OUTPUT_DIR/docker-compose.yml"
    fi
fi

# 5. List all volumes
run_and_save \
    "Listing Docker volumes" \
    "docker volume ls --format '{{.Name}}\t{{.Driver}}\t{{.Mountpoint}}'" \
    "$OUTPUT_DIR/volumes.txt"

# 6. List all networks
run_and_save \
    "Listing Docker networks" \
    "docker network ls --format 'table {{.Name}}\t{{.Driver}}\t{{.Scope}}'" \
    "$OUTPUT_DIR/networks.txt"

# 7. Get network details
run_and_save \
    "Getting network configurations" \
    "docker network ls -q | xargs -I {} docker network inspect {} | jq '[.[] | {Name: .Name, Driver: .Driver, IPAM: .IPAM, Containers: .Containers}]'" \
    "$OUTPUT_DIR/networks_detailed.json"

# 8. Prometheus configuration
if ssh "$SSH_USER@$VONNEGUT_HOST" "docker ps --format '{{.Names}}' | grep -q prometheus" 2>/dev/null; then
    PROM_CONTAINER=$(ssh "$SSH_USER@$VONNEGUT_HOST" "docker ps --format '{{.Names}}' | grep prometheus | head -1")
    
    run_and_save \
        "Getting Prometheus configuration" \
        "docker exec $PROM_CONTAINER cat /etc/prometheus/prometheus.yml 2>/dev/null || docker exec $PROM_CONTAINER cat /prometheus.yml 2>/dev/null || echo 'Config not found in standard locations'" \
        "$OUTPUT_DIR/prometheus.yml"
    
    run_and_save \
        "Getting Prometheus environment variables" \
        "docker exec $PROM_CONTAINER env | grep -i prometheus || true" \
        "$OUTPUT_DIR/prometheus_env.txt"
fi

# 9. Grafana configuration
if ssh "$SSH_USER@$VONNEGUT_HOST" "docker ps --format '{{.Names}}' | grep -q grafana" 2>/dev/null; then
    GRAF_CONTAINER=$(ssh "$SSH_USER@$VONNEGUT_HOST" "docker ps --format '{{.Names}}' | grep grafana | head -1")
    
    run_and_save \
        "Getting Grafana configuration" \
        "docker exec $GRAF_CONTAINER cat /etc/grafana/grafana.ini 2>/dev/null || echo 'Config not found in standard locations'" \
        "$OUTPUT_DIR/grafana.ini"
    
    run_and_save \
        "Getting Grafana environment variables" \
        "docker exec $GRAF_CONTAINER env | grep -i grafana || true" \
        "$OUTPUT_DIR/grafana_env.txt"
    
    run_and_save \
        "Getting Grafana data sources" \
        "docker exec $GRAF_CONTAINER find /var/lib/grafana -name '*.json' -type f 2>/dev/null | head -10 || true" \
        "$OUTPUT_DIR/grafana_data_sources.txt"
fi

# 10. Pushgateway configuration
if ssh "$SSH_USER@$VONNEGUT_HOST" "docker ps --format '{{.Names}}' | grep -q pushgateway" 2>/dev/null; then
    PG_CONTAINER=$(ssh "$SSH_USER@$VONNEGUT_HOST" "docker ps --format '{{.Names}}' | grep pushgateway | head -1")
    
    run_and_save \
        "Getting Pushgateway environment variables" \
        "docker exec $PG_CONTAINER env | grep -i pushgateway || true" \
        "$OUTPUT_DIR/pushgateway_env.txt"
fi

# 11. Get system information
run_and_save \
    "Getting Docker version" \
    "docker version" \
    "$OUTPUT_DIR/docker_version.txt"

run_and_save \
    "Getting Docker info" \
    "docker info" \
    "$OUTPUT_DIR/docker_info.txt"

# 12. Get container logs summary (last 50 lines per container)
echo -e "${YELLOW}📋 Getting container logs summary${NC}"
for container in $(ssh "$SSH_USER@$VONNEGUT_HOST" "docker ps --format '{{.Names}}'"); do
    echo "  Getting logs for $container..."
    ssh "$SSH_USER@$VONNEGUT_HOST" "docker logs --tail 50 $container 2>&1" > "$OUTPUT_DIR/logs_${container}.txt" || true
done
echo -e "${GREEN}✅ Logs saved to $OUTPUT_DIR/logs_*.txt${NC}"
echo ""

# 13. Create summary
echo -e "${YELLOW}📊 Creating discovery summary${NC}"
cat > "$OUTPUT_DIR/SUMMARY.md" <<EOF
# Vonnegut Observatory Stack Discovery Summary

**Date:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")  
**Host:** $VONNEGUT_HOST  
**User:** $SSH_USER

## Discovery Results

### Containers Found
\`\`\`
$(cat "$OUTPUT_DIR/containers.txt")
\`\`\`

### Docker Compose Files
\`\`\`
$(cat "$OUTPUT_DIR/docker_compose_files.txt")
\`\`\`

### Volumes
\`\`\`
$(cat "$OUTPUT_DIR/volumes.txt")
\`\`\`

### Networks
\`\`\`
$(cat "$OUTPUT_DIR/networks.txt")
\`\`\`

## Files Generated

- \`containers.txt\` - Running containers list
- \`containers_detailed.json\` - Detailed container configurations
- \`docker_compose_files.txt\` - Docker Compose file locations
- \`docker-compose.yml\` - Docker Compose configuration (if found)
- \`volumes.txt\` - Docker volumes
- \`networks.txt\` - Docker networks
- \`networks_detailed.json\` - Network configurations
- \`prometheus.yml\` - Prometheus configuration
- \`prometheus_env.txt\` - Prometheus environment variables
- \`grafana.ini\` - Grafana configuration
- \`grafana_env.txt\` - Grafana environment variables
- \`pushgateway_env.txt\` - Pushgateway environment variables
- \`logs_*.txt\` - Container logs (last 50 lines)

## Next Steps

1. Review \`containers_detailed.json\` for full container configs
2. Use \`docker-compose.yml\` (if found) as base for local stack
3. Extract Prometheus/Grafana configs for reuse
4. Document any manual configurations not captured

EOF

echo -e "${GREEN}✅ Summary saved to $OUTPUT_DIR/SUMMARY.md${NC}"
echo ""

echo -e "${GREEN}✅ Discovery complete!${NC}"
echo "   Output directory: $OUTPUT_DIR"
echo "   Review SUMMARY.md for overview"
echo ""

