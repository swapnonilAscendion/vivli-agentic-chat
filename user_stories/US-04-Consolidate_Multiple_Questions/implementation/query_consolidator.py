"""
US-04: Consolidate Multiple Questions
Identify and consolidate multiple questions in a single message into one response.

This module allows researchers to ask several questions at once and receive one
consolidated answer addressing all questions, when they are related enough to
consolidate meaningfully.
"""

import logging
import re
from typing import Tuple, List, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConsolidationResult:
    """Result of question consolidation analysis"""
    has_multiple_questions: bool
    questions: List[str]
    question_groups: List[List[str]]
    should_consolidate: bool
    consolidation_score: float
    reasoning: str


class QueryConsolidator:
    """
    Identify and consolidate multiple questions in a single message.

    Implements question detection, similarity analysis, and grouping to
    determine if multiple questions should be answered together or separately.
    """

    # Configuration
    CONSOLIDATION_ENABLED = True
    MIN_QUESTIONS_TO_CONSOLIDATE = 2
    MAX_QUESTIONS_PER_CONSOLIDATION = 5
    TOPIC_SIMILARITY_THRESHOLD = 0.75
    ALLOW_MIXED_INTENTS = False

    # Question delimiters
    QUESTION_MARKERS = [
        r'\?',  # Question mark
        r'how\s+(?:do|can|should|would)',  # How questions
        r'what\s+(?:is|are|would|will)',  # What questions
        r'why\s+(?:is|are|would|do)',  # Why questions
        r'when\s+(?:is|are|should|will)',  # When questions
        r'where\s+(?:is|are|can)',  # Where questions
        r'who\s+(?:is|are)',  # Who questions
    ]

    # Topic keywords for similarity matching
    TOPIC_KEYWORDS = {
        'submission': ['submit', 'send', 'file', 'upload', 'provide'],
        'timeline': ['how long', 'timeline', 'duration', 'when', 'deadline'],
        'eligibility': ['eligible', 'qualifies', 'requirements', 'criteria'],
        'status': ['status', 'progress', 'stage', 'approve', 'reject'],
        'process': ['process', 'procedure', 'steps', 'how to', 'way'],
        'data': ['data', 'dataset', 'information', 'records', 'download'],
    }

    def __init__(self):
        """Initialize query consolidator with compiled patterns"""
        self.question_patterns = [re.compile(p, re.IGNORECASE) for p in self.QUESTION_MARKERS]
        logger.info("QueryConsolidator initialized")

    def consolidate(self, query_text: str) -> ConsolidationResult:
        """
        Analyze query and determine if multiple questions should be consolidated.

        Args:
            query_text: User's complete query

        Returns:
            ConsolidationResult with analysis details
        """

        if not self.CONSOLIDATION_ENABLED:
            logger.warning("Question consolidation is disabled")
            return ConsolidationResult(
                has_multiple_questions=False,
                questions=[query_text],
                question_groups=[[query_text]],
                should_consolidate=False,
                consolidation_score=0.0,
                reasoning="Consolidation disabled"
            )

        # Step 1: Extract questions
        questions = self._extract_questions(query_text)

        # Check if multiple questions found
        if len(questions) < self.MIN_QUESTIONS_TO_CONSOLIDATE:
            logger.info(f"Only {len(questions)} question(s) found - no consolidation needed")
            return ConsolidationResult(
                has_multiple_questions=False,
                questions=questions,
                question_groups=[questions],
                should_consolidate=False,
                consolidation_score=0.0,
                reasoning=f"Found {len(questions)} question(s), need at least {self.MIN_QUESTIONS_TO_CONSOLIDATE}"
            )

        # Step 2: Check if exceeds max
        if len(questions) > self.MAX_QUESTIONS_PER_CONSOLIDATION:
            logger.warning(f"Found {len(questions)} questions - exceeds max of {self.MAX_QUESTIONS_PER_CONSOLIDATION}")
            return ConsolidationResult(
                has_multiple_questions=True,
                questions=questions,
                question_groups=[questions],
                should_consolidate=False,
                consolidation_score=0.0,
                reasoning=f"Too many questions ({len(questions)}) - max is {self.MAX_QUESTIONS_PER_CONSOLIDATION}"
            )

        # Step 3: Analyze similarity
        similarity_score = self._calculate_similarity(questions)

        # Step 4: Determine consolidation
        should_consolidate = similarity_score >= self.TOPIC_SIMILARITY_THRESHOLD

        reasoning = (
            f"Similarity score: {similarity_score:.2f} (threshold: {self.TOPIC_SIMILARITY_THRESHOLD}) - "
            f"{'Consolidate' if should_consolidate else 'Separate'}"
        )

        logger.info(f"Consolidation analysis: {len(questions)} questions, score={similarity_score:.2f}")

        return ConsolidationResult(
            has_multiple_questions=True,
            questions=questions,
            question_groups=[questions] if should_consolidate else [[q] for q in questions],
            should_consolidate=should_consolidate,
            consolidation_score=similarity_score,
            reasoning=reasoning
        )

    def _extract_questions(self, text: str) -> List[str]:
        """
        Extract individual questions from text.

        Args:
            text: Raw query text

        Returns:
            List of individual questions
        """
        # Split by question marks first
        parts = text.split('?')
        questions = []

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check if it contains question markers
            has_question_marker = any(
                pattern.search(part) for pattern in self.question_patterns
            )

            if has_question_marker:
                questions.append(part + '?')
            elif part and len(part) > 3:  # Non-empty phrase
                questions.append(part)

        return questions if questions else [text]

    def _calculate_similarity(self, questions: List[str]) -> float:
        """
        Calculate similarity score between questions.

        Args:
            questions: List of extracted questions

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if len(questions) < 2:
            return 1.0

        # Extract topics from questions
        topics = [self._extract_topics(q) for q in questions]

        # Calculate pairwise overlap
        total_score = 0.0
        comparisons = 0

        for i in range(len(topics)):
            for j in range(i + 1, len(topics)):
                overlap = len(set(topics[i]) & set(topics[j]))
                union = len(set(topics[i]) | set(topics[j]))

                if union > 0:
                    similarity = overlap / union
                    total_score += similarity
                    comparisons += 1

        if comparisons == 0:
            return 0.5  # Neutral score if no overlap

        return total_score / comparisons

    def _extract_topics(self, question: str) -> List[str]:
        """
        Extract topic keywords from a question.

        Args:
            question: Single question text

        Returns:
            List of detected topics
        """
        detected_topics = []
        question_lower = question.lower()

        for topic, keywords in self.TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword in question_lower:
                    detected_topics.append(topic)
                    break

        return detected_topics if detected_topics else ['unknown']

    def group_questions(self, questions: List[str]) -> List[List[str]]:
        """
        Group related questions together.

        Args:
            questions: List of questions to group

        Returns:
            List of question groups
        """
        if len(questions) <= 1:
            return [questions]

        groups = []
        used = set()

        for i, q1 in enumerate(questions):
            if i in used:
                continue

            group = [q1]
            used.add(i)

            topics1 = self._extract_topics(q1)

            # Find related questions
            for j, q2 in enumerate(questions):
                if j <= i or j in used:
                    continue

                topics2 = self._extract_topics(q2)
                overlap = len(set(topics1) & set(topics2))

                if overlap > 0:
                    group.append(q2)
                    used.add(j)

            groups.append(group)

        return groups


# Global consolidator instance
consolidator = QueryConsolidator()


def consolidate_multiple_questions(query_text: str) -> ConsolidationResult:
    """
    Main entry point for question consolidation.

    Args:
        query_text: User's query text

    Returns:
        ConsolidationResult with analysis and recommendations

    Example:
        >>> result = consolidate_multiple_questions("How do I submit? When will it be approved?")
        >>> print(f"Questions: {result.questions}")
        >>> print(f"Should consolidate: {result.should_consolidate}")
    """
    return consolidator.consolidate(query_text)


if __name__ == "__main__":
    # Test examples
    test_cases = [
        "How do I submit a data request? When will it be approved?",
        "What are the requirements? What documents do I need?",
        "How do I submit? What's the status of my request?",
        "Tell me about the process",
        "What? How? When? Where? Why?",
    ]

    for test in test_cases:
        result = consolidate_multiple_questions(test)
        print(f"\nQuery: {test}")
        print(f"Questions found: {len(result.questions)}")
        print(f"Should consolidate: {result.should_consolidate}")
        print(f"Score: {result.consolidation_score:.2f}")
        print(f"Reasoning: {result.reasoning}")
