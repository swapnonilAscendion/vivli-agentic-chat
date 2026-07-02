# Ingestion Pipeline - Detailed Walkthrough

This guide explains how the ingestion script works now, with all the improvements for handling multiple documents and avoiding API rate limits.

---

## 📊 High-Level Flow

```
Start
  ↓
Load Documents (from resources/organized-data)
  ↓
Chunk Documents (1000 chars per chunk, 200 char overlap)
  ↓
Generate Embeddings (with RATE LIMITING & BATCHING)
  ↓
Prepare for Indexing (add metadata, IDs)
  ↓
Upload to Azure AI Search (in batches of 10)
  ↓
Success ✓
```

---

## 🔄 Step-by-Step Explanation

### Step 1: Initialize Pipeline with Rate Limiting

```python
pipeline = IngestionPipeline(
    embedding_batch_size=10,      # chunks per batch
    batch_delay_seconds=1.0       # delay between batches
)
```

**What happens:**
- Creates embedder, chunker, and search client
- Sets up rate limiting parameters
- Default: 10 chunks per batch, 1 second delay

---

### Step 2: Load Documents

```python
logger.info("Step 1: Loading documents...")
documents = self.loader.load_from_organized_data()
```

**What it does:**
- Scans `../resources/organized-data/` recursively
- Loads all supported file formats:
  - `.md` (Markdown)
  - `.txt` (Text)
  - `.pdf` (PDF)
  - `.docx` (Word)
  - `.json` (JSON)
  - `.csv` (CSV)
  - `.xlsx` (Excel)

**Example output:**
```
Step 1: Loading documents...
Loading markdown files...
Loading PDF files...
Loading text files...
Loading DOCX files...
Loading JSON files...
Loading CSV files...
Loading Excel files...
Total documents loaded: 10
```

---

### Step 3: Chunk Documents

```python
logger.info("Step 2: Chunking documents...")
all_chunks = []
for doc in documents:
    chunks = self.chunker.chunk_document(doc)
    all_chunks.extend(chunks)
```

**What it does:**
- Splits each document into chunks
- **Chunk size:** 1000 characters
- **Overlap:** 200 characters (preserves context)
- **Purpose:** Makes documents small enough for good vector search

**Example:**
```
Document: "How to Submit a Data Request..."
Length: 2500 chars

Results in 3 chunks:
  Chunk 1: chars 0-1000
  Chunk 2: chars 800-1800 (200 char overlap)
  Chunk 3: chars 1600-2500 (200 char overlap)
```

**Output:**
```
Step 2: Chunking documents...
Created 45 chunks
```

---

### Step 4: Embed Chunks (WITH RATE LIMITING)

This is the most important step with all the rate limiting logic.

```python
logger.info("Step 3: Embedding chunks...")
documents_to_index = await self._prepare_documents_for_indexing(all_chunks)
```

**What happens:**

#### 4a. Calculate Batches
```python
total_chunks = len(chunks)  # e.g., 45
embedding_batch_size = 10   # from config
total_batches = (45 + 10 - 1) // 10  # = 5 batches
```

#### 4b. Show Time Estimate
```python
estimated_time = total_batches * batch_delay_seconds  # 5 * 1.0 = 5 seconds
logger.info(f"Processing 45 chunks in 5 batches")
logger.info(f"Batch size: 10 chunks/batch")
logger.info(f"Delay between batches: 1.0s")
logger.info(f"Estimated time: ~5 seconds (~0.1 minutes)")
```

**Output:**
```
Step 3: Embedding chunks...
Processing 45 chunks in 5 batches
Batch size: 10 chunks/batch
Delay between batches: 1.0s
Estimated time: ~5 seconds (~0.1 minutes)
```

#### 4c. Process in Batches with Delays

```python
for batch_num in range(0, 45, 10):  # batch_num = 0, 10, 20, 30, 40
    batch_chunks = chunks[batch_num : batch_num + 10]
    
    # Process each chunk in batch
    for chunk in batch_chunks:
        embedding = await embedder.embed_query(chunk.text)
        # Create document for indexing
        doc = {
            "id": uuid.uuid4(),
            "title": f"{chunk.source} - Part {chunk.chunk_index + 1}",
            "content": chunk.text,
            "source": chunk.source,
            "embedding": embedding,  # 3072-dimensional vector
            "metadata": json.dumps(chunk.metadata)
        }
        documents.append(doc)
    
    # Wait before next batch (except after last batch)
    if batch_end < total_chunks:
        await asyncio.sleep(1.0)  # Wait 1 second
        logger.info(f"Waiting 1.0s before next batch...")
```

**Why the delay?**
- Azure OpenAI has rate limits (tokens/minute)
- Delay prevents hitting 429 "Too Many Requests" error
- 1 second delay is safe for most cases

**Example Output:**
```
Batch 1/5: Processing chunks 1-10
  Embedded chunk 1/45
  Embedded chunk 2/45
  ...
  Embedded chunk 10/45
Waiting 1.0s before next batch...

Batch 2/5: Processing chunks 11-20
  Embedded chunk 11/45
  ...
```

**What the embedding vector looks like:**
```python
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "sample - Part 1",
    "content": "How to Submit a Data Request...",
    "source": "sample",
    "source_url": "sample:data-request-guide",
    "chunk_index": 0,
    "embedding": [0.0234, -0.0156, 0.0891, ..., 0.0045],  # 3072 numbers
    "metadata": "{\"title\": \"Data Request Submission Guide\"}"
}
```

**Output:**
```
Successfully embedded 45/45 chunks
```

---

### Step 5: Index Documents

```python
logger.info("Step 4: Indexing documents...")
return await self._index_documents(documents_to_index)
```

**What it does:**
- Uploads documents to Azure AI Search in batches
- **Batch size for indexing:** 10 documents
- **No delay needed** between index batches (different API)

**Process:**
```python
batch_size = 10
for i in range(0, len(documents), 10):  # 0, 10, 20, 30, 40
    batch = documents[i : i + batch_size]
    result = search_client.upload_documents(batch)
    successful = sum(1 for r in result if r.succeeded)
    logger.info(f"Indexed batch {i // batch_size + 1}: {successful} docs")
```

**Output:**
```
Step 4: Indexing documents...
Indexed batch 1: 10 docs
Indexed batch 2: 10 docs
Indexed batch 3: 10 docs
Indexed batch 4: 10 docs
Indexed batch 5: 5 docs
Total documents indexed: 45/45
```

---

## 🚀 Complete Execution Example

```bash
$ python ingestion_pipeline.py --batch-size 10 --batch-delay 1.0
```

**Output:**
```
============================================================
VIVLI RAG DOCUMENT INGESTION PIPELINE
============================================================

Step 1: Loading documents...
Loading markdown files...
Loading PDF files...
Loading text files...
Loading DOCX files...
Loading JSON files...
Loading CSV files...
Loading Excel files...
Loaded 10 documents

Step 2: Chunking documents...
Created 45 chunks

Step 3: Embedding chunks...
Processing 45 chunks in 5 batches
Batch size: 10 chunks/batch
Delay between batches: 1.0s
Estimated time: ~5 seconds (~0.1 minutes)

Batch 1/5: Processing chunks 1-10
  Embedded chunk 1/45
  Embedded chunk 2/45
  ...
  Embedded chunk 10/45
Waiting 1.0s before next batch...

Batch 2/5: Processing chunks 11-20
  Embedded chunk 11/45
  ...
Successfully embedded 45/45 chunks

Step 4: Indexing documents...
Indexed batch 1: 10 docs
Indexed batch 2: 10 docs
Indexed batch 3: 10 docs
Indexed batch 4: 10 docs
Indexed batch 5: 5 docs
Total documents indexed: 45/45

============================================================
INGESTION COMPLETE!
============================================================
```

---

## ⚙️ Configuration Parameters

### From Command Line

```bash
# Default (10 chunks per batch, 1 second delay)
python ingestion_pipeline.py

# Faster (20 chunks per batch, 0.5 second delay)
python ingestion_pipeline.py --batch-size 20 --batch-delay 0.5

# Slower/Safer (5 chunks per batch, 2 second delay)
python ingestion_pipeline.py --batch-size 5 --batch-delay 2

# Sample data (for testing)
python ingestion_pipeline.py --sample
```

### From Code

```python
from ingestion_pipeline import IngestionPipeline
import asyncio

# Custom configuration
pipeline = IngestionPipeline(
    embedding_batch_size=15,
    batch_delay_seconds=1.5
)

success = asyncio.run(pipeline.run())
```

---

## 📈 Time Estimation Formula

```
Total Time = (Number of Chunks / Batch Size) × Delay Between Batches
```

**Examples:**

| Chunks | Batch Size | Delay | Total Time |
|--------|-----------|-------|------------|
| 100    | 10        | 1.0s  | ~10 sec    |
| 100    | 20        | 0.5s  | ~2.5 sec   |
| 500    | 10        | 1.0s  | ~50 sec    |
| 500    | 20        | 1.0s  | ~25 sec    |
| 1000   | 10        | 2.0s  | ~200 sec (~3.3 min) |

---

## 🔍 What Gets Indexed

For each chunk, the system creates a document like this:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Data Request Submission Guide - Part 1",
  "content": "How to Submit a Data Request\n\nA data request is your formal application...",
  "source": "sample",
  "source_url": "sample:data-request-guide",
  "chunk_index": 0,
  "embedding": [0.0234, -0.0156, 0.0891, ..., 0.0045],  // 3072 dimensions
  "metadata": "{\"title\": \"Data Request Submission Guide\", \"category\": \"FAQ\"}"
}
```

**Searchable fields:**
- `title` - Document title
- `content` - The actual text (searchable)
- `embedding` - Vector for semantic search

**Filterable fields:**
- `source` - Where it came from (pdf, sample, text, etc.)
- `chunk_index` - Which chunk of the original document

---

## 💾 How Documents Are Retrieved Later

When a user asks "How do I submit a data request?":

1. **Embedding** - Generate embedding for query
2. **Keyword Search** - Find documents matching keywords
3. **Score** - Documents get relevance scores
4. **Filter** - Keep documents with score > 0.3
5. **LLM** - Use top documents as context

**Example retrieval:**
```
Query: "How do I submit a data request?"
↓
Retrieved 3 documents:
  1. Score 0.95 - "Data Request Submission Guide - Part 1"
  2. Score 0.63 - "Form Check Process"
  3. Score 0.38 - "Data Review Process"
↓
After filtering (threshold 0.3): 3 documents pass
↓
LLM generates response using these documents
```

---

## 🛠️ Troubleshooting

### Getting 429 Errors?
**Solution:** Increase batch delay or reduce batch size
```bash
python ingestion_pipeline.py --batch-size 5 --batch-delay 3
```

### Too Slow?
**Solution:** Increase batch size or reduce delay
```bash
python ingestion_pipeline.py --batch-size 25 --batch-delay 0.5
```

### Documents Not Found?
**Check:**
1. Files in `../resources/organized-data/`?
2. File extensions supported (`.md`, `.txt`, `.pdf`, etc.)?
3. Run `python ingestion_pipeline.py --sample` to test

### Embedding Failures?
**Check:**
1. Azure OpenAI credentials in `.env`?
2. Internet connection?
3. Rate limit not exceeded?

---

## 📝 Key Components Involved

| Component | Purpose |
|-----------|---------|
| `DocumentLoader` | Loads files from organized-data |
| `TextChunker` | Splits docs into 1000-char chunks |
| `EmbeddingClient` | Generates 3072-dim vectors |
| `IngestionPipeline` | Orchestrates the entire flow with rate limiting |
| `SearchClient` | Uploads to Azure AI Search |

---

## ✅ After Ingestion

Once documents are indexed, they're searchable via the chat endpoint:

```bash
# Start the server
python main.py

# User can ask questions
# GET http://localhost:8000/chat?query=How+do+I+submit+a+data+request
```

The indexed documents are automatically retrieved and used to answer questions!

---

## 🎯 Key Takeaway

The ingestion pipeline is now **production-ready** with:
- ✅ Automatic rate limiting (no more 429 errors)
- ✅ Support for 7 file formats
- ✅ Progress tracking with time estimation
- ✅ Configurable batch parameters
- ✅ Robust error handling
- ✅ Efficient semantic chunking
