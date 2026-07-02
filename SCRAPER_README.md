# PDF Processor with Recursive Web Scraper

**Extract content from PDFs and automatically scrape all linked websites recursively**

---

## 🎯 What It Does

```
Input: PDF File
  ↓
1. Extract text & links from PDF
  ↓
2. Visit each link with Playwright (handles JavaScript)
  ↓
3. Extract text from each page
  ↓
4. Find new links on those pages
  ↓
5. Recursively visit new links (configurable depth)
  ↓
Output: Combined data (text + links + metadata)
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_scraper.txt
```

You also need Playwright browsers:
```bash
playwright install
```

### 2. Basic Usage

```python
import asyncio
from pdf_scraper import process_pdf_with_scraping

async def main():
    result = await process_pdf_with_scraping(
        pdf_path="sample.pdf",
        max_depth=2,
        rate_limit=2.0
    )
    
    # Access results
    print(f"URLs processed: {result['scraping_results']['total_urls_processed']}")
    print(f"Combined text length: {result['statistics']['total_text_chars']}")

asyncio.run(main())
```

### 3. Run from Command Line

```bash
python pdf_scraper.py sample.pdf
```

---

## 📋 Function Parameters

### Main Function: `process_pdf_with_scraping()`

```python
async def process_pdf_with_scraping(
    pdf_path: str,                    # Path to PDF file (required)
    max_depth: int = 3,               # How deep to follow links (0-5)
    rate_limit: float = 2.0,          # Seconds between requests
    timeout: int = 30,                # Request timeout in seconds
    save_output: bool = True,         # Save to JSON file
    output_dir: str = './scraper_output'  # Where to save results
) -> Dict:
```

### Parameters Explained

| Parameter | Default | Options | Notes |
|-----------|---------|---------|-------|
| `pdf_path` | Required | any PDF path | Must exist |
| `max_depth` | 3 | 0-5 | 0=PDF only, 3=recommended, >3=slow |
| `rate_limit` | 2.0 | 1.0-10.0 | Higher = slower but more respectful |
| `timeout` | 30 | 10-60 | Seconds to wait per page |
| `save_output` | True | True/False | Save JSON results file |
| `output_dir` | ./scraper_output | any path | Where to store results |

---

## 📊 Understanding Recursion Depth

```
depth=0:  Just extract from PDF
          Links found: 5
          Total URLs: 5
          
depth=1:  PDF links + Links found in those pages
          Links found: 5 + ~20 from pages = ~25
          Total URLs: ~25
          
depth=2:  Add links found in 2nd level pages
          Links found: 5 + ~20 + ~60 = ~85
          Total URLs: ~85
          
depth=3:  Add links found in 3rd level pages
          Links found: 5 + ~20 + ~60 + ~100 = ~185
          Total URLs: ~185
```

**Recommendation:**
- Development: `max_depth=1` (fast, see output quickly)
- Production: `max_depth=2` (balanced)
- Thorough: `max_depth=3` (slow, comprehensive)

---

## 💾 Output Structure

The function returns a dictionary with this structure:

```python
{
    'execution_id': 'abc123def456',          # Unique ID for this run
    'started_at': '2026-06-30T10:30:00',     # Start timestamp
    'completed_at': '2026-06-30T10:45:00',   # End timestamp
    'execution_time_seconds': 900,           # Total time
    
    'source_pdf': {
        'file_path': '/full/path/to/file.pdf',
        'file_name': 'file.pdf',
        'page_count': 10,
        'file_size_bytes': 1048576,
        'text_length': 50000,
        'links_extracted': 5
    },
    
    'scraping_results': {
        'total_urls_processed': 85,
        'successful_scrapes': 80,
        'failed_scrapes': 5,
        'duplicate_urls_skipped': 3,
        'success_rate': '94.1%'
    },
    
    'combined_data': {
        'all_text': 'Combined text from PDF + all scraped pages...',
        'all_text_length': 500000,
        'all_links': ['https://url1.com', 'https://url2.com', ...],
        'unique_links_count': 85,
        'link_graph': {
            'https://url1.com': ['https://url2.com', 'https://url3.com'],
            'https://url2.com': ['https://url4.com'],
            # ...
        }
    },
    
    'errors': {
        'failed_urls': [
            {'url': 'https://bad.com', 'error': 'Timeout'},
            # ...
        ],
        'total_failed': 5
    },
    
    'statistics': {
        'total_text_chars': 500000,
        'unique_urls_found': 85,
        'pages_with_errors': 5,
        'extraction_success_rate': '94.1%'
    }
}
```

---

## 🔍 Accessing Results

### Get Combined Text

```python
result = await process_pdf_with_scraping("sample.pdf")

# All extracted text
combined_text = result['combined_data']['all_text']

# Save to file
with open('combined_output.txt', 'w') as f:
    f.write(combined_text)
```

### Get All Links

```python
# List of unique URLs found
all_links = result['combined_data']['all_links']

# See where links come from
link_graph = result['combined_data']['link_graph']
for source_url, links in link_graph.items():
    print(f"{source_url} links to {len(links)} pages")
```

### Check Success

```python
success_rate = result['scraping_results']['success_rate']
total_urls = result['scraping_results']['total_urls_processed']
failed = result['errors']['total_failed']

print(f"Scraped {total_urls} URLs")
print(f"Success rate: {success_rate}")
print(f"Failed: {failed}")
```

### See Failed URLs

```python
for error in result['errors']['failed_urls']:
    print(f"Failed: {error['url']}")
    print(f"Reason: {error['error']}")
```

---

## 📈 Real-World Examples

### Example 1: Process One PDF

```python
import asyncio
from pdf_scraper import process_pdf_with_scraping

async def main():
    result = await process_pdf_with_scraping(
        pdf_path="docs/guide.pdf",
        max_depth=2
    )
    print(f"Processed {result['scraping_results']['total_urls_processed']} URLs")

asyncio.run(main())
```

### Example 2: Process Multiple PDFs

```python
import asyncio
from pathlib import Path
from pdf_scraper import process_pdf_with_scraping

async def process_all_pdfs():
    pdf_dir = Path("docs/guides")
    
    for pdf_file in pdf_dir.glob("*.pdf"):
        print(f"\nProcessing {pdf_file.name}...")
        
        result = await process_pdf_with_scraping(
            pdf_path=str(pdf_file),
            max_depth=2
        )
        
        print(f"  URLs: {result['scraping_results']['total_urls_processed']}")
        print(f"  Text: {result['statistics']['total_text_chars']:,} chars")

asyncio.run(process_all_pdfs())
```

### Example 3: Save Results in Different Formats

```python
import json
from pdf_scraper import process_pdf_with_scraping

result = await process_pdf_with_scraping("sample.pdf")

# Save as JSON
with open('result.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

# Save combined text as markdown
with open('combined_text.md', 'w') as f:
    f.write(f"# Extracted Content\n\n")
    f.write(result['combined_data']['all_text'])

# Save links as CSV
import csv
with open('links.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['URL'])
    for link in result['combined_data']['all_links']:
        writer.writerow([link])
```

### Example 4: Filter Results

```python
result = await process_pdf_with_scraping("sample.pdf")

# Get only successful scrapes
successful_scrapes = []
for depth_key, results in result['scraping_results'].items():
    for scrape in results:
        if scrape['status'] == 'success':
            successful_scrapes.append(scrape)

# Get only links from successful pages
good_links = []
for scrape in successful_scrapes:
    good_links.extend(scrape['links_found'])

print(f"Links from successful pages: {len(good_links)}")
```

---

## ⚙️ Configuration Tips

### Fast Processing (Development)
```python
result = await process_pdf_with_scraping(
    pdf_path="sample.pdf",
    max_depth=1,           # Shallow
    rate_limit=0.5,        # Fast (0.5 sec between requests)
    timeout=15             # Short timeout
)
```
**Time:** ~1-2 minutes for 5-10 URLs
**Cost:** Low on server resources

### Balanced Processing (Recommended)
```python
result = await process_pdf_with_scraping(
    pdf_path="sample.pdf",
    max_depth=2,           # Medium
    rate_limit=2.0,        # Respectful (2 sec between requests)
    timeout=30             # Normal timeout
)
```
**Time:** ~3-5 minutes for 50-100 URLs
**Cost:** Medium server resources

### Thorough Processing (Production)
```python
result = await process_pdf_with_scraping(
    pdf_path="sample.pdf",
    max_depth=3,           # Deep
    rate_limit=3.0,        # Very respectful (3 sec between requests)
    timeout=45             # Long timeout
)
```
**Time:** ~10-15 minutes for 150-200 URLs
**Cost:** High server resources

---

## 🐛 Troubleshooting

### "No links found in PDF"
- The PDF doesn't contain URLs
- URLs are images/scanned text (not searchable)
- Solution: Check PDF manually, use OCR if needed

### "Timeout errors"
- Website is slow or down
- Rate limit too aggressive
- Solution: Increase `timeout` and `rate_limit`

```python
result = await process_pdf_with_scraping(
    pdf_path="sample.pdf",
    rate_limit=5.0,    # Slower
    timeout=60         # Longer timeout
)
```

### "Too many failed URLs"
- Websites blocking automated access
- Incorrect links in PDF
- Solution: Check the failed URLs, adjust rate limiting

### "Out of memory"
- Processing too many URLs
- Solution: Reduce `max_depth` or process in batches

---

## 📝 Logging

The scraper logs all activity to `pdf_scraper.log`:

```
2026-06-30 10:30:00 - pdf_scraper - INFO - Starting PDF Processing with Recursive Web Scraping
2026-06-30 10:30:00 - pdf_scraper - INFO - Extracting content from PDF: sample.pdf
2026-06-30 10:30:02 - pdf_scraper - INFO - Found 5 links in PDF
2026-06-30 10:30:02 - pdf_scraper - INFO - Scraping: https://example.com/page1
2026-06-30 10:30:15 - pdf_scraper - INFO - [Depth 0] Scraped https://example.com/page1: success
...
```

Check this file for debugging and understanding what happened during execution.

---

## 🔐 Rate Limiting & Ethics

The scraper includes built-in rate limiting to be respectful:

```python
# Default: 2 seconds between requests
result = await process_pdf_with_scraping(
    pdf_path="sample.pdf",
    rate_limit=2.0
)
```

**Recommendations:**
- Use `rate_limit ≥ 1.0` for public websites
- Use `rate_limit ≥ 3.0` for smaller websites
- Respect `robots.txt` if available
- Identify your scraper with User-Agent rotation (built-in)

---

## 📊 Next Steps

After scraping:

1. **Process the combined text**
   - Clean up formatting
   - Extract structured data
   - Deduplicate content

2. **Index for RAG**
   - Create embeddings (OpenAI API)
   - Store in vector database (Pinecone)
   - Build search interface

3. **Monitor results**
   - Check success rates
   - Identify broken links
   - Update sources periodically

---

## 📚 More Examples

See `scraper_usage_example.py` for more detailed examples:
- Basic usage
- Control recursion depth
- Rate limiting
- Batch processing
- Save in different formats
- Full workflow example

---

## ✅ Checklist Before Running

- [ ] PDF file exists and is readable
- [ ] Dependencies installed: `pip install -r requirements_scraper.txt`
- [ ] Playwright browsers installed: `playwright install`
- [ ] Sufficient disk space for output
- [ ] Output directory has write permissions
- [ ] Internet connection for web scraping
- [ ] Reasonable rate_limit (≥ 1.0)

---

## 🚀 Next: Integration with RAG Pipeline

Once you have the combined text and links:

1. **Generate embeddings**
   ```python
   from openai import OpenAI
   
   client = OpenAI()
   embedding = client.embeddings.create(
       input=result['combined_data']['all_text'],
       model="text-embedding-3-large"
   )
   ```

2. **Store in vector database**
   ```python
   from pinecone import Pinecone
   
   pc = Pinecone(api_key="...")
   index = pc.Index("vivli-chatbot-rag")
   index.upsert(vectors=[(id, embedding, metadata)])
   ```

3. **Query for RAG**
   ```python
   results = index.query(vector=query_embedding, top_k=5)
   ```

---

**Ready to start scraping! Happy extracting! 🎉**
