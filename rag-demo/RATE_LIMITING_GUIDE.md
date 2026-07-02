# Rate Limiting & 429 Error Prevention Guide

## What Changed?

The ingestion pipeline now includes **smart rate limiting** to prevent HTTP 429 (Too Many Requests) errors from Azure OpenAI.

### How It Works

Instead of embedding all chunks instantly, the pipeline:
1. Processes chunks in **configurable batches**
2. Adds **delays between batches** to respect API rate limits
3. Provides **time estimation** before starting

---

## Default Settings

```
Batch Size: 10 chunks per batch
Delay: 1.0 second between batches
```

This is **conservative and safe** for most cases.

---

## Estimated Processing Times

### Example: 100 chunks
- **Default (batch=10, delay=1s)**: ~10 batches × 1s = **~10 seconds**
- **Faster (batch=20, delay=0.5s)**: ~5 batches × 0.5s = **~2.5 seconds**
- **Slower (batch=5, delay=2s)**: ~20 batches × 2s = **~40 seconds**

### Example: 1,000 chunks
- **Default (batch=10, delay=1s)**: ~100 batches × 1s = **~100 seconds (~1.7 min)**
- **Faster (batch=50, delay=0.5s)**: ~20 batches × 0.5s = **~10 seconds**
- **Slower (batch=5, delay=2s)**: ~200 batches × 2s = **~400 seconds (~6.7 min)**

---

## How to Use

### Default (Recommended for first run)
```powershell
python ingestion_pipeline.py
```

Output will show:
```
Processing 100 chunks in 10 batches
Batch size: 10 chunks/batch
Delay between batches: 1.0s
Estimated time: ~10 seconds (~0.2 minutes)
```

### Faster (if you know your rate limits are high)
```powershell
python ingestion_pipeline.py --batch-size 20 --batch-delay 0.5
```

This runs **4x faster** but uses more API quota.

### Slower (if you're hitting 429 errors)
```powershell
python ingestion_pipeline.py --batch-size 5 --batch-delay 2
```

This is **safer** but takes longer.

### Sample data (for testing)
```powershell
python ingestion_pipeline.py --sample
```

---

## Understanding Your Rate Limits

Azure OpenAI has rate limits. For `text-embedding-3-large`:

| Metric | Typical Limit |
|--------|---------------|
| Requests/min | 30-100 per minute |
| Tokens/min | 240,000-1M tokens/minute |

**Formula**: `Tokens used = input_tokens + output_tokens`

For embeddings: `~tokens per request ≈ length(text) / 4`

### Example Calculation
- Batch size: 10 chunks
- Avg chunk size: 1000 characters ≈ 250 tokens
- Total tokens per batch: 10 × 250 = **2,500 tokens**
- Rate limit: 240,000 tokens/min = **4,000 tokens/sec**
- Time needed: 2,500 / 4,000 = **0.625 seconds**

So a **1 second delay is very safe**. You can often reduce it to **0.5 seconds** without hitting limits.

---

## Recommended Settings by Scenario

### Light Load (< 100 chunks)
```powershell
python ingestion_pipeline.py --batch-size 20 --batch-delay 0.5
```
**Time**: ~2.5 seconds | **Risk**: Low

### Medium Load (100-500 chunks)
```powershell
# Default is fine
python ingestion_pipeline.py
```
**Time**: ~50 seconds | **Risk**: Very Low

### Heavy Load (500+ chunks)
```powershell
python ingestion_pipeline.py --batch-size 15 --batch-delay 1.5
```
**Time**: ~2 minutes | **Risk**: Very Low

### Very Heavy Load (1000+ chunks)
```powershell
python ingestion_pipeline.py --batch-size 10 --batch-delay 2
```
**Time**: ~3.3 minutes | **Risk**: Minimal

---

## What to Do If You Still Get 429 Errors

1. **Increase delay:**
   ```powershell
   python ingestion_pipeline.py --batch-delay 3
   ```

2. **Reduce batch size:**
   ```powershell
   python ingestion_pipeline.py --batch-size 5
   ```

3. **Combine both:**
   ```powershell
   python ingestion_pipeline.py --batch-size 5 --batch-delay 3
   ```

4. **Check Azure limits:**
   - Go to Azure Portal
   - Find your OpenAI resource
   - Check "Quotas" for actual limits
   - Adjust accordingly

---

## Monitoring Progress

During ingestion, you'll see:

```
Processing 100 chunks in 10 batches
Batch size: 10 chunks/batch
Delay between batches: 1.0s
Estimated time: ~10 seconds (~0.2 minutes)

Batch 1/10: Processing chunks 1-10
  Embedded chunk 1/100
  Embedded chunk 2/100
  ...
  Embedded chunk 10/100
Waiting 1.0s before next batch...

Batch 2/10: Processing chunks 11-20
  ...
```

---

## Advanced: Custom Rate Limiting

You can also set rate limiting in code:

```python
from ingestion_pipeline import IngestionPipeline

# Create pipeline with custom settings
pipeline = IngestionPipeline(
    embedding_batch_size=15,      # chunks per batch
    batch_delay_seconds=1.2,      # delay in seconds
)

# Run it
import asyncio
success = asyncio.run(pipeline.run())
```

---

## Performance Tips

1. **Larger batch size = faster** (but higher error risk)
2. **Smaller delay = faster** (but higher error risk)
3. **Start conservative, increase if no errors**
4. **Monitor API usage in Azure Portal**

---

## Troubleshooting

### Q: Still getting 429 errors?
A: Try `--batch-delay 3` or `--batch-size 5`

### Q: Too slow?
A: Try `--batch-delay 0.5` or `--batch-size 25`

### Q: How long will 1000 chunks take?
A: Default settings: ~100 seconds (~1.7 minutes)

### Q: Can I run multiple ingestions in parallel?
A: **Not recommended** - this will trigger 429 errors
