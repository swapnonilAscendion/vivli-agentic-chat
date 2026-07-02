from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from config import AzureConfig

credential = AzureKeyCredential(AzureConfig.SEARCH_ADMIN_KEY)
client = SearchClient(
    endpoint=AzureConfig.SEARCH_ENDPOINT,
    index_name=AzureConfig.SEARCH_INDEX_NAME,
    credential=credential,
)

# Search for all documents
results = client.search(search_text='*', select=['id', 'title', 'content', 'source'])
docs = list(results)
print(f'Total documents in index: {len(docs)}')
for i, doc in enumerate(docs[:5]):
    print(f'{i+1}. {doc["title"][:60]}... (source: {doc["source"]})')
