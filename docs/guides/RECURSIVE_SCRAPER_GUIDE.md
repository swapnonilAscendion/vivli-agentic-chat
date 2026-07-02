# Recursive Data Scraper with Azure Services

**Complete guide for building a smart recursive scraper with intelligent data extraction**

---

## 🎯 ARCHITECTURE OVERVIEW

Your scraper will do this:

```
Input PDF/URL
    ↓
├─ Extract Content (text, links)
├─ Detect Tables → Azure Document Intelligence
├─ Detect Images → Azure Computer Vision
├─ Extract Links
│   ↓
└─ For each link:
    ├─ Add to queue
    ├─ Visit recursively (max depth 3)
    ├─ Extract content
    └─ Repeat process
    
Output: Structured data (JSON/Markdown)
```

---

## 📋 AZURE SERVICES NEEDED

### 1. **Azure Document Intelligence (Form Recognizer)**
**What:** Extract tables, forms, text from PDFs with high accuracy
```
Capabilities:
- Read API (extract text with layout)
- Layout API (detect tables, headers, paragraphs)
- Document analysis (forms, invoices)
```

### 2. **Azure Computer Vision**
**What:** Detect and extract images, OCR, image analysis
```
Capabilities:
- Image analysis (detect objects, text)
- Read API (OCR)
- Spatial analysis
```

### 3. **Azure Blob Storage**
**What:** Store PDFs and extracted data
```
Capabilities:
- Store uploaded PDFs
- Store extracted images
- Backup results
```

### 4. **Azure Cosmos DB (Optional)**
**What:** Store extracted data with relationships
```
Capabilities:
- Store document metadata
- Track processing status
- Store extracted content
```

---

## 🔧 SETUP: Azure Resources

### Step 1: Create Azure Resources

```bash
# Using Azure CLI
az group create --name vivli-scraper --location eastus

# Document Intelligence
az cognitiveservices account create \
  --name vivli-doc-intelligence \
  --resource-group vivli-scraper \
  --kind FormRecognizer \
  --sku S0 \
  --location eastus

# Computer Vision
az cognitiveservices account create \
  --name vivli-vision \
  --resource-group vivli-scraper \
  --kind ComputerVision \
  --sku S0 \
  --location eastus

# Blob Storage
az storage account create \
  --name vivistorage \
  --resource-group vivli-scraper \
  --kind StorageV2
```

### Step 2: Get Connection Strings

```bash
# Get keys for Document Intelligence
az cognitiveservices account keys list \
  --name vivli-doc-intelligence \
  --resource-group vivli-scraper

# Get keys for Computer Vision
az cognitiveservices account keys list \
  --name vivli-vision \
  --resource-group vivli-scraper

# Get Blob Storage connection string
az storage account show-connection-string \
  --name vivistorage \
  --resource-group vivli-scraper
```

### Step 3: Create .env file

```bash
# .env
AZURE_DOC_INTELLIGENCE_KEY=your_key_here
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://region.api.cognitive.microsoft.com/
AZURE_VISION_KEY=your_key_here
AZURE_VISION_ENDPOINT=https://region.api.cognitive.microsoft.com/
AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
AZURE_STORAGE_CONTAINER=vivli-documents
```

---

## 💻 COMPLETE RECURSIVE SCRAPER SCRIPT

### Main Scraper Class

**File: `scraper.py`**

```python
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import deque
import hashlib

import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import asyncio

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AzureDocumentExtractor:
    """Extract content from PDFs using Azure Document Intelligence"""
    
    def __init__(self):
        self.client = DocumentIntelligenceClient(
            endpoint=os.getenv('AZURE_DOC_INTELLIGENCE_ENDPOINT'),
            credential=AzureKeyCredential(os.getenv('AZURE_DOC_INTELLIGENCE_KEY'))
        )
    
    def extract_from_pdf(self, pdf_path: str) -> Dict:
        """
        Extract text, tables, and structure from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with extracted content
        """
        logger.info(f"Extracting content from PDF: {pdf_path}")
        
        with open(pdf_path, 'rb') as pdf_file:
            poller = self.client.begin_analyze_document(
                "prebuilt-layout",
                analyze_request=AnalyzeDocumentRequest(pdf_file=pdf_file)
            )
            result = poller.result()
        
        # Extract text
        full_text = ""
        for page in result.pages:
            for line in page.lines:
                full_text += line.content + "\n"
        
        # Extract tables
        tables = []
        for table in result.tables:
            table_data = {
                'cells': [],
                'rows': table.row_count,
                'cols': table.column_count
            }
            for cell in table.cells:
                table_data['cells'].append({
                    'row': cell.row_index,
                    'col': cell.column_index,
                    'content': cell.content
                })
            tables.append(table_data)
        
        return {
            'text': full_text,
            'tables': tables,
            'page_count': len(result.pages),
            'extracted_at': datetime.now().isoformat()
        }


class AzureImageProcessor:
    """Process and analyze images using Azure Computer Vision"""
    
    def __init__(self):
        self.client = ImageAnalysisClient(
            endpoint=os.getenv('AZURE_VISION_ENDPOINT'),
            credential=AzureKeyCredential(os.getenv('AZURE_VISION_KEY'))
        )
    
    def analyze_image(self, image_url: str) -> Dict:
        """
        Analyze image for objects, text, and metadata
        
        Args:
            image_url: URL to image
            
        Returns:
            Dict with analysis results
        """
        logger.info(f"Analyzing image: {image_url}")
        
        try:
            result = self.client.analyze_from_url(
                image_url=image_url,
                visual_features=[
                    VisualFeatures.OBJECTS,
                    VisualFeatures.TEXT,
                    VisualFeatures.TAGS
                ]
            )
            
            return {
                'objects': [
                    {'name': obj.tags[0].name, 'confidence': obj.tags[0].confidence}
                    for obj in result.objects
                ] if result.objects else [],
                'text': result.read.content if result.read else "",
                'tags': [tag.name for tag in result.tags] if result.tags else [],
                'analyzed_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {'error': str(e)}


class BlobStorageManager:
    """Manage storage of documents and extracted data"""
    
    def __init__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(
            os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        )
        self.container_name = os.getenv('AZURE_STORAGE_CONTAINER', 'vivli-documents')
        
        # Create container if it doesn't exist
        try:
            self.blob_service_client.create_container(name=self.container_name)
        except:
            pass  # Container already exists
    
    def upload_file(self, file_path: str, blob_name: str) -> str:
        """Upload file to Blob Storage"""
        logger.info(f"Uploading {file_path} to blob storage")
        
        container_client = self.blob_service_client.get_container_client(
            self.container_name
        )
        
        with open(file_path, 'rb') as data:
            container_client.upload_blob(name=blob_name, data=data, overwrite=True)
        
        return f"{self.blob_service_client.account_name}/{self.container_name}/{blob_name}"
    
    def download_file(self, blob_name: str, download_path: str) -> bool:
        """Download file from Blob Storage"""
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            blob_client = container_client.get_blob_client(blob_name)
            
            with open(download_path, 'wb') as file:
                file.write(blob_client.download_blob().readall())
            
            return True
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return False


class RecursiveWebScraper:
    """Main recursive scraper with link following and content extraction"""
    
    def __init__(self, max_depth: int = 3, rate_limit: float = 2.0):
        """
        Initialize scraper
        
        Args:
            max_depth: Maximum recursion depth
            rate_limit: Delay between requests (seconds)
        """
        self.max_depth = max_depth
        self.rate_limit = rate_limit
        self.visited_urls = set()
        self.visited_hashes = set()
        
        self.doc_extractor = AzureDocumentExtractor()
        self.image_processor = AzureImageProcessor()
        self.storage_manager = BlobStorageManager()
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _get_content_hash(self, content: str) -> str:
        """Generate hash of content for deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def scrape_pdf(self, pdf_path: str) -> Dict:
        """
        Scrape PDF and extract all content
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with extracted content
        """
        logger.info(f"Starting PDF scrape: {pdf_path}")
        
        # Extract using Azure Document Intelligence
        content = self.doc_extractor.extract_from_pdf(pdf_path)
        
        # Extract links from text
        links = self._extract_links_from_text(content['text'])
        
        return {
            'source': pdf_path,
            'type': 'pdf',
            'content': content,
            'links_found': links,
            'extracted_at': datetime.now().isoformat()
        }
    
    def _extract_links_from_text(self, text: str) -> List[str]:
        """Extract URLs from text"""
        import re
        
        url_pattern = r'https?://[^\s\)"\']+'
        urls = re.findall(url_pattern, text)
        
        # Filter and validate
        valid_urls = []
        for url in urls:
            if url not in self.visited_urls and len(valid_urls) < 10:  # Limit to 10 per doc
                valid_urls.append(url)
                self.visited_urls.add(url)
        
        return valid_urls
    
    async def scrape_url_recursive(self, url: str, depth: int = 0) -> Dict:
        """
        Recursively scrape URL and follow links
        
        Args:
            url: URL to scrape
            depth: Current recursion depth
            
        Returns:
            Dict with scraped content
        """
        if depth > self.max_depth:
            logger.info(f"Max depth reached for {url}")
            return None
        
        if url in self.visited_urls:
            logger.info(f"URL already visited: {url}")
            return None
        
        self.visited_urls.add(url)
        
        logger.info(f"Scraping [{depth}/{self.max_depth}]: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text
            text = soup.get_text()
            content_hash = self._get_content_hash(text)
            
            # Check if already processed
            if content_hash in self.visited_hashes:
                logger.info(f"Duplicate content detected: {url}")
                return None
            
            self.visited_hashes.add(content_hash)
            
            # Extract images
            images = []
            for img in soup.find_all('img'):
                img_url = img.get('src')
                if img_url:
                    if not img_url.startswith('http'):
                        img_url = url.rsplit('/', 1)[0] + '/' + img_url
                    images.append(img_url)
            
            # Extract tables
            tables = []
            for table in soup.find_all('table'):
                table_rows = []
                for tr in table.find_all('tr'):
                    row = [td.get_text() for td in tr.find_all(['td', 'th'])]
                    table_rows.append(row)
                tables.append(table_rows)
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if not href.startswith('http'):
                    href = url.rsplit('/', 1)[0] + '/' + href
                if href not in self.visited_urls:
                    links.append(href)
            
            result = {
                'url': url,
                'depth': depth,
                'text_content': text[:1000],  # First 1000 chars
                'images': images,
                'tables': tables,
                'links_found': links,
                'content_hash': content_hash,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Recursively scrape found links
            if depth < self.max_depth and links:
                result['child_content'] = []
                
                for link in links[:3]:  # Limit to 3 children per page
                    # Rate limiting
                    await asyncio.sleep(self.rate_limit)
                    
                    try:
                        child_content = await self.scrape_url_recursive(link, depth + 1)
                        if child_content:
                            result['child_content'].append(child_content)
                    except Exception as e:
                        logger.error(f"Error scraping child link {link}: {e}")
                        continue
            
            return result
        
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    async def process_extracted_data(self, data: Dict) -> Dict:
        """
        Process extracted content and analyze with Azure services
        
        Args:
            data: Extracted content dict
            
        Returns:
            Processed content with AI insights
        """
        logger.info("Processing extracted data")
        
        # Analyze images if found
        if data.get('images'):
            image_analyses = []
            for img_url in data['images'][:5]:  # Limit to 5 images
                try:
                    analysis = self.image_processor.analyze_image(img_url)
                    image_analyses.append({
                        'url': img_url,
                        'analysis': analysis
                    })
                except Exception as e:
                    logger.error(f"Error analyzing image {img_url}: {e}")
            
            data['image_analyses'] = image_analyses
        
        return data
    
    async def run(self, pdf_path: Optional[str] = None, 
                  start_url: Optional[str] = None) -> Dict:
        """
        Run scraper for PDF or URL
        
        Args:
            pdf_path: Path to PDF file (optional)
            start_url: Starting URL (optional)
            
        Returns:
            Complete scraped data
        """
        result = {
            'execution_start': datetime.now().isoformat(),
            'sources': []
        }
        
        # Scrape PDF if provided
        if pdf_path:
            pdf_data = await self.scrape_pdf(pdf_path)
            result['sources'].append(pdf_data)
            
            # Scrape links found in PDF
            links = pdf_data.get('links_found', [])
            for link in links[:3]:  # Limit to 3 links
                await asyncio.sleep(self.rate_limit)
                url_data = await self.scrape_url_recursive(link)
                if url_data:
                    result['sources'].append(url_data)
        
        # Scrape URL if provided
        elif start_url:
            url_data = await self.scrape_url_recursive(start_url)
            if url_data:
                result['sources'].append(url_data)
        
        result['execution_end'] = datetime.now().isoformat()
        result['total_items_scraped'] = len(result['sources'])
        
        return result


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

async def main():
    """Main execution"""
    
    scraper = RecursiveWebScraper(max_depth=2, rate_limit=2)
    
    # Example 1: Scrape a PDF
    pdf_path = "sample.pdf"
    if Path(pdf_path).exists():
        result = await scraper.run(pdf_path=pdf_path)
        
        # Save results
        with open('scrape_results.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Scraped {result['total_items_scraped']} items")
        print(json.dumps(result, indent=2))
    
    # Example 2: Scrape a URL
    # result = await scraper.run(start_url="https://example.com")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🧪 TESTING WITH A SAMPLE PDF

### Step 1: Prepare Test PDF

```python
# Create a minimal test PDF with requests library
import requests

# Download a sample PDF to test
url = "https://www.w3.org/WAI/WCAG21/Techniques/pdf/img/word2007-headings.pdf"
response = requests.get(url)

with open("test_sample.pdf", "wb") as f:
    f.write(response.content)

print("Sample PDF downloaded")
```

### Step 2: Run the Scraper

```python
import asyncio
from scraper import RecursiveWebScraper

async def test():
    scraper = RecursiveWebScraper(max_depth=2)
    
    # Scrape the test PDF
    result = await scraper.run(pdf_path="test_sample.pdf")
    
    # Print results
    print(f"Extracted text: {result['sources'][0]['content']['text'][:500]}")
    print(f"Tables found: {len(result['sources'][0]['content']['tables'])}")
    print(f"Links found: {result['sources'][0]['links_found']}")

asyncio.run(test())
```

### Step 3: Check Output

```json
{
  "execution_start": "2026-06-30T10:30:00",
  "sources": [
    {
      "source": "test_sample.pdf",
      "type": "pdf",
      "content": {
        "text": "extracted text here...",
        "tables": [],
        "page_count": 5,
        "extracted_at": "2026-06-30T10:30:05"
      },
      "links_found": [
        "https://example.com/page1",
        "https://example.com/page2"
      ]
    },
    {
      "url": "https://example.com/page1",
      "depth": 1,
      "text_content": "content here...",
      "images": ["url1", "url2"],
      "tables": [[...], [...]]
    }
  ],
  "total_items_scraped": 2
}
```

---

## 🔍 FEATURES EXPLANATION

### 1. **PDF Processing**
- Uses Azure Document Intelligence
- Extracts text with layout preservation
- Detects and extracts tables
- Identifies page structure

### 2. **Image Handling**
- Azure Computer Vision analyzes images
- Detects objects and text in images
- Extracts OCR content
- Provides image classification

### 3. **Link Discovery**
- Regex pattern matching for URLs
- Deduplication with visited_urls set
- HTML link parsing with BeautifulSoup
- Relative URL resolution

### 4. **Recursive Following**
- Configurable max depth (default: 3)
- Queue-based processing
- Rate limiting between requests
- Deduplication by content hash

### 5. **Data Storage**
- Azure Blob Storage for documents
- Structured JSON output
- Processing logs
- Metadata tracking

---

## 📊 OUTPUT STRUCTURE

```json
{
  "execution_start": "ISO timestamp",
  "sources": [
    {
      "source": "PDF path or URL",
      "type": "pdf|html",
      "depth": "recursion depth",
      "content": {
        "text": "extracted text",
        "tables": [["cell1", "cell2"]],
        "page_count": "number"
      },
      "images": ["url1", "url2"],
      "image_analyses": [
        {
          "url": "image url",
          "analysis": {
            "objects": ["object1"],
            "text": "ocr text",
            "tags": ["tag1"]
          }
        }
      ],
      "links_found": ["url1", "url2"],
      "child_content": [...]  // Recursively nested
    }
  ],
  "total_items_scraped": "number"
}
```

---

## ⚡ QUICK START CHECKLIST

- [ ] Create Azure resources (Document Intelligence, Computer Vision, Blob Storage)
- [ ] Get API keys and connection strings
- [ ] Create .env file with credentials
- [ ] Install required libraries: `pip install -r requirements.txt`
- [ ] Download or prepare a test PDF
- [ ] Run the scraper with test PDF
- [ ] Check results in JSON output
- [ ] Customize for your needs

---

## 📦 REQUIREMENTS.TXT

```
requests==2.31.0
beautifulsoup4==4.12.0
pillow==10.0.0
python-dotenv==1.0.0
azure-ai-documentintelligence==1.0.0
azure-ai-vision-imageanalysis==1.0.0
azure-storage-blob==12.16.0
azure-cosmos==4.5.0
```

---

## 🚀 NEXT STEPS

1. **Setup Azure Resources** (15 min)
   - Create resource group
   - Create Document Intelligence service
   - Create Computer Vision service
   - Get keys

2. **Configure Environment** (5 min)
   - Set .env file
   - Test Azure connectivity

3. **Test with Sample PDF** (10 min)
   - Run scraper with test PDF
   - Verify extraction works
   - Check image processing

4. **Customize for Your Data** (varies)
   - Adjust max_depth for recursion
   - Modify extraction logic
   - Add custom processors

5. **Scale to Production** (varies)
   - Add error handling
   - Implement retry logic
   - Set up monitoring
   - Deploy to Azure Functions (optional)

---

## 💡 TIPS & TRICKS

**To extract from specific elements:**
```python
# Extract only from specific DOM elements
content = soup.select('.main-content')[0].get_text()
```

**To handle authentication:**
```python
session.auth = ('username', 'password')
# or
session.headers['Authorization'] = f'Bearer {token}'
```

**To save images locally:**
```python
for img_url in data['images']:
    img_response = requests.get(img_url)
    with open(f"image_{i}.png", 'wb') as f:
        f.write(img_response.content)
```

**To filter links by domain:**
```python
def is_in_scope(url):
    return 'yourdomain.com' in url
```

**To increase recursion depth cautiously:**
```python
scraper = RecursiveWebScraper(max_depth=4)  # Be careful: exponential growth!
```

---

**Ready to build your recursive scraper! Start with the setup and test it with a sample PDF.** 🚀
