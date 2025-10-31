"""Lightweight Redis-backed mailbox service for inter-agent messaging."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional
from urllib.parse import urlparse
from uuid import uuid4

import redis.asyncio as redis


@dataclass
class RecoveryMetrics:
    """Metrics collected during pending message recovery."""

    total_recovered: int = 0
    batches_processed: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class MailboxConfig:
    """Configuration for connecting to Redis streams."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    stream_prefix: str = "beast:mailbox"
    max_stream_length: int = 1000
    poll_interval: float = 2.0
    enable_recovery: bool = True
    recovery_min_idle_time: int = 0
    recovery_batch_size: int = 50


def _create_config_from_env() -> MailboxConfig:
    """Create MailboxConfig from environment variables.
    
    Priority order:
    1. REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB (individual env vars)
    2. REDIS_URL (if REDIS_HOST not set)
    3. Defaults to localhost:6379 if no env vars are set
    
    Returns:
        MailboxConfig instance populated from environment variables or defaults
        
    Example:
        >>> os.environ["REDIS_HOST"] = "prod-redis.example.com"
        >>> os.environ["REDIS_PASSWORD"] = "secret"
        >>> config = _create_config_from_env()
        >>> assert config.host == "prod-redis.example.com"
        >>> assert config.password == "secret"
    """
    # Priority 1: Individual environment variables (REDIS_HOST, REDIS_PORT, etc.)
    redis_host = os.getenv("REDIS_HOST")
    
    if redis_host:
        # Individual env vars are set - use them
        return MailboxConfig(
            host=redis_host,
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            db=int(os.getenv("REDIS_DB", "0")),
            stream_prefix="beast:mailbox",
            enable_recovery=True,
        )
    
    # Priority 2: REDIS_URL (if REDIS_HOST not set)
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            parsed = urlparse(redis_url)
            
            # Validate scheme
            if parsed.scheme not in ("redis", "rediss"):
                logging.getLogger("beast_mailbox").warning(
                    f"Unsupported REDIS_URL scheme: {parsed.scheme}. "
                    "Use redis:// or rediss://. Falling back to defaults."
                )
                return MailboxConfig()
            
            # Extract components
            host = parsed.hostname or "localhost"
            port = parsed.port or 6379
            password = parsed.password
            db = 0
            if parsed.path and len(parsed.path) > 1:
                try:
                    db = int(parsed.path[1:])  # Skip leading '/'
                except ValueError:
                    pass
            
            return MailboxConfig(
                host=host,
                port=port,
                password=password,
                db=db,
                stream_prefix="beast:mailbox",
                enable_recovery=True,
            )
        except Exception as exc:
            logging.getLogger("beast_mailbox").warning(
                f"Invalid REDIS_URL format: {redis_url}. "
                f"Error: {exc}. Falling back to defaults."
            )
            return MailboxConfig()
    
    # Priority 3: Defaults (localhost:6379)
    return MailboxConfig()


@dataclass
class MailboxMessage:
    """Structured message exchanged between agents."""

    message_id: str
    sender: str
    recipient: str
    payload: Dict[str, Any]
    message_type: str = "direct_message"
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time())

    def to_redis_fields(self) -> Dict[str, str]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "payload": json.dumps(self.payload),
            "message_type": self.message_type,
            "timestamp": str(self.timestamp),
        }

    @classmethod
    def from_redis_fields(cls, fields: Dict[bytes, bytes]) -> "MailboxMessage":
        decoded = {k.decode(): v.decode() for k, v in fields.items()}
        payload = json.loads(decoded.get("payload", "{}"))
        return cls(
            message_id=decoded.get("message_id", str(uuid4())),
            sender=decoded.get("sender", "unknown"),
            recipient=decoded.get("recipient", "unknown"),
            payload=payload,
            message_type=decoded.get("message_type", "direct_message"),
            timestamp=float(decoded.get("timestamp", "0.0")),
        )


class RedisMailboxService:
    """Async Redis stream consumer/producer for inter-agent communication.
    
    This service manages bidirectional messaging using Redis Streams (XADD/XREADGROUP).
    Each agent has an inbox stream where other agents can send messages. Messages are
    consumed via consumer groups, providing at-least-once delivery with acknowledgment.
    
    Features:
        - Automatic consumer group creation and management
        - Message handler registration for inbound processing
        - Durable message queue with configurable retention
        - Async/await based for efficient concurrent operations
        - Automatic reconnection and error recovery
        - Pending message recovery on startup (XAUTOCLAIM-based)
        - Configurable recovery behavior (idle time, batch size)
        - Recovery metrics and instrumentation callbacks
        
    Example:
        >>> config = MailboxConfig(host="localhost", db=0)
        >>> service = RedisMailboxService("my-agent", config)
        >>> 
        >>> # Register a handler for incoming messages
        >>> async def handle_message(msg: MailboxMessage):
        ...     print(f"Received: {msg.payload}")
        >>> service.register_handler(handle_message)
        >>> 
        >>> # Optional: Add recovery callback for metrics
        >>> async def on_recovery_complete(metrics: RecoveryMetrics):
        ...     print(f"Recovered {metrics.total_recovered} messages")
        >>> service = RedisMailboxService("my-agent", config, recovery_callback=on_recovery_complete)
        >>> 
        >>> # Start consuming messages (recovery runs automatically)
        >>> await service.start()
        >>> 
        >>> # Send a message to another agent
        >>> await service.send_message("other-agent", {"text": "Hello!"})
        >>> 
        >>> # Graceful shutdown
        >>> await service.stop()
        
    Pending Message Recovery:
        On startup, the service automatically reclaims and processes any pending messages
        from the consumer group. This ensures messages that were in-flight during a previous
        shutdown are not lost. Recovery behavior can be configured via MailboxConfig:
        
        - enable_recovery: Enable/disable pending message recovery (default: True)
        - recovery_min_idle_time: Minimum time (seconds) before claiming pending messages (default: 0)
        - recovery_batch_size: Number of messages to process per batch (default: 50)
        
        Recovery runs before the consume loop starts, ensuring at-least-once delivery semantics.
    """

    def __init__(
        self,
        agent_id: str,
        config: Optional[MailboxConfig] = None,
        recovery_callback: Optional[Callable[[RecoveryMetrics], Awaitable[None]]] = None,
    ):
        """Initialize the mailbox service for a specific agent.
        
        Args:
            agent_id: Unique identifier for this agent instance
            config: Optional configuration. If None, reads from environment variables:
                   - REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB (priority 1)
                   - REDIS_URL (priority 2, if REDIS_HOST not set)
                   - Defaults to localhost:6379 if no env vars are set
            recovery_callback: Optional async callback invoked after recovery completes
                              Receives RecoveryMetrics object with recovery stats
            
        Note:
            The agent_id is used to generate unique inbox streams and consumer groups.
            Multiple service instances with the same agent_id will share the same inbox.
            
        Example:
            >>> # With explicit config
            >>> config = MailboxConfig(host="redis.example.com", password="secret")
            >>> service = RedisMailboxService("my-agent", config)
            
            >>> # With environment variables (production-friendly)
            >>> # export REDIS_HOST="prod-redis.example.com"
            >>> # export REDIS_PASSWORD="secret"
            >>> service = RedisMailboxService("my-agent", config=None)  # Reads from env
        """
        self.agent_id = agent_id
        if config is None:
            # Read from environment variables
            self.config = _create_config_from_env()
        else:
            # Use explicit config (backward compatible)
            self.config = config
        self.recovery_callback = recovery_callback
        self.logger = logging.getLogger(f"beast_mailbox.{agent_id}")
        self._client: Optional[redis.Redis] = None
        self._processing_task: Optional[asyncio.Task] = None
        self._handlers: List[Callable[[MailboxMessage], Awaitable[None]]] = []
        self._running = False
        self._consumer_group = f"{agent_id}:group"
        self._consumer_name = f"{agent_id}:{uuid4().hex[:6]}"

    @property
    def inbox_stream(self) -> str:
        """Get the Redis stream name for this agent's inbox.
        
        Returns:
            Fully qualified stream name in format: "{prefix}:{agent_id}:in"
            
        Example:
            For agent "alice" with prefix "beast:mailbox":
            Returns: "beast:mailbox:alice:in"
        """
        return f"{self.config.stream_prefix}:{self.agent_id}:in"

    async def connect(self) -> None:
        """Establish connection to Redis server and verify connectivity.
        
        Creates a Redis client if one doesn't exist and pings the server
        to ensure the connection is working.
        
        Raises:
            redis.exceptions.ConnectionError: If Redis server is unreachable
            redis.exceptions.AuthenticationError: If password is incorrect
            
        Note:
            This is idempotent - calling multiple times won't create multiple clients.
        """
        if self._client is None:
            self._client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                db=self.config.db,
                decode_responses=False,
            )
            # Ping to verify connection works
            await self._client.ping()

    async def _recover_pending_messages(self) -> RecoveryMetrics:
        """Recover pending messages from the consumer group.
        
        Claims pending entries using XAUTOCLAIM and dispatches them to registered handlers.
        Processes messages in batches until no more are available.
        
        Returns:
            RecoveryMetrics object containing recovery statistics
            
        Note:
            If no handlers are registered, logs a warning and skips recovery.
            If consumer group doesn't exist, exits gracefully without error.
        """
        metrics = RecoveryMetrics()
        metrics.start_time = asyncio.get_event_loop().time()
        
        if not self.config.enable_recovery:
            self.logger.info("Pending message recovery is disabled")
            return metrics
        
        if not self._handlers:
            self.logger.warning(
                "No handlers registered for recovery - pending messages will not be processed"
            )
            return metrics
        
        assert self._client is not None
        
        try:
            # Check if consumer group exists by querying pending info
            self.logger.debug("Checking pending messages: stream=%s, group=%s", self.inbox_stream, self._consumer_group)
            pending_info = await self._client.xpending_range(
                name=self.inbox_stream,
                groupname=self._consumer_group,
                min="-",
                max="+",
                count=1,
            )
            
            self.logger.debug("xpending_range returned: %s (type: %s, len: %s)", pending_info, type(pending_info), len(pending_info) if pending_info else 0)
            
            if not pending_info:
                self.logger.info("No pending messages to recover")
                metrics.end_time = asyncio.get_event_loop().time()
                # Invoke callback even when no messages to recover
                if self.recovery_callback:
                    try:
                        await self.recovery_callback(metrics)
                    except Exception as exc:
                        self.logger.exception("Recovery callback failed: %s", exc)
                return metrics
                
        except Exception as exc:
            if "NOGROUP" in str(exc):
                self.logger.debug("Consumer group does not exist yet - skipping recovery")
                metrics.end_time = asyncio.get_event_loop().time()
                # Invoke callback even when group doesn't exist
                if self.recovery_callback:
                    try:
                        await self.recovery_callback(metrics)
                    except Exception as exc:
                        self.logger.exception("Recovery callback failed: %s", exc)
                return metrics
            else:
                self.logger.warning("Failed to check pending messages: %s", exc)
                metrics.end_time = asyncio.get_event_loop().time()
                # Invoke callback even on error
                if self.recovery_callback:
                    try:
                        await self.recovery_callback(metrics)
                    except Exception as exc:
                        self.logger.exception("Recovery callback failed: %s", exc)
                return metrics
        
        self.logger.info("Starting pending message recovery...")
        start_id = "0-0"
        
        while True:
            try:
                self.logger.debug("Calling xautoclaim with start_id=%s, min_idle_time=%dms", start_id, self.config.recovery_min_idle_time * 1000)
                # Claim pending messages
                claimed_data = await self._client.xautoclaim(
                    name=self.inbox_stream,
                    groupname=self._consumer_group,
                    consumername=self._consumer_name,
                    min_idle_time=self.config.recovery_min_idle_time * 1000,  # Convert to ms
                    start_id=start_id,
                    count=self.config.recovery_batch_size,
                )
                
                self.logger.debug("xautoclaim returned: %s (type: %s, len: %s)", claimed_data, type(claimed_data), len(claimed_data) if claimed_data else None)
                
                if not claimed_data or len(claimed_data) < 3:
                    self.logger.debug("No more claims available (claimed_data=%s), breaking", claimed_data)
                    break
                    
                next_start_id = claimed_data[0]
                # claimed_data[1] is a list of messages
                messages = claimed_data[1]
                
                self.logger.debug("Next start ID: %s (type: %s), Messages: %d", next_start_id, type(next_start_id), len(messages) if messages else 0)
                
                # Convert bytes to string for comparison
                next_start_id_str = next_start_id.decode() if isinstance(next_start_id, bytes) else str(next_start_id)
                
                if not messages:
                    # If no messages were claimed, move to next ID to prevent infinite loop
                    self.logger.debug("No messages in this batch, next_start_id_str=%s", next_start_id_str)
                    if next_start_id_str == "0-0":
                        self.logger.debug("Next ID is '0-0' with no messages, breaking")
                        break
                    start_id = next_start_id_str if isinstance(next_start_id, bytes) else next_start_id
                    self.logger.debug("Continuing with next start_id=%s", start_id)
                    continue
                
                self.logger.debug(
                    "Recovered batch of %d pending messages (next: %s)",
                    len(messages),
                    next_start_id,
                )
                
                # Process and acknowledge each message
                for entry in messages:
                    message_id, fields = entry[:2]
                    mailbox_message = MailboxMessage.from_redis_fields(fields)
                    
                    self.logger.debug(
                        "Recovering message %s from %s",
                        message_id,
                        mailbox_message.sender,
                    )
                    
                    await self._dispatch(mailbox_message)
                    
                    # Acknowledge the recovered message
                    await self._client.xack(
                        self.inbox_stream,
                        self._consumer_group,
                        message_id,
                    )
                    
                    metrics.total_recovered += 1
                
                metrics.batches_processed += 1
                
                # Continue with next batch
                # Convert bytes to string if needed
                start_id = next_start_id_str if isinstance(next_start_id, bytes) else str(next_start_id)
                
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.logger.exception("Error during recovery: %s", exc)
                break
        
        metrics.end_time = asyncio.get_event_loop().time()
        elapsed = metrics.end_time - metrics.start_time
        
        self.logger.info(
            "Recovery complete: %d messages recovered in %d batches (%.2fs)",
            metrics.total_recovered,
            metrics.batches_processed,
            elapsed,
        )
        
        # Invoke callback if provided
        if self.recovery_callback:
            try:
                await self.recovery_callback(metrics)
            except Exception as exc:
                self.logger.exception("Recovery callback failed: %s", exc)
        
        return metrics
    
    async def start(self) -> bool:
        """Start the mailbox service and begin consuming messages.
        
        This method:
        1. Connects to Redis
        2. Creates the consumer group (if it doesn't exist)
        3. Recovers pending messages (if enabled and handlers are registered)
        4. Launches the background message consumption loop
        
        Returns:
            True if service started successfully
            
        Raises:
            Exception: If consumer group creation fails (except BUSYGROUP)
            
        Note:
            The service runs in a background asyncio task. Messages are
            dispatched to registered handlers as they arrive.
        """
        await self.connect()
        assert self._client is not None
        try:
            self.logger.debug("Creating consumer group: stream=%s, group=%s", self.inbox_stream, self._consumer_group)
            await self._client.xgroup_create(
                name=self.inbox_stream,
                groupname=self._consumer_group,
                id="0",  # Start from beginning of stream to read all messages, not just new ones
                mkstream=True,
            )
            self.logger.info(
                "Created consumer group %s for stream %s",
                self._consumer_group,
                self.inbox_stream,
            )
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                raise
            self.logger.debug("Consumer group already exists (BUSYGROUP), continuing")
        
        # Run pending message recovery before starting the consume loop
        if self.config.enable_recovery:
            self.logger.debug("Starting recovery after group setup")
            await self._recover_pending_messages()
        
        self._running = True
        self._processing_task = asyncio.create_task(self._consume_loop())
        return True

    async def stop(self) -> None:
        """Gracefully stop the mailbox service and cleanup resources.
        
        This method:
        1. Sets _running flag to False (stops consume loop)
        2. Cancels and waits for the processing task to complete
        3. Closes the Redis client connection
        
        The method is idempotent and safe to call multiple times.
        Exceptions during shutdown are suppressed to ensure cleanup completes.
        
        Note:
            CancelledError is intentionally suppressed here since stop() IS
            the cleanup handler. Re-raising would propagate to callers
            expecting graceful shutdown.
        """
        self._running = False
        
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:  # noqa: S7497
                # NOTE: SonarCloud flags this as python:S7497 (should re-raise)
                # However, stop() IS the cleanup handler - re-raising would propagate
                # to callers expecting graceful shutdown. This is intentional suppression.
                pass
            except Exception:
                pass  # Ignore other errors during shutdown
            finally:
                self._processing_task = None
        if self._client:
            await self._client.aclose()  # Replaced deprecated close() with aclose()
            self._client = None

    def register_handler(self, handler: Callable[[MailboxMessage], Awaitable[None]]) -> None:
        """Register an async handler function for incoming messages.
        
        Args:
            handler: Async function that takes a MailboxMessage and returns None
            
        Example:
            >>> async def my_handler(msg: MailboxMessage):
            ...     print(f"Got: {msg.payload}")
            >>> service.register_handler(my_handler)
            
        Note:
            Multiple handlers can be registered. They are called sequentially
            for each message. Handler errors are caught and logged but don't
            stop other handlers from running.
        """
        self._handlers.append(handler)

    async def send_message(
        self,
        recipient: str,
        payload: Dict[str, Any],
        message_type: str = "direct_message",
        message_id: Optional[str] = None,
    ) -> str:
        """Send a message to another agent's inbox stream.
        
        Args:
            recipient: Agent ID of the message recipient
            payload: JSON-serializable data (dict, list, or primitives)
            message_type: Classification of the message (default: "direct_message")
            message_id: Optional custom message ID (auto-generated if None)
            
        Returns:
            Message ID of the sent message (useful for tracking/correlation)
            
        Raises:
            redis.exceptions.ConnectionError: If Redis connection fails
            
        Example:
            >>> msg_id = await service.send_message(
            ...     recipient="bob",
            ...     payload={"action": "ping", "data": [1, 2, 3]},
            ...     message_type="command"
            ... )
            
        Note:
            Messages are added to the recipient's inbox stream with MAXLEN
            to prevent unbounded growth. The stream will automatically trim
            old messages when the limit is reached.
        """
        await self.connect()
        assert self._client is not None
        message = MailboxMessage(
            message_id=message_id or str(uuid4()),
            sender=self.agent_id,
            recipient=recipient,
            payload=payload,
            message_type=message_type,
        )
        stream = f"{self.config.stream_prefix}:{recipient}:in"
        await self._client.xadd(
            stream,
            message.to_redis_fields(),
            maxlen=self.config.max_stream_length,
            approximate=True,
        )
        self.logger.debug("Sent message %s to stream %s", message.message_id, stream)
        return message.message_id

    async def _consume_loop(self) -> None:
        """Background loop that consumes messages from the inbox stream.
        
        This infinite loop:
        1. Reads messages from the consumer group using XREADGROUP
        2. Deserializes each message to a MailboxMessage
        3. Dispatches to all registered handlers
        4. Acknowledges processed messages with XACK
        
        The loop runs until _running is set to False (via stop() method).
        Errors are logged and the loop continues after a delay.
        
        Raises:
            asyncio.CancelledError: When the task is cancelled (propagated)
            
        Note:
            This method should not be called directly - it's launched
            automatically by start() as a background task.
        """
        assert self._client is not None
        while self._running:
            try:
                response = await self._client.xreadgroup(
                    groupname=self._consumer_group,
                    consumername=self._consumer_name,
                    streams={self.inbox_stream: ">"},
                    count=10,
                    block=int(self.config.poll_interval * 1000),
                )
                if not response:
                    continue
                for stream_name, messages in response:
                    self.logger.debug(
                        "Redis mailbox received %d messages from %s",
                        len(messages),
                        stream_name,
                    )
                    for message_id, fields in messages:
                        mailbox_message = MailboxMessage.from_redis_fields(fields)
                        await self._dispatch(mailbox_message)
                        await self._client.xack(stream_name, self._consumer_group, message_id)
            except asyncio.CancelledError:
                # Task cancelled - re-raise to propagate cancellation properly
                raise
            except Exception as exc:
                self.logger.exception("Error in mailbox consume loop: %s", exc)
                await asyncio.sleep(self.config.poll_interval)

    async def _dispatch(self, message: MailboxMessage) -> None:
        """Dispatch a message to all registered handlers.
        
        Args:
            message: The MailboxMessage to dispatch
            
        Behavior:
            - If no handlers are registered, logs the message and returns
            - Calls each handler sequentially
            - Handler exceptions are caught, logged, and don't affect other handlers
            
        Note:
            Handlers must not modify the handler list during iteration.
            Each handler is called with the same message instance.
        """
        if not self._handlers:
            self.logger.info("Mailbox message received with no handlers registered: %s", message)
            return
        # Iterate directly - handlers must not modify the list during iteration
        for handler in self._handlers:
            try:
                await handler(message)
            except Exception as exc:
                self.logger.exception("Mailbox handler failed: %s", exc)

