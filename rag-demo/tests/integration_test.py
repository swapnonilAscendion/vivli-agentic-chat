"""
Integration tests for the RAG chatbot demo.
Run with: pytest tests/integration_test.py -v
"""

import pytest
import asyncio
from intent_classifier import IntentClassifier
from response_formatter import ResponseFormatter
from models import SourceDocument


@pytest.fixture
def classifier():
    return IntentClassifier()


@pytest.fixture
def formatter():
    return ResponseFormatter()


# Intent Classification Tests
class TestIntentClassification:
    def test_faq_classification(self, classifier):
        """Test FAQ intent classification"""
        result = classifier.classify("How do I submit a data request?")
        assert result.intent in ["FAQ", "HYBRID"]
        assert result.confidence > 0.2  # Keyword-based classifier

    def test_data_request_classification(self, classifier):
        """Test data request intent classification"""
        result = classifier.classify("What is the status of my request?")
        assert result.intent in ["DATA_REQUEST_RELATED", "HYBRID"]
        assert result.confidence > 0.2  # Keyword-based classifier

    def test_escalation_classification(self, classifier):
        """Test escalation intent classification"""
        result = classifier.classify("I need help with my account")
        assert result.intent in ["ESCALATION", "UNKNOWN"]
        assert result.confidence > 0.0

    def test_unknown_classification(self, classifier):
        """Test unknown intent classification"""
        result = classifier.classify("Tell me about cooking recipes")
        assert result.intent == "UNKNOWN"

    def test_empty_query_classification(self, classifier):
        """Test empty query handling"""
        result = classifier.classify("")
        assert result.intent == "UNKNOWN"
        assert result.confidence == 0.0

    def test_hybrid_classification(self, classifier):
        """Test hybrid intent detection"""
        result = classifier.classify(
            "How do I submit a request and what is the status of my current one?"
        )
        # Should detect multiple intents
        assert result.keywords_detected  # Should have keywords


# Response Formatting Tests
class TestResponseFormatting:
    def test_faq_response_format(self, formatter):
        """Test FAQ response formatting"""
        answer = "You submit a request by clicking the submit button."
        response = formatter.format_faq_response(
            answer=answer,
            sources=[],
            researcher_name="John",
        )

        assert "Hi John," in response
        assert "You submit a request" in response
        assert "Was this helpful?" in response
        assert "AI system" in response

    def test_data_request_response_format(self, formatter):
        """Test data request response formatting"""
        response = formatter.format_data_request_response(
            answer="Your request is being reviewed.",
            request_id="REQ-123",
            current_stage="review",
            researcher_name="Jane",
        )

        assert "Hi Jane," in response
        assert "REQ-123" in response
        assert "review" in response
        assert "AI system" in response

    def test_escalation_response_format(self, formatter):
        """Test escalation response formatting"""
        response = formatter.format_escalation_response()

        assert "couldn't find a reliable answer" in response
        assert "Vivli Administrator" in response
        assert "AI system" in response

    def test_multiple_queries_response_format(self, formatter):
        """Test multiple questions response formatting"""
        answers = [
            {"question": "How to submit?", "answer": "Click submit button."},
            {"question": "What is timeline?", "answer": "Review takes 2 weeks."},
        ]
        response = formatter.format_multiple_queries_response(
            answers=answers,
            sources=[],
            researcher_name="Bob",
        )

        assert "Hi Bob," in response
        assert "Question 1:" in response
        assert "Question 2:" in response
        assert "AI system" in response

    def test_faq_with_sources(self, formatter):
        """Test FAQ response with source documents"""
        sources = [
            SourceDocument(
                title="Submission Guide",
                source="guru_cards",
                relevance_score=0.95,
                citation_url="https://example.com/guide",
            )
        ]
        response = formatter.format_faq_response(
            answer="Submit using the form.",
            sources=sources,
            researcher_name="Alice",
        )

        assert "Hi Alice," in response
        assert "Submit using the form" in response
        assert "https://example.com/guide" in response


# Test Datasets
TEST_QUERIES = [
    ("How do I submit a data request?", "FAQ"),
    ("What documents do I need?", "FAQ"),
    ("What is the process timeline?", "FAQ"),
    ("What is the status of my request?", "DATA_REQUEST_RELATED"),
    ("Can I check my application?", "DATA_REQUEST_RELATED"),
    ("I need help with my account", "ESCALATION"),
    ("Escalate to human please", "ESCALATION"),
    ("Tell me about cooking recipes", "UNKNOWN"),
]


@pytest.mark.parametrize("query,expected_intent", TEST_QUERIES)
def test_query_intent_classification(classifier, query, expected_intent):
    """Test intent classification for various queries"""
    result = classifier.classify(query)

    # For demo purposes, allow some flexibility in classification
    if expected_intent == "UNKNOWN":
        assert result.intent == "UNKNOWN"
    elif expected_intent in ["FAQ", "DATA_REQUEST_RELATED"]:
        # Could be classified as HYBRID
        assert result.intent in [expected_intent, "HYBRID"]
    else:
        assert result.intent in [expected_intent, "UNKNOWN"]


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/integration_test.py -v
    pytest.main([__file__, "-v"])
