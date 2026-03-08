# Mnemosyne Python SDK

Official Python client for Mnemosyne - AI Memory Layer

## Installation

```bash
pip install mnemosyne-memory
```

With optional dependencies:
```bash
# Local mode (Chroma + Ollama)
pip install mnemosyne-memory[local]

# LangChain integration
pip install mnemosyne-memory[langchain]

# All extras
pip install mnemosyne-memory[all]
```

## Quick Start

```python
from mnemosyne import MnemosyneClient

# Initialize client
client = MnemosyneClient(api_key="your-api-key")

# Store a memory
result = client.store("I'm gluten-free and love Italian food")
print(result.status)  # "accepted"

# Retrieve memories
memories = client.retrieve("What food does the user like?")
for memory in memories:
    print(f"- {memory.content} (confidence: {memory.confidence})")
```

## Async Usage

```python
from mnemosyne import AsyncMnemosyneClient

async with AsyncMnemosyneClient(api_key="your-key") as client:
    result = await client.store("I prefer tea over coffee")
    memories = await client.retrieve("drink preferences")
```

## LangChain Integration

```python
from langchain import OpenAI, ConversationChain
from mnemosyne.integrations.langchain import MnemosyneMemory

memory = MnemosyneMemory(api_key="your-key", user_id="user-123")
llm = OpenAI()
chain = ConversationChain(llm=llm, memory=memory)

# Memory persists across conversations
chain.predict(input="I'm gluten-free")
chain.predict(input="What should I eat?")  # Knows about gluten-free preference
```

## Environment Variables

```bash
export MNEMOSYNE_API_KEY="your-api-key"
export MNEMOSYNE_BASE_URL="https://api.mnemosyne.dev"  # Optional
```

## API Reference

### Store
```python
client.store(
    content="Text to remember",
    memory_type=MemoryType.PREFERENCE,  # or FACT, ENTITY, etc.
    metadata={"source": "chat"},
    async_processing=True,  # True = queue for processing
)
```

### Retrieve
```python
memories = client.retrieve(
    query="What does user like?",
    top_k=5,
    memory_type=MemoryType.PREFERENCE,
    min_confidence=0.5,
)
```

### List Memories
```python
all_memories = client.list_memories(limit=20)
preferences = client.list_memories(memory_type=MemoryType.PREFERENCE)
```

### Delete
```python
client.delete_memory(memory_id)
```

## License

MIT
