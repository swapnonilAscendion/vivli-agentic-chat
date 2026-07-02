#!/usr/bin/env python
"""Diagnose relevance score filtering issue."""

import asyncio
import logging
from embeddings import EmbeddingClient
from retrieval import Retrieval
from config import AzureConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def diagnose(query: str):
    """Test a query and show relevance scores."""
    logger.info("=" * 60)
    logger.info(f"DIAGNOSING QUERY: '{query}'")
    logger.info("=" * 60)

    embedder = EmbeddingClient()
    retrieval = Retrieval()

    # Get embedding
    logger.info("\n1. Generating embedding...")
    embedding = await embedder.embed_query(query)
    logger.info(f"   Embedding generated: {len(embedding)} dimensions")

    # Retrieve documents (WITHOUT filtering)
    logger.info("\n2. Retrieving documents...")
    retrieval_result = await retrieval.retrieve_documents(
        embedding,
        query_text=query,
        top_k=10
    )

    logger.info(f"   Retrieved {len(retrieval_result.documents)} documents")

    # Show all documents with scores
    if retrieval_result.documents:
        logger.info("\n3. Relevance Scores:")
        logger.info(f"   Current threshold: {AzureConfig.RELEVANCE_THRESHOLD}")
        logger.info("")

        for i, doc in enumerate(retrieval_result.documents, 1):
            score = doc.relevance_score
            passed = "PASS" if score >= AzureConfig.RELEVANCE_THRESHOLD else "FAIL"
            logger.info(f"   {i}. Score: {score:.4f} [{passed}] - {doc.title[:50]}")

        # Filter
        filtered = [d for d in retrieval_result.documents if d.relevance_score >= AzureConfig.RELEVANCE_THRESHOLD]
        logger.info(f"\n4. After Filtering:")
        logger.info(f"   Documents passed filter: {len(filtered)}/{len(retrieval_result.documents)}")

        if filtered:
            logger.info("\n   These documents would be used:")
            for doc in filtered:
                logger.info(f"   - {doc.title}")
        else:
            logger.warning("\n   WARNING: No documents passed the relevance filter!")
            logger.warning("   The query would receive a generic escalation response.")

    else:
        logger.warning("   No documents found at all!")

    logger.info("\n" + "=" * 60)
    logger.info("RECOMMENDATION:")
    if retrieval_result.documents and not [d for d in retrieval_result.documents if d.relevance_score >= AzureConfig.RELEVANCE_THRESHOLD]:
        min_score = min(d.relevance_score for d in retrieval_result.documents)
        logger.info(f"   Lower RELEVANCE_THRESHOLD from 0.6 to ~{max(0.3, min_score - 0.05):.2f}")
        logger.info("   Edit config.py and change line 35")
    logger.info("=" * 60)

if __name__ == "__main__":
    queries = ["hi", "help", "data request", "how to submit"]

    for query in queries:
        asyncio.run(diagnose(query))
        print("\n")
