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
        Retrieve relevant documents using keyword search.
        Note: Vector search can be implemented once the index is configured with vector fields.

        Args:
            query_embedding: Query embedding vector (3072 dims from text-embedding-3-large) - for future vector search
            top_k: Number of documents to retrieve (default from config)
            query_text: Original query text for search

        Returns:
            RetrievalResult with retrieved documents
        """
        if top_k is None:
            top_k = AzureConfig.TOP_K_DOCUMENTS

        try:
            start_time = time.time()

            # Try keyword search (Azure Search SDK doesn't support vector search yet with simple API)
            # Using hybrid approach: keyword search is primary method
            documents = []

            if query_text:
                try:
                    results = list(self.client.search(
                        search_text=query_text,
                        top=top_k,
                    ))

                    logger.debug(f"Keyword search returned {len(results)} results")

                    for result in results:
                        doc = RetrievedDocument(
                            doc_id=result.get("id", ""),
                            title=result.get("title", ""),
                            content=result.get("content", ""),
                            source=result.get("source", ""),
                            relevance_score=result.get("@search.score", 0.0),
                        )
                        documents.append(doc)
                except Exception as ke:
                    logger.warning(f"Keyword search also failed: {str(ke)}")

            elapsed_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"Retrieved {len(documents)} documents in {elapsed_ms}ms (keyword search)"
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

    def format_for_llm(self, documents: List[RetrievedDocument], max_tokens: int = 2000) -> str:
        """
        Format retrieved documents for LLM context (with size limits).

        Args:
            documents: List of retrieved documents
            max_tokens: Maximum characters to include (roughly 250 chars per token)

        Returns:
            Formatted string for LLM prompt (truncated to fit within token limit)
        """
        if not documents:
            return "No relevant documents found."

        formatted = []
        current_size = 0
        max_chars = max_tokens * 250  # Rough estimate: 250 chars per token

        for i, doc in enumerate(documents, 1):
            doc_header = f"**Document {i}: {doc.title}**\nSource: {doc.source}\nRelevance: {doc.relevance_score:.2f}\n"

            # Truncate content to reasonable size
            max_content_size = 2000  # Max 2000 chars per document
            content = doc.content[:max_content_size]
            if len(doc.content) > max_content_size:
                content += "\n[Content truncated...]"

            doc_text = f"{doc_header}{content}\n"

            # Stop adding documents if we exceed token limit
            if current_size + len(doc_text) > max_chars:
                formatted.append(f"\n[Note: Additional {len(documents) - i + 1} documents available but truncated for length]")
                break

            formatted.append(doc_text)
            current_size += len(doc_text)

        return "\n".join(formatted)
