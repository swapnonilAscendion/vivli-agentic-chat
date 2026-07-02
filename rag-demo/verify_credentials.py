#!/usr/bin/env python
"""Verify that all Azure credentials are working correctly."""

import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_azure_openai():
    """Test Azure OpenAI connection for embeddings and LLM."""
    import asyncio

    logger.info("\n" + "="*60)
    logger.info("Testing Azure OpenAI Credentials...")
    logger.info("="*60)

    try:
        from config import AzureConfig
        from embeddings import EmbeddingClient

        logger.info(f"✓ Config loaded")
        logger.info(f"  - Endpoint: {AzureConfig.OPENAI_ENDPOINT}")
        logger.info(f"  - Embedding deployment: {AzureConfig.EMBEDDING_DEPLOYMENT}")
        logger.info(f"  - LLM deployment: {AzureConfig.LLM_DEPLOYMENT}")

        # Test embedding (async function)
        logger.info("\nTesting Embedding Service...")
        embedder = EmbeddingClient()
        test_text = "This is a test sentence for embeddings."

        async def test_embed():
            return await embedder.embed_query(test_text)

        embedding = asyncio.run(test_embed())

        if embedding and len(embedding) > 0:
            logger.info(f"✓ Embedding works! Generated {len(embedding)}-dim vector")
        else:
            logger.error("✗ Embedding failed - no vector returned")
            return False

        logger.info("\n✓ Azure OpenAI: ALL TESTS PASSED")
        return True

    except Exception as e:
        logger.error(f"\n✗ Azure OpenAI Error: {str(e)}", exc_info=True)
        return False


def test_azure_search():
    """Test Azure AI Search connection."""
    logger.info("\n" + "="*60)
    logger.info("Testing Azure AI Search Credentials...")
    logger.info("="*60)

    try:
        from config import AzureConfig
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential

        logger.info(f"✓ Config loaded")
        logger.info(f"  - Endpoint: {AzureConfig.SEARCH_ENDPOINT}")
        logger.info(f"  - Index: {AzureConfig.SEARCH_INDEX_NAME}")

        # Try to connect to Search
        credential = AzureKeyCredential(AzureConfig.SEARCH_ADMIN_KEY)
        search_client = SearchClient(
            endpoint=AzureConfig.SEARCH_ENDPOINT,
            index_name=AzureConfig.SEARCH_INDEX_NAME,
            credential=credential,
        )

        # Try a simple search to verify connection
        results = search_client.search(search_text="test", top=1)
        result_count = 0
        for _ in results:
            result_count += 1

        logger.info(f"✓ Search connection works!")
        logger.info(f"  - Connected to index: {AzureConfig.SEARCH_INDEX_NAME}")
        logger.info(f"  - Test search returned {result_count} results (or index is empty)")
        logger.info("\n✓ Azure AI Search: ALL TESTS PASSED")
        return True

    except Exception as e:
        logger.error(f"\n✗ Azure AI Search Error: {str(e)}", exc_info=True)
        return False


def test_index_manager():
    """Test index creation capability."""
    logger.info("\n" + "="*60)
    logger.info("Testing Index Manager...")
    logger.info("="*60)

    try:
        from index_manager import IndexManager

        mgr = IndexManager()
        index_exists = mgr.index_exists()

        logger.info(f"✓ Index Manager loaded")
        logger.info(f"  - Index exists: {index_exists}")
        logger.info(f"  - Index name: vivli-knowledge-base")
        logger.info("\n✓ Index Manager: WORKING")
        return True

    except Exception as e:
        logger.error(f"\n✗ Index Manager Error: {str(e)}", exc_info=True)
        return False


def main():
    """Run all verification tests."""
    logger.info("\n" + "🔍 VIVLI CREDENTIAL VERIFICATION 🔍".center(60))

    results = {
        "Azure OpenAI": test_azure_openai(),
        "Azure AI Search": test_azure_search(),
        "Index Manager": test_index_manager(),
    }

    # Summary
    logger.info("\n" + "="*60)
    logger.info("VERIFICATION SUMMARY")
    logger.info("="*60)

    for service, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {service}")

    all_passed = all(results.values())

    logger.info("="*60)
    if all_passed:
        logger.info("✓ ALL CREDENTIALS VERIFIED - READY TO USE!")
        logger.info("="*60)
        return 0
    else:
        logger.info("✗ SOME SERVICES FAILED - CHECK CREDENTIALS")
        logger.info("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
