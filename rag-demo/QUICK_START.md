# 🚀 Quick Start (5 Minutes)

## 1. Install Dependencies
```bash
cd rag-demo
pip install -r requirements.txt
```

## 2. Configure Azure
Copy `.env.example` to `.env` and add your Azure credentials:
```bash
cp .env.example .env
# Edit .env with your Azure OpenAI + Search keys
```

## 3. Start Server
```bash
python main.py
```

Server runs at `http://localhost:8000`

## 4. Test It
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I submit a data request?"}'
```

## Response Example
```json
{
  "query_id": "abc123",
  "answer": "To submit a data request, you can...",
  "intent": "FAQ",
  "confidence_score": 0.95,
  "sources": [{"title": "...", "source": "guru_cards", "relevance_score": 0.92}],
  "latency_ms": 245
}
```

## 🎯 Success!
If you get a response with an answer, the demo is working! 

---

**Next Steps:**
- Read [README_DEMO.md](README_DEMO.md) for full documentation
- Run tests: `pytest tests/integration_test.py -v`
- Check [RAG_CHATBOT_DEMO_SPEC.md](../RAG_CHATBOT_DEMO_SPEC.md) for architecture details
