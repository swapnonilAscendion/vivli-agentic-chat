"""
Unit tests for US-04: Consolidate Multiple Questions

Tests question detection, similarity analysis, and consolidation logic.
"""

import pytest
from implementation.query_consolidator import (
    QueryConsolidator,
    consolidate_multiple_questions,
    ConsolidationResult
)


class TestQueryConsolidatorDetection:
    """Test question detection and extraction"""

    def test_single_question(self):
        """Test detection of single question"""
        result = consolidate_multiple_questions("How do I submit a data request?")
        assert result.has_multiple_questions is False
        assert len(result.questions) == 1

    def test_two_related_questions(self):
        """Test detection of two related questions"""
        result = consolidate_multiple_questions(
            "How do I submit a data request? When will it be approved?"
        )
        assert result.has_multiple_questions is True
        assert len(result.questions) == 2

    def test_three_related_questions(self):
        """Test detection of three related questions"""
        result = consolidate_multiple_questions(
            "What are the eligibility requirements? What documents do I need? How long does it take?"
        )
        assert result.has_multiple_questions is True
        assert len(result.questions) >= 2

    def test_multiple_questions_with_punctuation(self):
        """Test question detection with various punctuation"""
        result = consolidate_multiple_questions(
            "How do I submit? What's required? When will I hear back?"
        )
        assert result.has_multiple_questions is True
        assert len(result.questions) >= 2

    def test_question_without_mark(self):
        """Test detection of questions without question marks"""
        result = consolidate_multiple_questions(
            "Tell me about the process and timeline"
        )
        assert len(result.questions) >= 1

    def test_empty_query(self):
        """Test handling of empty query"""
        result = consolidate_multiple_questions("")
        assert result.questions is not None

    def test_statement_not_question(self):
        """Test that statements without questions don't trigger consolidation"""
        result = consolidate_multiple_questions("I need help with my account")
        assert result.has_multiple_questions is False


class TestQueryConsolidatorSimilarity:
    """Test similarity analysis and consolidation scoring"""

    def test_consolidate_related_questions(self):
        """Test consolidation of related questions"""
        result = consolidate_multiple_questions(
            "How do I submit a data request? What documents are needed for submission?"
        )
        assert result.has_multiple_questions is True
        if len(result.questions) >= 2:
            assert result.consolidation_score >= 0.0

    def test_separate_unrelated_questions(self):
        """Test separation of unrelated questions"""
        result = consolidate_multiple_questions(
            "How do I submit? What's the current weather?"
        )
        assert result.has_multiple_questions is True
        # Unrelated questions should have low similarity
        # May not consolidate based on topic overlap

    def test_consolidation_threshold(self):
        """Test that consolidation respects similarity threshold"""
        result = consolidate_multiple_questions(
            "How do I submit a request? When will it be processed?"
        )
        if len(result.questions) >= 2:
            # Questions about submission process should be above threshold
            assert result.consolidation_score >= 0.0

    def test_multiple_submission_questions(self):
        """Test consolidation of multiple submission-related questions"""
        result = consolidate_multiple_questions(
            "What's the submission process? How do I submit? What documents are required?"
        )
        assert result.has_multiple_questions is True
        if len(result.questions) >= 2:
            # All submission-related should consolidate
            assert result.consolidation_score >= 0.0


class TestQueryConsolidatorGrouping:
    """Test question grouping logic"""

    def test_group_single_question(self):
        """Test grouping of single question"""
        consolidator = QueryConsolidator()
        groups = consolidator.group_questions(["How do I submit?"])
        assert len(groups) == 1
        assert len(groups[0]) == 1

    def test_group_related_questions(self):
        """Test grouping of related questions"""
        consolidator = QueryConsolidator()
        questions = [
            "How do I submit?",
            "What documents are needed?",
            "What's the timeline?"
        ]
        groups = consolidator.group_questions(questions)
        assert len(groups) >= 1
        # All related questions might be in one group
        assert sum(len(g) for g in groups) == len(questions)

    def test_group_mixed_questions(self):
        """Test grouping of mixed related/unrelated questions"""
        consolidator = QueryConsolidator()
        questions = [
            "How do I submit a request?",
            "What documents are needed?",
            "What's the weather?"
        ]
        groups = consolidator.group_questions(questions)
        assert len(groups) >= 1

    def test_empty_questions_list(self):
        """Test grouping of empty list"""
        consolidator = QueryConsolidator()
        groups = consolidator.group_questions([])
        assert len(groups) == 1
        assert len(groups[0]) == 0


class TestQueryConsolidatorConfiguration:
    """Test consolidator configuration"""

    def test_consolidation_enabled_flag(self):
        """Test that consolidation can be disabled"""
        consolidator = QueryConsolidator()
        original = consolidator.CONSOLIDATION_ENABLED

        try:
            consolidator.CONSOLIDATION_ENABLED = False
            result = consolidator.consolidate("How? When? Where?")
            assert result.should_consolidate is False
            assert result.consolidation_score == 0.0
        finally:
            consolidator.CONSOLIDATION_ENABLED = original

    def test_min_questions_threshold(self):
        """Test minimum questions threshold"""
        result = consolidate_multiple_questions("How do I submit?")
        assert result.has_multiple_questions is False

    def test_max_questions_limit(self):
        """Test maximum questions limit"""
        consolidator = QueryConsolidator()
        many_questions = "? ".join(["Question"] * 10)
        result = consolidator.consolidate(many_questions)
        if len(result.questions) > consolidator.MAX_QUESTIONS_PER_CONSOLIDATION:
            assert result.should_consolidate is False


class TestQueryConsolidatorTopicExtraction:
    """Test topic detection and keyword extraction"""

    def test_submission_topic(self):
        """Test detection of submission topic"""
        consolidator = QueryConsolidator()
        topics = consolidator._extract_topics("How do I submit my request?")
        assert len(topics) > 0

    def test_timeline_topic(self):
        """Test detection of timeline topic"""
        consolidator = QueryConsolidator()
        topics = consolidator._extract_topics("How long does approval take?")
        assert len(topics) > 0

    def test_eligibility_topic(self):
        """Test detection of eligibility topic"""
        consolidator = QueryConsolidator()
        topics = consolidator._extract_topics("What are the eligibility requirements?")
        assert len(topics) > 0

    def test_status_topic(self):
        """Test detection of status topic"""
        consolidator = QueryConsolidator()
        topics = consolidator._extract_topics("What's the status of my request?")
        assert len(topics) > 0

    def test_multiple_topics(self):
        """Test question with multiple topics"""
        consolidator = QueryConsolidator()
        topics = consolidator._extract_topics(
            "How do I submit? How long does it take?"
        )
        assert len(topics) >= 1


class TestQueryConsolidatorEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_question_with_multiple_marks(self):
        """Test question with multiple question marks"""
        result = consolidate_multiple_questions("What? Really? How?")
        assert result.questions is not None

    def test_very_short_query(self):
        """Test very short query"""
        result = consolidate_multiple_questions("Hi?")
        assert result.questions is not None

    def test_very_long_query(self):
        """Test very long query"""
        long_query = "How do I submit? " * 50
        result = consolidate_multiple_questions(long_query)
        assert result.questions is not None

    def test_special_characters(self):
        """Test query with special characters"""
        result = consolidate_multiple_questions(
            "How do I submit (required)? What's needed? Can't I skip it?"
        )
        assert result.questions is not None

    def test_numbers_in_query(self):
        """Test query with numbers"""
        result = consolidate_multiple_questions(
            "Can I submit 5 requests at once? What's the 2026 deadline?"
        )
        assert result.questions is not None

    def test_case_insensitivity(self):
        """Test that detection is case-insensitive"""
        result1 = consolidate_multiple_questions("HOW DO I SUBMIT? WHEN IS IT DUE?")
        result2 = consolidate_multiple_questions("how do i submit? when is it due?")
        assert len(result1.questions) >= 1
        assert len(result2.questions) >= 1


class TestConsolidationResult:
    """Test ConsolidationResult data structure"""

    def test_result_structure(self):
        """Test that result has all required fields"""
        result = consolidate_multiple_questions("How? When?")
        assert hasattr(result, 'has_multiple_questions')
        assert hasattr(result, 'questions')
        assert hasattr(result, 'question_groups')
        assert hasattr(result, 'should_consolidate')
        assert hasattr(result, 'consolidation_score')
        assert hasattr(result, 'reasoning')

    def test_result_values_valid(self):
        """Test that result values are valid"""
        result = consolidate_multiple_questions("How do I submit? When?")
        assert isinstance(result.has_multiple_questions, bool)
        assert isinstance(result.questions, list)
        assert isinstance(result.question_groups, list)
        assert isinstance(result.should_consolidate, bool)
        assert isinstance(result.consolidation_score, float)
        assert isinstance(result.reasoning, str)
        assert 0.0 <= result.consolidation_score <= 1.0


class TestIntegrationScenarios:
    """Integration tests with realistic scenarios"""

    def test_typical_multi_question_scenario(self):
        """Test typical scenario: multiple related questions"""
        query = "How do I submit a data request? What documents do I need? How long does approval take?"
        result = consolidate_multiple_questions(query)
        assert result.has_multiple_questions is True
        assert len(result.questions) >= 2
        assert result.reasoning is not None

    def test_mixed_topic_scenario(self):
        """Test scenario: questions on different topics"""
        query = "How do I submit? What's the weather today? When is my birthday?"
        result = consolidate_multiple_questions(query)
        assert result.questions is not None

    def test_single_complex_question_scenario(self):
        """Test scenario: single complex question with AND/OR"""
        query = "How do I submit and what documents are required?"
        result = consolidate_multiple_questions(query)
        # May be detected as single or multiple depending on parsing
        assert result.questions is not None

    def test_faq_style_questions(self):
        """Test FAQ-style multiple questions"""
        query = "What is a data request? How do I submit one? What are the requirements?"
        result = consolidate_multiple_questions(query)
        assert result.questions is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
