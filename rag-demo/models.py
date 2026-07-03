from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for /chat endpoint"""

    query: str = Field(
        default="",
        description="Your question about Vivli platform, data requests, or procedures",
        example="How do I submit a data request?"
    )
    user_role: str = Field(
        default="",
        description="User role for access control (researcher, team_member, vivli_admin, etc.)",
        example="researcher"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the user (optional)",
        example="user_001"
    )


class SourceDocument(BaseModel):
    """Source document citation"""

    title: str
    source: str  # guru_cards, policy_documents, website_faqs, howto_guides
    relevance_score: float = Field(ge=0.0)  # Allows scores > 1 from keyword search
    citation_url: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for /chat endpoint"""

    query_id: str = Field(description="Unique identifier for this query")
    answer: str = Field(description="The generated response to your query")
    intent: str = Field(
        description="Classification of your query: FAQ, DATA_REQUEST_RELATED, HYBRID, ESCALATION, or UNKNOWN"
    )
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in the answer (0.0-1.0, higher is better)"
    )
    sources: List[SourceDocument] = Field(
        default=[],
        description="Knowledge base documents used to generate the answer"
    )
    latency_ms: int = Field(
        description="Response time in milliseconds"
    )
    metadata: dict = Field(
        description="Additional metadata about the response (doc count, model used, etc.)"
    )


class HealthResponse(BaseModel):
    """Health check response"""

    status: str


class IntentClassificationResult(BaseModel):
    """Result of intent classification"""

    intent: str
    confidence: float
    keywords_detected: List[str] = []
    all_scores: Optional[dict] = None


class RetrievedDocument(BaseModel):
    """Document retrieved from vector DB"""

    doc_id: str
    title: str
    content: str
    source: str
    relevance_score: float


class RetrievalResult(BaseModel):
    """Result of knowledge base retrieval"""

    documents: List[RetrievedDocument]
    retrieval_time_ms: int
    total_docs_searched: int


class LLMGenerationResult(BaseModel):
    """Result of LLM response generation"""

    answer: str
    confidence_score: float
    validation_status: str  # passed, failed_with_reason
    tokens_used: Optional[dict] = None
    generation_time_ms: int
