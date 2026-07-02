# Tools & Azure Services Guide for Vivli Chatbot RAG

**Complete tooling overview with Azure alternatives**

---

## 📋 TOOLS BY CATEGORY

### 1. PDF & Document Extraction

| Tool | Purpose | Type | Cost |
|------|---------|------|------|
| **PyPDF2** | PDF text extraction | Python library | Free (open-source) |
| **pdfplumber** | Advanced PDF parsing (tables, text) | Python library | Free (open-source) |
| **EasyOCR** | Optical Character Recognition | Python library | Free (open-source) |
| **Tesseract** | OCR engine (alternative) | C library + Python wrapper | Free (open-source) |
| **python-docx** | Extract DOCX content | Python library | Free (open-source) |
| **openpyxl** | Parse Excel files | Python library | Free (open-source) |

**Azure Alternative:**
- **Azure Document Intelligence (Form Recognizer)** - Managed OCR & form extraction service
  - Pro: Enterprise-grade, handles complex layouts
  - Con: Per-document pricing (~$2-10 per page depending on model)
  - Best for: Large-scale production use, complex forms

---

### 2. Web Scraping & HTTP

| Tool | Purpose | Type | Cost |
|------|---------|------|------|
| **requests** | HTTP library for web requests | Python library | Free (open-source) |
| **BeautifulSoup4** | HTML parsing & extraction | Python library | Free (open-source) |
| **Selenium** | Browser automation (JS-heavy sites) | Python library | Free (open-source) |
| **Playwright** | Modern browser automation (alternative) | Python library | Free (open-source) |
| **httpx** | Modern HTTP client | Python library | Free (open-source) |

**Azure Alternative:**
- **Azure Bot Service** - For intelligent web data collection
  - Pro: Built-in logging, monitoring
  - Con: Overkill for simple scraping
  - Best for: Complex multi-step data collection workflows

---

### 3. Data Processing & Manipulation

| Tool | Purpose | Type | Cost |
|------|---------|------|------|
| **pandas** | Data manipulation & analysis | Python library | Free (open-source) |
| **numpy** | Numerical computing | Python library | Free (open-source) |
| **polars** | Fast dataframe processing | Python library | Free (open-source) |
| **lxml** | XML/HTML processing | Python library | Free (open-source) |

**Azure Alternative:**
- **Azure Data Factory** - Enterprise data orchestration
  - Pro: Visual pipeline builder, enterprise integration
  - Con: Overkill for simple processing, monthly costs
  - Best for: Complex data transformation workflows

---

### 4. Text Processing & Conversion

| Tool | Purpose | Type | Cost |
|------|---------|------|------|
| **markdown2** | Convert to Markdown | Python library | Free (open-source) |
| **python-slugify** | Create URL-friendly slugs | Python library | Free (open-source) |
| **chardet** | Detect text encoding | Python library | Free (open-source) |
| **langdetect** | Detect language | Python library | Free (open-source) |

---

### 5. Vector Embeddings

| Tool | Purpose | Type | Cost |
|------|---------|------|------|
| **OpenAI API** | Generate embeddings (text-embedding-3-large) | Cloud API | **$0.02 per 1M tokens** |
| **Sentence-Transformers** | Local embeddings (free alternative) | Python library | Free (open-source) |
| **Cohere Embeddings** | Alternative API | Cloud API | Similar pricing to OpenAI |
| **Hugging Face Models** | Free embeddings with transformers | Python library | Free (open-source) |

**Azure Alternative:**
- **Azure OpenAI Service** - Microsoft-hosted OpenAI models
  - Pro: Same quality as OpenAI, integrated with Azure ecosystem
  - Con: Slightly different pricing, requires Azure subscription
  - **RECOMMENDED for your use case** ✅

**Pricing Comparison:**
```
OpenAI API:           $0.02 per 1M tokens
Azure OpenAI:         $0.05 per 1K tokens (deployment cost) + $0.002 per 1K tokens (inference)
Sentence-Transformers: $0 (local) + compute cost
```

---

### 6. Vector Database

| Tool | Purpose | Type | Cost |
|------|---------|------|------|
| **Pinecone** | Managed vector database | SaaS | $0.10 per pod/day (starter: $12/month) |
| **Weaviate** | Self-hosted vector DB | Open-source | Free (self-hosted) + cloud pricing |
| **Milvus** | Distributed vector DB | Open-source | Free (self-hosted) |
| **Qdrant** | Vector database | Open-source + managed | Free (self-hosted) or managed pricing |
| **Chroma** | Lightweight vector DB | Open-source | Free (local) |

**Azure Alternative:**
- **Azure Cognitive Search** - AI-powered search with vector capabilities
  - Pro: Integrated with Azure AI, enterprise-ready
  - Con: Higher minimum cost (~$250/month)
  - Best for: Enterprise deployments
  - **RECOMMENDED** if you're committed to Azure ecosystem

**Cost Comparison for 1000 chunks:**
```
Pinecone:              $12-100/month (depending on queries)
Azure Cognitive Search: $250+/month (minimum)
Weaviate (self-hosted): $0 (on your infrastructure)
Milvus (self-hosted):  $0 (on your infrastructure)
```

---

### 7. RAG Frameworks & Orchestration

| Tool | Purpose | Type | Cost |
|------|---------|------|------|
| **LangChain** | RAG orchestration framework | Python library | Free (open-source) |
| **LlamaIndex** | Alternative RAG framework | Python library | Free (open-source) |
| **Haystack** | End-to-end RAG framework | Python library | Free (open-source) |

**Azure Alternative:**
- **Azure AI Search (Cognitive Search)** - Integrated RAG capabilities
- **Azure Machine Learning** - Full ML workflow orchestration
- **Azure OpenAI + Semantic Kernel** - Microsoft's RAG framework

---

### 8. Development & Testing

| Tool | Purpose | Type | Cost |
|------|---------|------|------|
| **pytest** | Unit testing | Python library | Free (open-source) |
| **black** | Code formatter | Python library | Free (open-source) |
| **flake8** | Linter | Python library | Free (open-source) |
| **mypy** | Type checker | Python library | Free (open-source) |
| **tqdm** | Progress bars | Python library | Free (open-source) |
| **colorama** | Terminal colors | Python library | Free (open-source) |

---

## 🏢 AZURE SERVICES FOR RAG PIPELINE

### **Option 1: Minimal Azure (Recommended for Budget-Conscious)**

```
Your Infrastructure:
├── Local Development
│   ├── Python (open-source libraries)
│   ├── Vector DB: Weaviate or Milvus (self-hosted)
│   └── Embedding: Sentence-Transformers (local)
│
└── Cloud Only:
    ├── Azure OpenAI Service (embeddings)
    └── Azure VM (host vector DB & API)

Monthly Cost: $50-150
```

### **Option 2: Azure-Native (Integrated, Enterprise)**

```
Your Infrastructure:
├── Data Collection & Processing
│   ├── Azure Document Intelligence (PDF/form extraction)
│   ├── Azure Data Factory (orchestration)
│   └── Azure Blob Storage (data storage)
│
├── AI & Embeddings
│   ├── Azure OpenAI Service (embeddings)
│   └── Azure Cognitive Services (NLP)
│
├── Vector Search
│   └── Azure Cognitive Search (vector search + RAG)
│
└── Deployment
    ├── Azure App Service (host chatbot API)
    └── Azure Monitor (logging & monitoring)

Monthly Cost: $500-2000+
```

### **Option 3: Hybrid (Balanced)**

```
Your Infrastructure:
├── Local Development
│   ├── Python libraries (free)
│   └── Open-source vector DB
│
└── Cloud Services
    ├── Azure OpenAI Service (embeddings)
    ├── Azure Blob Storage (data persistence)
    └── Azure App Service (host API)

Monthly Cost: $100-300
```

---

## 🎯 AZURE SERVICE DETAILS

### Azure Document Intelligence (Form Recognizer)
**Use for:** PDF extraction, OCR, form field extraction

**Capabilities:**
- Supports 200+ languages
- Handles handwriting
- Table extraction
- Forms analysis
- Layout analysis

**Pricing:**
```
Document Analysis: $2 per 1,000 pages
Layout Analysis: $0.50 per 1,000 pages
Read API: $1 per 1,000 pages
```

**Recommendation:** Use for Form Checks if you want enterprise-grade OCR

---

### Azure OpenAI Service
**Use for:** Text embeddings (text-embedding-3-large)

**Advantages:**
- Same models as OpenAI
- No rate limiting (dedicated quota)
- integrated with Azure ecosystem
- Same quality as OpenAI
- Data stays in your region

**Pricing:**
```
Model: text-embedding-3-large
$0.005 per 1K input tokens
For 1M tokens (your entire dataset): $5

That's MUCH cheaper than OpenAI's $0.02!
```

**✅ RECOMMENDED for this project**

---

### Azure Cognitive Search
**Use for:** Vector search and RAG

**Capabilities:**
- Vector search (1536-dim vectors)
- Hybrid search (keyword + vector)
- Semantic ranking
- RAG integration
- Built-in monitoring

**Pricing:**
```
Minimum: 1 Replica + 1 Partition = ~$250/month
Scaling: Add replicas as needed

For your use case: 1000 documents = probably 2-3 replicas
Estimated: $400-600/month
```

**Pros:**
- Everything integrated
- No separate vector DB needed
- Built-in RAG patterns
- Enterprise monitoring

**Cons:**
- Minimum $250/month cost
- Overkill if just prototyping

---

### Azure Data Factory
**Use for:** Orchestrating the data pipeline

**Capabilities:**
- Visual pipeline builder
- Data transformation
- Scheduling
- Error handling
- Monitoring

**Pricing:**
```
Pipeline runs: $1 per 1,000 runs
Data movement: $0.25 per GB moved
```

**Recommendation:** Only if processing >100GB of data regularly

---

## 💰 COST COMPARISON

### Scenario: Process 399 documents → 1000 embeddings

**Open-Source Only (Recommended for Development):**
```
Vector DB (self-hosted):    $0
Embeddings (Sentence-Trans): $0
Development VM (optional):   $30-100/month
─────────────────────────────
Total: $30-100/month (development only)
```

**Azure-Minimal (Production):**
```
Azure OpenAI (embeddings):   $5 (one-time for dataset)
Azure VM (vector DB host):   $30-100/month
Azure Storage:               $1-5/month
─────────────────────────────
Total: $36-106/month (production)
```

**Azure-Native (Full Enterprise):**
```
Azure OpenAI:                $5
Azure Cognitive Search:      $250-600/month
Azure Document Intelligence: $50-100 (one-time for extraction)
Azure App Service:           $50-150/month
Azure Monitor:               $10-20/month
─────────────────────────────
Total: $365-785/month (enterprise)
```

---

## 🎓 RECOMMENDED TECH STACK FOR YOUR PROJECT

### **Phase 1-5: Data Gathering (Development)**

```
Extraction:
  ✅ PyPDF2 + pdfplumber    (free, good enough)
  ⚠️  Azure Doc Intelligence (optional, if forms are complex)

Processing:
  ✅ pandas + python-docx    (free)
  ✅ Beautiful Soup           (free)

Storage:
  ✅ Local filesystem         (free, during dev)
  💡 Azure Blob Storage       (later, for backup)
```

### **Phase 6: Embedding & Indexing (Production)**

```
Embeddings:
  ✅ Azure OpenAI Service     (HIGHLY RECOMMENDED)
     └─ $5 for your 1M tokens
  Alternative: Sentence-Transformers (free but lower quality)

Vector Database:
  ✅ Weaviate Docker         (free, self-hosted)
  💡 Azure Cognitive Search   (enterprise option, $250+/month)
  Alternative: Milvus        (free, self-hosted)
```

### **Phase 7: Deployment (Production)**

```
API Hosting:
  ✅ Azure App Service        ($50-150/month)
  Alternative: AWS/GCP equivalent

Monitoring:
  ✅ Azure Monitor            ($10-20/month)
  Alternative: DataDog, New Relic

Orchestration:
  ✅ GitHub Actions           (free)
  Alternative: Azure DevOps (if corporate)
```

---

## 🛠️ STEP-BY-STEP IMPLEMENTATION GUIDE

### Week 1-3: Local Development (Zero Cost)

```
1. Extract documents locally
2. Use Sentence-Transformers for embeddings
3. Store vectors in Chroma (local vector DB)
4. Test end-to-end

Cost: $0
```

### Week 4-5: Production Prep (Minimal Cost)

```
1. Set up Azure OpenAI Service (create account)
2. Replace embeddings: Sentence-Transformers → Azure OpenAI
3. Deploy Weaviate on Azure VM
4. Migrate from Chroma → Weaviate

Cost: $5 (embeddings) + $30-100 (VM)
```

### Week 6+: Production (Ongoing)

```
1. Run pipeline with Azure OpenAI
2. Host API on Azure App Service
3. Monitor with Azure Monitor
4. Scale as needed

Cost: $5 (embeddings) + $50-150 (VM/App Service) + $10 (monitoring)
Total: $65-165/month
```

---

## ⚠️ AZURE SPECIFIC NOTES

### Why Azure OpenAI Instead of OpenAI?

| Feature | OpenAI | Azure OpenAI |
|---------|--------|--------------|
| Cost | $0.02 per 1M | $0.005 per 1K* |
| Rate Limits | Shared | Dedicated quota |
| Data Privacy | US data centers | Your region |
| Support | Community | Enterprise |
| Integration | REST API | Azure native |

*Azure's pricing is actually CHEAPER if you calculate correctly!

### Setting Up Azure OpenAI for Embeddings

```python
from azure.openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

response = client.embeddings.create(
    input="Your text here",
    model="text-embedding-3-large"  # deployment name
)
```

### Azure Cognitive Search Setup

```python
from azure.search.documents import SearchClient
from azure.search.documents.models import Vector

search_client = SearchClient(
    endpoint="https://your-resource.search.windows.net/",
    index_name="your-index",
    credential=AzureKeyCredential(key)
)

# Upsert with vectors
doc = {
    "id": "1",
    "content": "Your text",
    "vector": [0.1, 0.2, ..., 0.9]  # 1536 dims
}
search_client.upload_documents([doc])
```

---

## 🎯 MY RECOMMENDATION FOR YOUR PROJECT

### **Best Approach: Hybrid with Azure OpenAI**

```
Development Phase (Weeks 1-3):
├── Local extraction (free libraries)
├── Sentence-Transformers for testing (free)
└── Chroma for vector storage (free)

Production Phase (Weeks 4+):
├── ✅ Azure OpenAI Service (embeddings)
│   └─ Cost: $5 one-time for your dataset
│
├── ✅ Weaviate Docker on Azure VM
│   └─ Cost: $50-100/month
│
├── ✅ Azure App Service (host API)
│   └─ Cost: $50-100/month
│
└── ✅ Azure Monitor (logging)
    └─ Cost: $10/month

Total Monthly Cost: $110-210/month (production)
Total One-Time: ~$50 (Azure setup) + $5 (embeddings)
```

**Why this approach?**
- ✅ Most cost-effective
- ✅ Leverages Azure strengths (OpenAI embeddings)
- ✅ Easy to transition to full Azure ecosystem later
- ✅ No vendor lock-in (can switch vector DB easily)
- ✅ Enterprise-ready but lean

---

## 📊 FULL TOOL STACK FOR YOUR PROJECT

```
Data Extraction:
  ├── PyPDF2 + pdfplumber     ← PDFs
  ├── python-docx              ← DOCX
  ├── pandas                   ← CSV/JSON
  └── EasyOCR (optional)       ← OCR if needed

Web Scraping:
  ├── requests                 ← HTTP
  └── BeautifulSoup4           ← HTML parsing

Data Processing:
  ├── pandas                   ← Manipulation
  ├── markdown2                ← Format conversion
  └── python-slugify           ← URL generation

Embeddings:
  ├── Azure OpenAI Service     ← Production (RECOMMENDED)
  └── Sentence-Transformers    ← Development alternative

Vector DB:
  ├── Weaviate                 ← Recommended
  ├── Milvus                   ← Alternative
  └── Azure Cognitive Search   ← Enterprise option

RAG Framework:
  └── LangChain                ← Orchestration

Deployment:
  ├── Azure App Service        ← Host API
  ├── Azure Monitor            ← Logging
  └── Docker (optional)        ← Containerization

Development:
  ├── pytest                   ← Testing
  ├── black                    ← Formatting
  └── GitHub Actions           ← CI/CD
```

---

## ✅ QUICK DECISION MATRIX

**Choose based on your priorities:**

| Scenario | Recommendation |
|----------|-----------------|
| **Learning/Prototyping** | All open-source + local vector DB = $0 |
| **Small Team Startup** | Open-source + Azure OpenAI = $100-200/month |
| **Enterprise Production** | Full Azure stack = $400-800/month |
| **Cost-Sensitive** | Open-source everywhere = $30-100/month |
| **Time-Sensitive** | Azure Cognitive Search (ready-to-use) = $250+/month |

---

## 📚 NEXT STEPS

1. **For Development:** Start with local open-source tools
2. **For Embeddings:** Create Azure OpenAI account (free tier available)
3. **For Vector DB:** Docker Weaviate locally, migrate to VM later
4. **For Scaling:** Upgrade to Azure services as needed

---

**Recommendation: Use open-source for development, Azure OpenAI for production = Best of both worlds!** 🚀
