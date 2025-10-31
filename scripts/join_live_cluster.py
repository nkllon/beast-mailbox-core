#!/usr/bin/env python3
"""Join live Beast Mode cluster for testing.

This script connects to the live cluster and can discover/chat with other agents.
Requires: pip install beast-agent==0.1.3
"""

import asyncio
import sys
from beast_agent import BaseAgent
from beast_mailbox_core.redis_mailbox import MailboxConfig

# Update these for your cluster
REDIS_HOST = "192.168.1.119"  # Update with actual cluster host
REDIS_PORT = 6379
REDIS_PASSWORD = "beastmode2025"  # Update with actual password
REDIS_DB = 0

# Your agent ID (make it unique and descriptive)
AGENT_ID = "beast-mailbox-core-test-agent"


class ClusterTester(BaseAgent):
    """Test agent that can discover and chat with other agents."""
    
    def __init__(self):
        # Create authenticated mailbox config
        mailbox_config = MailboxConfig(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            stream_prefix="beast:mailbox"
        )
        
        super().__init__(
            agent_id=AGENT_ID,
            capabilities=["testing", "discovery", "chat"],
            mailbox_url=mailbox_config
        )
        self.discovered_agents = []
    
    async def on_startup(self) -> None:
        """Called after connection established."""
        self._logger.info("🚀 Connected to live cluster!")
        
        # Register handlers
        self.register_handler("CHAT_MESSAGE", self.handle_chat)
        self.register_handler("PING", self.handle_ping)
        self.register_handler("HELLO", self.handle_hello)
        
        # Discover other agents
        await self.discover_all_agents()
        
        # Say hello to everyone
        await self.broadcast_hello()
    
    async def discover_all_agents(self) -> None:
        """Discover all agents on the cluster."""
        try:
            agents = await self.discover_agents()
            self._logger.info(f"📡 Discovered {len(agents)} agents on cluster:")
            
            for agent_id, info in agents.items():
                if agent_id != self.agent_id:
                    capabilities = info.get('capabilities', 'no capabilities')
                    self._logger.info(f"  - {agent_id}: {capabilities}")
                    self.discovered_agents.append(agent_id)
        except Exception as e:
            self._logger.warning(f"Discovery failed: {e}")
    
    async def broadcast_hello(self) -> None:
        """Send hello message to all discovered agents."""
        if not self.discovered_agents:
            self._logger.info("No other agents discovered yet")
            return
        
        self._logger.info(f"👋 Saying hello to {len(self.discovered_agents)} agents...")
        for agent_id in self.discovered_agents:
            try:
                await self.send_message(
                    target=agent_id,
                    message_type="HELLO",
                    content={
                        "from": self.agent_id,
                        "greeting": "Hello from beast-mailbox-core test agent!",
                        "capabilities": ["testing", "discovery", "chat"]
                    }
                )
            except Exception as e:
                self._logger.warning(f"Failed to message {agent_id}: {e}")
    
    async def handle_chat(self, content: dict) -> None:
        """Handle incoming chat messages."""
        sender = content.get("sender") or content.get("from", "unknown")
        message = content.get("message", "")
        self._logger.info(f"💬 Chat from {sender}: {message}")
    
    async def handle_ping(self, content: dict) -> None:
        """Handle ping messages."""
        sender = content.get("sender") or content.get("from", "unknown")
        self._logger.info(f"🏓 Ping from {sender}")
        
        # Respond with pong
        try:
            await self.send_message(
                target=sender,
                message_type="PONG",
                content={"from": self.agent_id, "response": "pong"}
            )
        except Exception as e:
            self._logger.warning(f"Failed to send pong: {e}")
    
    async def handle_hello(self, content: dict) -> None:
        """Handle hello messages."""
        sender = content.get("from", "unknown")
        greeting = content.get("greeting", "")
        self._logger.info(f"👋 Hello from {sender}: {greeting}")
    
    async def on_shutdown(self) -> None:
        """Called before disconnection."""
        self._logger.info("👋 Disconnecting from cluster...")


async def main():
    """Main entry point."""
    agent = ClusterTester()
    
    try:
        # Connect and register
        await agent.startup()
        
        # Keep running
        self._logger.info("✅ Agent is live! Press Ctrl+C to exit...")
        await asyncio.sleep(3600)  # Run for 1 hour, or until interrupted
        
    except KeyboardInterrupt:
        self._logger.info("\n🛑 Shutting down...")
    finally:
        await agent.shutdown()


if __name__ == "__main__":
    # Check version
    try:
        import beast_agent
        version = getattr(beast_agent, '__version__', 'unknown')
        if version < "0.1.3":
            print("⚠️  WARNING: beast-agent v0.1.3+ required for discovery methods")
            print(f"   Current version: {version}")
            print("   Upgrade: pip install beast-agent==0.1.3")
            sys.exit(1)
    except ImportError:
        print("❌ ERROR: beast-agent not installed")
        print("   Install: pip install beast-agent==0.1.3")
        sys.exit(1)
    
    asyncio.run(main())

