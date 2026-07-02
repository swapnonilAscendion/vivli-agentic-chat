#!/usr/bin/env python
"""Quick test of greeting response."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("Testing greeting response for 'hi'...\n")

response = client.post("/chat", json={"query": "hi"})
data = response.json()

print(f"Intent: {data['intent']}")
print(f"Confidence: {data['confidence_score']}")
print(f"Retrieved docs: {data['metadata']['retrieved_doc_count']}")
print(f"\nAnswer:\n{data['answer']}")
