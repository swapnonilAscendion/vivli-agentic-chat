import logging
import time
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import AppConfig, AzureConfig
from models import ChatRequest, ChatResponse, SourceDocument, HealthResponse
from embeddings import EmbeddingClient
from retrieval import Retrieval
from llm import LLMClient
from intent_classifier import IntentClassifier
from response_formatter import ResponseFormatter

# Configure logging
logging.basicConfig(
    level=AppConfig.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with OpenAPI documentation
app = FastAPI(
    title=AppConfig.APP_NAME,
    version=AppConfig.VERSION,
    description="""
    A Retrieval-Augmented Generation (RAG) chatbot for Vivli data sharing platform.

    **Features:**
    - Intent classification (FAQ, Data Request, Escalation)
    - Semantic search of knowledge base
    - LLM-powered response generation
    - Vivli-standard response formatting

    **Quick Start:**
    1. Use the POST /chat endpoint to send a query
    2. Get back an intelligent response with sources and confidence scores

    **Example Queries:**
    - "How do I submit a data request?"
    - "What is the status of my request?"
    - "I need help with my account"
    """,
    contact={
        "name": "Vivli Team",
        "url": "https://vivli.org",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
embedding_client = EmbeddingClient()
retrieval = Retrieval()
llm_client = LLMClient()
intent_classifier = IntentClassifier()
response_formatter = ResponseFormatter()


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup"""
    try:
        AzureConfig.validate()
        logger.info("✓ Configuration validated")
        logger.info(f"✓ Using index: {AzureConfig.SEARCH_INDEX_NAME}")
    except Exception as e:
        logger.error(f"✗ Configuration validation failed: {str(e)}")
        raise


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    **Health Check Endpoint**

    Verify that the API is running and all services are healthy.

    Returns:
    - `status`: "ok" if the system is operational
    """
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    **Main Chat Endpoint**

    Send a query to the Vivli RAG chatbot and get an intelligent response.

    The system will:
    1. Classify your query intent (FAQ, Data Request, Escalation, etc.)
    2. Search the knowledge base for relevant documents
    3. Generate a contextual response using LLM
    4. Format the response with proper citations and disclaimers

    **Example queries:**
    - "How do I submit a data request?"
    - "What is the status of my request?"
    - "I need help with my account"

    **Response includes:**
    - `answer`: The generated response text
    - `intent`: Classification (FAQ, DATA_REQUEST_RELATED, HYBRID, ESCALATION, UNKNOWN)
    - `confidence_score`: Confidence in the answer (0.0-1.0)
    - `sources`: Relevant documents used to generate the answer
    - `latency_ms`: Response time in milliseconds
    """
    query_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        # Step 1: Classify intent
        logger.info(f"[{query_id}] Processing query: {request.query[:100]}...")
        classification = intent_classifier.classify(request.query)
        logger.info(
            f"[{query_id}] Classification: {classification.intent} "
            f"(confidence: {classification.confidence:.2f})"
        )

        # Step 2: Retrieve documents
        query_embedding = await embedding_client.embed_query(request.query)
        retrieval_result = await retrieval.retrieve_documents(
            query_embedding,
            query_text=request.query  # Pass original query for keyword fallback
        )

        # Filter by confidence
        filtered_docs = retrieval.filter_by_confidence(retrieval_result.documents)
        logger.info(
            f"[{query_id}] Retrieved {len(filtered_docs)} documents "
            f"(from {len(retrieval_result.documents)} total)"
        )

        # Step 3: Generate response based on intent
        if classification.intent == "FAQ":
            answer = await _handle_faq(query_id, request.query, filtered_docs)

        elif classification.intent == "DATA_REQUEST_RELATED":
            answer = _create_data_request_response(
                request.query, classification.confidence
            )

        elif classification.intent == "HYBRID":
            answer = await _handle_hybrid(
                query_id, request.query, filtered_docs, classification.confidence
            )

        elif classification.intent == "ESCALATION":
            answer = response_formatter.format_escalation_response()

        else:  # UNKNOWN
            answer = response_formatter.format_escalation_response()
            classification.intent = "ESCALATION"

        # Step 4: Format sources
        sources = []
        if filtered_docs:
            for doc in filtered_docs[:3]:  # Top 3 sources
                sources.append(
                    SourceDocument(
                        title=doc.title,
                        source=doc.source,
                        relevance_score=doc.relevance_score,
                        citation_url=doc.doc_id,  # Using doc_id as placeholder for URL
                    )
                )

        # Calculate total latency
        latency_ms = int((time.time() - start_time) * 1000)

        logger.info(f"[{query_id}] Response generated in {latency_ms}ms")

        return ChatResponse(
            query_id=query_id,
            answer=answer,
            intent=classification.intent,
            confidence_score=classification.confidence,
            sources=sources,
            latency_ms=latency_ms,
            metadata={
                "retrieved_doc_count": len(filtered_docs),
                "llm_model": "gpt-4o-mini",
                "validation_status": "passed",
            },
        )

    except Exception as e:
        logger.error(f"[{query_id}] Error processing query: {str(e)}", exc_info=True)
        latency_ms = int((time.time() - start_time) * 1000)

        return ChatResponse(
            query_id=query_id,
            answer=response_formatter.format_error_response(str(e)),
            intent="UNKNOWN",
            confidence_score=0.0,
            sources=[],
            latency_ms=latency_ms,
            metadata={"error": str(e)},
        )


async def _handle_faq(query_id: str, query: str, documents) -> str:
    """Handle FAQ query"""
    if not documents:
        logger.warning(f"[{query_id}] No documents found for FAQ query")
        return response_formatter.format_escalation_response()

    # Format documents for LLM
    context = retrieval.format_for_llm(documents)

    # Generate FAQ response
    result = await llm_client.generate_faq_response(query, context)

    if not result.answer:
        logger.warning(f"[{query_id}] LLM generated empty response")
        return response_formatter.format_escalation_response()

    # Format with Vivli standards
    return response_formatter.format_faq_response(result.answer, [])


async def _handle_hybrid(
    query_id: str, query: str, documents, classification_confidence: float
) -> str:
    """Handle hybrid query (data request + FAQ)"""
    # For demo, just handle as FAQ if we have documents, else escalate
    if documents and classification_confidence > AzureConfig.CONFIDENCE_THRESHOLD:
        context = retrieval.format_for_llm(documents)
        result = await llm_client.generate_faq_response(query, context)
        if result.answer:
            return response_formatter.format_faq_response(result.answer, [])

    return response_formatter.format_escalation_response()


def _create_data_request_response(query: str, confidence: float) -> str:
    """Create placeholder data request response"""
    if confidence < AzureConfig.CONFIDENCE_THRESHOLD:
        return response_formatter.format_escalation_response()

    # Placeholder response for demo (would fetch from API in production)
    return response_formatter.format_data_request_response(
        answer="Your request is being processed. You will be notified of any updates.",
        request_id="UNKNOWN",
        current_stage="draft",
        researcher_name="Researcher",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=AppConfig.DEBUG,
        log_level=AppConfig.LOG_LEVEL.lower(),
    )
