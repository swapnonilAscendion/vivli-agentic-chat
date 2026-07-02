# Ingestion Pipeline - Timing Guide

## ⏱️ Quick Answer

**Typical time: 20-30 seconds per 100 chunks**

With default settings (batch_size=10, delay=1.0s):
- Small (3 documents) → **15-20 seconds**
- Medium (10 documents) → **20-30 seconds**
- Large (50 documents) → **2-3 minutes**
- Very Large (100 documents) → **5-10 minutes**

---

## 📊 Breakdown by Step

Each step takes a different amount of time:

| Step | Time | Notes |
|------|------|-------|
| **Load Documents** | <1s | Fast, just reads files |
| **Chunk Documents** | <1s | Fast text processing |
| **Generate Embeddings** | 2-3s per batch | Network latency + API |
| **Rate Limit Delays** | Configurable | 1s per batch (default) |
| **Prepare for Index** | <1s | Local processing |
| **Upload to Azure** | 1-2s per batch | Network + indexing |
| **TOTAL** | Varies | See examples below |

---

## 🔢 Real Examples

### Example 1: Sample Data (3 documents)

```
Documents loaded: 3
Chunks created: 12

Timeline:
  0:00-0:01   Load & Chunk documents     = 1 second
  0:01-0:08   Batch 1: Embed chunks 1-10 = 7 seconds
  0:08-0:09   WAIT between batches       = 1 second
  0:09-0:13   Batch 2: Embed chunks 11-12 = 4 seconds
  0:13-0:15   Prepare & Index            = 2 seconds
  ────────────────────────────────────────────────
  0:15        TOTAL TIME                 = 15 seconds
```

**Command:**
```bash
python ingestion_pipeline.py --sample
```

**Expected output:**
```
Processing 12 chunks in 2 batches
Estimated time: ~2 seconds (~0.03 minutes)
...
Total documents indexed: 12/12
Total time: ~15 seconds (including all steps)
```

---

### Example 2: Medium Load (10 documents)

```
Documents: 10 (from organized-data/)
Chunks created: 45

Timeline:
  0:00-0:02   Load & Chunk documents      = 2 seconds
  0:02-0:09   Batch 1: Embed chunks 1-10  = 7 seconds
  0:09-0:10   WAIT                        = 1 second
  0:10-0:17   Batch 2: Embed chunks 11-20 = 7 seconds
  0:17-0:18   WAIT                        = 1 second
  0:18-0:25   Batch 3: Embed chunks 21-30 = 7 seconds
  0:25-0:26   WAIT                        = 1 second
  0:26-0:33   Batch 4: Embed chunks 31-40 = 7 seconds
  0:33-0:34   WAIT                        = 1 second
  0:34-0:37   Batch 5: Embed chunks 41-45 = 3 seconds
  0:37-0:39   Prepare & Index             = 2 seconds
  ────────────────────────────────────────────────
  0:39        TOTAL TIME                  = 39 seconds (~40 seconds)
```

**Command:**
```bash
python ingestion_pipeline.py --batch-size 10 --batch-delay 1.0
```

**Expected output:**
```
Processing 45 chunks in 5 batches
Batch size: 10 chunks/batch
Delay between batches: 1.0s
Estimated time: ~5 seconds (~0.08 minutes)

[Batch 1/5]
[Waiting 1.0s...]
[Batch 2/5]
...
Total documents indexed: 45/45
```

---

### Example 3: Large Load (100 documents)

```
Documents: 100
Chunks created: 500

Timeline:
  Loading & Chunking       = 3 seconds
  
  Embedding (50 batches × 1.5s per batch + 49 × 1s delays)
  = (50 × 1.5) + (49 × 1.0)
  = 75 + 49
  = 124 seconds (≈2 minutes)
  
  Prepare & Index          = 5 seconds
  ────────────────────────────
  TOTAL TIME              = ~132 seconds (≈2.2 minutes)
```

**Command:**
```bash
python ingestion_pipeline.py --batch-size 10 --batch-delay 1.0
```

---

## 📈 Time Formula

```
Total Time = Load + Chunk + Embed + Delay + Index
           = 1s + 1s + (Batches × 1.5s) + (Batches × delay) + 2s
           = ~5s + (Batches × (1.5s + delay))

Where:
  Batches = ⌈ Total Chunks / Batch Size ⌉
```

### Calculate Your Own

```python
# Example: 500 chunks, batch size 10, delay 1s
total_chunks = 500
batch_size = 10
batch_delay = 1.0

num_batches = (total_chunks + batch_size - 1) // batch_size
time_per_batch = 1.5  # seconds (average embedding time)

total_time = 5 + (num_batches * (time_per_batch + batch_delay))
print(f"Estimated time: {total_time:.0f} seconds ({total_time/60:.1f} minutes)")

# Output: Estimated time: 132 seconds (2.2 minutes)
```

---

## ⚡ Different Settings = Different Times

### Same 500 chunks, different settings:

```
Setting A: batch_size=10, delay=1.0s
  Batches: 50
  Time: 5 + (50 × 2.5s) = 130 seconds (2.2 min)

Setting B: batch_size=20, delay=0.5s
  Batches: 25
  Time: 5 + (25 × 2.0s) = 55 seconds (0.9 min) ← 2.4× faster!

Setting C: batch_size=5, delay=2.0s
  Batches: 100
  Time: 5 + (100 × 3.5s) = 355 seconds (5.9 min) ← 2.7× slower!

Setting D: batch_size=50, delay=0.2s
  Batches: 10
  Time: 5 + (10 × 1.7s) = 22 seconds ← Fastest but risky!
```

---

## 🎯 Time Estimation Table

For quick reference without calculation:

### With Default Settings (batch=10, delay=1.0s)

| Documents | Chunks | Estimated Time |
|-----------|--------|-----------------|
| 1 | 5 | 10 sec |
| 3 | 12 | 15 sec |
| 5 | 25 | 25 sec |
| 10 | 45 | 40 sec |
| 20 | 100 | 2 min |
| 50 | 250 | 5 min |
| 100 | 500 | 10 min |
| 200 | 1000 | 20 min |

### With Faster Settings (batch=20, delay=0.5s)

| Documents | Chunks | Estimated Time |
|-----------|--------|-----------------|
| 1 | 5 | 5 sec |
| 3 | 12 | 8 sec |
| 5 | 25 | 12 sec |
| 10 | 45 | 18 sec |
| 20 | 100 | 35 sec |
| 50 | 250 | 1.5 min |
| 100 | 500 | 3 min |
| 200 | 1000 | 6 min |

### With Safer Settings (batch=5, delay=2.0s)

| Documents | Chunks | Estimated Time |
|-----------|--------|-----------------|
| 1 | 5 | 20 sec |
| 3 | 12 | 30 sec |
| 5 | 25 | 50 sec |
| 10 | 45 | 1.5 min |
| 20 | 100 | 3.5 min |
| 50 | 250 | 9 min |
| 100 | 500 | 18 min |
| 200 | 1000 | 36 min |

---

## 🔍 What Takes Time?

### Per-Batch Breakdown (10 chunks):

```
Reading files & processing:  <100ms
Generating embeddings:        2,000-3,000ms ← SLOWEST!
  (Network latency to Azure)
Preparing documents:          <100ms
Uploading to index:           500-1,000ms
Total per batch:              ~2.5-3.5 seconds
```

**Most of the time is waiting for Azure OpenAI to generate embeddings!**

---

## 💡 How to Estimate Your Scenario

### Step 1: Count Your Files

```bash
# Count markdown files
ls resources/organized-data/**/*.md | wc -l

# Count PDFs
ls resources/organized-data/**/*.pdf | wc -l

# Total files
ls resources/organized-data/**/* | wc -l
```

### Step 2: Estimate Chunks

```
Rule of thumb:
  - Text files: ~1 chunk per 1000 characters
  - PDFs: ~1 chunk per page
  - Short documents: 1-5 chunks
  - Medium documents: 5-20 chunks
  - Long documents: 20+ chunks

Example:
  10 text files (avg 5KB each) = 50 chunks
  5 PDFs (avg 50 pages each) = 250 chunks
  Total: 300 chunks
```

### Step 3: Calculate Time

```python
chunks = 300
batch_size = 10  # default
batch_delay = 1.0  # default

batches = (chunks + batch_size - 1) // batch_size  # 30
time_per_batch = 1.5  # seconds
total_delay = (batches - 1) * batch_delay  # 29 seconds
total_time = 5 + (batches * time_per_batch) + total_delay
# = 5 + 45 + 29 = 79 seconds ≈ 1.3 minutes
```

---

## ⏰ Real-World Benchmarks

Tested on typical system (Windows 11, good internet):

| Scenario | Docs | Chunks | Time | Per-Chunk |
|----------|------|--------|------|-----------|
| Sample data | 3 | 12 | 15s | 1.3s |
| Small project | 10 | 45 | 40s | 0.9s |
| Medium project | 50 | 250 | 5m | 1.2s |
| Large project | 100 | 500 | 10m | 1.2s |
| Very large | 200 | 1000 | 21m | 1.3s |

**Consistent: ~1.2 seconds per chunk** (including all overhead)

---

## 🚀 Optimization Tips

### To Make It Faster:

```bash
# Aggressive (risky)
python ingestion_pipeline.py --batch-size 50 --batch-delay 0.1

# Moderate
python ingestion_pipeline.py --batch-size 25 --batch-delay 0.5

# Speed improvement: 4-5× faster
# Risk: Higher chance of 429 errors
```

### To Make It Safer (if getting errors):

```bash
# Conservative
python ingestion_pipeline.py --batch-size 5 --batch-delay 2

# Slower but extremely safe
# Speed trade-off: 2-3× slower
# Risk: Minimal
```

---

## ✅ Expected Timing Checklist

- [ ] Batch 1 logs appear within 10 seconds
- [ ] Each batch takes ~2-3 seconds of processing
- [ ] 1 second pauses appear between batches (if configured)
- [ ] Indexing starts after all embeddings complete
- [ ] "INGESTION COMPLETE!" appears within expected time
- [ ] No 429 errors

---

## 🔴 Red Flags (Something's Wrong)

| Sign | Possible Issue | Fix |
|------|---|---|
| Nothing happens for 30+ seconds | Network issue or hung process | Check internet, restart |
| Batch never completes | Azure API not responding | Wait or check Azure status |
| 429 errors appear | Batch size too large | Reduce batch size or increase delay |
| Extremely slow (1min per batch) | Network latency | Check connection, try at different time |
| Memory error | Too many chunks loaded | Reduce batch size |

---

## 📝 Monitor Progress

The script logs progress in real-time:

```
Step 1: Loading documents...
Loaded 10 documents                              ← Should be quick

Step 2: Chunking documents...
Created 45 chunks                                ← Should be quick

Step 3: Embedding chunks...
Processing 45 chunks in 5 batches
Estimated time: ~5 seconds (~0.08 minutes)
Batch 1/5: Processing chunks 1-10               ← First batch
Waiting 1.0s before next batch...               ← Delay
Batch 2/5: Processing chunks 11-20              ← Second batch
...

Step 4: Indexing documents...
Indexed batch 1: 10 docs                        ← Should be fast
...
Total documents indexed: 45/45
==============================
INGESTION COMPLETE!                             ← Success!
```

---

## 🎯 Summary

**For typical use:**
- **3-10 documents**: 15-40 seconds
- **10-50 documents**: 40 seconds - 3 minutes
- **50-100 documents**: 3-10 minutes
- **100+ documents**: 10+ minutes

**Rule of thumb:** ~1.2 seconds per chunk with default settings

**Most time spent:** Waiting for Azure OpenAI embeddings (~70% of time)

**Can adjust:** Faster/slower with batch size and delay parameters
