"""
Pinecone vector database client
"""

from typing import List, Optional, Dict, Any
import uuid

from pinecone import Pinecone, ServerlessSpec

from app.core.config import get_settings

settings = get_settings()


class PineconeClient:
    """Pinecone vector store client for Mnemosyne"""
    
    def __init__(self):
        self._client: Optional[Pinecone] = None
        self._index = None
    
    async def connect(self):
        """Initialize Pinecone connection"""
        if self._client is None:
            self._client = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Get or create index
            index_name = settings.PINECONE_INDEX_NAME
            
            if index_name not in self._client.list_indexes().names():
                # Create index if it doesn't exist
                self._client.create_index(
                    name=index_name,
                    dimension=settings.VECTOR_DIMENSION,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )
            
            self._index = self._client.Index(index_name)
    
    async def disconnect(self):
        """Close Pinecone connection"""
        self._index = None
        self._client = None
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if not self._index:
            return {}
        return self._index.describe_index_stats()
    
    async def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]],
        namespace: Optional[str] = None,
    ):
        """
        Upsert vectors to Pinecone.
        
        Args:
            vectors: List of {id: str, values: List[float], metadata: dict}
            namespace: Optional namespace (user_id for multi-tenancy)
        """
        if not self._index:
            raise RuntimeError("Pinecone not connected")
        
        # Batch upsert (Pinecone has 1000 vector limit per request)
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self._index.upsert(vectors=batch, namespace=namespace)
    
    async def query_vectors(
        self,
        vector: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filter: Optional[Dict] = None,
        include_metadata: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Query vectors from Pinecone.
        
        Args:
            vector: Query embedding
            top_k: Number of results
            namespace: Optional namespace
            filter: Metadata filter
        """
        if not self._index:
            raise RuntimeError("Pinecone not connected")
        
        results = self._index.query(
            vector=vector,
            top_k=top_k,
            namespace=namespace,
            filter=filter,
            include_metadata=include_metadata,
        )
        
        return [
            {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata if include_metadata else None,
            }
            for match in results.matches
        ]
    
    async def delete_vectors(
        self,
        ids: List[str],
        namespace: Optional[str] = None,
    ):
        """Delete vectors by ID"""
        if not self._index:
            raise RuntimeError("Pinecone not connected")
        
        self._index.delete(ids=ids, namespace=namespace)
    
    async def delete_all_vectors(self, namespace: Optional[str] = None):
        """Delete all vectors in namespace (DANGER)"""
        if not self._index:
            raise RuntimeError("Pinecone not connected")
        
        self._index.delete(delete_all=True, namespace=namespace)
    
    async def fetch_vectors(
        self,
        ids: List[str],
        namespace: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch vectors by ID"""
        if not self._index:
            raise RuntimeError("Pinecone not connected")
        
        return self._index.fetch(ids=ids, namespace=namespace)
