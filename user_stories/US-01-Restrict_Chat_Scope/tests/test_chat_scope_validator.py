"""
US-01 Chat Scope Validator Tests

Test scenarios for chat scope validation:
- Eligible conditions (should ALLOW)
- Ineligible conditions (should DENY)
- Edge cases and error handling
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "implementation"))

from chat_scope_validator import validate_chat_scope, get_scope_validation_summary


class TestChatScopeValidator:
    """Test chat scope validation logic"""

    # =========================================================================
    # TEST SCENARIOS - ELIGIBLE (Should ALLOW)
    # =========================================================================

    def test_open_chat_draft_revision_stage_allowed(self):
        """Test 1: Standard researcher in open chat during draft stage"""
        is_valid, error = validate_chat_scope("open_chat", "draft_revision")
        assert is_valid == True
        assert error == ""
        print("[PASS] Test 1: Open chat + draft_revision allowed")

    def test_open_chat_form_check_stage_allowed(self):
        """Test 2: Researcher in open chat during form-check stage"""
        is_valid, error = validate_chat_scope("open_chat", "form_check")
        assert is_valid == True
        assert error == ""
        print("[PASS] Test 2: Open chat + form_check allowed")

    # =========================================================================
    # TEST SCENARIOS - INELIGIBLE (Should DENY)
    # =========================================================================

    def test_contributors_chat_denied(self):
        """Test 3: Researcher in contributors chat (wrong chat type)"""
        is_valid, error = validate_chat_scope("contributors_chat", "draft_revision")
        assert is_valid == False
        assert "open chat" in error.lower()
        print("[PASS] Test 3: Contributors chat denied")

    def test_requestor_chat_denied(self):
        """Test 4: Researcher in requestor chat (wrong chat type)"""
        is_valid, error = validate_chat_scope("requestor_chat", "form_check")
        assert is_valid == False
        assert "open chat" in error.lower()
        print("[PASS] Test 4: Requestor chat denied")

    def test_private_org_chat_denied(self):
        """Test 5: Researcher in private org chat (wrong chat type)"""
        is_valid, error = validate_chat_scope("private_org_chat", "draft_revision")
        assert is_valid == False
        assert "open chat" in error.lower()
        print("[PASS] Test 5: Private org chat denied")

    def test_submitted_stage_denied(self):
        """Test 6: Open chat but request already submitted (wrong stage)"""
        is_valid, error = validate_chat_scope("open_chat", "submitted")
        assert is_valid == False
        assert "form-check" in error.lower()
        print("[PASS] Test 6: Submitted stage denied")

    def test_approved_stage_denied(self):
        """Test 7: Open chat but request approved (completed)"""
        is_valid, error = validate_chat_scope("open_chat", "approved")
        assert is_valid == False
        assert "completed" in error.lower()
        print("[PASS] Test 7: Approved stage denied")

    def test_rejected_stage_denied(self):
        """Test 8: Open chat but request rejected (completed)"""
        is_valid, error = validate_chat_scope("open_chat", "rejected")
        assert is_valid == False
        assert "completed" in error.lower()
        print("[PASS] Test 8: Rejected stage denied")

    # =========================================================================
    # TEST SCENARIOS - EDGE CASES
    # =========================================================================

    def test_case_insensitive_open_chat(self):
        """Test 9: Case insensitivity for open_chat"""
        is_valid, error = validate_chat_scope("OPEN_CHAT", "draft_revision")
        assert is_valid == True
        print("[PASS] Test 9: Case insensitive - OPEN_CHAT accepted")

    def test_case_insensitive_stage(self):
        """Test 10: Case insensitivity for stage"""
        is_valid, error = validate_chat_scope("open_chat", "DRAFT_REVISION")
        assert is_valid == True
        print("[PASS] Test 10: Case insensitive - DRAFT_REVISION accepted")

    def test_empty_chat_type_denied(self):
        """Test 11: Empty chat type denied"""
        is_valid, error = validate_chat_scope("", "draft_revision")
        assert is_valid == False
        print("[PASS] Test 11: Empty chat_type denied")

    def test_none_chat_type_denied(self):
        """Test 12: None chat type denied"""
        is_valid, error = validate_chat_scope(None, "draft_revision")
        assert is_valid == False
        print("[PASS] Test 12: None chat_type denied")

    def test_unknown_stage_denied(self):
        """Test 13: Unknown stage denied"""
        is_valid, error = validate_chat_scope("open_chat", "unknown_stage")
        assert is_valid == False
        print("[PASS] Test 13: Unknown stage denied")

    def test_whitespace_normalization(self):
        """Test 14: Whitespace trimmed"""
        is_valid, error = validate_chat_scope("  open_chat  ", "  draft_revision  ")
        assert is_valid == True
        print("[PASS] Test 14: Whitespace normalized")

    # =========================================================================
    # TEST SCENARIOS - SUMMARY FUNCTION
    # =========================================================================

    def test_validation_summary_valid(self):
        """Test 15: Validation summary for valid case"""
        summary = get_scope_validation_summary("open_chat", "draft_revision")
        assert summary["is_valid"] == True
        assert summary["chat_type"] == "open_chat"
        assert summary["request_stage"] == "draft_revision"
        assert summary["error_message"] is None
        print("[PASS] Test 15: Validation summary - valid case")

    def test_validation_summary_invalid(self):
        """Test 16: Validation summary for invalid case"""
        summary = get_scope_validation_summary("contributors_chat", "draft_revision")
        assert summary["is_valid"] == False
        assert summary["chat_type"] == "contributors_chat"
        assert summary["error_message"] is not None
        print("[PASS] Test 16: Validation summary - invalid case")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("US-01 CHAT SCOPE VALIDATOR - TEST SUITE")
    print("=" * 70 + "\n")

    test_instance = TestChatScopeValidator()

    # Eligible scenarios
    print("\n[ELIGIBLE SCENARIOS - Should ALLOW]")
    test_instance.test_open_chat_draft_revision_stage_allowed()
    test_instance.test_open_chat_form_check_stage_allowed()

    # Ineligible scenarios
    print("\n[INELIGIBLE SCENARIOS - Should DENY]")
    test_instance.test_contributors_chat_denied()
    test_instance.test_requestor_chat_denied()
    test_instance.test_private_org_chat_denied()
    test_instance.test_submitted_stage_denied()
    test_instance.test_approved_stage_denied()
    test_instance.test_rejected_stage_denied()

    # Edge cases
    print("\n[EDGE CASES & NORMALIZATION]")
    test_instance.test_case_insensitive_open_chat()
    test_instance.test_case_insensitive_stage()
    test_instance.test_empty_chat_type_denied()
    test_instance.test_none_chat_type_denied()
    test_instance.test_unknown_stage_denied()
    test_instance.test_whitespace_normalization()

    # Summary function
    print("\n[VALIDATION SUMMARY FUNCTION]")
    test_instance.test_validation_summary_valid()
    test_instance.test_validation_summary_invalid()

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_tests()
