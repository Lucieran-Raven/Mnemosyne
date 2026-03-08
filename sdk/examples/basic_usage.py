"""
Mnemosyne SDK Examples

Quick examples showing how to use the Mnemosyne Python SDK.
"""

import asyncio
from mnemosyne import MnemosyneClient, AsyncMnemosyneClient, MemoryType

# Example 1: Basic sync usage
def basic_example():
    """Store and retrieve memories synchronously"""
    client = MnemosyneClient(api_key="your-api-key")
    
    # Store a memory
    result = client.store(
        content="I'm gluten-free and love Italian food",
        memory_type=MemoryType.PREFERENCE
    )
    print(f"Stored with status: {result.status}")
    
    # Retrieve memories
    memories = client.retrieve("What food does the user like?")
    for memory in memories:
        print(f"- {memory.content} (confidence: {memory.confidence})")
    
    client.close()


# Example 2: Async usage
async def async_example():
    """Store and retrieve memories asynchronously"""
    async with AsyncMnemosyneClient(api_key="your-api-key") as client:
        # Store multiple memories concurrently
        tasks = [
            client.store("I prefer email over phone calls"),
            client.store("My favorite color is blue"),
            client.store("I'm allergic to peanuts"),
        ]
        results = await asyncio.gather(*tasks)
        print(f"Stored {len(results)} memories")
        
        # Search memories
        memories = await client.retrieve("What are my preferences?")
        for memory in memories:
            print(f"- {memory.content}")


# Example 3: Conversation storage
def conversation_example():
    """Store a full conversation"""
    client = MnemosyneClient(api_key="your-api-key")
    
    turns = [
        {"role": "user", "content": "I need a restaurant recommendation"},
        {"role": "assistant", "content": "What type of cuisine do you prefer?"},
        {"role": "user", "content": "Italian, but I need gluten-free options"},
        {"role": "assistant", "content": "I know a great place - Luigi's has excellent GF pasta"},
    ]
    
    result = client.store_turns(turns)
    print(f"Conversation stored: {result.status}")
    
    # Later, retrieve what we learned
    memories = client.retrieve("What are my dietary restrictions?")
    for m in memories:
        print(f"Learned: {m.content}")
    
    client.close()


# Example 4: Error handling
def error_handling_example():
    """Handle errors gracefully"""
    from mnemosyne import AuthenticationError, RateLimitError, NotFoundError
    
    try:
        client = MnemosyneClient(api_key="invalid-key")
        memories = client.retrieve("test query")
    except AuthenticationError:
        print("Invalid API key - please check your credentials")
    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after} seconds")
    except NotFoundError:
        print("Memory not found")
    except Exception as e:
        print(f"Unexpected error: {e}")


# Example 5: Health check and connection test
def health_check_example():
    """Check API health before making requests"""
    client = MnemosyneClient(api_key="your-api-key")
    
    if client.ping():
        print("✓ API is healthy")
        
        # Get detailed health info
        health = client.health_check()
        print(f"Status: {health.get('status')}")
        print(f"Database: {health.get('database', 'unknown')}")
        print(f"Vector DB: {health.get('vector_db', 'unknown')}")
    else:
        print("✗ API is not responding")
    
    client.close()


if __name__ == "__main__":
    print("Mnemosyne SDK Examples")
    print("=" * 40)
    
    # Run sync example
    print("\n1. Basic Sync Example:")
    basic_example()
    
    # Run async example
    print("\n2. Async Example:")
    asyncio.run(async_example())
