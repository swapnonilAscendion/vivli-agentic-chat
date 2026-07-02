#!/usr/bin/env python
"""Check the status of the Azure AI Search index."""

import logging
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from config import AzureConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def check_index():
    """Check index status and document count."""
    logger.info("=" * 60)
    logger.info("INDEX STATUS CHECK")
    logger.info("=" * 60)

    try:
        credential = AzureKeyCredential(AzureConfig.SEARCH_ADMIN_KEY)
        search_client = SearchClient(
            endpoint=AzureConfig.SEARCH_ENDPOINT,
            index_name=AzureConfig.SEARCH_INDEX_NAME,
            credential=credential,
        )

        # Try to get document count
        results = search_client.search(search_text="*", top=1)
        doc_count = 0
        for _ in results:
            doc_count += 1

        logger.info(f"Index: {AzureConfig.SEARCH_INDEX_NAME}")
        logger.info(f"Endpoint: {AzureConfig.SEARCH_ENDPOINT}")
        logger.info(f"Documents in index: {doc_count}")

        if doc_count == 0:
            logger.warning("\nWARNING: Index is empty!")
            logger.warning("No documents have been indexed yet.")
            logger.warning("\nYou need to run the ingestion pipeline:")
            logger.warning("  python ingestion_pipeline.py")
            return False
        else:
            logger.info(f"\nGood! Index has {doc_count} documents.")

            # Try a test query
            logger.info("\nTesting retrieval with a sample query...")
            test_results = search_client.search(search_text="data request", top=5)
            count = 0
            for result in test_results:
                count += 1
                logger.info(f"  Result {count}: {result.get('title', 'N/A')[:50]}")

            logger.info(f"\nRetrieval working! Found {count} results.")
            return True

    except Exception as e:
        logger.error(f"Error checking index: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    check_index()
