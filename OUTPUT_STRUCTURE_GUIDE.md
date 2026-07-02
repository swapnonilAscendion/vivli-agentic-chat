# PDF Scraper - Output Structure & Data Flow Guide

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     INPUT: PDF FILE                                  │
│                   (sample.pdf)                                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   STEP 1: PDF EXTRACTION                             │
│                                                                       │
│  • Extract all text from all pages                                  │
│  • Preserve page structure (headers, paragraphs)                    │
│  • Extract metadata (page count, file size)                         │
│  • Scan for URLs/links                                              │
│                                                                       │
│  OUTPUT:                                                             │
│  ├── pdf_text: "Page 1: ... Page 2: ..."                           │
│  ├── pdf_links: ["https://url1.com", "https://url2.com", ...]     │
│  └── pdf_metadata: {file_size, page_count, ...}                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 2: RECURSIVE WEB SCRAPING                          │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ DEPTH 0: Scrape PDF links (2-5 URLs)                         │  │
│  │  • Use Playwright to render JavaScript                       │  │
│  │  • Extract page title + text content                         │  │
│  │  • Find all links on those pages (~5-10 per page)           │  │
│  │                                                              │  │
│  │  Example:                                                    │  │
│  │  Scrape: https://app.getguru.com/card/T74MLx5c             │  │
│  │    ├── Title: "Form Validation Guide"                        │  │
│  │    ├── Text: "How to validate forms..."                      │  │
│  │    └── Links: [url1, url2, url3, ...]                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│               │                                                       │
│               ▼                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ DEPTH 1: Scrape links found in Depth 0 pages (~10-20 URLs)  │  │
│  │  • Same process: fetch, extract, find new links             │  │
│  │  • Add rate limiting (2 sec between requests)               │  │
│  │  • Track visited URLs (no duplicates)                       │  │
│  │  • Detect duplicate content (same text = skip)              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│               │                                                       │
│               ▼                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ DEPTH 2: Scrape links found in Depth 1 pages (~30-50 URLs)  │  │
│  │  • Continue same process                                    │  │
│  │  • Still respect rate limiting                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│               │                                                       │
│               ▼                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ DEPTH 3: STOP (or scrape if configured)                      │  │
│  │  • Found links are collected but not scraped                │  │
│  │  • Prevents infinite recursion                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 3: COMBINE & STRUCTURE DATA                        │
│                                                                       │
│  • Merge all extracted text                                          │
│  • Collect all unique URLs                                           │
│  • Build link graph (which pages link to which)                     │
│  • Calculate statistics                                              │
│  • Track errors/failures                                             │
│                                                                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│               OUTPUT: STRUCTURED RESULT DICT                         │
│                 (JSON-serializable)                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Output Structure - Complete Example

```json
{
  "execution_id": "a1b2c3d4e5f6",
  "started_at": "2026-06-30T10:30:00.000000",
  "completed_at": "2026-06-30T10:45:30.000000",
  "execution_time_seconds": 930,
  
  "source_pdf": {
    "file_path": "/Users/you/docs/form_validation_guide.pdf",
    "file_name": "form_validation_guide.pdf",
    "page_count": 12,
    "file_size_bytes": 2457600,
    "text_length": 45230,
    "links_extracted": 4
  },
  
  "scraping_results": {
    "total_urls_processed": 87,
    "successful_scrapes": 82,
    "failed_scrapes": 5,
    "duplicate_urls_skipped": 3,
    "success_rate": "94.3%"
  },
  
  "combined_data": {
    "all_text": "--- Page 1 ---\nForm Validation Guide...\n\n--- Source: https://app.getguru.com/card/T74MLx5c ---\nHow to validate forms...",
    "all_text_length": 523450,
    "all_links": [
      "https://app.getguru.com/card/T74MLx5c",
      "https://app.getguru.com/card/T84rrG5c",
      "https://docs.google.com/spreadsheets/...",
      "https://example.com/page1",
      "https://example.com/page2",
      ...
    ],
    "unique_links_count": 87,
    "link_graph": {
      "https://app.getguru.com/card/T74MLx5c": [
        "https://app.getguru.com/card/T84rrG5c",
        "https://example.com/related",
        "https://docs.google.com/..."
      ],
      "https://app.getguru.com/card/T84rrG5c": [
        "https://example.com/page1",
        "https://example.com/page2"
      ],
      ...
    }
  },
  
  "errors": {
    "failed_urls": [
      {
        "url": "https://dead-link.com/page",
        "error": "Timeout: Page took longer than 30 seconds to load"
      },
      {
        "url": "https://blocked.com/page",
        "error": "403 Forbidden: Access denied"
      },
      ...
    ],
    "total_failed": 5
  },
  
  "statistics": {
    "total_text_chars": 523450,
    "unique_urls_found": 87,
    "pages_with_errors": 5,
    "extraction_success_rate": "94.3%"
  }
}
```

---

## 🔍 Breaking Down Each Section

### 1. Execution Metadata

```python
{
  "execution_id": "a1b2c3d4e5f6",           # Unique ID for this run
  "started_at": "2026-06-30T10:30:00",      # When execution started
  "completed_at": "2026-06-30T10:45:30",    # When execution ended
  "execution_time_seconds": 930             # Total time (15.5 minutes)
}
```

**Use for:**
- Tracking when scraping happened
- Measuring performance
- Debugging slow runs

---

### 2. Source PDF Information

```python
{
  "source_pdf": {
    "file_path": "/full/path/to/file.pdf",  # Full path to PDF
    "file_name": "form_validation_guide.pdf",
    "page_count": 12,                        # Pages in PDF
    "file_size_bytes": 2457600,              # Size (2.3 MB)
    "text_length": 45230,                    # Chars extracted from PDF
    "links_extracted": 4                     # URLs found in PDF
  }
}
```

**Use for:**
- Verifying which PDF was processed
- Understanding source file characteristics
- Tracking how many initial links

---

### 3. Scraping Statistics

```python
{
  "scraping_results": {
    "total_urls_processed": 87,         # Total URLs visited
    "successful_scrapes": 82,           # Successful scrapes
    "failed_scrapes": 5,                # Failed URLs
    "duplicate_urls_skipped": 3,        # Duplicate content
    "success_rate": "94.3%"             # Success percentage
  }
}
```

**Interpretation:**
- `success_rate > 90%` → Good scraping quality
- `success_rate > 95%` → Excellent
- `success_rate < 80%` → Check error logs

---

### 4. Combined Data

#### 4.1 All Extracted Text

```python
"all_text": "--- Page 1 ---\nForm Validation...\n\n--- Source: https://url1.com ---\nContent..."
"all_text_length": 523450  # Characters
```

**This is:**
- Full PDF text + all scraped page text combined
- Ready for embedding generation
- Can be saved to markdown/text file
- Used for RAG retrieval

---

#### 4.2 All Unique Links

```python
"all_links": [
  "https://app.getguru.com/card/T74MLx5c",
  "https://app.getguru.com/card/T84rrG5c",
  "https://docs.google.com/spreadsheets/...",
  "https://example.com/page1",
  ...
],
"unique_links_count": 87
```

**This is:**
- Every URL found during the entire scraping process
- Deduplicated (no duplicates)
- Useful for building a sitemap
- Can be exported for further analysis

---

#### 4.3 Link Graph

```python
"link_graph": {
  "https://app.getguru.com/card/T74MLx5c": [
    "https://app.getguru.com/card/T84rrG5c",
    "https://example.com/related",
    "https://docs.google.com/..."
  ],
  "https://app.getguru.com/card/T84rrG5c": [
    "https://example.com/page1",
    "https://example.com/page2"
  ]
}
```

**This is:**
- Shows which page links to which other pages
- Can build network visualization
- Understand content relationships
- Identify important hubs (pages with many links)

---

### 5. Errors & Failures

```python
"errors": {
  "failed_urls": [
    {
      "url": "https://dead-link.com/page",
      "error": "Timeout: Page took longer than 30 seconds"
    },
    {
      "url": "https://blocked.com/page",
      "error": "403 Forbidden: Access denied"
    }
  ],
  "total_failed": 5
}
```

**Types of errors:**
- `Timeout`: Page too slow
- `403 Forbidden`: Site blocking scrapers
- `404 Not Found`: Link is dead
- `Connection Error`: Network issue
- `JavaScript Error`: Page JavaScript failed

**What to do:**
- Review failed URLs manually
- Increase `timeout` for slow sites
- Adjust `rate_limit` if getting blocked
- Remove dead links from sources

---

### 6. Final Statistics

```python
"statistics": {
  "total_text_chars": 523450,        # Combined text size
  "unique_urls_found": 87,           # Unique URLs discovered
  "pages_with_errors": 5,            # Failed URL count
  "extraction_success_rate": "94.3%" # Success percentage
}
```

---

## 📈 How to Use Each Section

### Scenario 1: Create a Knowledge Base Document

```python
result = await process_pdf_with_scraping("guide.pdf")

# Use the combined text
with open('knowledge_base.md', 'w') as f:
    f.write("# Knowledge Base\n\n")
    f.write("**Generated from:**\n")
    f.write(f"- PDF: {result['source_pdf']['file_name']}\n")
    f.write(f"- Web scraping: {result['scraping_results']['total_urls_processed']} URLs\n")
    f.write("\n---\n\n")
    f.write(result['combined_data']['all_text'])
```

### Scenario 2: Create a Link Index

```python
result = await process_pdf_with_scraping("guide.pdf")

with open('link_index.csv', 'w') as f:
    f.write("URL,Source\n")
    for url in result['combined_data']['all_links']:
        f.write(f"{url},scraped\n")
```

### Scenario 3: Analyze Link Relationships

```python
result = await process_pdf_with_scraping("guide.pdf")

link_graph = result['combined_data']['link_graph']

# Find pages with most outgoing links
for url, links in sorted(link_graph.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
    print(f"{url}: {len(links)} outgoing links")
```

### Scenario 4: Generate Embeddings for RAG

```python
from openai import OpenAI

result = await process_pdf_with_scraping("guide.pdf")

client = OpenAI()

# Create embedding from combined text
embedding = client.embeddings.create(
    input=result['combined_data']['all_text'],
    model="text-embedding-3-large"
).data[0].embedding

# Store in vector database
vector_db.upsert(
    id=result['execution_id'],
    vector=embedding,
    metadata={
        'source_pdf': result['source_pdf']['file_name'],
        'urls_count': result['scraping_results']['total_urls_processed'],
        'success_rate': result['scraping_results']['success_rate']
    }
)
```

### Scenario 5: Monitor Quality

```python
result = await process_pdf_with_scraping("guide.pdf")

quality_metrics = {
    'success_rate': float(result['scraping_results']['success_rate'].rstrip('%')),
    'text_length': result['statistics']['total_text_chars'],
    'urls_found': result['statistics']['unique_urls_found'],
    'failures': result['statistics']['pages_with_errors']
}

# Log for monitoring
import json
with open('metrics.json', 'w') as f:
    json.dump(quality_metrics, f)

# Alert if quality is low
if quality_metrics['success_rate'] < 80:
    print("⚠️  Low success rate detected!")
    for error in result['errors']['failed_urls'][:5]:
        print(f"  - {error['url']}: {error['error']}")
```

---

## 🎯 Expected Data Sizes

```
Small PDF (1 page, 1-2 links):
├── Links scraped: 2-5
├── Execution time: 30-60 seconds
├── Combined text: 5K-50K chars
└── Memory usage: <100 MB

Medium PDF (10 pages, 5 links):
├── Links scraped: 20-50 (depth=2)
├── Execution time: 3-5 minutes
├── Combined text: 100K-500K chars
└── Memory usage: 200-500 MB

Large PDF (50 pages, 10 links):
├── Links scraped: 80-150 (depth=2)
├── Execution time: 10-20 minutes
├── Combined text: 500K-2M chars
└── Memory usage: 500MB-2GB
```

---

## ✅ Quality Checklist

After scraping, verify:

- [ ] `success_rate > 90%`
- [ ] `unique_links_count > 0`
- [ ] `total_text_chars > 5000`
- [ ] `failed_urls < 10%`
- [ ] Output files saved successfully
- [ ] No timeout errors if possible

---

## 🚀 Next Steps

1. **If success_rate > 90%**
   → Proceed to embedding generation

2. **If success_rate 70-90%**
   → Investigate failed URLs, retry with higher timeout

3. **If success_rate < 70%**
   → Check if websites are blocking scrapers
   → Adjust rate_limit and timeout
   → Try again

---

**Your combined data is now ready for RAG pipeline! 🎉**
