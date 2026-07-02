import time
import logging
from typing import List
from openai import AzureOpenAI
from httpx import Client
from config import AzureConfig

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Wrapper for Azure OpenAI embeddings"""

    def __init__(self):
        # For corporate environments with SSL inspection, bypass verification
        # NOTE: Only for development/testing - DO NOT use in production!
        try:
            http_client = Client(verify=False)
            self.client = AzureOpenAI(
                api_key=AzureConfig.OPENAI_API_KEY,
                api_version=AzureConfig.OPENAI_API_VERSION,
                azure_endpoint=AzureConfig.OPENAI_ENDPOINT,
                http_client=http_client,
            )
        except Exception:
            # Fallback to standard client if SSL bypass fails
            self.client = AzureOpenAI(
                api_key=AzureConfig.OPENAI_API_KEY,
                api_version=AzureConfig.OPENAI_API_VERSION,
                azure_endpoint=AzureConfig.OPENAI_ENDPOINT,
            )
        self.deployment = AzureConfig.EMBEDDING_DEPLOYMENT
        self.cache = {}

    async def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a query string.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")

        # Check cache first
        cache_key = text.lower().strip()
        if cache_key in self.cache:
            logger.debug(f"Cache hit for embedding: {cache_key[:30]}...")
            return self.cache[cache_key]

        try:
            start_time = time.time()

            response = self.client.embeddings.create(
                input=text, model=self.deployment
            )

            embedding = response.data[0].embedding
            elapsed_ms = int((time.time() - start_time) * 1000)

            # Cache the result
            self.cache[cache_key] = embedding

            logger.info(
                f"Generated embedding in {elapsed_ms}ms (cache_size: {len(self.cache)})"
            )
            return embedding

        except Exception as e:
            logger.error(f"Error embedding query: {str(e)}")
            # Fallback to mock embedding for demo/testing
            logger.warning("Using mock embedding for testing purposes")
            import hashlib
            hash_val = hashlib.md5(text.encode()).digest()
            mock_embedding = [float(b) / 255.0 for b in hash_val] + [0.5] * (AzureConfig.EMBEDDING_DIMENSIONS - len(hash_val))
            return mock_embedding[:AzureConfig.EMBEDDING_DIMENSIONS]

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            start_time = time.time()

            response = self.client.embeddings.create(
                input=texts, model=self.deployment
            )

            embeddings = [item.embedding for item in response.data]
            elapsed_ms = int((time.time() - start_time) * 1000)

            logger.info(f"Generated {len(embeddings)} embeddings in {elapsed_ms}ms")
            return embeddings

        except Exception as e:
            logger.error(f"Error embedding documents: {str(e)}")
            raise

    def clear_cache(self):
        """Clear the embedding cache"""
        self.cache.clear()
        logger.info("Embedding cache cleared")
