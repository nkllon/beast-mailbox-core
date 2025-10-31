#!/usr/bin/env python3
"""
Test Babel Fish - Make sure it actually works
"""

import asyncio
from babel_fish import ask_apple_intelligence, review_code, diagnose_error, get_architecture_advice


async def test_simple_query():
    """Test a simple query."""
    print("🧪 Testing simple query...")
    response = await ask_apple_intelligence("What's the best way to handle errors in Python?")
    print(f"✅ Response: {response[:200]}...")
    return response


async def test_code_review():
    """Test code review."""
    print("🧪 Testing code review...")
    code = """
async def sync_metrics():
    await fetch_from_sonarcloud()
    await push_to_prometheus()
"""
    response = await review_code(code, "Review this code for issues")
    print(f"✅ Response: {response[:200]}...")
    return response


async def test_error_diagnosis():
    """Test error diagnosis."""
    print("🧪 Testing error diagnosis...")
    error_log = """
ERROR: Connection refused
Traceback: File "sync.py", line 150
    await push_to_prometheus()
ConnectionError: Failed to connect to localhost:9091
"""
    response = await diagnose_error(error_log)
    print(f"✅ Response: {response[:200]}...")
    return response


async def test_architecture():
    """Test architecture advice."""
    print("🧪 Testing architecture advice...")
    response = await get_architecture_advice(
        "How should I structure a sync service for reliability?",
        context="Current implementation uses single sync loop"
    )
    print(f"✅ Response: {response[:200]}...")
    return response


async def main():
    """Run all tests."""
    print("🐟 Babel Fish Test Suite")
    print("=" * 50)
    
    try:
        await test_simple_query()
        await test_code_review()
        await test_error_diagnosis()
        await test_architecture()
        print("\n✅ All tests passed!")
    except TimeoutError as e:
        print(f"\n❌ Timeout: {e}")
        print("   Make sure apple-intelligence agent is running!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

