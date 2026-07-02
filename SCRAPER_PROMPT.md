# PDF Processor with Recursive Web Scraper - Development Prompt

## 🎯 OBJECTIVE
Create a Python function that:
1. Extracts text and links from PDF files
2. Automatically scrapes websites found in those links
3. Recursively follows links from scraped pages
4. Combines all extracted data into a structured format

---

## 📋 DETAILED REQUIREMENTS

### Part 1: PDF Processing
**Input:** Path to a PDF file  
**Output:** Dictionary with:
- `pdf_text`: Full extracted text content
- `pdf_links`: List of URLs found in the PDF
- `pdf_metadata`: File name, page count, extraction timestamp

**Implementation:**
- Use `pdfplumber` for text extraction
- Use regex to extract URLs from text
- Handle errors gracefully (corrupted PDFs, etc.)
- Extract text while preserving structure (maintain headings, paragraphs)

---

### Part 2: Web Scraping with Automation
**Tool Choice:** Playwright (preferred) or Selenium
**Why:** Some websites need JavaScript rendering; simple requests won't work

**Per-URL Requirements:**
- Fetch the website content
- Extract main text content (remove noise - ads, nav, footer)
- Extract all hyperlinks found on the page
- Capture page title and metadata
- Handle JavaScript-heavy pages
- Implement timeout (30 seconds max)
- Add user-agent rotation to avoid blocks

**Output per URL:**
```json
{
  "url": "https://example.com/page",
  "title": "Page Title",
  "text_content": "extracted text",
  "links_found": ["url1", "url2"],
  "status": "success|timeout|failed",
  "error": null or "error message",
  "scraped_at": "2026-06-30T10:30:00"
}
```

---

### Part 3: Recursive Link Following
**Rules:**
- Maximum recursion depth: 3 levels
- Rate limiting: 2 seconds between requests (be respectful)
- Visited URL tracking: Don't scrape same URL twice
- Deduplication by URL hash
- Filter out non-HTML content (images, pdfs, archives)
- Scope limiting: Only follow links from the same domain (optional, configurable)

**Recursion Algorithm:**
```
Level 0: Links found in original PDF
  ↓ Scrape each
Level 1: Links found in those pages
  ↓ Scrape each
Level 2: Links found in those pages
  ↓ Scrape each
Level 3: Links found (but don't scrape further)
  ↓ Stop here
```

---

### Part 4: Data Combination & Output

**Final Output Structure:**
```json
{
  "execution_id": "unique-id",
  "started_at": "2026-06-30T10:30:00",
  "completed_at": "2026-06-30T10:45:00",
  
  "source_pdf": {
    "file_path": "/path/to/file.pdf",
    "text": "extracted pdf text...",
    "links_extracted": 5,
    "page_count": 10
  },
  
  "scraping_results": {
    "total_urls_processed": 12,
    "successful_scrapes": 10,
    "failed_scrapes": 2,
    "duplicate_urls_skipped": 3,
    
    "by_depth": {
      "depth_0": [
        {
          "url": "...",
          "title": "...",
          "text_preview": "first 500 chars...",
          "child_links": 5
        }
      ],
      "depth_1": [...],
      "depth_2": [...]
    }
  },
  
  "combined_data": {
    "all_text": "combined text from pdf + all scraped pages",
    "all_links": [list of unique URLs found],
    "link_graph": {
      "url1": ["url2", "url3"],  // url1 links to url2, url3
      "url2": ["url4"]
    }
  },
  
  "statistics": {
    "total_text_chars": 50000,
    "unique_urls_found": 45,
    "pages_with_errors": [list of failed URLs],
    "execution_time_seconds": 900
  }
}
```

---

## 🛠️ IMPLEMENTATION DETAILS

### Libraries to Use:
```python
pdfplumber          # PDF text extraction
playwright          # Web automation (preferred)
beautifulsoup4      # HTML parsing (light fallback)
requests            # HTTP requests
re                  # Regex for link extraction
asyncio             # Async processing for speed
logging             # Error tracking
hashlib             # URL deduplication
time                # Rate limiting
```

### Key Functions to Create:
1. `extract_pdf_content(pdf_path)` → dict
2. `scrape_webpage(url)` → dict
3. `extract_links_from_html(html_content)` → list
4. `scrape_recursive(start_urls, max_depth, visited=set())` → dict
5. `combine_all_data(pdf_data, scraping_data)` → dict
6. `process_pdf_with_scraping(pdf_path, max_depth=3)` → dict (main function)

### Error Handling:
- Try/except for each URL (don't crash on one bad link)
- Log all failures with reasons
- Skip dead links gracefully
- Handle timeouts (30 second limit)
- Catch JavaScript errors in Playwright
- Validate URLs before scraping

### Rate Limiting:
- 2-second delay between requests
- Respect robots.txt (optional but good practice)
- User-Agent rotation

---

## 📊 EXAMPLE USAGE

```python
# Simple usage
result = process_pdf_with_scraping(
    pdf_path="docs/guides/sample.pdf",
    max_depth=2,
    rate_limit=2
)

# Check results
print(f"Found {result['scraping_results']['total_urls_processed']} URLs")
print(f"Combined text length: {result['statistics']['total_text_chars']} chars")

# Access combined data
all_text = result['combined_data']['all_text']
all_links = result['combined_data']['all_links']
```

---

## 🎨 DESIRED BEHAVIOR

### What It Should Do:
1. Read a PDF ✓
2. Find all URLs in that PDF (e.g., "https://app.getguru.com/card/T74MLx5c") ✓
3. Visit each URL with Playwright (render JavaScript) ✓
4. Extract text from each page ✓
5. Find all links on those pages ✓
6. Visit those new links (recursively, up to depth 3) ✓
7. Stop when max depth reached ✓
8. Combine everything into one structured output ✓

### What It Should NOT Do:
- Don't crash on a single bad URL ✗
- Don't scrape the same URL twice ✗
- Don't go deeper than depth 3 ✗
- Don't make requests too fast (spam) ✗
- Don't include raw HTML in output ✗
- Don't ignore errors silently ✗

---

## 🧪 TEST CASE

**Input:** A sample PDF with 2-3 URLs inside
**Expected Output:**
- PDF text extracted
- 2-3 URLs identified
- Each URL scraped successfully
- Each scraped page yields 3-5 new links
- Those new links scraped recursively
- Everything combined into the JSON output above

---

## 📝 ADDITIONAL CONSIDERATIONS

### Performance:
- Should process a PDF + scrape ~15 URLs in ~2-3 minutes (with 2-sec delays)
- Use async if possible for speed

### Scalability:
- Design so we can later batch-process 380 PDFs
- Make parameters configurable (max_depth, rate_limit, timeout)

### Output Format:
- Should be easily serializable to JSON
- Should be easy to visualize or process further
- Include metadata for debugging

### Logging:
- Log each step (PDF opened, URL scraped, links found)
- Log errors with context
- Save a detailed log file alongside the results

---

## 🎯 SUCCESS CRITERIA

✅ Function takes a PDF path as input  
✅ Extracts links from PDF  
✅ Scrapes those links with Playwright  
✅ Recursively follows links (max 3 levels)  
✅ Combines all data into a single structured output  
✅ Handles errors gracefully  
✅ Respects rate limits  
✅ Deduplicates visited URLs  
✅ Includes statistics and metadata  
✅ Code is clean and well-commented  

---

## 🚀 DELIVERABLE

**A Python module** with:
- Main function: `process_pdf_with_scraping(pdf_path, max_depth=3, rate_limit=2.0)`
- Helper functions as needed
- Example usage showing:
  1. How to process one PDF
  2. How to extract the combined text
  3. How to view the link graph
  4. How to save results to JSON

**Optional Extras:**
- A simple example showing the result visualization
- Sample output JSON
- Usage documentation

---

## 📌 NOTES FOR DEVELOPER

- Feel free to adjust the exact output format if it makes sense
- Use Playwright over Selenium (cleaner API, faster)
- Consider using asyncio for concurrent scraping (within rate limits)
- Make it robust - this will eventually process 380 PDFs
- Think about how we'd scale this to batch processing

---

**Ready to receive this prompt? Review and let me know if you'd like any changes!**
