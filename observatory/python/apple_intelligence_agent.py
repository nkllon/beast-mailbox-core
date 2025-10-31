#!/usr/bin/env python3
"""
Apple Intelligence Agent for Beast Cohort

Bridges Apple Intelligence (Swift/AppIntents) with Beast Cohort (Python/mailbox)
Allows Python agents to query Apple Intelligence via mailbox messages.
"""

import asyncio
import httpx
import logging
import os
from typing import Dict, Any, Optional

# Import beast-mailbox-core
from beast_mailbox_core import RedisMailboxService, MailboxMessage, MailboxConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("apple_intelligence_agent")

# HTTP endpoint for Swift Apple Intelligence server
INTELLIGENCE_SERVER_URL = os.getenv("APPLE_INTELLIGENCE_SERVER_URL", "http://localhost:8081")


class AppleIntelligenceAgent:
    """Agent that bridges Apple Intelligence with Beast Cohort mailbox."""
    
    def __init__(self, config: MailboxConfig):
        self.mailbox = RedisMailboxService(
            agent_id="apple-intelligence",
            config=config
        )
        self.server_url = INTELLIGENCE_SERVER_URL
        
        # Register handler
        self.mailbox.register_handler(self.handle_message)
        
        logger.info(f"Apple Intelligence Agent initialized")
        logger.info(f"Server URL: {self.server_url}")
    
    async def handle_message(self, message: MailboxMessage) -> None:
        """Handle mailbox messages requesting Apple Intelligence queries."""
        
        if message.message_type != "QUERY_APPLE_INTELLIGENCE":
            logger.warning(f"Ignoring message type: {message.message_type}")
            return
        
        payload = message.payload
        query = payload.get("query", "")
        context = payload.get("context")
        query_type = payload.get("query_type", "general")
        
        logger.info(f"Processing query from {message.sender}: {query[:50]}...")
        
        try:
            # Query Apple Intelligence via HTTP server (Swift app)
            response = await self.query_apple_intelligence(
                query=query,
                context=context,
                query_type=query_type
            )
            
            # Send response back via mailbox
            await self.mailbox.send_message(
                recipient=message.sender,
                message_type="APPLE_INTELLIGENCE_RESPONSE",
                payload={
                    "response": response,
                    "original_query": query,
                    "query_type": query_type
                }
            )
            
            logger.info(f"✅ Response sent to {message.sender}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process query: {e}", exc_info=True)
            
            # Send error response
            await self.mailbox.send_message(
                recipient=message.sender,
                message_type="APPLE_INTELLIGENCE_ERROR",
                payload={
                    "error": str(e),
                    "original_query": query
                }
            )
    
    async def query_apple_intelligence(
        self,
        query: str,
        context: Optional[str] = None,
        query_type: str = "general"
    ) -> str:
        """Query Apple Intelligence via HTTP server."""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.server_url}/query",
                json={
                    "query": query,
                    "context": context,
                    "query_type": query_type
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
    
    async def start(self) -> None:
        """Start the agent and listen to mailbox."""
        logger.info("Starting Apple Intelligence Agent...")
        await self.mailbox.start()
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            await self.mailbox.stop()


async def main():
    """Main entry point."""
    
    # Get Redis config from environment
    config = MailboxConfig(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.getenv("REDIS_PASSWORD"),
        db=int(os.getenv("REDIS_DB", "0")),
        stream_prefix="beast:observatory"
    )
    
    agent = AppleIntelligenceAgent(config)
    await agent.start()


if __name__ == "__main__":
    asyncio.run(main())

