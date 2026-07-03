"""
Unit tests for Input Validator (US-05)
Tests all edge cases from FRD
"""

import pytest
from input_validator import InputValidator, ValidationError, validate_input


class TestInputValidator:
    """Test input validation logic"""

    def setup_method(self):
        """Setup validator for each test"""
        self.validator = InputValidator()

    # ===== BLANK MESSAGE TESTS =====
    def test_blank_message(self):
        """Should reject blank message"""
        is_valid, error = self.validator.validate("")
        assert not is_valid
        assert error == ValidationError.BLANK_MESSAGE

    def test_whitespace_only_message(self):
        """Should reject whitespace-only message"""
        is_valid, error = self.validator.validate("   ")
        assert not is_valid
        assert error == ValidationError.BLANK_MESSAGE

    def test_newline_only_message(self):
        """Should reject newline-only message"""
        is_valid, error = self.validator.validate("\n\n\n")
        assert not is_valid
        assert error == ValidationError.BLANK_MESSAGE

    # ===== LENGTH TESTS =====
    def test_too_short_message(self):
        """Should reject single word"""
        is_valid, error = self.validator.validate("hi")
        assert not is_valid
        assert error == ValidationError.TOO_SHORT

    def test_too_long_message(self):
        """Should reject message with 500+ words"""
        long_text = " ".join(["word"] * 501)
        is_valid, error = self.validator.validate(long_text)
        assert not is_valid
        assert error == ValidationError.TOO_LONG

    def test_valid_length_message(self):
        """Should accept message with 2-500 words"""
        valid_text = "What is a data request?"
        is_valid, error = self.validator.validate(valid_text)
        assert is_valid
        assert error == ValidationError.VALID

    # ===== HTML DETECTION TESTS =====
    def test_html_tag_detection(self):
        """Should detect HTML tags"""
        is_valid, error = self.validator.validate("Check this <script>alert('hi')</script>")
        assert not is_valid
        assert error == ValidationError.HTML_DETECTED

    def test_html_onclick_detection(self):
        """Should detect onclick handlers"""
        is_valid, error = self.validator.validate("Click here <button onclick='alert()'>")
        assert not is_valid
        assert error == ValidationError.HTML_DETECTED

    def test_html_doctype_detection(self):
        """Should detect DOCTYPE"""
        is_valid, error = self.validator.validate("<!DOCTYPE html><html>")
        assert not is_valid
        assert error == ValidationError.HTML_DETECTED

    # ===== CODE DETECTION TESTS =====
    def test_python_code_detection(self):
        """Should detect Python code"""
        is_valid, error = self.validator.validate("def my_function(): pass")
        assert not is_valid
        assert error == ValidationError.CODE_DETECTED

    def test_javascript_code_detection(self):
        """Should detect JavaScript code"""
        is_valid, error = self.validator.validate("function test() { return true; }")
        assert not is_valid
        assert error == ValidationError.CODE_DETECTED

    def test_code_fence_detection(self):
        """Should detect code fences"""
        is_valid, error = self.validator.validate("```python\ncode here\n```")
        assert not is_valid
        assert error == ValidationError.CODE_DETECTED

    # ===== EMOJI TESTS =====
    def test_emoji_only_message(self):
        """Should reject emoji-only messages"""
        is_valid, error = self.validator.validate("😂😂😂 🎉🎉🎉")
        assert not is_valid
        assert error == ValidationError.ONLY_EMOJIS

    def test_emoji_with_text_is_valid(self):
        """Should accept text with emojis"""
        is_valid, error = self.validator.validate("Great question! 😊 How can I help?")
        assert is_valid
        assert error == ValidationError.VALID

    # ===== SPECIAL CHARACTERS TESTS =====
    def test_special_chars_only(self):
        """Should reject special character only messages"""
        is_valid, error = self.validator.validate("!@#$%^&*()")
        assert not is_valid
        assert error == ValidationError.ONLY_SPECIAL_CHARS

    def test_special_chars_with_text_is_valid(self):
        """Should accept text with special chars"""
        is_valid, error = self.validator.validate("What is the cost? (USD)")
        assert is_valid
        assert error == ValidationError.VALID

    # ===== LANGUAGE TESTS =====
    def test_chinese_non_english(self):
        """Should detect Chinese text as non-English"""
        is_valid, error = self.validator.validate("你好，这是什么？")
        assert not is_valid
        assert error == ValidationError.NON_ENGLISH

    def test_japanese_non_english(self):
        """Should detect Japanese as non-English"""
        is_valid, error = self.validator.validate("これは何ですか？")
        assert not is_valid
        assert error == ValidationError.NON_ENGLISH

    def test_korean_non_english(self):
        """Should detect Korean as non-English"""
        is_valid, error = self.validator.validate("이것은 무엇입니까?")
        assert not is_valid
        assert error == ValidationError.NON_ENGLISH

    def test_english_text_is_valid(self):
        """Should accept English text"""
        is_valid, error = self.validator.validate("How do I submit a data request?")
        assert is_valid
        assert error == ValidationError.VALID

    # ===== SPAM TESTS =====
    def test_url_spam_detection(self):
        """Should detect URLs as potential spam"""
        is_valid, error = self.validator.validate(
            "Click here http://malicious-site.com/malware and check this link https://another-bad-site.com"
        )
        assert not is_valid
        assert error == ValidationError.SPAM_DETECTED

    def test_clickbait_spam_detection(self):
        """Should detect clickbait patterns"""
        is_valid, error = self.validator.validate("Click here now for amazing deal!")
        assert not is_valid
        assert error == ValidationError.SPAM_DETECTED

    def test_legitimate_message_not_spam(self):
        """Should not flag legitimate messages as spam"""
        is_valid, error = self.validator.validate("What is the form check process?")
        assert is_valid
        assert error == ValidationError.VALID

    # ===== INTEGRATION TESTS =====
    def test_real_world_valid_query_1(self):
        """Real world: FAQ question about data request"""
        query = "How do I submit a data request to Vivli?"
        is_valid, error = self.validator.validate(query)
        assert is_valid
        assert error == ValidationError.VALID

    def test_real_world_valid_query_2(self):
        """Real world: Question about form check"""
        query = "What changes do I need to make following the form check feedback?"
        is_valid, error = self.validator.validate(query)
        assert is_valid
        assert error == ValidationError.VALID

    def test_real_world_valid_query_3(self):
        """Real world: Status question"""
        query = "What is the current status of my data request?"
        is_valid, error = self.validator.validate(query)
        assert is_valid
        assert error == ValidationError.VALID

    def test_real_world_invalid_pasted_code(self):
        """Real world: Pasted code"""
        code_snippet = """
        def process_request(req_id):
            url = f"/api/requests/{req_id}"
            response = requests.get(url)
            return response.json()
        """ * 20  # Make it long
        is_valid, error = self.validator.validate(code_snippet)
        assert not is_valid
        # Could be too long or code detection
        assert error in [ValidationError.CODE_DETECTED, ValidationError.TOO_LONG]

    def test_real_world_invalid_pasted_html(self):
        """Real world: Pasted HTML"""
        html_snippet = "<html><body><div class='content'>" * 50
        is_valid, error = self.validator.validate(html_snippet)
        assert not is_valid
        assert error == ValidationError.HTML_DETECTED

    # ===== EDGE CASES =====
    def test_punctuation_and_numbers(self):
        """Should accept text with numbers and punctuation"""
        is_valid, error = self.validator.validate("What is REQ-123456? Can I track it?")
        assert is_valid
        assert error == ValidationError.VALID

    def test_contracted_words(self):
        """Should accept contractions"""
        is_valid, error = self.validator.validate("I don't understand what's happening. Can you help?")
        assert is_valid
        assert error == ValidationError.VALID

    def test_mixed_case(self):
        """Should accept mixed case"""
        is_valid, error = self.validator.validate("WHAT is a Data Request?")
        assert is_valid
        assert error == ValidationError.VALID

    # ===== ERROR MESSAGE TESTS =====
    def test_error_message_for_blank(self):
        """Should get appropriate error message for blank"""
        msg = InputValidator.get_error_message(ValidationError.BLANK_MESSAGE)
        assert "couldn't understand" in msg or "rephrase" in msg

    def test_error_message_for_too_long(self):
        """Should get appropriate error message for too long"""
        msg = InputValidator.get_error_message(ValidationError.TOO_LONG)
        assert "too long" in msg or "smaller" in msg

    def test_error_message_for_non_english(self):
        """Should get appropriate error message for non-English"""
        msg = InputValidator.get_error_message(ValidationError.NON_ENGLISH)
        assert "English" in msg

    # ===== INTEGRATION WITH HELPER FUNCTION =====
    def test_validate_input_wrapper_valid(self):
        """Test validate_input helper function with valid input"""
        is_valid, msg = validate_input("How do I submit a request?")
        assert is_valid
        assert msg == ""

    def test_validate_input_wrapper_invalid(self):
        """Test validate_input helper function with invalid input"""
        is_valid, msg = validate_input("")
        assert not is_valid
        assert len(msg) > 0
        assert "couldn't understand" in msg


class TestValidatorConfiguration:
    """Test validator configuration"""

    def test_message_length_limits(self):
        """Verify message length limits are configured"""
        validator = InputValidator()
        assert validator.MIN_MESSAGE_LENGTH > 0
        assert validator.MAX_MESSAGE_LENGTH > validator.MIN_MESSAGE_LENGTH
        assert validator.MAX_MESSAGE_CHARS > 0

    def test_patterns_are_compiled(self):
        """Verify regex patterns are compiled"""
        validator = InputValidator()
        assert len(validator.html_regex) > 0
        assert len(validator.code_regex) > 0
        assert len(validator.spam_regex) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
