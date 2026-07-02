"""
Simple step-by-step ingestion test
"""
import asyncio
import logging
from config import AzureConfig
from embeddings import EmbeddingClient
from chunking import TextChunker
from document_loader import DocumentLoader
from index_manager import IndexManager
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import uuid
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PASS = "[PASS]"
FAIL = "[FAIL]"


async def test_config():
    """Test 1: Verify credentials"""
    print("\n" + "="*60)
    print("TEST 1: AZURE CREDENTIALS")
    print("="*60)
    try:
        AzureConfig.validate()
        print(PASS + " Config validated!")
        print(f"  OpenAI Endpoint: {AzureConfig.OPENAI_ENDPOINT}")
        print(f"  Search Endpoint: {AzureConfig.SEARCH_ENDPOINT}")
        return True
    except Exception as e:
        print(FAIL + f" {str(e)}")
        return False


async def test_embeddings():
    """Test 2: Test embeddings"""
    print("\n" + "="*60)
    print("TEST 2: EMBEDDINGS")
    print("="*60)
    try:
        embedder = EmbeddingClient()
        emb = await embedder.embed_query("How do I submit a data request?")
        print(PASS + f" Embedding generated ({len(emb)} dims)")
        return True
    except Exception as e:
        print(FAIL + f" {str(e)}")
        return False


async def test_loading():
    """Test 3: Load documents"""
    print("\n" + "="*60)
    print("TEST 3: DOCUMENT LOADING")
    print("="*60)
    try:
        loader = DocumentLoader()
        docs = loader.load_sample_documents()
        print(PASS + f" Loaded {len(docs)} sample document(s)")
        for i, doc in enumerate(docs, 1):
            print(f"    {i}. {doc['source']} ({len(doc['content'])} chars)")
        return True
    except Exception as e:
        print(FAIL + f" {str(e)}")
        return False


async def test_chunking():
    """Test 4: Chunk documents"""
    print("\n" + "="*60)
    print("TEST 4: CHUNKING")
    print("="*60)
    try:
        loader = DocumentLoader()
        docs = loader.load_sample_documents()
        chunker = TextChunker(chunk_size=1000, overlap=200)

        all_chunks = []
        for doc in docs:
            chunks = chunker.chunk_document(doc)
            all_chunks.extend(chunks)

        print(PASS + f" Created {len(all_chunks)} chunk(s) from {len(docs)} document(s)")
        return True
    except Exception as e:
        print(FAIL + f" {str(e)}")
        return False


async def test_index():
    """Test 5: Create index"""
    print("\n" + "="*60)
    print("TEST 5: INDEX CREATION")
    print("="*60)
    try:
        mgr = IndexManager()
        mgr.create_index()
        exists = mgr.index_exists()
        print(PASS + f" Index '{AzureConfig.SEARCH_INDEX_NAME}' exists: {exists}")
        return True
    except Exception as e:
        print(FAIL + f" {str(e)}")
        return False


async def test_full_ingest():
    """Test 6: Full ingestion"""
    print("\n" + "="*60)
    print("TEST 6: FULL INGESTION (ONE DOCUMENT)")
    print("="*60)
    try:
        # Load
        loader = DocumentLoader()
        docs = loader.load_sample_documents()
        doc = docs[0]
        print("  Loading: " + doc['source'])

        # Chunk
        chunker = TextChunker(chunk_size=1000, overlap=200)
        chunks = chunker.chunk_document(doc)
        print(f"  Chunking: {len(chunks)} chunk(s)")

        # Embed
        embedder = EmbeddingClient()
        embeddings_list = []
        for chunk in chunks:
            emb = await embedder.embed_query(chunk.text)
            embeddings_list.append(emb)
        print(f"  Embedding: {len(embeddings_list)} embedding(s)")

        # Prepare
        docs_to_index = []
        for chunk, emb in zip(chunks, embeddings_list):
            docs_to_index.append({
                "id": str(uuid.uuid4()),
                "title": f"{chunk.source} - Part {chunk.chunk_index + 1}",
                "content": chunk.text,
                "source": chunk.source,
                "source_url": chunk.source_url or chunk.source,
                "chunk_index": chunk.chunk_index,
                "embedding": emb,
                "metadata": json.dumps(chunk.metadata or {}),
            })

        # Index
        credential = AzureKeyCredential(AzureConfig.SEARCH_ADMIN_KEY)
        client = SearchClient(
            endpoint=AzureConfig.SEARCH_ENDPOINT,
            index_name=AzureConfig.SEARCH_INDEX_NAME,
            credential=credential,
        )
        result = client.upload_documents(docs_to_index)
        successful = sum(1 for r in result if r.succeeded)

        print(f"  Indexing: {successful}/{len(docs_to_index)} document(s) indexed")
        print(PASS + " Full ingestion successful!")
        return successful > 0

    except Exception as e:
        print(FAIL + f" {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_verify():
    """Test 7: Verify documents in index"""
    print("\n" + "="*60)
    print("TEST 7: VERIFICATION - CHECK INDEX CONTENTS")
    print("="*60)
    try:
        credential = AzureKeyCredential(AzureConfig.SEARCH_ADMIN_KEY)
        client = SearchClient(
            endpoint=AzureConfig.SEARCH_ENDPOINT,
            index_name=AzureConfig.SEARCH_INDEX_NAME,
            credential=credential,
        )
        results = list(client.search(search_text='*', select=['id', 'title', 'source']))
        print(PASS + f" Found {len(results)} document(s) in index")
        for i, doc in enumerate(results[:5], 1):
            print(f"    {i}. {doc['title']} (source: {doc['source']})")
        return len(results) > 0
    except Exception as e:
        print(FAIL + f" {str(e)}")
        return False


async def main():
    print("\n")
    print("=" * 60)
    print("VIVLI RAG INGESTION - STEP-BY-STEP TEST")
    print("=" * 60)

    results = {}
    results['1. Config'] = await test_config()
    results['2. Embeddings'] = await test_embeddings()
    results['3. Loading'] = await test_loading()
    results['4. Chunking'] = await test_chunking()
    results['5. Index'] = await test_index()
    results['6. Full Ingest'] = await test_full_ingest()
    results['7. Verify'] = await test_verify()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test}")

    all_pass = all(results.values())
    print("\n" + "=" * 60)
    if all_pass:
        print("SUCCESS! All tests passed. Ingestion is working properly.")
        print("Your credentials are correct and ready to use.")
    else:
        print("FAILURE! Some tests failed. Check above for details.")
    print("=" * 60 + "\n")

    return all_pass


if __name__ == "__main__":
    asyncio.run(main())
