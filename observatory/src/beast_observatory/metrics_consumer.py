#!/usr/bin/env python3
"""
Observatory Metrics Consumer

Consumes metrics from Redis mailbox and pushes to Prometheus Pushgateway.
Decouples sync service from Prometheus availability.
"""

import asyncio
import logging
import os
from typing import Dict, Optional

try:
    from beast_mailbox_core import RedisMailboxService, MailboxMessage
    # MailboxConfig is in redis_mailbox module
    from beast_mailbox_core.redis_mailbox import MailboxConfig
except ImportError as e:
    print(f"ERROR: beast-mailbox-core not installed or incomplete: {e}")
    print("Install with: pip install beast-mailbox-core>=0.4.4")
    raise

try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp not installed. Install with: pip install aiohttp")
    raise

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("beast_observatory.consumer")


class PushgatewayPusher:
    """Pushes metrics to Prometheus Pushgateway."""
    
    def __init__(self, pushgateway_url: str, auth: Optional[str] = None):
        self.pushgateway_url = pushgateway_url.rstrip("/")
        self.auth = auth
        self.session = None
    
    async def __aenter__(self):
        headers = {}
        if self.auth:
            import base64
            auth_bytes = self.auth.encode()
            auth_b64 = base64.b64encode(auth_bytes).decode()
            headers["Authorization"] = f"Basic {auth_b64}"
        
        self.session = aiohttp.ClientSession(headers=headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def push(self, metrics_content: str, job: str, instance: str, labels: Dict) -> bool:
        """Push metrics to Pushgateway."""
        url = f"{self.pushgateway_url}/metrics/job/{job}/instance/{instance}"
        for key, value in labels.items():
            url += f"/{key}/{value}"
        
        try:
            async with self.session.put(url, data=metrics_content) as response:
                response.raise_for_status()
                logger.info(f"Metrics pushed to Pushgateway (HTTP {response.status})")
                return True
        except Exception as e:
            logger.error(f"Failed to push to Pushgateway: {e}")
            return False


class MetricsConsumer:
    """Consumes metrics from mailbox and pushes to Pushgateway."""
    
    def __init__(
        self,
        mailbox_service: RedisMailboxService,
        pushgateway_url: str,
        pushgateway_auth: Optional[str] = None
    ):
        self.mailbox = mailbox_service
        self.pusher = PushgatewayPusher(pushgateway_url, pushgateway_auth)
    
    async def handle_metrics_message(self, message: MailboxMessage):
        """Handle metrics message from mailbox."""
        if message.message_type != "METRICS_UPDATE":
            logger.warning(f"Ignoring message type: {message.message_type}")
            return
        
        payload = message.payload
        metrics_content = payload.get("metrics")
        metadata = payload.get("metadata", {})
        
        logger.info(f"Received metrics update: {metadata}")
        
        # Push to Pushgateway
        async with self.pusher:
            job = "beast-mailbox-core"
            instance = f"{metadata.get('version', 'unknown')}-{metadata.get('source', 'unknown')}"
            labels = {
                "branch": metadata.get("branch", "main"),
                "version": metadata.get("version", "unknown"),
                "source": metadata.get("source", "mailbox")
            }
            
            success = await self.pusher.push(metrics_content, job, instance, labels)
            if success:
                logger.info("Metrics successfully pushed to Pushgateway")
            else:
                logger.warning("Failed to push metrics - will be retried by mailbox")
    
    async def start(self):
        """Start consuming messages."""
        # Register handler
        self.mailbox.register_handler("METRICS_UPDATE", self.handle_metrics_message)
        
        # Start mailbox service
        await self.mailbox.start()
        logger.info("Metrics consumer started, listening for messages...")
        
        # Keep running
        try:
            await asyncio.Event().wait()  # Run forever
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            await self.mailbox.stop()


async def main():
    """Main entry point."""
    redis_config = MailboxConfig(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.getenv("REDIS_PASSWORD"),
        db=int(os.getenv("REDIS_DB", "0")),
        stream_prefix="beast:observatory"
    )
    
    pushgateway_url = os.getenv("PROMETHEUS_PUSHGATEWAY_URL", "http://localhost:9091")
    pushgateway_auth = os.getenv("PROMETHEUS_PUSHGATEWAY_AUTH")
    
    mailbox_service = RedisMailboxService(
        agent_id="observatory-consumer",
        config=redis_config
    )
    
    consumer = MetricsConsumer(mailbox_service, pushgateway_url, pushgateway_auth)
    await consumer.start()


def main_cli():
    """CLI entry point for setuptools."""
    asyncio.run(main())


if __name__ == "__main__":
    main_cli()

