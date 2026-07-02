import json
import logging
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
from azure.core.credentials import AzureKeyCredential
from config import AzureConfig

logger = logging.getLogger(__name__)


class IndexManager:
    """Manage Azure AI Search index creation and configuration"""

    def __init__(self):
        credential = AzureKeyCredential(AzureConfig.SEARCH_ADMIN_KEY)
        self.client = SearchIndexClient(
            endpoint=AzureConfig.SEARCH_ENDPOINT,
            credential=credential,
        )
        self.index_name = AzureConfig.SEARCH_INDEX_NAME

    def create_index(self) -> bool:
        """
        Create Azure AI Search index for RAG documents.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if index already exists
            try:
                existing = self.client.get_index(self.index_name)
                logger.info(f"Index '{self.index_name}' already exists")
                return True
            except Exception:
                pass  # Index doesn't exist, create it

            # Define index schema
            fields = [
                SimpleField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                    sortable=True,
                ),
                SearchableField(
                    name="title",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    retrievable=True,
                ),
                SearchableField(
                    name="content",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    retrievable=True,
                ),
                SimpleField(
                    name="source",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    retrievable=True,
                ),
                SimpleField(
                    name="source_url",
                    type=SearchFieldDataType.String,
                    retrievable=True,
                ),
                SimpleField(
                    name="chunk_index",
                    type=SearchFieldDataType.Int32,
                    retrievable=True,
                ),
                SearchField(
                    name="embedding",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=AzureConfig.EMBEDDING_DIMENSIONS,
                    vector_search_profile_name="myHnsw",
                ),
                SimpleField(
                    name="metadata",
                    type=SearchFieldDataType.String,
                    retrievable=True,
                ),
            ]

            # Configure vector search
            vector_search = VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(name="myHnsw"),
                ],
                profiles=[
                    VectorSearchProfile(
                        name="myHnsw",
                        algorithm_configuration_name="myHnsw",
                    ),
                ],
            )

            # Create index
            index = SearchIndex(
                name=self.index_name,
                fields=fields,
                vector_search=vector_search,
            )

            self.client.create_index(index)
            logger.info(f"Successfully created index '{self.index_name}'")
            return True

        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            return False

    def delete_index(self) -> bool:
        """Delete the search index"""
        try:
            self.client.delete_index(self.index_name)
            logger.info(f"Deleted index '{self.index_name}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting index: {str(e)}")
            return False

    def index_exists(self) -> bool:
        """Check if index exists"""
        try:
            self.client.get_index(self.index_name)
            return True
        except Exception:
            return False
