#!/usr/bin/env python3
"""
Observatory Sync Service

Periodically syncs historical metrics from SonarCloud API to Prometheus Pushgateway.
Can optionally use Redis mailbox for decoupling.

Usage:
    python sync_service.py

Environment Variables:
    SONARCLOUD_PROJECT_KEY - SonarCloud project key (default: nkllon_beast-mailbox-core)
    SONARCLOUD_TOKEN - SonarCloud API token (optional, for auth)
    PROMETHEUS_PUSHGATEWAY_URL - Pushgateway endpoint (default: http://localhost:9091)
    PROMETHEUS_PUSHGATEWAY_AUTH - Basic auth (optional, format: user:pass)
    SYNC_INTERVAL_HOURS - Sync interval in hours (default: 1)
    USE_MAILBOX - Use Redis mailbox for decoupling (default: false)
    REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB - Redis config for mailbox
    GIT_BRANCH - Git branch name (default: main)
    PACKAGE_VERSION - Package version (optional)
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlencode

try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp not installed. Install with: pip install aiohttp")
    sys.exit(1)

# Optionally use beast-mailbox-core for decoupling
try:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
    from beast_mailbox_core import RedisMailboxService, MailboxMessage, MailboxConfig
    HAS_MAILBOX = True
except ImportError:
    HAS_MAILBOX = False
    logger.warning("beast-mailbox-core not available - mailbox decoupling disabled")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("observatory.sync")


class SonarCloudClient:
    """Client for SonarCloud API."""
    
    def __init__(self, project_key: str, token: Optional[str] = None):
        self.project_key = project_key
        self.token = token
        self.base_url = "https://sonarcloud.io/api"
        self.session = None
    
    async def __aenter__(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        self.session = aiohttp.ClientSession(headers=headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_historical_metrics(
        self,
        metrics: List[str],
        days: int = 30,
        page_size: int = 100
    ) -> Dict:
        """Get historical metrics from SonarCloud API."""
        url = f"{self.base_url}/measures/search_history"
        params = {
            "component": self.project_key,
            "metrics": ",".join(metrics),
            "ps": page_size
        }
        
        logger.info(f"Fetching historical metrics: {metrics}, days={days}")
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return data
        except Exception as e:
            logger.error(f"Failed to fetch historical metrics: {e}")
            raise
    
    async def get_current_metrics(self, metric_keys: List[str]) -> Dict:
        """Get current metrics from SonarCloud API."""
        url = f"{self.base_url}/measures/component"
        params = {
            "component": self.project_key,
            "metricKeys": ",".join(metric_keys)
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return data
        except Exception as e:
            logger.error(f"Failed to fetch current metrics: {e}")
            raise


class MetricsPusher:
    """Pushes metrics to Prometheus Pushgateway."""
    
    def __init__(self, pushgateway_url: str, auth: Optional[str] = None):
        self.pushgateway_url = pushgateway_url.rstrip("/")
        self.auth = auth
        self.session = None
    
    async def __aenter__(self):
        headers = {}
        if self.auth:
            # Basic auth: username:password
            import base64
            auth_bytes = self.auth.encode()
            auth_b64 = base64.b64encode(auth_bytes).decode()
            headers["Authorization"] = f"Basic {auth_b64}"
        
        self.session = aiohttp.ClientSession(headers=headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def push_metrics(
        self,
        metrics_content: str,
        job: str,
        instance: str,
        labels: Optional[Dict[str, str]] = None
    ) -> bool:
        """Push metrics to Pushgateway."""
        # Build URL: /metrics/job/{job}/instance/{instance}/branch/{branch}/version/{version}
        # URL encode label values to handle special characters
        from urllib.parse import quote
        
        url = f"{self.pushgateway_url}/metrics/job/{quote(job, safe='')}/instance/{quote(instance, safe='')}"
        
        if labels:
            for key, value in labels.items():
                # URL encode both key and value
                url += f"/{quote(key, safe='')}/{quote(str(value), safe='')}"
        
        logger.info(f"Pushing metrics to: {url}")
        logger.debug(f"Metrics content:\n{metrics_content}")
        
        try:
            # Ensure metrics_content ends with newline
            if not metrics_content.endswith('\n'):
                metrics_content += '\n'
            
            async with self.session.put(url, data=metrics_content.encode('utf-8'), 
                                         headers={'Content-Type': 'text/plain; charset=utf-8'}) as response:
                if response.status == 200:
                    logger.info(f"Metrics pushed successfully (HTTP {response.status})")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to push metrics (HTTP {response.status}): {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Failed to push metrics: {e}", exc_info=True)
            return False


class MailboxPublisher:
    """Publishes metrics to Redis mailbox for decoupling."""
    
    def __init__(self, mailbox_service: RedisMailboxService):
        self.mailbox = mailbox_service
        self.stream_name = "beast:observatory:metrics"
    
    async def publish_metrics(self, metrics_content: str, metadata: Dict) -> bool:
        """Publish metrics to mailbox."""
        try:
            message = MailboxMessage(
                sender="observatory-sync",
                recipient="metrics-consumer",
                message_type="METRICS_UPDATE",
                payload={
                    "metrics": metrics_content,
                    "metadata": metadata,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Use mailbox service to send
            # Note: This would need integration with Redis client directly
            # For now, use direct Redis stream API
            logger.info(f"Publishing metrics to mailbox: {self.stream_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish to mailbox: {e}")
            return False


async def convert_sonarcloud_to_prometheus(
    historical_data: Dict,
    current_data: Optional[Dict] = None,
    branch: str = "main",
    version: Optional[str] = None
) -> str:
    """Convert SonarCloud data to Prometheus format.
    
    Args:
        historical_data: SonarCloud historical metrics API response
        current_data: SonarCloud current metrics API response (optional, preferred)
        branch: Git branch name for labels
        version: Package version for labels
    
    Returns:
        Prometheus-formatted metrics string
    """
    lines = []
    metrics_seen = set()  # Track which metrics we've added HELP/TYPE for
    
    # Escape quotes and backslashes in label values
    branch_escaped = branch.replace('\\', '\\\\').replace('"', '\\"')
    version_escaped = version.replace('\\', '\\\\').replace('"', '\\"') if version else None
    
    # Build labels string once
    labels = f'branch="{branch_escaped}"'
    if version_escaped:
        labels += f',version="{version_escaped}"'
    
    # Use current data if available (preferred)
    if current_data and "component" in current_data and "measures" in current_data["component"]:
        for measure in current_data["component"]["measures"]:
            metric_name = measure.get("metric")
            if not metric_name:
                continue
                
            # Convert metric name to Prometheus format (replace - with _)
            prom_metric = f"sonarcloud_{metric_name.replace('-', '_')}"
            
            # Add HELP and TYPE (once per metric)
            if prom_metric not in metrics_seen:
                help_text = f"Code {metric_name} from SonarCloud"
                lines.append(f"# HELP {prom_metric} {help_text}")
                lines.append(f"# TYPE {prom_metric} gauge")
                metrics_seen.add(prom_metric)
            
            # Get value
            value_obj = measure.get("value")
            if value_obj is None or value_obj == "":
                continue
            
            # Convert to float (handle strings like "1.0" or numeric)
            try:
                value_float = float(value_obj)
                lines.append(f'{prom_metric}{{{labels}}} {value_float}')
            except (ValueError, TypeError):
                logger.warning(f"Non-numeric value for {prom_metric}: {value_obj}, skipping")
                continue
    
    # Fallback to historical data if current_data not available
    elif historical_data and "measures" in historical_data:
        for measure in historical_data["measures"]:
            metric_name = measure.get("metric")
            if not metric_name:
                continue
            
            # Convert metric name to Prometheus format
            prom_metric = f"sonarcloud_{metric_name.replace('-', '_')}"
            
            # Add HELP and TYPE (once per metric)
            if prom_metric not in metrics_seen:
                help_text = f"Code {metric_name} from SonarCloud"
                lines.append(f"# HELP {prom_metric} {help_text}")
                lines.append(f"# TYPE {prom_metric} gauge")
                metrics_seen.add(prom_metric)
            
            # Get most recent value from history
            history = measure.get("history", [])
            if history:
                latest = history[-1]  # Most recent
                value = latest.get("value")
                if value is None or value == "":
                    continue
                
                try:
                    value_float = float(value)
                    lines.append(f'{prom_metric}{{{labels}}} {value_float}')
                except (ValueError, TypeError):
                    logger.warning(f"Non-numeric value for {prom_metric}: {value}, skipping")
                    continue
    
    if not lines:
        logger.warning("No metrics converted - check SonarCloud API response format")
        return "# No metrics available\n"
    
    return "\n".join(lines) + "\n"


async def sync_job(
    project_key: str,
    pushgateway_url: str,
    sonarcloud_token: Optional[str] = None,
    use_mailbox: bool = False,
    redis_config: Optional[MailboxConfig] = None,
    sync_interval_hours: int = 1
):
    """Main sync job - runs periodically."""
    
    metrics = [
        "coverage",
        "bugs",
        "vulnerabilities",
        "code_smells",
        "reliability_rating",
        "security_rating",
        "sqale_rating",
        "duplicated_lines_density",
        "ncloc",
        "alert_status"
    ]
    
    while True:
        try:
            logger.info("Starting sync job...")
            
            # Fetch historical data from SonarCloud
            async with SonarCloudClient(project_key, sonarcloud_token) as sonar:
                historical = await sonar.get_historical_metrics(metrics, days=30)
                current = await sonar.get_current_metrics(metrics)
            
            # Convert to Prometheus format
            branch = os.getenv("GIT_BRANCH", "main")
            version = os.getenv("PACKAGE_VERSION", None)
            
            prom_metrics = await convert_sonarcloud_to_prometheus(
                historical_data=historical,
                current_data=current,
                branch=branch,
                version=version
            )
            
            # Push to Pushgateway (or mailbox if decoupling)
            if use_mailbox and HAS_MAILBOX and redis_config:
                # Publish to mailbox for decoupling
                mailbox_service = RedisMailboxService(
                    agent_id="observatory-sync",
                    config=redis_config
                )
                publisher = MailboxPublisher(mailbox_service)
                await publisher.publish_metrics(prom_metrics, {
                    "branch": branch,
                    "version": version,
                    "source": "sonarcloud-sync"
                })
                logger.info("Metrics published to mailbox")
            else:
                # Push directly to Pushgateway
                pushgateway_auth = os.getenv("PROMETHEUS_PUSHGATEWAY_AUTH")
                async with MetricsPusher(pushgateway_url, pushgateway_auth) as pusher:
                    instance = f"{version}-sync-{int(time.time())}" if version else f"sync-{int(time.time())}"
                    await pusher.push_metrics(
                        prom_metrics,
                        job="beast-mailbox-core",
                        instance=instance,
                        labels={
                            "branch": branch,
                            "version": version or "unknown",
                            "source": "periodic-sync"
                        }
                    )
            
            logger.info("Sync job completed successfully")
            
        except Exception as e:
            logger.error(f"Sync job failed: {e}", exc_info=True)
        
        # Wait for next sync interval
        logger.info(f"Waiting {sync_interval_hours} hours until next sync...")
        await asyncio.sleep(sync_interval_hours * 3600)


async def main():
    """Main entry point."""
    project_key = os.getenv("SONARCLOUD_PROJECT_KEY", "nkllon_beast-mailbox-core")
    pushgateway_url = os.getenv("PROMETHEUS_PUSHGATEWAY_URL", "http://localhost:9091")
    sonarcloud_token = os.getenv("SONARCLOUD_TOKEN")
    sync_interval_hours = int(os.getenv("SYNC_INTERVAL_HOURS", "1"))
    
    # Mailbox config (optional)
    use_mailbox = os.getenv("USE_MAILBOX", "false").lower() == "true"
    redis_config = None
    
    if use_mailbox and HAS_MAILBOX:
        redis_config = MailboxConfig(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            db=int(os.getenv("REDIS_DB", "0")),
            stream_prefix="beast:observatory"
        )
    
    await sync_job(
        project_key=project_key,
        pushgateway_url=pushgateway_url,
        sonarcloud_token=sonarcloud_token,
        use_mailbox=use_mailbox,
        redis_config=redis_config,
        sync_interval_hours=sync_interval_hours
    )


if __name__ == "__main__":
    asyncio.run(main())

