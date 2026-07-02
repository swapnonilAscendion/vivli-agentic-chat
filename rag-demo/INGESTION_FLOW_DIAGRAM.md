# Ingestion Pipeline - Visual Flow Diagrams

## 1. Overall Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   INGESTION PIPELINE START                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Load Documents            │
        │  (from resources/)         │
        │  Supports:                 │
        │  - .md, .txt, .pdf         │
        │  - .docx, .json, .csv      │
        │  - .xlsx                   │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Chunk Documents           │
        │  Size: 1000 chars          │
        │  Overlap: 200 chars        │
        │  Result: 45 chunks ↓       │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────────┐
        │  EMBED WITH RATE LIMITING (Key Part!)   │
        │                                         │
        │  Total Chunks: 45                       │
        │  Batch Size: 10                         │
        │  Total Batches: 5                       │
        │  Delay: 1.0 second between batches     │
        │  Estimated Time: ~5 seconds             │
        │                                         │
        │  Process:                               │
        │  ├─ Batch 1: chunks 1-10 (WAIT 1s)     │
        │  ├─ Batch 2: chunks 11-20 (WAIT 1s)    │
        │  ├─ Batch 3: chunks 21-30 (WAIT 1s)    │
        │  ├─ Batch 4: chunks 31-40 (WAIT 1s)    │
        │  └─ Batch 5: chunks 41-45 (NO WAIT)    │
        │                                         │
        │  Each chunk becomes a 3072-dim vector   │
        └────────────┬─────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Prepare for Indexing      │
        │  Add to each chunk:        │
        │  - UUID ID                 │
        │  - Title                   │
        │  - Source metadata         │
        │  Result: 45 documents ↓    │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Index to Azure AI Search  │
        │  Batch Size: 10 docs       │
        │                            │
        │  ├─ Batch 1: 10 docs       │
        │  ├─ Batch 2: 10 docs       │
        │  ├─ Batch 3: 10 docs       │
        │  ├─ Batch 4: 10 docs       │
        │  └─ Batch 5: 5 docs        │
        │                            │
        │  Total Indexed: 45/45 ✓    │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   INGESTION COMPLETE! ✓    │
        │   Ready for searches       │
        └────────────────────────────┘
```

---

## 2. Rate Limiting Detail (The Key Innovation)

```
WITHOUT RATE LIMITING (Old way - causes 429 errors):
═══════════════════════════════════════════════════════════════

Chunk 1 ─────┐
Chunk 2 ─────┤
Chunk 3 ─────├──→ API (Too many requests at once!)
...          │    
Chunk 45 ────┘
             
             ✗ API Rate Limit Hit!
             HTTP 429: Too Many Requests


WITH RATE LIMITING (New way - no errors):
═══════════════════════════════════════════════════════════════

Batch 1 (Chunks 1-10)  ──→ API (Request 1)
                         [WAIT 1 second]
Batch 2 (Chunks 11-20) ──→ API (Request 2)
                         [WAIT 1 second]
Batch 3 (Chunks 21-30) ──→ API (Request 3)
                         [WAIT 1 second]
Batch 4 (Chunks 31-40) ──→ API (Request 4)
                         [WAIT 1 second]
Batch 5 (Chunks 41-45) ──→ API (Request 5)

             ✓ All requests processed successfully!
             No 429 errors!
```

---

## 3. Document Structure Timeline

```
Original Document (2500 chars):
────────────────────────────────────────────────────────────────
"How to Submit a Data Request

A data request is your formal application to access data
available on Vivli.

Steps to submit:
1. Create an account or log in
2. Click "New Data Request"
3. Fill in your research details
4. Upload required documents (CV, institution letter)
5. Submit for review

Timeline: Most requests are reviewed within 2 weeks.

Eligibility:
- Must be affiliated with a research institution
- Must have institutional approval
- Must agree to data use terms"
────────────────────────────────────────────────────────────────
                     │
                     │ CHUNKING (1000 chars, 200 overlap)
                     ▼
                     
Chunk 1 (0-1000 chars):
────────────────────────────────────────────────────────────────
"How to Submit a Data Request

A data request is your formal application to access data
available on Vivli.

Steps to submit:
1. Create an account or log in
2. Click "New Data Request"
3. Fill in your research details
4. Upload required documents (CV, institution letter)
5. Submit for review"
────────────────────────────────────────────────────────────────
                     │
        ┌────────────┴────────────┬──────────────┐
        │                         │              │
        ▼                         ▼              ▼
    EMBED              Embedding 1          Store with
    (3072-dim         [0.0234, ...]        metadata
     vector)                                

Chunk 2 (800-1800 chars):
────────────────────────────────────────────────────────────────
"Fill in your research details
4. Upload required documents (CV, institution letter)
5. Submit for review

Timeline: Most requests are reviewed within 2 weeks.

Eligibility:
- Must be affiliated with a research institution
- Must have institutional approval
- Must agree to data use terms"
────────────────────────────────────────────────────────────────
        │
        ▼
    EMBED + STORE
    
(Note: 200 char overlap preserves context between chunks)
```

---

## 4. Rate Limiting Timeline

```
Time (seconds)  Activity
──────────────  ───────────────────────────────────────────────
0:00            START
                Pipeline initialized
                45 chunks ready to embed

0:00-2:50       BATCH 1: Embedding chunks 1-10
                - Chunk 1 embedded → vector stored
                - Chunk 2 embedded → vector stored
                - ...
                - Chunk 10 embedded → vector stored
                ✓ 10 vectors generated

2:50-3:00       WAIT 1 second (rate limiting)
                💤 Sleeping to respect API rate limits

3:00-5:40       BATCH 2: Embedding chunks 11-20
                ✓ 10 vectors generated

5:40-6:40       WAIT 1 second

6:40-9:20       BATCH 3: Embedding chunks 21-30
                ✓ 10 vectors generated

9:20-10:20      WAIT 1 second

10:20-13:00     BATCH 4: Embedding chunks 31-40
                ✓ 10 vectors generated

13:00-14:00     WAIT 1 second

14:00-16:40     BATCH 5: Embedding chunks 41-45
                ✓ 5 vectors generated

16:40           ✓ ALL EMBEDDING COMPLETE (45/45)
                Total time: ~16 seconds

17:00           Indexing complete
                All 45 docs in Azure AI Search ✓
```

---

## 5. Embedding Process Detail

```
Input: "How do I submit a data request?"
       (32 characters)

       │
       ▼
    
┌─────────────────────────────────────────────┐
│  Azure OpenAI Embedding Service             │
│  Model: text-embedding-3-large              │
│  Endpoint: https://ascendion-resource...   │
│                                             │
│  Process:                                   │
│  1. Tokenize: [how, do, i, submit, ...]    │
│  2. Generate semantic representation        │
│  3. Return 3072-dimensional vector          │
└─────────────────────────────────────────────┘

       │
       ▼
       
Output: [0.0234, -0.0156, 0.0891, ..., 0.0045]
        (3072 numbers, each in range -1 to 1)
        
        This vector captures the meaning of the text
        and is used for semantic search!
```

---

## 6. Indexing Pipeline

```
45 Embedded Documents
        │
        ├─ Doc 1 (embedding: [0.023, -0.015, ...])
        ├─ Doc 2 (embedding: [0.045, 0.032, ...])
        ├─ Doc 3 (embedding: [0.011, -0.008, ...])
        └─ ... (42 more docs)
        
                │
                ▼
        
        BATCH UPLOAD TO AZURE AI SEARCH
        (Batch size: 10 docs)
        
        ┌──────────────────────────────┐
        │ Batch 1: Docs 1-10           │
        │ ✓ Indexed successfully       │
        └──────────────────────────────┘
        
        ┌──────────────────────────────┐
        │ Batch 2: Docs 11-20          │
        │ ✓ Indexed successfully       │
        └──────────────────────────────┘
        
        ┌──────────────────────────────┐
        │ Batch 3: Docs 21-30          │
        │ ✓ Indexed successfully       │
        └──────────────────────────────┘
        
        ┌──────────────────────────────┐
        │ Batch 4: Docs 31-40          │
        │ ✓ Indexed successfully       │
        └──────────────────────────────┘
        
        ┌──────────────────────────────┐
        │ Batch 5: Docs 41-45          │
        │ ✓ Indexed successfully       │
        └──────────────────────────────┘
        
                │
                ▼
        
        AZURE AI SEARCH INDEX
        ┌──────────────────────────────────┐
        │ vivli-knowledge-base             │
        │                                  │
        │ Total Documents: 45              │
        │ Searchable: YES ✓                │
        │ Vector Search: Enabled ✓         │
        │ Keyword Search: Enabled ✓        │
        └──────────────────────────────────┘
```

---

## 7. Document Retrieval (After Indexing)

```
USER ASKS: "How do I submit a data request?"
       │
       ▼
       
┌──────────────────────────────────────┐
│ 1. Generate Query Embedding          │
│    Input: "How do I submit..."       │
│    Output: [0.052, -0.031, ..., 0.019]  │
│            (3072 dimensions)         │
└──────────────────────────────────────┘
       │
       ▼
       
┌──────────────────────────────────────┐
│ 2. Search Azure AI Search            │
│    Keyword Search: "data request"    │
│    Find: documents matching keywords │
│                                      │
│    Results:                          │
│    ├─ Doc A: Score 0.95  ✓ PASS      │
│    ├─ Doc B: Score 0.63  ✓ PASS      │
│    ├─ Doc C: Score 0.38  ✓ PASS      │
│    └─ Doc D: Score 0.25  ✗ FAIL      │
│                                      │
│    (Threshold: 0.3)                  │
└──────────────────────────────────────┘
       │
       ▼
       
┌──────────────────────────────────────┐
│ 3. Filter by Relevance Score         │
│    Threshold: 0.3                    │
│                                      │
│    Documents passed filter: 3        │
│    ├─ Data Request Guide             │
│    ├─ Form Check Process             │
│    └─ Data Review Process            │
└──────────────────────────────────────┘
       │
       ▼
       
┌──────────────────────────────────────┐
│ 4. Send to LLM with Context          │
│                                      │
│    "Using these documents, answer    │
│    'How do I submit a data request?'"│
│                                      │
│    Context:                          │
│    [Doc A content]                   │
│    [Doc B content]                   │
│    [Doc C content]                   │
└──────────────────────────────────────┘
       │
       ▼
       
┌──────────────────────────────────────┐
│ 5. LLM Generates Answer              │
│                                      │
│    "To submit a data request:        │
│     1. Create an account             │
│     2. Click 'New Data Request'      │
│     3. Fill in research details      │
│     4. Upload documents              │
│     5. Submit for review"            │
└──────────────────────────────────────┘
       │
       ▼
       
RESPONSE RETURNED TO USER ✓
```

---

## 8. Configuration Options

```
COMMAND LINE USAGE:
═══════════════════════════════════════════════════════════════

Default (Conservative, Safe):
$ python ingestion_pipeline.py
  → Batch size: 10, Delay: 1.0s
  → Safest option, no 429 errors

Faster (Aggressive):
$ python ingestion_pipeline.py --batch-size 25 --batch-delay 0.2
  → Batch size: 25, Delay: 0.2s
  → Faster but higher error risk

Slower (Very Safe):
$ python ingestion_pipeline.py --batch-size 5 --batch-delay 3
  → Batch size: 5, Delay: 3s
  → Slowest but safest option

Sample Data (Testing):
$ python ingestion_pipeline.py --sample
  → Uses built-in sample documents
  → Good for testing without real files
```

---

## 9. Error Handling Flow

```
Document Processing
       │
       ├─ Success ──→ Add to batch
       │
       ├─ PDF extraction fails ──→ Log warning, continue
       │
       ├─ Embedding fails ──→ Log error, skip chunk, continue
       │
       ├─ Index upload fails ──→ Log error, continue to next batch
       │
       └─ Network error ──→ Retry or log & continue

Result: Robust pipeline that doesn't fail on individual errors
        Completes as much as possible
```

---

## Key Takeaways

1. **Rate Limiting** - Prevents 429 errors by adding delays between batches
2. **Chunking** - Splits large documents into searchable pieces
3. **Embedding** - Converts text to 3072-dim vectors for semantic search
4. **Batching** - Processes embeddings in groups of 10 (configurable)
5. **Indexing** - Stores vectors + metadata in Azure AI Search
6. **Retrieval** - Later uses keyword + vector search to find relevant docs

The system is designed to handle **many files** without hitting API rate limits!
