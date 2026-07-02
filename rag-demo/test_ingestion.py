"""
Step-by-step ingestion test - test each component independently
"""
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import asyncio
import logging
from config import AzureConfig
from embeddings import EmbeddingClient
from chunking import TextChunker
from document_loader import DocumentLoader
from index_manager import IndexManager
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_step_1_config():
    """Test 1: Verify Azure credentials are correct"""
    print("\n" + "="*60)
    print("STEP 1: TESTING AZURE CREDENTIALS")
    print("="*60)

    try:
        AzureConfig.validate()
        print("[OK] Config validated successfully!")
        print(f"  - OpenAI Endpoint: {AzureConfig.OPENAI_ENDPOINT}")
        print(f"  - Search Endpoint: {AzureConfig.SEARCH_ENDPOINT}")
        print(f"  - Index Name: {AzureConfig.SEARCH_INDEX_NAME}")
        return True
    except Exception as e:
        print(f"✗ Config validation failed: {str(e)}")
        return False


async def test_step_2_embeddings():
    """Test 2: Test embedding generation"""
    print("\n" + "="*60)
    print("STEP 2: TESTING EMBEDDINGS")
    print("="*60)

    try:
        embedder = EmbeddingClient()
        test_text = "How do I submit a data request?"

        print(f"Testing embedding for: '{test_text}'")
        embedding = await embedder.embed_query(test_text)

        print(f"✓ Embedding generated successfully!")
        print(f"  - Embedding length: {len(embedding)} dimensions")
        print(f"  - Sample values: {embedding[:5]}...")
        return True
    except Exception as e:
        print(f"✗ Embedding failed: {str(e)}")
        return False


async def test_step_3_document_loading():
    """Test 3: Load a sample document"""
    print("\n" + "="*60)
    print("STEP 3: TESTING DOCUMENT LOADING")
    print("="*60)

    try:
        loader = DocumentLoader()

        # Load sample documents
        documents = loader.load_sample_documents()

        if not documents:
            print("✗ No documents loaded!")
            return False

        print(f"✓ Loaded {len(documents)} sample document(s)")

        # Show first document
        doc = documents[0]
        print(f"\nDocument 1:")
        print(f"  - Title: {doc.get('source', 'N/A')}")
        print(f"  - Content length: {len(doc.get('content', ''))} chars")
        print(f"  - Preview: {doc.get('content', '')[:100]}...")

        return True
    except Exception as e:
        print(f"✗ Document loading failed: {str(e)}")
        return False


async def test_step_4_chunking():
    """Test 4: Chunk a single document"""
    print("\n" + "="*60)
    print("STEP 4: TESTING CHUNKING")
    print("="*60)

    try:
        loader = DocumentLoader()
        documents = loader.load_sample_documents()

        if not documents:
            print("✗ No documents to chunk!")
            return False

        chunker = TextChunker(chunk_size=1000, overlap=200)
        doc = documents[0]

        chunks = chunker.chunk_document(doc)

        print(f"✓ Chunked document into {len(chunks)} chunk(s)")

        for i, chunk in enumerate(chunks):
            print(f"\nChunk {i+1}:")
            print(f"  - Size: {len(chunk.text)} chars")
            print(f"  - Preview: {chunk.text[:100]}...")

        return True
    except Exception as e:
        print(f"✗ Chunking failed: {str(e)}")
        return False


async def test_step_5_index_creation():
    """Test 5: Create/verify Azure Search index"""
    print("\n" + "="*60)
    print("STEP 5: TESTING INDEX CREATION")
    print("="*60)

    try:
        index_manager = IndexManager()

        # Create index
        result = index_manager.create_index()

        if result:
            print(f"✓ Index created/verified successfully!")
        else:
            print(f"⚠ Index already exists or creation failed")

        # Check if index exists
        exists = index_manager.index_exists()
        print(f"  - Index exists: {exists}")
        print(f"  - Index name: {AzureConfig.SEARCH_INDEX_NAME}")

        return True
    except Exception as e:
        print(f"✗ Index creation failed: {str(e)}")
        return False


async def test_step_6_full_ingestion():
    """Test 6: Full ingestion of ONE document"""
    print("\n" + "="*60)
    print("STEP 6: TESTING FULL INGESTION (ONE DOCUMENT)")
    print("="*60)

    try:
        # Load
        loader = DocumentLoader()
        documents = loader.load_sample_documents()
        doc = documents[0]
        print(f"✓ Loaded document: {doc['source']}")

        # Chunk
        chunker = TextChunker(chunk_size=1000, overlap=200)
        chunks = chunker.chunk_document(doc)
        print(f"✓ Created {len(chunks)} chunk(s)")

        # Embed
        embedder = EmbeddingClient()
        embeddings = []
        for i, chunk in enumerate(chunks):
            emb = await embedder.embed_query(chunk.text)
            embeddings.append(emb)
            print(f"✓ Embedded chunk {i+1}/{len(chunks)}")

        # Prepare for indexing
        import uuid
        import json

        documents_to_index = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            doc_dict = {
                "id": str(uuid.uuid4()),
                "title": f"{chunk.source} - Part {chunk.chunk_index + 1}",
                "content": chunk.text,
                "source": chunk.source,
                "source_url": chunk.source_url or chunk.source,
                "chunk_index": chunk.chunk_index,
                "embedding": emb,
                "metadata": json.dumps(chunk.metadata or {}),
            }
            documents_to_index.append(doc_dict)

        print(f"✓ Prepared {len(documents_to_index)} document(s) for indexing")

        # Index
        credential = AzureKeyCredential(AzureConfig.SEARCH_ADMIN_KEY)
        search_client = SearchClient(
            endpoint=AzureConfig.SEARCH_ENDPOINT,
            index_name=AzureConfig.SEARCH_INDEX_NAME,
            credential=credential,
        )

        result = search_client.upload_documents(documents_to_index)
        successful = sum(1 for r in result if r.succeeded)

        print(f"✓ Indexed {successful}/{len(documents_to_index)} document(s)")

        if successful > 0:
            print(f"\n✓ FULL INGESTION SUCCESSFUL!")
            return True
        else:
            print(f"✗ No documents were indexed")
            return False

    except Exception as e:
        print(f"✗ Full ingestion failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def verify_documents_in_index():
    """Verify documents are actually in the index"""
    print("\n" + "="*60)
    print("VERIFICATION: CHECKING INDEX CONTENTS")
    print("="*60)

    try:
        credential = AzureKeyCredential(AzureConfig.SEARCH_ADMIN_KEY)
        search_client = SearchClient(
            endpoint=AzureConfig.SEARCH_ENDPOINT,
            index_name=AzureConfig.SEARCH_INDEX_NAME,
            credential=credential,
        )

        # Search for all documents
        results = list(search_client.search(search_text='*', select=['id', 'title', 'source']))

        print(f"✓ Found {len(results)} document(s) in index")

        for i, doc in enumerate(results[:5]):
            print(f"  {i+1}. {doc['title']} (source: {doc['source']})")

        return len(results) > 0

    except Exception as e:
        print(f"✗ Verification failed: {str(e)}")
        return False


async def main():
    """Run all tests in sequence"""
    print("\n\n")
    print("=" * 60)
    print("VIVLI RAG INGESTION - STEP-BY-STEP TEST".center(60))
    print("=" * 60)

    results = {}

    # Run tests
    results['Config'] = await test_step_1_config()
    results['Embeddings'] = await test_step_2_embeddings()
    results['Document Loading'] = await test_step_3_document_loading()
    results['Chunking'] = await test_step_4_chunking()
    results['Index Creation'] = await test_step_5_index_creation()
    results['Full Ingestion'] = await test_step_6_full_ingestion()
    results['Index Verification'] = await verify_documents_in_index()

    # Summary
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED - INGESTION IS WORKING!")
        print("Your credentials are correct and ready to ingest documents.")
    else:
        print("✗ SOME TESTS FAILED - SEE ABOVE FOR DETAILS")
        print("Check the error messages above to identify the issue.")
    print("="*60 + "\n")

    return all_passed


if __name__ == "__main__":
    asyncio.run(main())
