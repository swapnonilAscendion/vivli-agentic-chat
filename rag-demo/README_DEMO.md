# Vivli RAG Chatbot Demo

A quick proof-of-concept RAG (Retrieval-Augmented Generation) chatbot for Vivli, built in 1-2 days.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Navigate to rag-demo directory
cd rag-demo

# Create virtual environment (Python 3.9+)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Azure Credentials

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env with your Azure credentials:
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - AZURE_SEARCH_ENDPOINT
# - AZURE_SEARCH_ADMIN_KEY
```

**Required Azure Resources:**
- Azure OpenAI with `text-embedding-3-large` and `gpt-4o-mini` deployments
- Azure AI Search with an index named `vivli-knowledge-base` (can be customized)

### 3. Start the API Server

```bash
# Run the FastAPI server
python main.py

# Or with uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`

### 4. Test the API

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Chat Endpoint:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I submit a data request?"}'
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={"query": "How do I submit a data request?"}
)
print(response.json())
```

## 📊 API Endpoints

### POST /chat
**Request:**
```json
{
  "query": "How do I submit a data request?"
}
```

**Response:**
```json
{
  "query_id": "uuid",
  "answer": "To submit a data request...",
  "intent": "FAQ|DATA_REQUEST_RELATED|HYBRID|ESCALATION|UNKNOWN",
  "confidence_score": 0.95,
  "sources": [
    {
      "title": "Document Title",
      "source": "guru_cards",
      "relevance_score": 0.92,
      "citation_url": "url"
    }
  ],
  "latency_ms": 245,
  "metadata": {
    "retrieved_doc_count": 3,
    "llm_model": "gpt-4o-mini",
    "validation_status": "passed"
  }
}
```

### GET /health
**Response:**
```json
{
  "status": "ok"
}
```

## 🧪 Running Tests

```bash
# Install pytest
pip install pytest

# Run integration tests
pytest tests/integration_test.py -v
```

## 📝 Sample Test Queries

Use these to validate the demo:

```bash
# FAQ queries
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I submit a data request?"}'

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What documents do I need?"}'

# Data request queries
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the status of my request?"}'

# Escalation
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "I need help with my account"}'
```

## 🏗️ Architecture

```
User Query
    ↓
[Intent Classification] → FAQ | Data Request | Escalation | Unknown
    ↓
[Query Embedding] → Azure OpenAI embeddings
    ↓
[Knowledge Base Retrieval] → Azure AI Search (top-5 documents)
    ↓
[LLM Response Generation] → Azure OpenAI (GPT-4o-mini)
    ↓
[Response Formatting] → Vivli standards format
    ↓
JSON Response to user
```

## 📂 File Structure

```
rag-demo/
├── main.py                 # FastAPI application
├── config.py              # Configuration & Azure setup
├── models.py              # Pydantic request/response models
├── embeddings.py          # Embedding client
├── retrieval.py           # Vector DB search
├── llm.py                 # LLM response generation
├── intent_classifier.py   # Intent classification
├── response_formatter.py  # Response formatting
├── requirements.txt       # Python dependencies
├── .env.example           # Config template
└── tests/
    └── integration_test.py # Test suite
```

## 🔧 Configuration

All settings are in `config.py`. Key thresholds:

```python
CONFIDENCE_THRESHOLD = 0.6          # Min confidence for auto-response
RELEVANCE_THRESHOLD = 0.6           # Min doc relevance score
TOP_K_DOCUMENTS = 5                 # Max documents to retrieve
INTENT_HIGH_CONFIDENCE = 0.7        # High confidence intent score
```

## 📊 Performance

**Expected Performance:**
- Response latency: 200-500ms
- Intent classification: <50ms
- Document retrieval: 100-200ms
- LLM generation: 100-300ms

## 🐛 Troubleshooting

### "Missing required config" Error
Check that all environment variables are set in `.env`:
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_ENDPOINT
- AZURE_SEARCH_ENDPOINT
- AZURE_SEARCH_ADMIN_KEY

### "Cannot connect to Azure Search"
Verify:
- Azure Search endpoint is correct
- Admin key is valid
- Network access to Azure Search is allowed

### "No documents found"
Check:
- Azure AI Search index exists and is named correctly
- Documents are indexed with embeddings field
- Query is being embedded correctly

## 📈 Next Steps (Post-MVP)

1. Add conversation history tracking
2. Implement feedback loop (helpful/not helpful)
3. Expand to data request API integration
4. Add monitoring and logging to Azure Application Insights
5. Scale to production infrastructure
6. Build web UI frontend
7. Fine-tune LLM prompts based on real queries

## 🎯 Demo Success Criteria

- [ ] `/chat` endpoint responds without errors
- [ ] Test queries return meaningful answers
- [ ] Confidence scores are between 0.0-1.0
- [ ] Response latency < 500ms
- [ ] Sources are included in response
- [ ] Responses follow Vivli format standards
- [ ] All tests pass

## 📧 Support

For issues or questions about the demo, please contact the Vivli team.

---

**Built with:** FastAPI, Azure OpenAI, Azure AI Search
**Python Version:** 3.9+
**Demo Version:** 0.1.0
