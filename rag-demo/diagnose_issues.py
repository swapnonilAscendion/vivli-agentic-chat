#!/usr/bin/env python
"""Comprehensive diagnosis of chatbot issues."""

import asyncio
import json
import logging
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from config import AzureConfig
from embeddings import EmbeddingClient
from retrieval import Retrieval
from intent_classifier import IntentClassifier
from document_loader import DocumentLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def diagnose_index():
    """Check how many documents are in the index."""
    logger.info("\n" + "="*70)
    logger.info("DIAGNOSIS 1: INDEX STATUS")
    logger.info("="*70)

    try:
        credential = AzureKeyCredential(AzureConfig.SEARCH_ADMIN_KEY)
        search_client = SearchClient(
            endpoint=AzureConfig.SEARCH_ENDPOINT,
            index_name=AzureConfig.SEARCH_INDEX_NAME,
            credential=credential,
        )

        # Get all documents
        results = list(search_client.search(search_text="*", top=1000))
        doc_count = len(results)

        logger.info(f"Index: {AzureConfig.SEARCH_INDEX_NAME}")
        logger.info(f"Total documents in index: {doc_count}")

        if doc_count == 0:
            logger.warning("❌ INDEX IS EMPTY - This is the problem!")
            logger.warning("No documents indexed. Need to run ingestion pipeline.")
            return False

        logger.info(f"✓ Index has {doc_count} documents")

        # Show sample documents
        logger.info("\nSample documents in index:")
        for i, doc in enumerate(results[:3], 1):
            logger.info(f"\n{i}. Title: {doc.get('title', 'N/A')[:50]}")
            logger.info(f"   Content: {doc.get('content', 'N/A')[:60]}...")
            logger.info(f"   Source: {doc.get('source', 'N/A')}")

        return True

    except Exception as e:
        logger.error(f"Error checking index: {str(e)}", exc_info=True)
        return False


async def diagnose_retrieval():
    """Test retrieval with sample queries."""
    logger.info("\n" + "="*70)
    logger.info("DIAGNOSIS 2: RETRIEVAL FUNCTIONALITY")
    logger.info("="*70)

    try:
        embedder = EmbeddingClient()
        retrieval = Retrieval()

        test_queries = [
            "data request",
            "form check",
            "review process",
            "submit",
            "hi"
        ]

        for query in test_queries:
            logger.info(f"\n{'─'*70}")
            logger.info(f"Query: '{query}'")
            logger.info(f"{'─'*70}")

            # Generate embedding
            embedding = await embedder.embed_query(query)

            # Retrieve documents
            result = await retrieval.retrieve_documents(
                embedding,
                query_text=query,
                top_k=10
            )

            logger.info(f"Retrieved: {len(result.documents)} documents")

            # Show all retrieved with scores
            if result.documents:
                for i, doc in enumerate(result.documents, 1):
                    status = "✓" if doc.relevance_score >= AzureConfig.RELEVANCE_THRESHOLD else "✗"
                    logger.info(f"  {i}. [{status}] Score: {doc.relevance_score:.4f} - {doc.title[:40]}")

                # Count how many pass threshold
                passed = len([d for d in result.documents if d.relevance_score >= AzureConfig.RELEVANCE_THRESHOLD])
                logger.info(f"\nAfter filtering (threshold {AzureConfig.RELEVANCE_THRESHOLD}): {passed}/{len(result.documents)} pass")
            else:
                logger.warning(f"  ❌ No documents retrieved at all!")

    except Exception as e:
        logger.error(f"Error in retrieval: {str(e)}", exc_info=True)


def diagnose_intent_classification():
    """Test intent classification."""
    logger.info("\n" + "="*70)
    logger.info("DIAGNOSIS 3: INTENT CLASSIFICATION")
    logger.info("="*70)

    try:
        classifier = IntentClassifier()

        test_queries = [
            "hi",
            "data request",
            "how do I submit?",
            "form check",
            "help me",
        ]

        for query in test_queries:
            result = classifier.classify(query)
            logger.info(f"\nQuery: '{query}'")
            logger.info(f"  Intent: {result.intent}")
            logger.info(f"  Confidence: {result.confidence:.2f}")
            logger.info(f"  Keywords: {result.keywords_detected}")

            if result.all_scores:
                logger.info(f"  All scores: {result.all_scores}")

    except Exception as e:
        logger.error(f"Error in classification: {str(e)}", exc_info=True)


def diagnose_config():
    """Check current configuration."""
    logger.info("\n" + "="*70)
    logger.info("DIAGNOSIS 4: CONFIGURATION")
    logger.info("="*70)

    logger.info(f"Embedding dimensions: {AzureConfig.EMBEDDING_DIMENSIONS}")
    logger.info(f"Relevance threshold: {AzureConfig.RELEVANCE_THRESHOLD}")
    logger.info(f"Confidence threshold: {AzureConfig.CONFIDENCE_THRESHOLD}")
    logger.info(f"Top K documents: {AzureConfig.TOP_K_DOCUMENTS}")
    logger.info(f"Search endpoint: {AzureConfig.SEARCH_ENDPOINT}")
    logger.info(f"Search index: {AzureConfig.SEARCH_INDEX_NAME}")
    logger.info(f"OpenAI endpoint: {AzureConfig.OPENAI_ENDPOINT}")


def diagnose_documents_in_resources():
    """Check what documents are available to ingest."""
    logger.info("\n" + "="*70)
    logger.info("DIAGNOSIS 5: AVAILABLE DOCUMENTS")
    logger.info("="*70)

    try:
        loader = DocumentLoader(base_path="../resources/organized-data")
        docs = loader.load_from_organized_data()

        logger.info(f"Documents available to ingest: {len(docs)}")

        if len(docs) > 0:
            logger.info("Documents found:")
            for i, doc in enumerate(docs[:5], 1):
                content = doc.get('content', '')[:60]
                logger.info(f"  {i}. {doc.get('source', 'unknown')}: {content}...")
        else:
            logger.warning("❌ No documents found in resources/organized-data/")
            logger.warning("This might be the issue - need to add documents there")

    except Exception as e:
        logger.error(f"Error checking documents: {str(e)}", exc_info=True)


async def main():
    """Run all diagnostics."""
    logger.info("\n" + "█"*70)
    logger.info("VIVLI CHATBOT - COMPREHENSIVE DIAGNOSTIC REPORT")
    logger.info("█"*70)

    # Run diagnostics
    index_ok = diagnose_index()
    await diagnose_retrieval()
    diagnose_intent_classification()
    diagnose_config()
    diagnose_documents_in_resources()

    # Summary
    logger.info("\n" + "█"*70)
    logger.info("SUMMARY & RECOMMENDATIONS")
    logger.info("█"*70)

    if not index_ok:
        logger.warning("\n🔴 CRITICAL ISSUE: Index is empty!")
        logger.warning("Action: Run ingestion pipeline")
        logger.warning("Command: python ingestion_pipeline.py --sample")
    else:
        logger.info("\n✓ Index has documents")

    logger.info("\n📊 Check the output above for:")
    logger.info("  1. How many documents are in the index")
    logger.info("  2. What documents are being retrieved")
    logger.info("  3. What relevance scores are being assigned")
    logger.info("  4. How intent is being classified")
    logger.info("  5. What documents are available to ingest")

    logger.info("\n" + "█"*70)


if __name__ == "__main__":
    asyncio.run(main())
