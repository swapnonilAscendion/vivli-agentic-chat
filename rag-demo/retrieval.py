import time
import logging
from typing import List
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from config import AzureConfig
from models import RetrievedDocument, RetrievalResult

logger = logging.getLogger(__name__)


class Retrieval:
    """Vector search in Azure AI Search"""

    def __init__(self):
        credential = AzureKeyCredential(AzureConfig.SEARCH_ADMIN_KEY)
        self.client = SearchClient(
            endpoint=AzureConfig.SEARCH_ENDPOINT,
            index_name=AzureConfig.SEARCH_INDEX_NAME,
            credential=credential,
        )

    async def retrieve_documents(
        self, query_embedding: List[float], top_k: int = None, query_text: str = None
    ) -> RetrievalResult:
        """
        Retrieve relevant documents from vector DB using keyword search (hybrid).
        For now using keyword search as primary method.

        Args:
            query_embedding: Query embedding vector (for future vector search)
            top_k: Number of documents to retrieve (default from config)
            query_text: Original query text for search

        Returns:
            RetrievalResult with retrieved documents
        """
        if top_k is None:
            top_k = AzureConfig.TOP_K_DOCUMENTS

        try:
            start_time = time.time()

            # Use keyword search for now (hybrid approach)
            # Vector search will be implemented once API is properly configured
            if not query_text:
                query_text = "*"

            results = list(self.client.search(
                search_text=query_text,
                top=top_k,
            ))

            documents = []
            for result in results:
                doc = RetrievedDocument(
                    doc_id=result.get("id", ""),
                    title=result.get("title", ""),
                    content=result.get("content", ""),
                    source=result.get("source", ""),
                    relevance_score=result.get("@search.score", 0.0),
                )
                documents.append(doc)

            elapsed_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"Retrieved {len(documents)} documents in {elapsed_ms}ms (top_k={top_k})"
            )

            return RetrievalResult(
                documents=documents,
                retrieval_time_ms=elapsed_ms,
                total_docs_searched=len(documents),
            )

        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}", exc_info=True)
            # Return empty result instead of failing
            return RetrievalResult(
                documents=[], retrieval_time_ms=0, total_docs_searched=0
            )

    def filter_by_confidence(
        self, documents: List[RetrievedDocument], threshold: float = None
    ) -> List[RetrievedDocument]:
        """
        Filter documents by relevance score.

        Args:
            documents: List of retrieved documents
            threshold: Minimum relevance score (default from config)

        Returns:
            Filtered list of documents
        """
        if threshold is None:
            threshold = AzureConfig.RELEVANCE_THRESHOLD

        filtered = [d for d in documents if d.relevance_score >= threshold]
        logger.debug(
            f"Filtered {len(documents)} docs to {len(filtered)} (threshold={threshold})"
        )
        return filtered

    def format_for_llm(self, documents: List[RetrievedDocument]) -> str:
        """
        Format retrieved documents for LLM context.

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted string for LLM prompt
        """
        if not documents:
            return "No relevant documents found."

        formatted = []
        for i, doc in enumerate(documents, 1):
            formatted.append(f"**Document {i}: {doc.title}**")
            formatted.append(f"Source: {doc.source}")
            formatted.append(f"Relevance: {doc.relevance_score:.2f}")
            formatted.append(f"\n{doc.content}\n")

        return "\n".join(formatted)
