"""
LangChain integration for Mnemosyne

Provides Memory class compatible with LangChain's memory system.
"""

from typing import Any, Dict, List, Optional
from langchain_core.memory import BaseMemory
from langchain_core.messages import BaseMessage, get_buffer_string

from mnemosyne import MnemosyneClient, MemoryType


class MnemosyneMemory(BaseMemory):
    """
    LangChain-compatible memory using Mnemosyne.
    
    Example:
        >>> from langchain import OpenAI, ConversationChain
        >>> from mnemosyne.integrations.langchain import MnemosyneMemory
        >>>
        >>> memory = MnemosyneMemory(api_key="your-key", user_id="user-123")
        >>> llm = OpenAI()
        >>> chain = ConversationChain(llm=llm, memory=memory)
    """
    
    # LangChain required attributes
    memory_key: str = "history"
    input_key: str = "input"
    output_key: str = "output"
    
    # Mnemosyne attributes
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    user_id: Optional[str] = None  # Used for namespacing memories
    memory_type: MemoryType = MemoryType.FACT
    
    # Internal
    _client: Optional[MnemosyneClient] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = MnemosyneClient(
            api_key=self.api_key,
            base_url=self.base_url,
        )
    
    @property
    def memory_variables(self) -> List[str]:
        """Return memory variables used by this memory"""
        return [self.memory_key]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load memories relevant to the current input.
        
        Queries Mnemosyne with the input text and returns
        relevant memories as context.
        """
        query = inputs.get(self.input_key, "")
        if not query:
            return {self.memory_key: ""}
        
        # Retrieve relevant memories
        memories = self._client.retrieve(
            query=query,
            top_k=5,
        )
        
        # Format memories as context
        if memories:
            memory_texts = [f"- {m.content}" for m in memories]
            history = "Relevant context from previous conversations:\n" + "\n".join(memory_texts)
        else:
            history = ""
        
        return {self.memory_key: history}
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Save the conversation turn to Mnemosyne.
        
        Stores both input and output for future retrieval.
        """
        # Extract input and output
        input_text = inputs.get(self.input_key, "")
        output_text = outputs.get(self.output_key, "")
        
        # Combine into conversation format
        content = f"User: {input_text}\nAssistant: {output_text}"
        
        # Store to Mnemosyne
        self._client.store(
            content=content,
            memory_type=self.memory_type,
            metadata={
                "user_id": self.user_id,
                "input": input_text,
                "output": output_text,
            },
            async_processing=True,  # Don't block on storage
        )
    
    def clear(self) -> None:
        """Clear memory - not implemented for Mnemosyne"""
        pass


class MnemosyneChatMessageHistory:
    """
    LangChain ChatMessageHistory implementation using Mnemosyne.
    
    Stores full conversation history with message roles.
    """
    
    def __init__(
        self,
        api_key: str,
        session_id: str,
        base_url: Optional[str] = None,
    ):
        self.client = MnemosyneClient(api_key=api_key, base_url=base_url)
        self.session_id = session_id
    
    def add_user_message(self, message: str) -> None:
        """Add user message to history"""
        self.client.store(
            content=message,
            memory_type=MemoryType.FACT,
            metadata={
                "session_id": self.session_id,
                "role": "user",
            },
        )
    
    def add_ai_message(self, message: str) -> None:
        """Add AI message to history"""
        self.client.store(
            content=message,
            memory_type=MemoryType.FACT,
            metadata={
                "session_id": self.session_id,
                "role": "assistant",
            },
        )
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a LangChain message"""
        content = message.content
        role = "user" if message.type == "human" else "assistant" if message.type == "ai" else "system"
        
        self.client.store(
            content=content,
            memory_type=MemoryType.FACT,
            metadata={
                "session_id": self.session_id,
                "role": role,
            },
        )
    
    def clear(self) -> None:
        """Clear history - deletes all messages for this session"""
        # Get all memories for this session
        memories = self.client.list_memories(limit=100)
        
        for memory in memories:
            if memory.extracted_data and memory.extracted_data.get("session_id") == self.session_id:
                self.client.delete_memory(memory.id)
