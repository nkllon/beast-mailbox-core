# Discovering and Interacting with Agents on the Cluster

**Status:** Live-fire testing active 🚀

## Quick Connect

To join the live cluster and discover other agents:

```python
import asyncio
from beast_agent import BaseAgent
from beast_mailbox_core.redis_mailbox import MailboxConfig

class ClusterExplorer(BaseAgent):
    def __init__(self):
        # Connect to live cluster
        mailbox_config = MailboxConfig(
            host="192.168.1.119",  # Update with actual cluster host
            port=6379,
            password="beastmode2025",  # Update with actual password
            db=0
        )
        
        super().__init__(
            agent_id="explorer-agent",
            capabilities=["discovery", "chat"],
            mailbox_url=mailbox_config
        )
        self.discovered_agents = []
    
    async def on_startup(self) -> None:
        self._logger.info("Connecting to live cluster...")
        self.register_handler("CHAT_MESSAGE", self.handle_chat)
        self.register_handler("PING", self.handle_ping)
        
        # Discover other agents
        await self.discover_agents()
    
    async def discover_agents(self) -> None:
        """Discover all active agents on the cluster."""
        import redis.asyncio as redis
        
        # Connect to same Redis
        client = redis.Redis(
            host=self._mailbox_config.host,
            port=self._mailbox_config.port,
            password=self._mailbox_config.password,
            db=self._mailbox_config.db
        )
        
        # Get all active agent IDs
        agent_ids = await client.smembers("beast:agents:all")
        
        self._logger.info(f"Found {len(agent_ids)} active agents:")
        for agent_id_bytes in agent_ids:
            agent_id = agent_id_bytes.decode() if isinstance(agent_id_bytes, bytes) else agent_id_bytes
            
            # Get agent metadata
            agent_info = await client.hgetall(f"beast:agents:{agent_id}")
            if agent_info:
                decoded_info = {k.decode() if isinstance(k, bytes) else k: 
                               v.decode() if isinstance(v, bytes) else v 
                               for k, v in agent_info.items()}
                self._logger.info(f"  - {agent_id}: {decoded_info.get('capabilities', 'no capabilities')}")
                self.discovered_agents.append(agent_id)
        
        await client.aclose()
    
    async def handle_chat(self, content: dict) -> None:
        """Handle incoming chat messages."""
        sender = content.get("sender", "unknown")
        message = content.get("message", "")
        self._logger.info(f"💬 {sender}: {message}")
    
    async def handle_ping(self, content: dict) -> None:
        """Handle ping messages."""
        sender = content.get("sender", "unknown")
        self._logger.info(f"🏓 Ping from {sender}")
        
        # Respond with pong
        await self.send_message(
            target=sender,
            message_type="PONG",
            content={"sender": self.agent_id, "response": "pong"}
        )
    
    async def broadcast_message(self, message: str) -> None:
        """Send message to all discovered agents."""
        for agent_id in self.discovered_agents:
            if agent_id != self.agent_id:  # Don't message ourselves
                await self.send_message(
                    target=agent_id,
                    message_type="CHAT_MESSAGE",
                    content={"message": message, "sender": self.agent_id}
                )
    
    async def ping_agent(self, target_agent_id: str) -> None:
        """Ping a specific agent."""
        await self.send_message(
            target=target_agent_id,
            message_type="PING",
            content={"sender": self.agent_id}
        )
    
    async def on_shutdown(self) -> None:
        self._logger.info("Disconnecting from cluster...")

async def main():
    explorer = ClusterExplorer()
    await explorer.startup()
    
    # Wait a moment for discovery
    await asyncio.sleep(2)
    
    # Send a broadcast message
    if explorer.discovered_agents:
        await explorer.broadcast_message("Hello from explorer-agent! 👋")
    
    # Keep running
    try:
        await asyncio.sleep(3600)  # Run for 1 hour
    except KeyboardInterrupt:
        pass
    finally:
        await explorer.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Cluster Discovery Pattern

### Discovering All Agents

```python
import redis.asyncio as redis

async def discover_cluster(host, port, password, db=0):
    client = redis.Redis(host=host, port=port, password=password, db=db)
    
    # Get all active agent IDs
    agent_ids = await client.smembers("beast:agents:all")
    
    agents = {}
    for agent_id_bytes in agent_ids:
        agent_id = agent_id_bytes.decode() if isinstance(agent_id_bytes, bytes) else agent_id_bytes
        
        # Get agent metadata
        info = await client.hgetall(f"beast:agents:{agent_id}")
        if info:
            decoded = {k.decode() if isinstance(k, bytes) else k: 
                      v.decode() if isinstance(v, bytes) else v 
                      for k, v in info.items()}
            agents[agent_id] = decoded
    
    await client.aclose()
    return agents

# Usage
agents = await discover_cluster("192.168.1.119", 6379, "beastmode2025")
for agent_id, info in agents.items():
    print(f"{agent_id}: {info.get('capabilities')}")
```

### Sending Messages to Discovered Agents

```python
# After discovering agents
for agent_id in discovered_agents:
    await agent.send_message(
        target=agent_id,
        message_type="HELLO",
        content={"from": my_agent_id, "greeting": "Hi!"}
    )
```

## Message Types for Testing

Common message types you might encounter:

- `CHAT_MESSAGE` - Chat between agents
- `PING` / `PONG` - Liveness checking
- `HELLO` - Introduction messages
- `DISCOVERY` - Agent discovery requests
- `STATUS` - Status updates

## Cluster Redis Keys

The cluster uses these Redis keys:

- `beast:agents:all` - Set of all active agent IDs
- `beast:agents:{agent_id}` - Hash with agent metadata (capabilities, state, timestamp)
- `beast:mailbox:{agent_id}:in` - Inbox stream for each agent

## Troubleshooting

**Can't discover agents:**
- Verify Redis connection (check host/port/password)
- Check that your agent successfully called `startup()`
- Verify your agent appears in `beast:agents:all` set

**Can't receive messages:**
- Ensure handlers are registered before calling `startup()`
- Check message type matches registered handler
- Verify recipient agent ID is correct

**Connection errors:**
- Verify Redis host/port are accessible
- Check password is correct
- Ensure Redis server is running

## Example: Join Live Cluster

```bash
# Install beast-agent
pip install beast-agent

# Run the explorer script above
python cluster_explorer.py
```

Your agent will:
1. ✅ Connect to Redis cluster
2. ✅ Register itself on the cluster
3. ✅ Discover all other active agents
4. ✅ Start receiving messages from other agents
5. ✅ Be able to send messages to any discovered agent

