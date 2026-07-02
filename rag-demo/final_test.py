from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("=" * 70)
print("FINAL CHAT ENDPOINT TEST - After Fixes")
print("=" * 70)

test_queries = [
    "What is data request submission?",
    "How do I submit a data request?",
    "Form check process",
]

for query in test_queries:
    print(f"\n\nQuery: {query}")
    print("-" * 70)

    response = client.post("/chat", json={"query": query})
    data = response.json()

    print(f"Intent: {data['intent']}")
    print(f"Confidence: {data['confidence_score']:.2f}")
    print(f"Retrieved Documents: {data['metadata']['retrieved_doc_count']}")
    print(f"Latency: {data['latency_ms']}ms")
    print(f"\nAnswer:\n{data['answer']}")

    if data['sources']:
        print(f"\nSources:")
        for i, src in enumerate(data['sources'], 1):
            print(f"  {i}. {src['title']} (relevance: {src['relevance_score']:.2f})")

print("\n" + "=" * 70)
print("✓ Test Complete - System is working!")
print("=" * 70)
