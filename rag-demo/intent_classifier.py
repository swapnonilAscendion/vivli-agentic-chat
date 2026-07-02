import logging
import re
from typing import List, Tuple
from config import AzureConfig
from models import IntentClassificationResult

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classify user queries into intent categories"""

    # Keywords for each intent
    FAQ_KEYWORDS = [
        "how",
        "what",
        "where",
        "when",
        "process",
        "procedure",
        "policy",
        "requirements",
        "timeline",
        "eligible",
        "guide",
        "tutorial",
        "help with",
    ]

    DATA_REQUEST_KEYWORDS = [
        "status",
        "my request",
        "my application",
        "update",
        "feedback",
        "revision",
        "submission",
        "reviewed",
        "submitted",
        "progress",
        "check",
        "tracking",
    ]

    ESCALATION_KEYWORDS = [
        "help",
        "escalate",
        "human",
        "staff",
        "not helpful",
        "need assistance",
        "speak to",
        "contact",
        "urgent",
    ]

    def __init__(self):
        self.faq_keywords = self.FAQ_KEYWORDS
        self.data_request_keywords = self.DATA_REQUEST_KEYWORDS
        self.escalation_keywords = self.ESCALATION_KEYWORDS

    def classify(self, query_text: str) -> IntentClassificationResult:
        """
        Classify a query into intent categories.

        Args:
            query_text: User's query

        Returns:
            IntentClassificationResult with classification and confidence scores
        """
        if not query_text or not query_text.strip():
            return IntentClassificationResult(
                intent="UNKNOWN",
                confidence=0.0,
                keywords_detected=[],
                all_scores={
                    "faq": 0.0,
                    "data_request": 0.0,
                    "escalation": 0.0,
                },
            )

        # Normalize query
        normalized = query_text.lower().strip()

        # Calculate scores
        faq_score = self._calculate_score(normalized, self.faq_keywords)
        data_request_score = self._calculate_score(
            normalized, self.data_request_keywords
        )
        escalation_score = self._calculate_score(
            normalized, self.escalation_keywords
        )

        # Determine intent
        intent, confidence = self._determine_intent(
            faq_score, data_request_score, escalation_score
        )

        # Extract keywords
        keywords = self._extract_detected_keywords(normalized)

        logger.info(
            f"Classification: intent={intent}, confidence={confidence:.2f}, query_len={len(query_text)}"
        )

        return IntentClassificationResult(
            intent=intent,
            confidence=confidence,
            keywords_detected=keywords,
            all_scores={
                "faq": round(faq_score, 3),
                "data_request": round(data_request_score, 3),
                "escalation": round(escalation_score, 3),
            },
        )

    def _calculate_score(self, text: str, keywords: List[str]) -> float:
        """
        Calculate intent score based on keyword matches.

        Args:
            text: Normalized query text
            keywords: List of keywords for this intent

        Returns:
            Score between 0.0 and 1.0
        """
        if not keywords:
            return 0.0

        matches = 0
        for keyword in keywords:
            # Check for exact word matches or substring matches
            if keyword in text:
                matches += 1

        # Score is based on matches, capped at 1.0
        # More lenient: sqrt of ratio gives higher scores with fewer matches
        score = min((matches / max(len(keywords), 3)) ** 0.5, 1.0)
        return score

    def _determine_intent(
        self, faq_score: float, data_request_score: float, escalation_score: float
    ) -> Tuple[str, float]:
        """
        Determine intent category and confidence.

        Args:
            faq_score: Score for FAQ intent
            data_request_score: Score for Data Request intent
            escalation_score: Score for Escalation intent

        Returns:
            Tuple of (intent, confidence)
        """
        high = AzureConfig.INTENT_HIGH_CONFIDENCE
        low = AzureConfig.INTENT_LOW_CONFIDENCE
        multi = AzureConfig.INTENT_MULTI_THRESHOLD

        # Check escalation first (highest priority)
        if escalation_score > high:
            return "ESCALATION", escalation_score

        # Check clear FAQ
        if faq_score > high and data_request_score < low:
            return "FAQ", faq_score

        # Check clear Data Request
        if data_request_score > high and faq_score < low:
            return "DATA_REQUEST_RELATED", data_request_score

        # Check hybrid (multiple intents)
        if faq_score > multi and data_request_score > multi:
            max_score = max(faq_score, data_request_score)
            return "HYBRID", max_score

        # Check moderate confidence for single intent
        if faq_score > multi:
            return "FAQ", faq_score

        if data_request_score > multi:
            return "DATA_REQUEST_RELATED", data_request_score

        # Unknown - below threshold
        return "UNKNOWN", max(faq_score, data_request_score, escalation_score)

    def _extract_detected_keywords(self, text: str) -> List[str]:
        """Extract keywords that were detected in the query."""
        all_keywords = (
            self.faq_keywords + self.data_request_keywords + self.escalation_keywords
        )
        detected = [kw for kw in all_keywords if kw in text]
        return list(set(detected))  # Remove duplicates
