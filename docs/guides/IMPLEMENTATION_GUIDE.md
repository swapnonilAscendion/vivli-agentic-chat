# Vivli Chatbot RAG - Implementation Guide & Code Templates

**Quick Reference for Executing the Data Plan**

---

## 🚀 QUICK START (First Day)

### Step 1: Create Project Structure
```bash
mkdir -p data-processing/{config,scripts,raw_data,processed_data,logs}
cd data-processing
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Step 2: Install Dependencies
```bash
pip install pypdf2 python-docx openpyxl requests beautifulsoup4
pip install pandas lxml validators urllib3 httpx asyncio
pip install markdown2 python-slugify chardet langdetect pydantic tqdm
pip install openai pinecone-client langchain
```

### Step 3: Create Configuration
**config/settings.json:**
```json
{
  "sources": {
    "pdf_guides": "C:/path/to/PDFs/Guides/",
    "docx_files": "C:/path/to/DOCX/",
    "csv_files": "C:/path/to/CSV/",
    "form_checks": "C:/path/to/PDFs/Form_Checks/"
  },
  "output": {
    "raw_data": "./raw_data/",
    "processed_data": "./processed_data/",
    "logs": "./logs/"
  },
  "processing": {
    "ocr_enabled": true,
    "ocr_confidence_threshold": 0.9,
    "max_workers": 12,
    "chunk_size": 750,
    "chunk_overlap": 100
  },
  "embedding": {
    "model": "text-embedding-3-large",
    "api_key": "${OPENAI_API_KEY}",
    "batch_size": 10
  },
  "vector_db": {
    "provider": "pinecone",
    "api_key": "${PINECONE_API_KEY}",
    "index_name": "vivli-chatbot-rag",
    "dimension": 1536
  }
}
```

---

## 📄 PDF EXTRACTION (Phase 1.1)

### Template: PDF Extractor Script
**scripts/01_pdf_extractor.py:**

```python
import PyPDF2
import pdfplumber
from pathlib import Path
from typing import Dict, List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.content = {}
    
    def extract_text(self) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text += f"\n\n--- Page {i+1} ---\n\n"
                    text += page.extract_text()
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
        return text
    
    def extract_tables(self) -> List[Dict]:
        """Extract tables from PDF"""
        tables = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table_idx, table in enumerate(page_tables):
                            tables.append({
                                'page': i+1,
                                'table_index': table_idx,
                                'data': table
                            })
        except Exception as e:
            logger.error(f"Error extracting tables: {e}")
        return tables
    
    def extract_links(self) -> List[Dict]:
        """Extract hyperlinks from PDF"""
        links = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    if hasattr(page, 'annots') and page.annots:
                        for annot in page.annots:
                            if annot['subtype'] == 'Link':
                                links.append({
                                    'page': i+1,
                                    'url': annot.get('uri', 'unknown'),
                                    'rect': annot.get('rect')
                                })
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
        return links
    
    def extract_all(self) -> Dict:
        """Extract all content from PDF"""
        return {
            'text': self.extract_text(),
            'tables': self.extract_tables(),
            'links': self.extract_links(),
            'file': Path(self.pdf_path).name
        }

# Usage
if __name__ == "__main__":
    pdf_dir = Path("../data/PDFs/Guides/")
    
    for pdf_file in pdf_dir.glob("*.pdf"):
        logger.info(f"Processing: {pdf_file.name}")
        
        extractor = PDFExtractor(str(pdf_file))
        result = extractor.extract_all()
        
        # Save extracted content
        output_file = Path("../raw_data") / f"{pdf_file.stem}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
```

---

## 📋 DOCX EXTRACTION (Phase 1.2)

### Template: DOCX Extractor
**scripts/02_docx_extractor.py:**

```python
from docx import Document
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class DOCXExtractor:
    def __init__(self, docx_path: str):
        self.doc = Document(docx_path)
        self.file_name = Path(docx_path).name
    
    def extract_text(self) -> str:
        """Extract all paragraphs"""
        text = ""
        for para in self.doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"
        return text
    
    def extract_tables(self) -> list:
        """Extract tables as structured data"""
        tables = []
        for table in self.doc.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                table_data.append(row_data)
            tables.append(table_data)
        return tables
    
    def extract_hyperlinks(self) -> list:
        """Extract hyperlinks from document"""
        links = []
        for para in self.doc.paragraphs:
            for run in para.runs:
                # Check for hyperlinks
                if 'hyperlink' in run._element.xml:
                    links.append(run.text)
        return links
    
    def extract_all(self) -> dict:
        return {
            'file': self.file_name,
            'text': self.extract_text(),
            'tables': self.extract_tables(),
            'hyperlinks': self.extract_hyperlinks()
        }

# Usage
if __name__ == "__main__":
    docx_dir = Path("../data/DOCX/")
    
    for docx_file in docx_dir.glob("*.docx"):
        logger.info(f"Processing: {docx_file.name}")
        
        extractor = DOCXExtractor(str(docx_file))
        result = extractor.extract_all()
        
        output_file = Path("../raw_data") / f"{docx_file.stem}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
```

---

## 🔗 LINK EXTRACTION (Phase 2)

### Template: Link Extractor
**scripts/05_link_extractor.py:**

```python
import re
import json
from pathlib import Path
from urllib.parse import urljoin
import validators

class LinkExtractor:
    def __init__(self):
        self.url_pattern = r'https?://[^\s\)\]"\']+'
        self.all_links = set()
    
    def extract_from_text(self, text: str) -> list:
        """Extract URLs from text"""
        urls = re.findall(self.url_pattern, text)
        return [url for url in urls if validators.url(url)]
    
    def validate_link(self, url: str) -> dict:
        """Validate and classify link"""
        result = {
            'url': url,
            'valid': validators.url(url),
            'type': self.classify_link(url)
        }
        return result
    
    def classify_link(self, url: str) -> str:
        """Classify link by domain"""
        if 'app.getguru.com' in url:
            return 'guru_card'
        elif 'docs.google.com' in url:
            return 'google_sheet'
        elif 'vivli.org' in url:
            return 'internal'
        else:
            return 'external'
    
    def extract_from_sources(self, source_dir: Path) -> dict:
        """Extract links from all source files"""
        links = {}
        
        for json_file in source_dir.glob("*.json"):
            with open(json_file) as f:
                data = json.load(f)
            
            # Extract from text
            if 'text' in data:
                urls = self.extract_from_text(data['text'])
                links[json_file.stem] = urls
        
        return links

# Usage
if __name__ == "__main__":
    extractor = LinkExtractor()
    links = extractor.extract_from_sources(Path("../raw_data/"))
    
    # Save links
    output = {
        'total_links': sum(len(v) for v in links.values()),
        'by_source': links,
        'validated': {
            url: extractor.validate_link(url)
            for urls in links.values()
            for url in urls
        }
    }
    
    with open("../processed_data/extracted_links.json", 'w') as f:
        json.dump(output, f, indent=2)
```

---

## 🌐 WEB SCRAPING (Phase 3)

### Template: Web Scraper
**scripts/06_web_scraper.py:**

```python
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import hashlib
import json
from pathlib import Path

class WebScraper:
    def __init__(self, rate_limit=2):
        self.session = requests.Session()
        self.rate_limit = rate_limit  # seconds between requests
        self.scraped_content = {}
    
    def scrape_url(self, url: str) -> dict:
        """Scrape a single URL"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            content = {
                'url': url,
                'title': soup.title.string if soup.title else 'Unknown',
                'body': soup.get_text(),
                'status_code': response.status_code,
                'scraped_date': datetime.now().isoformat(),
                'content_hash': hashlib.sha256(soup.get_text().encode()).hexdigest()
            }
            
            return content
        
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'status': 'failed'
            }
    
    def scrape_guru_cards(self, card_ids: list) -> dict:
        """Scrape Guru cards"""
        results = {}
        
        for i, card_id in enumerate(card_ids):
            # Rate limiting
            if i > 0:
                time.sleep(self.rate_limit)
            
            url = f"https://app.getguru.com/card/{card_id}"
            print(f"Scraping: {url}")
            
            content = self.scrape_url(url)
            results[card_id] = content
        
        return results
    
    def scrape_recursive(self, start_urls: list, max_depth=3):
        """Recursively scrape URLs and follow links"""
        visited = set()
        queue = [(url, 0) for url in start_urls]  # (url, depth)
        
        while queue:
            url, depth = queue.pop(0)
            
            if url in visited or depth > max_depth:
                continue
            
            visited.add(url)
            print(f"Scraping [{depth}]: {url}")
            
            content = self.scrape_url(url)
            self.scraped_content[url] = content
            
            # Extract new links
            if 'body' in content:
                soup = BeautifulSoup(content['body'], 'html.parser')
                for link in soup.find_all('a', href=True):
                    new_url = link['href']
                    if new_url not in visited:
                        queue.append((new_url, depth + 1))
            
            time.sleep(self.rate_limit)
        
        return self.scraped_content

# Usage
if __name__ == "__main__":
    scraper = WebScraper(rate_limit=2)
    
    # Guru cards to scrape
    guru_cards = [
        'T74MLx5c',
        'T84rrG5c',
        # ... more card IDs
    ]
    
    results = scraper.scrape_guru_cards(guru_cards)
    
    # Save results
    output_dir = Path("../processed_data/web_content")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "guru_cards.json", 'w') as f:
        json.dump(results, f, indent=2)
```

---

## 📝 MARKDOWN CONVERSION (Phase 4)

### Template: Markdown Converter
**scripts/07_markdown_converter.py:**

```python
import json
from pathlib import Path
from datetime import datetime

class MarkdownConverter:
    def __init__(self):
        self.frontmatter_template = """---
title: {title}
source: {source}
source_type: {source_type}
date_extracted: {date}
category: {category}
tags: {tags}
confidence_score: {confidence}
---

"""
    
    def create_frontmatter(self, metadata: dict) -> str:
        """Create YAML frontmatter"""
        return self.frontmatter_template.format(
            title=metadata.get('title', 'Untitled'),
            source=metadata.get('source', 'unknown'),
            source_type=metadata.get('source_type', 'unknown'),
            date=datetime.now().isoformat(),
            category=metadata.get('category', 'uncategorized'),
            tags=metadata.get('tags', []),
            confidence=metadata.get('confidence_score', 0.0)
        )
    
    def convert_pdf_to_markdown(self, pdf_data: dict) -> str:
        """Convert extracted PDF data to markdown"""
        markdown = self.create_frontmatter({
            'title': pdf_data.get('file', 'Document'),
            'source_type': 'pdf',
            'category': 'guide'
        })
        
        markdown += f"# {pdf_data.get('file', 'Document')}\n\n"
        
        # Add text content
        text = pdf_data.get('text', '')
        markdown += text + "\n\n"
        
        # Add tables
        tables = pdf_data.get('tables', [])
        if tables:
            markdown += "## Tables\n\n"
            for i, table in enumerate(tables):
                markdown += f"### Table {i+1}\n\n"
                markdown += self.create_markdown_table(table) + "\n\n"
        
        # Add links
        links = pdf_data.get('links', [])
        if links:
            markdown += "## References\n\n"
            for link in links:
                markdown += f"- [{link.get('url')}]({link.get('url')})\n"
        
        return markdown
    
    def create_markdown_table(self, table_data: list) -> str:
        """Convert table data to markdown table"""
        if not table_data or len(table_data) == 0:
            return ""
        
        # Create header
        header = " | ".join(str(cell) for cell in table_data[0])
        separator = " | ".join(["---"] * len(table_data[0]))
        
        # Create rows
        rows = []
        for row in table_data[1:]:
            rows.append(" | ".join(str(cell) for cell in row))
        
        return f"{header}\n{separator}\n" + "\n".join(rows)
    
    def save_markdown(self, content: str, output_path: Path):
        """Save markdown to file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

# Usage
if __name__ == "__main__":
    converter = MarkdownConverter()
    
    raw_data_dir = Path("../raw_data/")
    output_dir = Path("../processed_data/markdown/")
    output_dir.mkdir(exist_ok=True)
    
    for json_file in raw_data_dir.glob("*.json"):
        with open(json_file) as f:
            data = json.load(f)
        
        markdown = converter.convert_pdf_to_markdown(data)
        
        output_file = output_dir / f"{json_file.stem}.md"
        converter.save_markdown(markdown, output_file)
        print(f"Converted: {output_file}")
```

---

## 🔢 EMBEDDING GENERATION (Phase 6)

### Template: Embedding Generator
**scripts/embedding_generator.py:**

```python
from openai import OpenAI
import json
from pathlib import Path
import asyncio

class EmbeddingGenerator:
    def __init__(self, model="text-embedding-3-large"):
        self.client = OpenAI()
        self.model = model
    
    def chunk_text(self, text: str, chunk_size=750, overlap=100) -> list:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i+chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def generate_embedding(self, text: str) -> list:
        """Generate embedding for text"""
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding
    
    def embed_document(self, doc_path: Path) -> dict:
        """Embed entire document with metadata"""
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from frontmatter
        title = doc_path.stem
        
        # Chunk content
        chunks = self.chunk_text(content)
        
        # Generate embeddings
        embeddings = []
        for i, chunk in enumerate(chunks):
            print(f"Embedding chunk {i+1}/{len(chunks)}")
            
            embedding = self.generate_embedding(chunk)
            embeddings.append({
                'chunk_id': f"{title}_chunk_{i}",
                'chunk_text': chunk[:200] + "...",  # Preview
                'embedding': embedding,
                'metadata': {
                    'document': title,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
            })
        
        return {
            'document': title,
            'total_chunks': len(chunks),
            'embeddings': embeddings
        }

# Usage
if __name__ == "__main__":
    generator = EmbeddingGenerator()
    
    markdown_dir = Path("../processed_data/markdown/")
    output_dir = Path("../processed_data/embeddings/")
    output_dir.mkdir(exist_ok=True)
    
    for md_file in markdown_dir.glob("*.md"):
        print(f"Processing: {md_file.name}")
        
        result = generator.embed_document(md_file)
        
        output_file = output_dir / f"{md_file.stem}_embeddings.json"
        with open(output_file, 'w') as f:
            json.dump(result, f)
        
        print(f"Saved embeddings to: {output_file}")
```

---

## 📌 PINECONE INDEXING

### Template: Pinecone Indexer
**scripts/pinecone_indexer.py:**

```python
from pinecone import Pinecone
import json
from pathlib import Path

class PineconeIndexer:
    def __init__(self, api_key: str, index_name: str):
        self.client = Pinecone(api_key=api_key)
        self.index = self.client.Index(index_name)
    
    def upsert_embeddings(self, embeddings_file: Path, batch_size=100):
        """Upsert embeddings to Pinecone"""
        with open(embeddings_file) as f:
            data = json.load(f)
        
        vectors = []
        for embedding in data['embeddings']:
            vectors.append({
                'id': embedding['chunk_id'],
                'values': embedding['embedding'],
                'metadata': {
                    **embedding['metadata'],
                    'text_preview': embedding['chunk_text']
                }
            })
        
        # Batch upsert
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            self.index.upsert(vectors=batch)
            print(f"Upserted {i+len(batch)}/{len(vectors)}")

# Usage
if __name__ == "__main__":
    indexer = PineconeIndexer(
        api_key="pk-...",
        index_name="vivli-chatbot-rag"
    )
    
    embeddings_dir = Path("../processed_data/embeddings/")
    
    for emb_file in embeddings_dir.glob("*_embeddings.json"):
        print(f"Indexing: {emb_file.name}")
        indexer.upsert_embeddings(emb_file)
```

---

## 🧪 TESTING & RETRIEVAL

### Template: Query Tester
**scripts/test_retrieval.py:**

```python
from pinecone import Pinecone

class QueryTester:
    def __init__(self, api_key: str, index_name: str):
        self.client = Pinecone(api_key=api_key)
        self.index = self.client.Index(index_name)
    
    def test_query(self, query: str, top_k=5):
        """Test a query"""
        # Generate embedding for query
        from openai import OpenAI
        openai_client = OpenAI()
        
        query_embedding = openai_client.embeddings.create(
            input=query,
            model="text-embedding-3-large"
        ).data[0].embedding
        
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Display results
        print(f"\nQuery: {query}\n")
        for i, match in enumerate(results['matches'], 1):
            print(f"{i}. Score: {match['score']:.4f}")
            print(f"   Document: {match['metadata']['document']}")
            print(f"   Preview: {match['metadata']['text_preview'][:100]}...")
            print()

# Usage
if __name__ == "__main__":
    tester = QueryTester(
        api_key="pk-...",
        index_name="vivli-chatbot-rag"
    )
    
    test_queries = [
        "How do I fix a form check failure?",
        "What is the process for data access?",
        "When will my request be reviewed?"
    ]
    
    for query in test_queries:
        tester.test_query(query)
```

---

## ✅ EXECUTION CHECKLIST

### Day 1-2: Setup
- [ ] Create folder structure
- [ ] Install dependencies
- [ ] Create config file
- [ ] Test environment

### Day 3-7: PDF Extraction
- [ ] Run PDF extractor on 11 guides
- [ ] Verify text quality
- [ ] Check OCR confidence
- [ ] Extract tables
- [ ] Extract links

### Day 8-14: DOCX, CSV, Links
- [ ] Extract DOCX files
- [ ] Process CSV chat export
- [ ] Process JSON
- [ ] Extract all links
- [ ] Validate links

### Day 15-21: Form Checks + Web Scraping
- [ ] Batch process 380 PDFs
- [ ] Scrape Guru Cards
- [ ] Scrape Google Sheets
- [ ] Deduplication
- [ ] Quality checks

### Day 22-25: Embedding + Indexing
- [ ] Chunk all documents
- [ ] Generate embeddings
- [ ] Create Pinecone index
- [ ] Upsert vectors

### Day 26-28: Testing
- [ ] Test retrieval
- [ ] Check quality metrics
- [ ] Optimize performance
- [ ] Deploy to production

---

## 📊 KEY METRICS TO TRACK

```
Extraction Phase:
- Documents processed: X/Y
- Success rate: X%
- OCR confidence avg: X%

Processing Phase:
- Markdown files created: X
- Total characters: X
- Duplicates found: X

Embedding Phase:
- Total chunks: X
- API calls made: X
- Cost: $X

Indexing Phase:
- Vectors indexed: X
- Query latency: Xms
- Memory usage: XGB

Testing Phase:
- Test queries passed: X/Y
- Precision@5: X
- Avg relevance score: X
```

---

**Ready to start implementing! Follow the code templates and use the execution checklist to stay on track.**
