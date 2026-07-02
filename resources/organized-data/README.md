# Vivli Chatbot - Resource Library

## Overview
This folder contains all resources needed for building and training the Vivli chatbot RAG (Retrieval-Augmented Generation) system. Resources are organized by file format for easy access and processing.

**Last Updated:** 2026-06-29  
**Total Resources:** 45 documents + 22 links for scraping  
**Total Size:** ~90 MB (excluding Form_Checks folder)

---

## 📁 Folder Structure

\\\
Vivli_Chatbot_Resources/
├── PDFs/                          # All PDF documents
│   ├── Guides/                    # User guides, policies, tips (9 PDFs)
│   ├── DRF_Samples/              # Sample Data Request Forms (1 PDF)
│   ├── Architecture/             # System architecture docs (1 PDF)
│   └── Form_Checks/              # Real DRF snapshots (380 PDFs) ⭐ CRITICAL
├── DOCX/                          # Word documents
│   ├── Templates/                # Form templates & worksheets (3 DOCXs)
│   └── Metadata/                 # Taxonomy & metadata (1 DOCX)
├── XLSX/                          # Excel spreadsheets (1 XLSX)
├── CSV/                           # Comma-separated data
│   └── Chat exports & logs (2 files)
├── JSON/                          # JSON formatted data (1 file)
└── Links/                         # Web resources & URLs
    └── Extracted_Links.txt       # 22 links + scraping guide
\\\

---

## 📊 Content By Category

### PDFs/Guides/ (9 files - 8.5 MB)
**Purpose:** User documentation and policy guides

| File | Size | Content | Priority |
|------|------|---------|----------|
| 2026_02_28-Vivli_quick_start_users_guide-3.9.pdf | 1.6 MB | Quick start for new users | HIGH |
| 2026_02_28-Request-Studies-on-Vivli-3.9-Final-2.pdf | 11.8 MB | Comprehensive DRF guide | HIGH |
| 2026_02_28-Study-Submission-Guide-3.9.pdf | 6.7 MB | Full submission workflow | HIGH |
| 2025_11_05-Anonymization-and-Data-De-Identificaton-Guide-1.pdf | 1.2 MB | De-identification guidelines | MEDIUM |
| 2025_03_25-Vivli-AI-ML-Model-Requirements.pdf | 211 KB | AI/ML validation | MEDIUM |
| 2025_01_22-Using-Vivli-to-meet-ICMJE-requirements.pdf | 184 KB | ICMJE compliance | MEDIUM |
| 2024_11_25-Study-Submission-Checklist_3.5.pdf | 166 KB | Submission checklist | MEDIUM |
| 2022_10_28-Vivli-Policies-in-Brief.pdf | 172 KB | Policies overview | LOW |
| 2026_02_28-Vivli-DRF-Tips-and-Tricks-3.9.pdf | 1.1 MB | Practical tips | MEDIUM |
| 2026_02_28-Vivli-Lay-Summary.pdf | 265 KB | Platform overview | LOW |
| 2026_2_28_Software_Available_in_Research_Environment-1.pdf | 323 KB | Software documentation | LOW |

**Total Size:** ~8.5 MB  
**Processing:** Standard PDF text extraction + OCR for scanned pages

---

### PDFs/DRF_Samples/ (1 file - 1 MB)
**Purpose:** Sample DRF to demonstrate form structure

| File | Size | Content |
|------|------|---------|
| 2026_02_28-Data-Request-Form-Sample-3.9.pdf | 1.0 MB | Sample filled DRF |

**Processing:** Form field extraction + table parsing

---

### PDFs/Architecture/ (1 file - 1.5 MB)
**Purpose:** System design and architecture

| File | Size | Content |
|------|------|---------|
| 2024_03_26_Vivli Platform System architecture_Release_3.pdf | 1.5 MB | Vivli platform architecture |

**Processing:** Diagram extraction + text content

---

### PDFs/Form_Checks/ (380 files - 27 MB) ⭐ **CRITICAL**
**Purpose:** Real DRF snapshots for training data

**Contents:**
- 380 actual Data Request Form snapshots (PDF exports)
- Covers submission dates from Oct 2025 to May 2026
- Mix of DrPrintView and DrSnapshot PDFs
- Average file size: 70-100 KB per document

**Naming Convention:**
- \DrPrintView-{REQUEST_ID}-{DATE}-{TIME}.pdf\ - Full form print views
- \DrSnapshot-{REQUEST_ID}-{DATE}-{TIME}.pdf\ - Form snapshots
- Example: \DrPrintView-00012802-28-Feb-2026-04-03-09.pdf\

**Usage in RAG:**
- Primary training data for understanding real DRF patterns
- Extract request IDs, dates, validation states
- Learn from actual researcher submissions

**Processing:**
1. Batch processing (parallel extraction)
2. Extract form fields, data patterns
3. Create training embeddings
4. Index by date range and request status

**Size Consideration:** Total 27 MB - recommended chunking strategy:
- Chunk by page or form section
- Index by request ID for retrieval
- Consider temporal indexing (date ranges)

---

### DOCX/Templates/ (3 files - 1.1 MB)
**Purpose:** Form templates and validation worksheets

| File | Size | Content |
|------|------|---------|
| 2026_05_22 Vivli ID 000 Form Check Template 5.9 annotated.docx | 512 KB | **ANNOTATED** with validation rules ⭐ |
| 2026_05_22 Vivli ID 000 Form Check Template 5.9.docx | 443 KB | Clean form template |
| 2026_02_28-DRF-Worksheet-3.9.docx | 135 KB | Worksheet for form completion |

**Processing:**
- Extract structured tables
- Parse annotations from annotated version
- Extract form field definitions
- Use for validation rule training

---

### DOCX/Metadata/ (1 file - 14 KB)
**Purpose:** Vivli Intent Taxonomy and embedded links

| File | Size | Content |
|------|------|---------|
| metadata file for the Vivli category json aka Vivli Intent Taxonomy document.docx | 14 KB | Intent taxonomy + 22 embedded URLs |

**Contents:**
- Vivli category classifications
- Intent taxonomy structure
- 21 Guru Card links
- 1 Google Sheets reference

**Processing:**
- Extract taxonomy hierarchy
- Extract all hyperlinks (see Links/Extracted_Links.txt)
- Map intents to knowledge base articles

---

### XLSX/ (1 file - 28 KB)
**Purpose:** Test case templates and examples

| File | Size | Content |
|------|------|---------|
| Vivli Manual Test Case Example and Template.xlsx | 28 KB | Test templates & examples |

**Processing:**
- Parse spreadsheet structure
- Extract test scenarios
- Use for QA/validation testing

---

### CSV/ (2 files - 17.8 MB + 89 KB log)
**Purpose:** Chat export and form check logs

| File | Size | Content |
|------|------|---------|
| vivli_chats_export.csv | 17.8 MB | Chat conversation export |
| form_check_download_log.csv | 89 KB | Form check processing log |

**Processing:**
- Tokenize chat content for intent classification
- Create conversational training data
- Parse timestamps and user interactions
- Extract common questions and responses

**Chunking Strategy:**
- Chunk by conversation thread
- Maintain temporal order
- Create intent labels from chat content

---

### JSON/ (1 file - 17.7 MB)
**Purpose:** Chat export in JSON format

| File | Size | Content |
|------|------|---------|
| vivli_chats_export.json | 17.7 MB | Chat data (JSON format) |

**Processing:**
- Parse JSON structure
- Extract metadata (user_id, timestamp, message, etc.)
- Use for structured intent training
- Create embeddings from chat content

**Note:** Consider CSV vs JSON - use whichever has better structure/completeness

---

### Links/ (1 file)
**Purpose:** Extracted URLs and web scraping guide

| File | Content |
|------|---------|
| Extracted_Links.txt | 22 categorized links + scraping instructions |

**Contents:**
- 21 Guru Cards (organized by 8 categories)
- 1 Google Sheets reference
- Usage guide for RAG pipeline

**Categories in Extracted_Links.txt:**
1. Form Validation Issues (4 links)
2. Request & Enquiry Management (5 links)
3. Data Access & Download (2 links)
4. Timeline & SLA Questions (3 links)
5. Submission Process (2 links)
6. Account Management & Changes (3 links)
7. Legal & Compliance (1 link)
8. Standards & Terminology (1 link)

---

## 🎯 Quick Access Guide

### For Chatbot Intent Training
**Start with these files:**
1. PDFs/Guides/ - Understand platform features
2. DOCX/Templates/Annotated - Learn validation rules
3. CSV/vivli_chats_export.csv - Real chat examples
4. Links/Extracted_Links.txt - Knowledge base mapping

### For Form Validation
**Priority files:**
1. PDFs/Form_Checks/ (380 real examples) ⭐
2. PDFs/DRF_Samples/ (sample forms)
3. DOCX/Templates/Annotated (validation rules)

### For Knowledge Base Integration
**Required files:**
1. Links/Extracted_Links.txt (22 URLs)
2. DOCX/Metadata/ (Intent taxonomy)
3. PDFs/Guides/ (Supporting docs)

### For System Understanding
**Read these first:**
1. PDFs/Architecture/
2. PDFs/Guides/2026_02_28-Vivli_quick_start_users_guide-3.9.pdf
3. DOCX/Metadata/

---

## 📋 File Statistics

| Category | Count | Size | Notes |
|----------|-------|------|-------|
| PDFs | 392 | ~30 MB | Includes 380 Form Checks |
| DOCX | 4 | 1.1 MB | Forms + Metadata |
| XLSX | 1 | 28 KB | Test cases |
| CSV | 1 | 17.8 MB | Chat export |
| JSON | 1 | 17.7 MB | Chat export (alt) |
| Links | 1 | ~5 KB | 22 URLs |
| **TOTAL** | **400** | **~90 MB** | Ready for RAG ingestion |

---

## ⚙️ Processing Recommendations

### Phase 1: Structured Content (Week 1)
- [ ] Process DOCX Templates → Extract validation rules
- [ ] Process XLSX → Extract test cases
- [ ] Process Links → Validate URLs
- [ ] Process Metadata → Extract taxonomy

### Phase 2: PDF Content (Week 2)
- [ ] Process PDFs/Guides → Text extraction + chunking
- [ ] Process PDFs/Architecture → Diagram + text
- [ ] Process PDFs/DRF_Samples → Form field extraction

### Phase 3: Training Data (Week 3)
- [ ] Process PDFs/Form_Checks (380 files) → Batch extraction
- [ ] Process CSV/vivli_chats_export.csv → Intent tokenization
- [ ] Process JSON/vivli_chats_export.json → Structured parsing

### Phase 4: Knowledge Base (Week 4)
- [ ] Web scraping: Guru Cards (21 links)
- [ ] Web scraping: Google Sheets
- [ ] Integration testing with all sources

---

## 🚀 RAG Integration Checklist

- [ ] All files successfully copied to organized structure
- [ ] Inventory Excel sheet maintained (Vivli_Chatbot_Resource_Inventory.xlsx)
- [ ] Links extracted and validated (Extracted_Links.txt)
- [ ] PDF text extraction tools configured (OCR for scanned docs)
- [ ] Chunking strategy defined per file type
- [ ] Vector embedding model selected
- [ ] Indexing database configured (Pinecone, Weaviate, etc.)
- [ ] Metadata schema defined
- [ ] Integration tests written
- [ ] Performance benchmarks established

---

## 📝 Notes

### Important Considerations

1. **Form Checks (PDFs/Form_Checks/):**
   - 380 files is large for batch processing
   - Consider parallel processing
   - Implement pagination in vector DB
   - May need separate indexing strategy

2. **Chat Exports (CSV/JSON - 35.5 MB combined):**
   - Requires tokenization/chunking before embedding
   - Consider creating separate intent index
   - May have duplicates between CSV and JSON versions

3. **Large PDFs in Guides:**
   - "Request-Studies" PDF (11.8 MB) - will need aggressive chunking
   - Some PDFs have scanned images - OCR required
   - Consider extracting tables separately

4. **Links (Guru Cards):**
   - Requires web scraping implementation
   - May need authentication
   - Consider rate limiting for API calls
   - Implement caching for frequently accessed cards

### Future Enhancements

- [ ] Implement automated link validation
- [ ] Create web scraping pipeline for Guru Cards
- [ ] Develop incremental update mechanism
- [ ] Add version control for resources
- [ ] Create data quality metrics

---

## 📧 Contact & Maintenance

**Created:** 2026-06-29  
**Maintained by:** Vivli Chatbot Development Team  
**Last Verified:** 2026-06-29  

For questions about resource organization or processing, refer to:
- Vivli_Chatbot_Resource_Inventory.xlsx (detailed metadata)
- Individual README files in each subfolder (if created)

---

Generated with ❤️ for the Vivli Chatbot RAG Pipeline
