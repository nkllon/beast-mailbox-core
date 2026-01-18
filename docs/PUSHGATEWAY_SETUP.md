# Prometheus Pushgateway Setup

This guide covers the permanent Pushgateway instance that runs alongside the Beast telemetry stack. Deploy it on the canonical port (9091) so agents and suites can push metrics without relying on remote hosts.

## Docker Compose Deployment
```bash
cd telemetry/pushgateway
docker compose up -d
```

The compose file mounts persistent storage and restarts the container automatically. Prometheus should be configured with a scrape job similar to:

```yaml
scrape_configs:
  - job_name: 'pushgateway'
    honor_labels: true
    static_configs:
      - targets: ['pushgateway:9091']
```

## Operational Notes
- Restart policy: `unless-stopped`; use `docker compose ps` to verify status.
- Health monitoring: add Grafana panels/alerts to detect downtime or scrape failures.
- Cleanup: `docker compose down` stops the service; persistent data remains in the named volume.

## Smoke Suite Integration
Smoke tests push metrics via the Pushgateway URL exposed as `PROMETHEUS_PUSHGATEWAY_URL` or `BEAST_SMOKE_PUSHGATEWAY_URL`. Ensure Prometheus scrapes the job so telemetry validation can confirm counter deltas during the run.
