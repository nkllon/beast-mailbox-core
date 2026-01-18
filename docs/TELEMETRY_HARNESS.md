# Telemetry Harness (Local High-Port Stack)

Use this harness when running smoke tests locally. It launches Prometheus, Grafana, and Pushgateway on reserved high ports so other engineers know the stack is temporary. Always stop the harness when tests finish.

## Ports
- Prometheus: `http://localhost:20090`
- Grafana: `http://localhost:20300`
- Pushgateway: `http://localhost:20637`

## Commands
```bash
# Start the harness
bash telemetry/harness/harness.sh start

# Check status
bash telemetry/harness/harness.sh status

# Stop the harness (must do when finished)
bash telemetry/harness/harness.sh stop
```

The script writes `telemetry/harness/harness.json` with active endpoints so fellow agents can attach to the same stack when coordinating tests.

## Notes
- Containers run via Docker Compose; ensure Docker Desktop or the daemon is available.
- These ports signal an ephemeral stack. It is safe to tear down any harness you find running on them if no active test session is documented.
- Permanent infrastructure continues to use Prometheus/Grafana standard ports and the dedicated Pushgateway on port 9091.
