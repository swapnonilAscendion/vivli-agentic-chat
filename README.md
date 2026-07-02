# Vivli Chatbot - RAG-Based Conversational AI System

**Complete RAG-powered chatbot for Vivli form validation and data request guidance**

---

## 📋 PROJECT OVERVIEW

This project builds an intelligent chatbot using Retrieval-Augmented Generation (RAG) architecture that:
- Answers questions about Vivli data request forms (DRFs)
- Guides users through form validation
- Provides real-time help with common issues
- Learns from 399+ documents and web resources
- Uses Azure AI services for intelligence

**Status:** In Development  
**Start Date:** 2026-06-30  
**Team:** Data Science + Dev Ops

---

## 🎯 PROJECT GOALS

### Phase 1: Data Preparation (Weeks 1-4)
- ✓ Organize 399 resources by format
- ✓ Extract links and web content (22 URLs)
- → Create recursive scraper for intelligent content gathering
- → Process all PDFs, DOCX, and web content
- → Generate embeddings and index vectors

### Phase 2: RAG System (Weeks 5-8)
- Build vector search database
- Deploy LLM integration
- Create RAG pipeline
- Test retrieval quality

### Phase 3: Chatbot Interface (Weeks 9-12)
- Build API backend
- Create web chat interface
- Implement user authentication
- Deploy to Azure

### Phase 4: Production (Weeks 13+)
- Monitor performance
- Collect user feedback
- Iterate and improve
- Scale infrastructure

---

## 📁 PROJECT STRUCTURE

```
vivli-chatbot/
├── README.md                           ← You are here
│
├── docs/                               # Documentation
│   ├── guides/                         # Implementation guides
│   │   ├── 00_MASTER_INDEX.md         # Navigation guide
│   │   ├── RAG_DATA_PLAN.md            # 8-phase data strategy
│   │   ├── IMPLEMENTATION_GUIDE.md     # Code templates
│   │   ├── TOOLS_AND_AZURE_GUIDE.md    # Tech stack & Azure
│   │   └── RECURSIVE_SCRAPER_GUIDE.md  # Web scraper setup
│   │
│   └── architecture/                   # Architecture docs
│       ├── RAG_ARCHITECTURE.md         # System design
│       ├── DATA_FLOW.md                # Data pipeline
│       └── API_SPEC.md                 # API specifications
│
├── data-processing/                    # Data pipeline
│   ├── scripts/
│   │   ├── 01_pdf_extractor.py
│   │   ├── 02_docx_extractor.py
│   │   ├── 03_csv_processor.py
│   │   ├── 04_json_processor.py
│   │   ├── 05_link_extractor.py
│   │   ├── 06_web_scraper.py
│   │   ├── 07_markdown_converter.py
│   │   ├── 08_deduplication.py
│   │   └── 09_embedding_generator.py
│   │
│   └── config/
│       ├── settings.json
│       └── azure_config.env
│
├── resources/
│   ├── Vivli_Chatbot_Resource_Inventory.xlsx
│   │
│   └── organized-data/                 # 399 organized resources
│       ├── PDFs/
│       │   ├── Guides/ (9 files)
│       │   ├── DRF_Samples/ (1 file)
│       │   ├── Architecture/ (1 file)
│       │   └── Form_Checks/ (380 files)
│       ├── DOCX/ (3 files)
│       ├── XLSX/ (1 file)
│       ├── CSV/ (2 files)
│       ├── JSON/ (1 file)
│       └── Links/ (22 URLs)
│
├── testing/                            # Testing & validation
│   ├── test_scraper.py
│   ├── test_extraction.py
│   ├── test_embeddings.py
│   └── test_retrieval.py
│
└── deployment/                         # Deployment configs
    ├── azure_deployment.yaml
    ├── docker-compose.yml
    └── kubernetes_manifest.yaml
```

---

## 🚀 QUICK START

### Prerequisites
- Python 3.10+
- Azure Subscription
- Git

### Setup (30 minutes)

#### 1. Clone & Navigate
```bash
cd vivli-chatbot
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

#### 2. Configure Azure
```bash
# Install Azure CLI
# Create resources (see TOOLS_AND_AZURE_GUIDE.md)
# Get keys from Azure Portal
```

#### 3. Setup Environment
```bash
cp data-processing/config/azure_config.env .env
# Edit .env with your Azure keys
```

#### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 5. Test Scraper
```bash
python testing/test_scraper.py
```

#### 6. Run Data Pipeline
```bash
cd data-processing/scripts
python 01_pdf_extractor.py
python 06_web_scraper.py
python 09_embedding_generator.py
```

---

## 📚 DOCUMENTATION MAP

| Document | Purpose | Time | Location |
|----------|---------|------|----------|
| **00_MASTER_INDEX.md** | Navigation hub | 10 min | docs/guides/ |
| **RAG_DATA_PLAN.md** | Complete strategy (8 phases) | 30 min | docs/guides/ |
| **IMPLEMENTATION_GUIDE.md** | Code templates & setup | 20 min | docs/guides/ |
| **TOOLS_AND_AZURE_GUIDE.md** | Tech stack & Azure options | 15 min | docs/guides/ |
| **RECURSIVE_SCRAPER_GUIDE.md** | Build web scraper | 25 min | docs/guides/ |

---

## 🔧 ARCHITECTURE

```
User Query
    ↓
[Chat API]
    ↓
[Query Processing]
    ├─ Intent Detection
    ├─ Entity Extraction
    └─ Query Expansion
         ↓
[Vector Search]
    ├─ Azure Cognitive Search
    ├─ Query Embedding (Azure OpenAI)
    └─ Retrieve Top-K Documents
         ↓
[Context Assembly]
    ├─ Deduplicate results
    ├─ Rank by relevance
    └─ Create context window
         ↓
[LLM Response Generation]
    ├─ Azure OpenAI
    ├─ Prompt engineering
    └─ Response formatting
         ↓
[Post-Processing]
    ├─ Citation generation
    ├─ Confidence scoring
    └─ User feedback collection
         ↓
User Response
```

---

## 📊 DATA PIPELINE

### Phase 1: Extraction (Days 3-7)
```
PDFs (311) + DOCX (3) + CSV (1) + JSON (1)
    ↓
Extract: Text, Tables, Images, Links
    ↓
Raw content (JSON format)
```

### Phase 2: Web Scraping (Days 8-15)
```
22 Extracted URLs (Guru Cards)
    ↓
Recursive scraping (depth: 3)
    ↓
Enriched content
```

### Phase 3: Processing (Days 16-22)
```
All content
    ↓
Markdown conversion + Standardization
    ↓
Deduplication (hash-based)
    ↓
Quality scoring
    ↓
Clean, deduplicated markdown (600+ files)
```

### Phase 4: Embedding & Indexing (Days 23-25)
```
Markdown files
    ↓
Chunking (500-1000 tokens)
    ↓
Azure OpenAI embeddings (1536-dim)
    ↓
Pinecone/Weaviate indexing
    ↓
Production-ready vector DB
```

---

## 🛠️ TECHNOLOGY STACK

### Data Processing
- **PDF:** PyPDF2 + pdfplumber
- **OCR:** EasyOCR
- **DOCX:** python-docx
- **Web:** BeautifulSoup4 + requests
- **Data:** pandas

### Azure Services
- **Document Intelligence:** PDF/form extraction
- **Computer Vision:** Image analysis & OCR
- **OpenAI Service:** Text embeddings
- **Cognitive Search:** Vector search (optional)
- **Blob Storage:** Data persistence
- **App Service:** API hosting

### Vector & RAG
- **Embeddings:** Azure OpenAI (text-embedding-3-large)
- **Vector DB:** Weaviate or Pinecone
- **Framework:** LangChain
- **LLM:** Azure OpenAI (GPT-4)

### DevOps
- **CI/CD:** GitHub Actions
- **Containerization:** Docker
- **Orchestration:** Kubernetes (optional)
- **Monitoring:** Azure Monitor

---

## 📈 KEY METRICS

### Data Metrics
- Documents: 399 sources
- After extraction: 600+ markdown files
- Vector chunks: 1000+
- Embeddings: 1536-dimensional
- Links: 22 (Guru Cards + references)

### Quality Metrics
- OCR confidence: >90%
- Extraction completeness: >95%
- Quality score: >0.90
- Deduplication rate: <5%

### RAG Metrics
- Retrieval MRR: >0.8
- Precision@5: >0.6
- Query latency: <200ms
- Throughput: >100 queries/sec

---

## 🎯 CURRENT PROGRESS

### ✅ Completed (2026-06-30)
- ✓ Resource library created (399 files organized)
- ✓ 8-phase data strategy documented
- ✓ Technology stack finalized
- ✓ Azure services identified
- ✓ Recursive scraper design completed
- ✓ Code templates prepared

### 🔄 In Progress
- → Implementation guide finalization
- → Scraper testing with sample PDFs
- → Azure resource provisioning

### ⏳ Next Steps
- Data extraction pipeline (Weeks 1-2)
- Web scraping (Weeks 3-4)
- Markdown conversion (Weeks 5-6)
- Embedding generation (Weeks 7-8)
- Vector indexing (Weeks 9-10)
- Chatbot deployment (Weeks 11-12)

---

## 💡 KEY DECISIONS

### Why Azure?
- Client subscription available
- Azure OpenAI cheaper than OpenAI ($5 vs $20 for this dataset)
- Enterprise support
- Data residency compliance

### Why RAG Instead of Fine-tuning?
- Lower cost (no model fine-tuning)
- Easier to update (just update documents)
- Better for Q&A systems
- Reduced hallucination

### Why Weaviate/Pinecone?
- Weaviate: Free software, self-hosted flexibility
- Pinecone: Managed service, easy scaling
- Both support semantic search at scale

---

## 📞 SUPPORT & RESOURCES

### Documentation
- See `docs/guides/00_MASTER_INDEX.md` for navigation
- See `docs/guides/RAG_DATA_PLAN.md` for detailed strategy
- See `docs/guides/TOOLS_AND_AZURE_GUIDE.md` for tech stack

### Azure Documentation
- [Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/)
- [Computer Vision](https://learn.microsoft.com/azure/ai-services/computer-vision/)
- [Cognitive Search](https://learn.microsoft.com/azure/search/)
- [OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)

### Open Source
- [LangChain Docs](https://python.langchain.com/)
- [Weaviate Docs](https://weaviate.io/developers)
- [Pinecone Docs](https://docs.pinecone.io/)

---

## 📝 DEVELOPMENT WORKFLOW

### Daily Development
1. Check progress on current phase
2. Review logs in `data-processing/logs/`
3. Update resource inventory as needed
4. Commit changes with clear messages

### Testing
- Unit tests: `testing/test_*.py`
- Integration tests: Run full pipeline
- Performance tests: Latency & throughput
- User acceptance: ChatBot testing

### Deployment
1. Test in staging environment
2. Run smoke tests
3. Monitor metrics
4. Deploy to production
5. Monitor performance

---

## 📊 PROJECT TIMELINE

```
Week 1: Data extraction pipeline
Week 2: Web scraping & link following
Week 3: Markdown conversion
Week 4: Quality assurance & deduplication
Week 5-6: Embedding generation
Week 7: Vector database indexing
Week 8: RAG system testing
Week 9-10: Chatbot API development
Week 11-12: Frontend & deployment
Week 13+: Production monitoring
```

---

## 🔐 Security Considerations

- ✓ Store Azure keys in `.env` (never in code)
- ✓ Use managed identities for Azure services
- ✓ Implement API authentication
- ✓ Audit logging for all operations
- ✓ Rate limiting on API endpoints
- ✓ PII handling in compliance with regulations

---

## 📈 SCALING STRATEGY

### Phase 1: MVP (Current)
- Single instance deployment
- Manual data updates
- 100 concurrent users

### Phase 2: Growth
- Load balancer + multiple instances
- Automated pipeline scheduling
- 1000 concurrent users
- Caching layer

### Phase 3: Enterprise
- Multi-region deployment
- Advanced analytics
- Custom models per domain
- 10,000+ concurrent users

---

## 🎓 LEARNING RESOURCES

The project includes comprehensive guides on:
1. **RAG Architecture** - How to build production RAG systems
2. **Data Processing** - PDF extraction, web scraping, text processing
3. **Azure Services** - Optimal use of Azure AI services
4. **Vector Databases** - Scaling similarity search
5. **LLM Integration** - Prompt engineering, response generation

---

## 📞 CONTACT & CONTRIBUTION

**Project Lead:** [Your Name]  
**Start Date:** 2026-06-30  
**Status:** Active Development

For questions:
1. Check the documentation in `docs/guides/`
2. Review the relevant guide file
3. Refer to code comments and examples

---

## 📄 LICENSE

[Your License Here]

---

## ✅ CHECKLIST FOR SUCCESS

- [ ] Read all documentation in `docs/guides/`
- [ ] Setup Azure resources and get keys
- [ ] Configure `.env` file
- [ ] Install Python dependencies
- [ ] Run test scraper with sample PDF
- [ ] Execute data extraction pipeline
- [ ] Generate embeddings
- [ ] Index vectors in database
- [ ] Build chatbot API
- [ ] Deploy to Azure
- [ ] Monitor production metrics
- [ ] Collect user feedback
- [ ] Iterate and improve

---

**Welcome to the Vivli Chatbot project! Start with the guides in `docs/guides/` and follow the timeline above.** 🚀

---

*Last Updated: 2026-06-30*  
*Project Status: In Development*
