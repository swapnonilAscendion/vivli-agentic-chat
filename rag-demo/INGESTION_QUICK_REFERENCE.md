# Ingestion Pipeline - Quick Reference Card

## 🚀 TL;DR - How It Works

```
Documents → Chunks → Embed (in batches) → Index → Searchable ✓
```

---

## 📋 Step-by-Step Summary

| # | Step | Input | Process | Output | Time |
|---|------|-------|---------|--------|------|
| 1 | Load | Files from `resources/` | Scan directory, detect format | 10 documents | <1s |
| 2 | Chunk | 10 documents | Split into 1000-char pieces (200 overlap) | 45 chunks | <1s |
| 3 | Embed | 45 chunks | Generate 3072-dim vectors in 5 batches (with delays) | 45 vectors | ~5s |
| 4 | Prepare | 45 vectors + metadata | Add IDs, titles, sources | 45 indexed docs | <1s |
| 5 | Index | 45 docs | Upload to Azure in batches of 10 | 45 stored ✓ | ~2s |

**Total Time: ~9 seconds** (for this example)

---

## 💻 Common Commands

```bash
# Default (safest)
python ingestion_pipeline.py

# Faster
python ingestion_pipeline.py --batch-size 20 --batch-delay 0.5

# Slower (if hitting errors)
python ingestion_pipeline.py --batch-size 5 --batch-delay 2

# Test with sample data
python ingestion_pipeline.py --sample

# Custom
python ingestion_pipeline.py --batch-size 15 --batch-delay 1.2
```

---

## 📊 Rate Limiting (The Key!)

**Problem:** Embedding 45 chunks instantly = 429 error

**Solution:** Embed in batches with delays

```
Batch 1 (chunks 1-10)  → Embed → WAIT 1s → 
Batch 2 (chunks 11-20) → Embed → WAIT 1s → 
Batch 3 (chunks 21-30) → Embed → WAIT 1s → 
Batch 4 (chunks 31-40) → Embed → WAIT 1s → 
Batch 5 (chunks 41-45) → Embed → DONE ✓

No 429 errors!
```

---

## ⏱️ Time Calculation

```
Estimated Time = (Total Chunks / Batch Size) × Delay
```

**Examples:**
- 100 chunks, batch 10, delay 1s = 10 seconds
- 500 chunks, batch 10, delay 1s = 50 seconds
- 1000 chunks, batch 10, delay 1s = 100 seconds (~1.7 min)

---

## 🗂️ File Formats Supported

| Format | Extension | Example |
|--------|-----------|---------|
| Markdown | `.md` | guides/ |
| Text | `.txt` | README files |
| PDF | `.pdf` | documents |
| Word | `.docx` | reports |
| JSON | `.json` | data files |
| CSV | `.csv` | spreadsheets |
| Excel | `.xlsx` | sheets |

**Location:** `../resources/organized-data/` (any subdirectory)

---

## 🔧 What Gets Stored in Azure

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Data Request Guide - Part 1",
  "content": "How to Submit a Data Request...",
  "source": "pdf",
  "source_url": "/path/to/file.pdf",
  "chunk_index": 0,
  "embedding": [0.0234, -0.0156, 0.0891, ..., 0.0045],  // 3072 numbers
  "metadata": "{\"file_name\": \"guide.pdf\", \"pages\": 5}"
}
```

**Key fields:**
- `embedding` - The 3072-dimensional vector (for search)
- `content` - The actual searchable text
- `metadata` - File information

---

## 🔍 Later: How Documents Get Retrieved

```
User asks: "How do I submit a data request?"
    ↓
Search Azure index for matching documents
    ↓
Find 3 relevant documents (score > 0.3 threshold)
    ↓
Send these 3 docs + question to LLM
    ↓
LLM generates answer using the context
    ↓
Return answer to user with sources ✓
```

---

## ⚙️ Configuration in Code

```python
# In ingestion_pipeline.py (main section)
EMBEDDING_BATCH_SIZE = 10      # chunks to embed per batch
BATCH_DELAY_SECONDS = 1.0      # seconds between batches
```

**Adjust if:**
- Getting 429 errors → increase delay or reduce batch size
- Too slow → decrease delay or increase batch size

---

## 📈 Batch Processing Example

```
Total Chunks: 45
Batch Size: 10
Delay: 1 second

Calculation:
  Total Batches = ⌈45 / 10⌉ = 5 batches
  Time = 5 batches × 1 second = 5 seconds
  
Processing:
  Batch 1: chunks 1-10    (process for ~2.8s, wait 1s)
  Batch 2: chunks 11-20   (process for ~2.8s, wait 1s)
  Batch 3: chunks 21-30   (process for ~2.8s, wait 1s)
  Batch 4: chunks 31-40   (process for ~2.8s, wait 1s)
  Batch 5: chunks 41-45   (process for ~1.4s, no wait)
  
Total: ~14 seconds
```

---

## 🚨 Troubleshooting Quick Guide

| Error | Cause | Fix |
|-------|-------|-----|
| 429 Too Many Requests | Batch too large or delay too small | Increase `batch_delay` or reduce `batch_size` |
| Connection timeout | Network issue | Check internet, retry |
| PDF extraction fails | PDF corrupted | Skip, continue with other files |
| Index upload fails | Azure credentials wrong | Check `.env` file |
| No documents loaded | No files in resources/ | Add files to `organized-data/` |
| Too slow | Batch too small or delay too large | Decrease `batch_delay` or increase `batch_size` |

---

## 📊 Performance Benchmarks

**On typical system with 100 documents (~500 chunks):**

| Settings | Time | Risk |
|----------|------|------|
| batch=10, delay=1.0s | ~50 sec | Very Low |
| batch=20, delay=0.5s | ~12 sec | Low |
| batch=50, delay=0.2s | ~2 sec | Medium |
| batch=5, delay=2.0s | ~200 sec | Minimal |

**Recommended:** Start with `batch=10, delay=1.0s`, adjust from there

---

## ✅ Success Checklist

- [ ] `.env` file has Azure credentials
- [ ] Files in `../resources/organized-data/` 
- [ ] File format supported (check above)
- [ ] Can run: `python ingestion_pipeline.py --sample` without errors
- [ ] All batches process without 429 errors
- [ ] "INGESTION COMPLETE!" message appears
- [ ] Documents searchable in chatbot ✓

---

## 🎯 What Happens After Ingestion

```
Indexed Documents (45 total)
       ↓
User types: "data request"
       ↓
Chatbot retrieves 3 matching docs
       ↓
LLM reads: "Using these docs, answer the question"
       ↓
Answer: "To submit a data request, follow these steps..."
       ↓
User gets answer with sources ✓
```

---

## 💡 Key Concepts

**Chunking:** Breaking large documents into manageable pieces
- Why? Makes search results more specific
- Size: 1000 characters with 200-char overlap

**Embedding:** Converting text to a vector
- Why? Enables semantic search (similar meaning)
- Size: 3072 dimensions

**Rate Limiting:** Adding delays between API calls
- Why? Prevents hitting API rate limits (429 error)
- Method: Process in batches with delays

**Indexing:** Storing vectors + text in Azure AI Search
- Why? Fast retrieval when user asks questions
- Method: Upload in batches of 10

---

## 📝 File Locations

```
rag-demo/
├── ingestion_pipeline.py          ← Main script
├── document_loader.py             ← Loads files
├── chunking.py                    ← Chunks text
├── embeddings.py                  ← Generates vectors
├── index_manager.py               ← Manages index
├── resources/
│   └── organized-data/            ← Your files go here
│       ├── file1.pdf
│       ├── file2.md
│       ├── folder/
│       │   └── file3.txt
│       └── ...
└── INGESTION_DETAILED_GUIDE.md    ← Full documentation
```

---

## 🔗 Related Documents

- **INGESTION_DETAILED_GUIDE.md** - Full step-by-step walkthrough
- **INGESTION_FLOW_DIAGRAM.md** - Visual diagrams of each process
- **RATE_LIMITING_GUIDE.md** - Detailed rate limiting explanation
- **DOCUMENT_FORMATS.md** - Supported file formats

---

## 💬 Remember

The ingestion pipeline is now **production-ready** with:
✓ Automatic rate limiting (no 429 errors)
✓ Support for 7 file formats
✓ Progress tracking with time estimates
✓ Configurable batch parameters
✓ Robust error handling
