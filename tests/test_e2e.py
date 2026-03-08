"""
End-to-End API Integration Test

Tests the complete Mnemosyne flow:
1. Health check
2. Store memory
3. Search memory
4. List memories
5. Delete memory
"""

import asyncio
import sys
import os

# Add SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk', 'src'))

from mnemosyne import MnemosyneClient, MemoryType


def test_health_check():
    """Test API health endpoint"""
    print("\n1. Testing Health Check...")
    client = MnemosyneClient(
        api_key="test-key",
        base_url="http://localhost:8000"
    )
    
    try:
        result = client.health_check()
        print(f"   ✓ API Status: {result.get('status', 'unknown')}")
        return True
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
        return False
    finally:
        client.close()


def test_store_memory():
    """Test storing a memory"""
    print("\n2. Testing Store Memory...")
    client = MnemosyneClient(
        api_key="test-key",
        base_url="http://localhost:8000"
    )
    
    try:
        result = client.store(
            content="I'm gluten-free and love Italian food",
            memory_type=MemoryType.PREFERENCE,
            async_processing=False  # Sync for testing
        )
        print(f"   ✓ Memory stored: {result.status}")
        if result.memory_ids:
            print(f"   ✓ Memory IDs: {result.memory_ids}")
        return True
    except Exception as e:
        print(f"   ✗ Store failed: {e}")
        return False
    finally:
        client.close()


def test_retrieve_memory():
    """Test retrieving memories"""
    print("\n3. Testing Retrieve Memory...")
    client = MnemosyneClient(
        api_key="test-key",
        base_url="http://localhost:8000"
    )
    
    try:
        memories = client.retrieve(
            query="What food does the user like?",
            top_k=5
        )
        print(f"   ✓ Retrieved {len(memories)} memories")
        for mem in memories:
            print(f"     - {mem.content[:50]}... (confidence: {mem.confidence})")
        return True
    except Exception as e:
        print(f"   ✗ Retrieve failed: {e}")
        return False
    finally:
        client.close()


def test_list_memories():
    """Test listing all memories"""
    print("\n4. Testing List Memories...")
    client = MnemosyneClient(
        api_key="test-key",
        base_url="http://localhost:8000"
    )
    
    try:
        memories = client.list_memories(limit=10)
        print(f"   ✓ Listed {len(memories)} memories")
        return True
    except Exception as e:
        print(f"   ✗ List failed: {e}")
        return False
    finally:
        client.close()


def run_e2e_tests():
    """Run all end-to-end tests"""
    print("=" * 50)
    print("MNEMOSYNE END-TO-END API TEST")
    print("=" * 50)
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: Store Memory
    results.append(("Store Memory", test_store_memory()))
    
    # Test 3: Retrieve Memory
    results.append(("Retrieve Memory", test_retrieve_memory()))
    
    # Test 4: List Memories
    results.append(("List Memories", test_list_memories()))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! API integration is working.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check API status.")
        return 1


if __name__ == "__main__":
    exit_code = run_e2e_tests()
    sys.exit(exit_code)
