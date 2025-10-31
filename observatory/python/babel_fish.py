#!/usr/bin/env python3
"""
Babel Fish - Apple Intelligence Wrapper

Makes Apple Intelligence accessible as a simple function call.
Translates between "Apple's way" and "actually useful way".

Usage:
    from babel_fish import ask_apple_intelligence
    
    response = await ask_apple_intelligence(
        "Review this code for issues",
        context=code,
        query_type="code_review"
    )
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from beast_mailbox_core import RedisMailboxService, MailboxMessage, MailboxConfig
import os

logging.basicConfig(level=logging.WARNING)  # Quiet by default
logger = logging.getLogger("babel_fish")

# Global connection pool - reuse mailbox service
_babel_fish_pool: Dict[str, Any] = {}


async def ask_apple_intelligence(
    query: str,
    context: Optional[str] = None,
    query_type: str = "general",
    timeout: float = 30.0,
    mailbox_config: Optional[MailboxConfig] = None,
    agent_id: Optional[str] = None,
) -> str:
    """
    Ask Apple Intelligence a question. Simple as that.
    
    Args:
        query: Your question (e.g., "Review this code", "Why did this error occur?")
        context: Optional context (code, logs, etc.)
        query_type: Type of query - "general", "code_review", "error_diagnosis", 
                    "architecture", or "documentation"
        timeout: How long to wait for response (seconds)
        mailbox_config: Optional mailbox config (auto-detects from env if None)
        agent_id: Optional agent ID (auto-generated if None)
    
    Returns:
        Apple Intelligence's response as a string
    
    Raises:
        TimeoutError: If Apple Intelligence doesn't respond in time
        ConnectionError: If can't connect to mailbox
        Exception: If Apple Intelligence returns an error
    
    Example:
        # Simple query
        response = await ask_apple_intelligence("How should I structure this?")
        
        # Code review
        response = await ask_apple_intelligence(
            "Review this code",
            context=my_code,
            query_type="code_review"
        )
        
        # Error diagnosis
        response = await ask_apple_intelligence(
            "Why did this fail?",
            context=error_log,
            query_type="error_diagnosis"
        )
    """
    # Get or create mailbox service (connection pooling)
    cache_key = str(mailbox_config) if mailbox_config else "default"
    
    if cache_key not in _babel_fish_pool:
        if mailbox_config is None:
            mailbox_config = MailboxConfig()  # Auto-detects from env
        
        if agent_id is None:
            agent_id = f"babel-fish-{os.getpid()}"
        
        _babel_fish_pool[cache_key] = {
            "mailbox": RedisMailboxService(agent_id=agent_id, config=mailbox_config),
            "agent_id": agent_id,
            "response_queue": asyncio.Queue(),
            "started": False,
        }
    
    pool_entry = _babel_fish_pool[cache_key]
    mailbox: RedisMailboxService = pool_entry["mailbox"]
    response_queue: asyncio.Queue = pool_entry["response_queue"]
    agent_id = pool_entry["agent_id"]
    
    # Start mailbox if not already started
    if not pool_entry["started"]:
        await mailbox.start()
        
        # Register response handler
        async def handle_response(msg: MailboxMessage) -> None:
            if msg.message_type in ("APPLE_INTELLIGENCE_RESPONSE", "APPLE_INTELLIGENCE_ERROR"):
                await response_queue.put(msg)
        
        mailbox.register_handler(handle_response)
        pool_entry["started"] = True
        logger.debug(f"Babel Fish connected as {agent_id}")
    
    # Generate unique request ID
    request_id = f"{agent_id}-{asyncio.get_event_loop().time():.6f}"
    
    # Send query to Apple Intelligence agent
    await mailbox.send_message(
        recipient="apple-intelligence",
        message_type="QUERY_APPLE_INTELLIGENCE",
        payload={
            "query": query,
            "context": context,
            "query_type": query_type,
            "request_id": request_id,
        }
    )
    
    logger.debug(f"Babel Fish sent query: {query[:50]}...")
    
    # Wait for response (with timeout)
    try:
        response_msg = await asyncio.wait_for(
            response_queue.get(),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        raise TimeoutError(
            f"Apple Intelligence didn't respond within {timeout}s. "
            f"Is the apple-intelligence agent running?"
        )
    
    # Check for error response
    if response_msg.message_type == "APPLE_INTELLIGENCE_ERROR":
        error = response_msg.payload.get("error", "Unknown error")
        raise Exception(f"Apple Intelligence error: {error}")
    
    # Extract response
    response = response_msg.payload.get("response", "")
    
    logger.debug(f"Babel Fish received response: {len(response)} chars")
    
    return response


async def review_code(code: str, query: str = "Review this code for issues and improvements") -> str:
    """
    Convenience function for code review.
    
    Example:
        feedback = await review_code(my_code)
    """
    return await ask_apple_intelligence(query, context=code, query_type="code_review")


async def diagnose_error(error_log: str, query: str = "Why did this error occur and how do I fix it?") -> str:
    """
    Convenience function for error diagnosis.
    
    Example:
        diagnosis = await diagnose_error(my_error_log)
    """
    return await ask_apple_intelligence(query, context=error_log, query_type="error_diagnosis")


async def get_architecture_advice(query: str, context: Optional[str] = None) -> str:
    """
    Convenience function for architecture advice.
    
    Example:
        advice = await get_architecture_advice("How should I structure this feature?")
    """
    return await ask_apple_intelligence(query, context=context, query_type="architecture")


def close_all_connections():
    """
    Close all Babel Fish connections. Call this when done.
    """
    async def _close():
        for pool_entry in _babel_fish_pool.values():
            if pool_entry["started"]:
                await pool_entry["mailbox"].stop()
        _babel_fish_pool.clear()
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Can't await in running loop, schedule for later
            asyncio.create_task(_close())
        else:
            loop.run_until_complete(_close())
    except RuntimeError:
        # No event loop, create one
        asyncio.run(_close())


# Auto-cleanup on exit
import atexit
atexit.register(close_all_connections)

