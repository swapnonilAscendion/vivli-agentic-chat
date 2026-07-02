import asyncio
from embeddings import EmbeddingClient
from retrieval import Retrieval
from config import AzureConfig

async def test():
    embedder = EmbeddingClient()
    retrieval = Retrieval()

    for query in ["hi", "data request", "how to submit"]:
        print(f"\nTesting query: '{query}'")
        print("=" * 50)

        embedding = await embedder.embed_query(query)
        result = await retrieval.retrieve_documents(embedding, query_text=query, top_k=5)

        print(f"Documents retrieved: {len(result.documents)}")
        for i, doc in enumerate(result.documents, 1):
            status = "PASS" if doc.relevance_score >= AzureConfig.RELEVANCE_THRESHOLD else "FAIL"
            print(f"{i}. Score: {doc.relevance_score:.4f} [{status}] - {doc.title[:40]}")

        filtered = [d for d in result.documents if d.relevance_score >= AzureConfig.RELEVANCE_THRESHOLD]
        print(f"\nAfter filtering (threshold {AzureConfig.RELEVANCE_THRESHOLD}): {len(filtered)}/{len(result.documents)}")

asyncio.run(test())
