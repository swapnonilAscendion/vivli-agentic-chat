import asyncio
import logging
import uuid
import json
import time
from typing import List
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

from config import AzureConfig
from embeddings import EmbeddingClient
from chunking import TextChunker
from document_loader import DocumentLoader
from index_manager import IndexManager

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Complete RAG document ingestion pipeline with rate limiting"""

    def __init__(self, embedding_batch_size: int = 10, batch_delay_seconds: float = 1.0):
        """
        Initialize ingestion pipeline with rate limiting.

        Args:
            embedding_batch_size: Number of embeddings to process per batch (default: 10)
            batch_delay_seconds: Delay in seconds between embedding batches (default: 1.0)
        """
        self.loader = DocumentLoader(base_path="../resources/organized-data")
        self.chunker = TextChunker(chunk_size=1000, overlap=200)
        self.embedder = EmbeddingClient()
        self.index_manager = IndexManager()

        # Rate limiting configuration
        self.embedding_batch_size = embedding_batch_size
        self.batch_delay_seconds = batch_delay_seconds

        # Search client for indexing
        credential = AzureKeyCredential(AzureConfig.SEARCH_ADMIN_KEY)
        self.search_client = SearchClient(
            endpoint=AzureConfig.SEARCH_ENDPOINT,
            index_name=AzureConfig.SEARCH_INDEX_NAME,
            credential=credential,
        )

    async def setup_index(self) -> bool:
        """Create Azure AI Search index if it doesn't exist"""
        logger.info("Setting up search index...")
        return self.index_manager.create_index()

    async def ingest_documents(self, use_sample: bool = False) -> bool:
        """
        Ingest documents into Azure AI Search.

        Args:
            use_sample: If True, use sample documents; else load from organized-data

        Returns:
            True if successful
        """
        try:
            # Step 1: Load documents
            logger.info("Step 1: Loading documents...")
            if use_sample:
                documents = self.loader.load_sample_documents()
                logger.info(f"Loaded {len(documents)} sample documents")
            else:
                documents = self.loader.load_from_organized_data()
                if not documents:
                    logger.warning("No documents found! Using sample documents instead...")
                    documents = self.loader.load_sample_documents()
                logger.info(f"Loaded {len(documents)} documents from organized-data")

            if not documents:
                logger.error("No documents to ingest")
                return False

            # Step 2: Chunk documents
            logger.info("Step 2: Chunking documents...")
            all_chunks = []
            for doc in documents:
                chunks = self.chunker.chunk_document(doc)
                all_chunks.extend(chunks)
            logger.info(f"Created {len(all_chunks)} chunks")

            # Step 3: Embed and prepare for indexing
            logger.info("Step 3: Embedding chunks...")
            documents_to_index = await self._prepare_documents_for_indexing(
                all_chunks
            )
            logger.info(f"Prepared {len(documents_to_index)} documents for indexing")

            # Step 4: Index documents
            logger.info("Step 4: Indexing documents...")
            return await self._index_documents(documents_to_index)

        except Exception as e:
            logger.error(f"Ingestion pipeline error: {str(e)}", exc_info=True)
            return False

    async def _prepare_documents_for_indexing(self, chunks: List) -> List[dict]:
        """
        Embed chunks with rate limiting and prepare for Azure AI Search indexing.

        Uses batching and delays to avoid 429 (Too Many Requests) errors.

        Args:
            chunks: List of Chunk objects

        Returns:
            List of documents ready for indexing
        """
        documents = []
        total_chunks = len(chunks)
        total_batches = (total_chunks + self.embedding_batch_size - 1) // self.embedding_batch_size

        # Estimate total time
        estimated_time = total_batches * self.batch_delay_seconds
        logger.info(f"Processing {total_chunks} chunks in {total_batches} batches")
        logger.info(f"Batch size: {self.embedding_batch_size} chunks/batch")
        logger.info(f"Delay between batches: {self.batch_delay_seconds}s")
        logger.info(f"Estimated time: ~{estimated_time:.0f} seconds (~{estimated_time/60:.1f} minutes)")

        # Process chunks in batches with delay
        for batch_num in range(0, total_chunks, self.embedding_batch_size):
            batch_end = min(batch_num + self.embedding_batch_size, total_chunks)
            batch_chunks = chunks[batch_num:batch_end]
            current_batch = (batch_num // self.embedding_batch_size) + 1

            logger.info(f"\nBatch {current_batch}/{total_batches}: Processing chunks {batch_num + 1}-{batch_end}")

            for i, chunk in enumerate(batch_chunks):
                chunk_index = batch_num + i
                try:
                    # Embed the chunk
                    embedding = await self.embedder.embed_query(chunk.text)

                    # Prepare document for Azure AI Search
                    doc = {
                        "id": str(uuid.uuid4()),
                        "title": f"{chunk.source} - Part {chunk.chunk_index + 1}",
                        "content": chunk.text,
                        "source": chunk.source,
                        "source_url": chunk.source_url or chunk.source,
                        "chunk_index": chunk.chunk_index,
                        "embedding": embedding,
                        "metadata": json.dumps(chunk.metadata or {}),
                    }
                    documents.append(doc)
                    logger.debug(f"  Embedded chunk {chunk_index + 1}/{total_chunks}")

                except Exception as e:
                    logger.error(f"Error embedding chunk {chunk_index}: {str(e)}")
                    continue

            # Add delay between batches (except after the last batch)
            if batch_end < total_chunks:
                logger.info(f"Waiting {self.batch_delay_seconds}s before next batch...")
                await asyncio.sleep(self.batch_delay_seconds)

        logger.info(f"\nSuccessfully embedded {len(documents)}/{total_chunks} chunks")
        return documents

    async def _index_documents(self, documents: List[dict]) -> bool:
        """
        Upload documents to Azure AI Search.

        Args:
            documents: List of documents to index

        Returns:
            True if successful
        """
        try:
            # Upload in batches
            batch_size = 10
            total_indexed = 0

            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]

                try:
                    result = self.search_client.upload_documents(batch)
                    successful = sum(1 for r in result if r.succeeded)
                    total_indexed += successful
                    logger.info(f"Indexed batch {i // batch_size + 1}: {successful} docs")
                except Exception as e:
                    logger.error(f"Error indexing batch {i // batch_size + 1}: {str(e)}")

            logger.info(f"Total documents indexed: {total_indexed}/{len(documents)}")
            return total_indexed > 0

        except Exception as e:
            logger.error(f"Error during indexing: {str(e)}")
            return False

    async def run(self, use_sample: bool = False):
        """
        Run the complete ingestion pipeline.

        Args:
            use_sample: If True, use sample data; else load from organized-data
        """
        logger.info("=" * 60)
        logger.info("VIVLI RAG DOCUMENT INGESTION PIPELINE")
        logger.info("=" * 60)

        # Setup index
        if not await self.setup_index():
            logger.error("Failed to create index")
            return False

        # Ingest documents
        if not await self.ingest_documents(use_sample=use_sample):
            logger.error("Failed to ingest documents")
            return False

        logger.info("=" * 60)
        logger.info("INGESTION COMPLETE!")
        logger.info("=" * 60)
        return True


if __name__ == "__main__":
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Rate limiting configuration
    # Adjust these values based on your Azure OpenAI rate limits
    EMBEDDING_BATCH_SIZE = 10      # chunks per batch
    BATCH_DELAY_SECONDS = 1.0      # seconds between batches

    # Parse command line arguments
    use_sample = "--sample" in sys.argv
    if "--batch-size" in sys.argv:
        idx = sys.argv.index("--batch-size")
        if idx + 1 < len(sys.argv):
            EMBEDDING_BATCH_SIZE = int(sys.argv[idx + 1])

    if "--batch-delay" in sys.argv:
        idx = sys.argv.index("--batch-delay")
        if idx + 1 < len(sys.argv):
            BATCH_DELAY_SECONDS = float(sys.argv[idx + 1])

    # Run pipeline with rate limiting
    pipeline = IngestionPipeline(
        embedding_batch_size=EMBEDDING_BATCH_SIZE,
        batch_delay_seconds=BATCH_DELAY_SECONDS,
    )

    success = asyncio.run(pipeline.run(use_sample=use_sample))
    sys.exit(0 if success else 1)
