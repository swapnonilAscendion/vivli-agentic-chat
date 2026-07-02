# RAG Document Ingestion Setup Guide

Complete guide to ingest your documents into Azure AI Search and enable the chatbot to answer questions.

---

## 📋 Overview

The ingestion pipeline will:
1. ✅ Create an Azure AI Search index
2. ✅ Load documents from your `/organized-data/` directory
3. ✅ Split documents into semantic chunks
4. ✅ Embed chunks using Azure OpenAI
5. ✅ Index everything in Azure AI Search

---

## 🚀 Quick Start (3 Steps)

### Step 1: Create Azure AI Search Index

```powershell
cd "c:\Users\swapnonil.mukherjee\projects\vivli-chatbot\rag-demo"

# First time only - create the search index
python -c "from index_manager import IndexManager; mgr = IndexManager(); print('Index created!' if mgr.create_index() else 'Index already exists')"
```

Expected output:
```
Index created!
```

---

### Step 2: Verify Your Azure Credentials

Make sure your `.env` file has all the required credentials:

```env
AZURE_OPENAI_API_KEY=[your_key]
AZURE_OPENAI_ENDPOINT=https://vivli-common-eus-ops-ai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_EMBEDDING=text-embedding-3-large
AZURE_OPENAI_DEPLOYMENT_LLM=gpt-4o-mini
AZURE_SEARCH_ENDPOINT=https://vivli-demo-cus-srch.search.windows.net
AZURE_SEARCH_ADMIN_KEY=[your_key]
AZURE_SEARCH_INDEX_NAME=vivli-knowledge-base
```

---

### Step 3: Run Ingestion Pipeline

**Option A: Use Sample Documents (FASTEST - 2 minutes)**
```powershell
python ingestion_pipeline.py --sample
```

This loads 3 sample Vivli FAQ documents and indexes them.

**Option B: Load Your Real Documents**
```powershell
python ingestion_pipeline.py
```

This will:
- Load all markdown files (`.md`)
- Load all PDF files (`.pdf`)
- Load all text files (`.txt`)
- Load all Word documents (`.docx`)
- Load all JSON files (`.json`)
- Load all CSV files (`.csv`)
- Load all Excel files (`.xlsx`)
- If no documents found, uses samples as fallback

All files are searched recursively from `/organized-data/` and all subdirectories.

---

## 📊 What Each Component Does

### **index_manager.py**
Creates the Azure AI Search index with:
- Text search fields (title, content)
- Metadata fields (source, chunk_index)
- Vector search field (embedding with 1536 dimensions)

### **chunking.py**
Splits documents into 1000-character chunks with 200-character overlap:
- Preserves semantic boundaries
- Avoids splitting mid-sentence
- Tracks chunk position and source

### **document_loader.py**
Loads documents from multiple formats:
- **Markdown** (`.md`)
- **PDF** (`.pdf`) — requires `pypdf`
- **Text** (`.txt`)
- **Word** (`.docx`) — requires `python-docx`
- **JSON** (`.json`)
- **CSV** (`.csv`)
- **Excel** (`.xlsx`) — requires `openpyxl`
- **Sample documents** (built-in fallback)

Location: `../resources/organized-data/` (relative to `rag-demo/`)

All formats are loaded recursively from the base directory and subdirectories.

### **embeddings.py**
Embeds text using Azure OpenAI:
- Model: `text-embedding-3-large`
- Dimensions: 1536
- Includes caching for efficiency

### **ingestion_pipeline.py**
Orchestrates the complete flow:
```
Load Docs → Chunk → Embed → Index
```

---

## 🔍 Monitoring Ingestion

The pipeline logs progress:

```
==================== VIVLI RAG DOCUMENT INGESTION PIPELINE ====================
INFO:root:Setting up search index...
INFO:root:Index created!
INFO:root:Loading documents...
INFO:root:Loaded 3 sample documents
INFO:root:Chunking documents...
INFO:root:Created 12 chunks
INFO:root:Embedding chunks...
INFO:root:Embedded 10/12 chunks
INFO:root:Indexing documents...
INFO:root:Total documents indexed: 12/12
==================== INGESTION COMPLETE! ====================
```

---

## ✅ Verify It Worked

### Check Azure AI Search

1. Go to [Azure Portal](https://portal.azure.com)
2. Find your Search Service
3. Look for **Search Explorer** in the left menu
4. Click "Search" with empty query to see all documents
5. You should see 12 documents (if using sample) or more (if using your docs)

### Test the Chatbot

Once indexed, start the API and test:

```powershell
# Start server
python main.py

# In another terminal, test in Swagger:
# http://localhost:8000/docs
# Or use curl:
curl -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"How do I submit a data request?\"}"
```

You should get a response with:
- Generated answer
- Source documents
- Confidence score
- Response time

---

## 🐛 Troubleshooting

### Error: "DeploymentNotFound"
**Problem:** Azure OpenAI deployments don't match your .env

**Solution:** 
1. Check Azure Portal for actual deployment names
2. Update `.env` with correct names:
   ```env
   AZURE_OPENAI_DEPLOYMENT_EMBEDDING=text-embedding-3-large  # Check this!
   AZURE_OPENAI_DEPLOYMENT_LLM=gpt-4o-mini                  # Check this!
   ```
3. Restart the script

### Error: "Cannot connect to Azure Search"
**Problem:** Search endpoint or key is wrong

**Solution:**
1. Verify in Azure Portal:
   - Endpoint: Copy from **Keys** section (URL format)
   - Admin Key: Copy from **Keys** section
2. Update `.env` and try again

### Error: "No documents found"
**Problem:** Can't find files in `/organized-data/`

**Solution:**
1. Check that the directory path is correct
2. Files must be `.md` or `.txt` format
3. Use `--sample` flag to test with built-in documents first

### Index is empty after ingestion
**Problem:** Documents were indexed but search returns nothing

**Solution:**
1. Wait 30 seconds (Azure indexing is eventual)
2. Check Azure Search Explorer to confirm docs exist
3. Try a simple search query

---

## 📈 Performance

Expected timing:
- **Sample documents**: 30-60 seconds
- **Real documents** (50 files): 2-5 minutes
- **Large knowledge base** (500+ files): 15-30 minutes

Bottleneck: Embedding API calls (sequential, one at a time)

---

## 🔄 Re-ingesting Documents

To update the index with new documents:

```powershell
# Delete old index and start fresh
python -c "from index_manager import IndexManager; mgr = IndexManager(); mgr.delete_index(); print('Index deleted')"

# Then run ingestion again
python ingestion_pipeline.py
```

Or add to existing index (embeddings will be deduplicated):
```powershell
python ingestion_pipeline.py
```

---

## 📝 Architecture

```
Your Documents (organized-data/)
        ↓
  DocumentLoader
        ↓
  TextChunker (1000 chars + 200 overlap)
        ↓
  EmbeddingClient (Azure OpenAI)
        ↓
  Prepare for Indexing (add IDs, metadata)
        ↓
  SearchClient.upload_documents()
        ↓
  Azure AI Search Index ✓
        ↓
  Chatbot can now answer questions!
```

---

## 🎯 Next Steps

1. **First time**: Run with `--sample` to verify everything works
2. **Then**: Run without `--sample` to load your real documents
3. **Finally**: Start the API server and test in Swagger UI

```powershell
# Test with sample (fast)
python ingestion_pipeline.py --sample

# Verify it works
python main.py
# Open http://localhost:8000/docs

# Load real documents when ready
python ingestion_pipeline.py
```

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all `.env` credentials
3. Check Azure Portal that resources exist
4. Review the ingestion logs for error messages

You're now ready for a complete end-to-end RAG system! 🚀
