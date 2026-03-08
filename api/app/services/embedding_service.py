"""
Embedding service - Generate vector embeddings for text
"""

from typing import List
import google.generativeai as genai

from app.core.config import get_settings

settings = get_settings()


class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = settings.EMBEDDING_MODEL
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        Returns 768-dimensional vector for text-embedding-004.
        """
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        Note: Gemini API supports batching but we'll do sequential for now.
        """
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding optimized for retrieval queries.
        """
        result = genai.embed_content(
            model=self.model,
            content=query,
            task_type="retrieval_query",
        )
        return result["embedding"]
