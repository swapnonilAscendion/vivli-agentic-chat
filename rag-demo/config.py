import os
from dotenv import load_dotenv
import urllib3

# Disable SSL verification warnings (for corporate network environments)
# NOTE: Only for development/testing. DO NOT use in production!
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()


class AzureConfig:
    """Azure OpenAI and Search configuration"""

    # Azure OpenAI
    OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    # Deployment names
    EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBEDDING", "text-embedding-3-large")
    LLM_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_LLM", "gpt-4o-mini")

    # Azure AI Search
    SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
    SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "vivli-knowledge-base")

    # Application settings
    EMBEDDING_DIMENSIONS = 3072  # text-embedding-3-large outputs 3072 dimensions
    MAX_TOKENS = 500
    TEMPERATURE = 0.7

    # Thresholds
    CONFIDENCE_THRESHOLD = 0.3  # Lower threshold to allow more documents through (vector search scores are typically lower)
    RELEVANCE_THRESHOLD = 0.1  # Minimum relevance score for documents to be included
    TOP_K_DOCUMENTS = 5

    # Intent classification thresholds
    INTENT_HIGH_CONFIDENCE = 0.15   # High confidence threshold (lowered for better intent detection)
    INTENT_LOW_CONFIDENCE = 0.05    # Low confidence threshold
    INTENT_MULTI_THRESHOLD = 0.08   # Multi-intent threshold (lowered to catch more intent matches)

    @staticmethod
    def validate():
        """Validate that all required config is set"""
        required = [
            "OPENAI_API_KEY",
            "OPENAI_ENDPOINT",
            "SEARCH_ENDPOINT",
            "SEARCH_ADMIN_KEY",
        ]
        missing = [key for key in required if not getattr(AzureConfig, key)]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")


class AppConfig:
    """Application configuration"""

    APP_NAME = "Vivli RAG Chatbot Demo"
    VERSION = "0.1.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


if __name__ == "__main__":
    AzureConfig.validate()
    print("✓ Configuration validated successfully")
