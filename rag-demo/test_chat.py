from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("Testing Chat Endpoint")
print("=" * 60)

queries = ["data request", "how to submit", "what is vivli"]

for query in queries:
    try:
        response = client.post("/chat", json={"query": query})
        data = response.json()

        print(f"\nQuery: '{query}'")
        print(f"Status: {response.status_code}")
        print(f"Intent: {data['intent']}")
        print(f"Confidence: {data['confidence_score']:.2f}")
        print(f"Retrieved docs: {data['metadata']['retrieved_doc_count']}")
        print(f"Answer: {data['answer'][:100]}...")
        print(f"Latency: {data['latency_ms']}ms")

    except Exception as e:
        print(f"\nError testing query '{query}': {str(e)}")

print("\n" + "=" * 60)
print("Chat endpoint test complete!")
