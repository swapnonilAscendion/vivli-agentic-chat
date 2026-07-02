# Vivli Chatbot - Data Gathering & Processing Plan for RAG Architecture

**Created:** 2026-06-30  
**Purpose:** Comprehensive strategy for extracting, processing, and preparing all data for RAG pipeline  
**Status:** Planning Phase

---

## 📋 EXECUTIVE SUMMARY

This plan outlines how to:
1. **Gather data** from all 399 resources (PDFs, DOCX, CSV, JSON)
2. **Extract hyperlinks** and handle recursive web scraping
3. **Process content** into optimized markdown for RAG
4. **Manage quality** and deduplication
5. **Create embeddings** and index for vector database

**Total Effort:** 4-6 weeks | **Team:** 1-2 engineers

---

## 🎯 PHASE 0: FOUNDATION & SETUP (Days 1-2)

### 0.1 Environment Setup

**Install Core Libraries:**
```bash
pip install pypdf2 python-docx openpyxl requests beautifulsoup4 selenium
pip install pandas lxml validators urllib3 httpx asyncio
pip install markdown2 python-slugify chardet langdetect
pip install pydantic tqdm colorama
```

### 0.2 Folder Structure

```
data-processing/
├── config/
│   └── settings.json
├── scripts/
│   ├── 01_pdf_extractor.py
│   ├── 02_docx_extractor.py
│   ├── 03_csv_processor.py
│   ├── 04_json_processor.py
│   ├── 05_link_extractor.py
│   ├── 06_web_scraper.py
│   ├── 07_markdown_converter.py
│   └── 08_deduplication.py
├── raw_data/
├── processed_data/
└── logs/
```

### 0.3 Markdown Standard Format

```yaml
---
title: Document Title
source: original_file.pdf
source_type: pdf|docx|web|csv
source_url: https://...
date_extracted: 2026-06-30
category: guide|knowledge_base|faq
tags: [tag1, tag2]
confidence_score: 0.95
---

# Document Title

## Section 1

Content here...

### Subsection 1.1

More content...

**References:**
- [Link](url)
- [[Internal Link]]
```

---

## 🔄 PHASE 1: LOCAL DATA EXTRACTION (Days 3-7)

### 1.1 PDF Extraction (311 files)

**Strategy:**
- **Scanned PDFs:** Apply OCR (EasyOCR/Tesseract)
- **Native PDFs:** Direct text extraction
- **Form PDFs:** Extract fields + structure

**Processing Steps:**
1. Text extraction (preserve hierarchy)
2. Table extraction (convert to Markdown)
3. Image/diagram extraction
4. Link extraction
5. Structure validation

**Quality Checks:**
- OCR confidence > 90%
- No missing sections
- Tables properly formatted
- Links valid

---

### 1.2 DOCX Extraction (3 files + metadata)

**Special Processing:**
1. Document structure (maintain hierarchy)
2. Tables (extract as JSON/Markdown)
3. Embedded objects (images, links)
4. Annotations (comments, highlights)
5. **Annotated Form Template:** Extract validation rules

**Output per DOCX:**
```
docx_name/
├── content.md
├── tables.json
├── validation_rules.json   (for annotated template)
└── images/
```

---

### 1.3 CSV Processing (Chat Export)

**Strategy:**
1. Structure analysis (identify columns)
2. Conversation grouping (thread extraction)
3. Intent extraction (question/answer classification)
4. Data cleaning (remove PII, normalize)

**Output Format:**
```markdown
# FAQ: Form Validation

## Question: How do I fix a form check failure?
**Source:** vivli_chats_export.csv

**Answer:**
[Response content]

**Related Topics:**
- [[Form_Validation_Guide]]

**Frequency:** 145 similar questions
```

---

### 1.4 JSON Processing

Similar to CSV but leverage structured metadata:
- Parse JSON schema
- Extract timestamps + user data
- Create structured FAQs
- Compare with CSV (deduplication)

---

### 1.5 Form Checks (380 PDFs) ⭐ CRITICAL

**Large-Scale Batch Processing:**

```python
# Parallel processing (8-16 workers)
from multiprocessing import Pool

with Pool(12) as p:
    results = p.map(process_pdf, pdf_files)
```

**Per-File Processing:**
- Extract request ID
- Extract submission date
- Extract form fields
- Classify status
- Aggregate patterns

**Output Structure:**
```
form_checks/
├── by_request_id/
│   ├── 00012802/
│   │   ├── form_content.md
│   │   ├── extracted_fields.json
│   │   └── metadata.json
└── index.json
```

---

## 🔗 PHASE 2: LINK EXTRACTION & VALIDATION (Days 8-10)

### 2.1 Extract All Links

From PDFs, DOCX, CSV, JSON:
- Hyperlinks (from documents)
- Reference links
- URL patterns in text

**Output:**
```json
{
  "links": [
    {
      "url": "https://app.getguru.com/card/T74MLx5c/",
      "anchor_text": "If researcher initiates withdrawal",
      "source_document": "metadata_file.docx",
      "link_type": "guru_card"
    }
  ]
}
```

### 2.2 Link Validation & Classification

**Validation Steps:**
1. URL format check (regex)
2. Domain accessibility (ping)
3. SSL certificate validation
4. Response code check

**Classification:**
- Internal (Vivli platform)
- External (Google Sheets, etc.)
- Dead/invalid

### 2.3 Recursive Link Following

**Algorithm:**
```
Level 1: Known links from documents (22 URLs)
├─ Scrape & extract new links
├─ Level 2: New links found
│  ├─ Scrape & extract more links
│  └─ Level 3: Even more links
└─ Max depth: 3 (configurable)
```

**Deduplication:** Track URL hashes to avoid re-crawling  
**Rate Limiting:** 1-2 requests/second  
**Scope:** Keep in-domain (vivli.org, app.getguru.com)

---

## 🌐 PHASE 3: WEB SCRAPING (Days 11-15)

### 3.1 Guru Card Scraping (21 links)

**Per-Card Processing:**

```markdown
# [Card Title]

**Card ID:** T74MLx5c  
**Category:** Form Validation  
**Source:** https://app.getguru.com/card/...  

## Content

[Main article content]

### Examples

[Code/examples]

### Related Cards

- [[Related Card 1]]
- [[Related Card 2]]
```

**Implementation:**
```python
import requests
from bs4 import BeautifulSoup

session = requests.Session()
response = session.get(url, timeout=30)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract title, body, links, etc.
```

### 3.2 Google Sheets Scraping

**Approach:**
1. Use Sheets API (preferred) + Google service account
2. Fallback: Manual export + parsing

**Convert to Markdown:**
```markdown
# Vivli Resources

| Resource | Type | Link | Category |
|----------|------|------|----------|
| ... | ... | ... | ... |
```

### 3.3 Error Handling & Recovery

**Retry Strategy:**
```python
@retry(max_attempts=3, backoff_factor=2, timeout=30)
def scrape_with_retry(url):
    response = requests.get(url)
    response.raise_for_status()
    return response
```

**Track:**
- Failed URLs
- Timeout URLs
- Invalid URLs

---

## 📝 PHASE 4: MARKDOWN CONVERSION & STRUCTURING (Days 16-20)

### 4.1 Standard Markdown Template

```yaml
---
title: Document Title
source: original_filename
source_type: pdf|docx|web|csv
source_category: guide|knowledge_base|faq
date_extracted: 2026-06-30
confidence_score: 0.95
tags: [tag1, tag2]
character_count: 5234
word_count: 1123
section_count: 5
quality_score: 0.96
---

# Document Title

## Section 1

Content...

### Subsection 1.1

Details...

---

## References

- [External Link](url)
- [[Internal Document]]
```

### 4.2 Document Organization

```
markdown_output/
├── 01_guides/
│   ├── quickstart_guide.md
│   ├── submission_checklist.md
│   └── ...
├── 02_knowledge_base/
│   ├── form_validation/
│   ├── data_access/
│   ├── timelines/
│   └── ...
├── 03_faqs/
│   ├── form_validation_faq.md
│   └── ...
├── 04_form_checks/
│   ├── request_patterns.md
│   └── validation_rules.md
├── 05_architecture/
│   └── system_design.md
├── 06_reference/
│   ├── glossary.md
│   ├── acronyms.md
│   └── data_dictionary.md
└── 00_index.md
```

### 4.3 Cross-Linking Strategy

```json
{
  "cross_references": [
    {
      "from_doc": "form_validation_guide.md",
      "to_doc": "form_check_failed.md",
      "link_type": "related"
    }
  ]
}
```

---

## 🧹 PHASE 5: DATA QUALITY & DEDUPLICATION (Days 21-22)

### 5.1 Deduplication Strategy

**Methods:**
1. Content hash (SHA-256)
2. Fuzzy matching (>95% similar)
3. Semantic similarity (embeddings, >0.9)

**Resolution:**
- **Exact duplicates:** Keep original, remove copies
- **Near duplicates:** Merge or cross-reference
- **Partial overlap:** Analyze & decide

### 5.2 Quality Scoring

```json
{
  "quality_metrics": {
    "extraction_completeness": 0.98,
    "ocr_confidence": 0.95,
    "structure_preservation": 0.99,
    "link_validity": 0.92,
    "overall_score": 0.96
  }
}
```

### 5.3 Manual Review

**Flag if:**
- Quality score < 0.80
- Complex tables not extracted
- OCR confidence < 85%
- Multiple dead links

---

## 📊 PHASE 6: VECTOR EMBEDDING & INDEXING (Days 23-25)

### 6.1 Document Chunking

**Strategy:**
```
Split by logical sections (not character count):
├── Document level (if small)
├── Section level (H1/H2)
├── Subsection level (H3)
└── Paragraph level (for detailed docs)

Chunk size: 500-1000 tokens
Overlap: 50-100 tokens
Max: 2000 tokens
```

### 6.2 Embedding Generation

**Recommended Model:** OpenAI `text-embedding-3-large`
- Dimensions: 1536
- Cost: ~$0.02/1M tokens
- Quality: State-of-the-art

**Implementation:**
```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")

response = client.embeddings.create(
    input=text,
    model="text-embedding-3-large"
)
embedding = response.data[0].embedding
```

### 6.3 Vector Database Setup

**Recommended:** Pinecone
- Managed service
- Easy scaling
- Good API

**Index Structure:**
```
Index: "vivli-chatbot-rag"
Dimension: 1536
Metric: cosine
Metadata: document_id, title, source, category, tags
```

**Upsert:**
```python
from pinecone import Pinecone

client = Pinecone(api_key="pk-...")
index = client.Index("vivli-chatbot-rag")

vectors = [
    {
        'id': 'chunk_001',
        'values': [0.1, 0.2, ..., 0.9],
        'metadata': {
            'document_id': 'doc_001',
            'title': 'Quick Start',
            'category': 'guide'
        }
    }
]

index.upsert(vectors=vectors)
```

---

## 🧪 PHASE 7: TESTING & VALIDATION (Days 26-27)

### 7.1 Retrieval Testing

**Sample Queries:**
- "How do I fix a form check failure?"
- "What is the process for data access?"
- "When will my request be reviewed?"
- "What is a DUA?"

**Evaluate:**
- Top 5 results
- Relevance scores
- Source documents

### 7.2 Quality Metrics

**MRR (Mean Reciprocal Rank):** > 0.8  
**Precision@5:** > 0.6  
**Precision@10:** > 0.5  
**NDCG:** > 0.7

### 7.3 Hallucination Testing

- Test with non-existent features
- Verify exact quotes
- Check numeric accuracy

---

## 📈 PHASE 8: OPTIMIZATION & DEPLOYMENT (Days 28-30)

### 8.1 Performance Targets

- Query latency: < 200ms
- Index size: < 5GB
- Throughput: > 100 queries/sec

### 8.2 Deployment Pipeline

```
Development → Staging (test) → Production (live)
```

### 8.3 Monitoring

Track:
- Query success rate
- Average latency
- User satisfaction
- Index size & growth
- API costs

---

## 🗂️ TECHNOLOGY STACK

| Component | Recommended | Alternative |
|-----------|------------|-------------|
| PDF | PyPDF2 + pdfplumber | Poppler |
| OCR | EasyOCR | Tesseract |
| DOCX | python-docx | - |
| Scraping | requests + BeautifulSoup | Selenium |
| Embeddings | OpenAI API | Sentence-Transformers |
| Vector DB | Pinecone | Weaviate |
| Framework | LangChain | LlamaIndex |

---

## ⏱️ TIMELINE

### Week 1: Foundation + PDF Extraction
- Days 1-2: Setup infrastructure
- Days 3-5: Extract 311 PDFs
- Days 6-7: Quality validation

**Output:** 200+ markdown files

### Week 2: DOCX, CSV, JSON + Links
- Day 8: DOCX extraction
- Day 9: CSV processing
- Day 10: JSON processing
- Days 11-13: Link extraction & validation
- Day 14: Buffer

**Output:** 300+ markdown files, 22 validated links

### Week 3: Form Checks + Web Scraping
- Days 15-16: Batch process 380 PDFs
- Days 17-20: Web scraping (Guru Cards + Sheets)
- Day 21: Deduplication + QA

**Output:** 600+ markdown files, scraped content

### Week 4: Embedding + Indexing + Testing
- Days 22-23: Chunking strategy
- Day 24: Generate embeddings
- Day 25: Index in vector DB
- Days 26-27: Test + validate
- Day 28: Optimize + deploy

**Output:** Indexed vector database, test results

### Week 5: Buffer + Documentation
- Days 29-30: Buffer for issues, final docs

---

## ✅ SUCCESS METRICS

### Quantitative
- 99%+ documents successfully processed
- < 1% data loss
- OCR confidence > 90% average
- Extraction completeness > 95%
- Quality score > 0.90 average
- Retrieval precision@5 > 0.6
- Query latency < 200ms

### Qualitative
- Clear documentation
- Modular code
- Easy to maintain & extend

---

## 🚨 RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Rate limiting on scraping | Cannot get all content | Exponential backoff, rotating proxies |
| Inconsistent data quality | Poor retrieval | Quality scoring, manual review |
| Vector DB costs | Budget overrun | Cache embeddings, batch processing |
| Duplicate content | Wasted storage | Multi-strategy deduplication |
| Stale content | Outdated info served | Monitor sources, version tracking |

---

## ✅ ROLLOUT CHECKLIST

- [ ] All documents extracted
- [ ] Quality score > 0.90 for 95% of docs
- [ ] All links validated
- [ ] Embeddings generated for all chunks
- [ ] Pinecone index populated
- [ ] Retrieval tests pass (MRR > 0.8)
- [ ] Hallucination tests pass
- [ ] Documentation complete
- [ ] Monitoring set up
- [ ] Team trained
- [ ] Stakeholder sign-off

---

## 🔄 CONTINUOUS IMPROVEMENT

**Post-Launch:**
1. Monitor performance metrics
2. Collect user feedback
3. Iterative updates to strategy
4. Monthly content refresh
5. Quarterly strategy review

---

**End of RAG Data Gathering & Processing Plan**
