"""
Input Validator for Vivli Agentic Chat
Handles edge cases and invalid inputs gracefully per US-05
"""

import logging
import re
from typing import Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationError(Enum):
    """Validation error types"""
    BLANK_MESSAGE = "blank_message"
    TOO_SHORT = "too_short"
    TOO_LONG = "too_long"
    HTML_DETECTED = "html_detected"
    CODE_DETECTED = "code_detected"
    NON_ENGLISH = "non_english"
    SPAM_DETECTED = "spam_detected"
    OFFENSIVE_CONTENT = "offensive_content"
    ONLY_EMOJIS = "only_emojis"
    ONLY_SPECIAL_CHARS = "only_special_chars"
    VALID = "valid"


class InputValidator:
    """Validate incoming chat messages for quality and safety"""

    # Configuration
    MIN_MESSAGE_LENGTH = 1  # Minimum words (allow single-word greetings/queries)
    MAX_MESSAGE_LENGTH = 500  # Maximum words (avoid pasted documents)
    MAX_MESSAGE_CHARS = 3000  # Maximum characters

    # HTML/code patterns
    HTML_PATTERNS = [
        r'<[^>]+>',  # HTML tags
        r'<!DOCTYPE',
        r'<html',
        r'<script',
        r'onclick=',
        r'onerror=',
    ]

    CODE_PATTERNS = [
        r'def\s+\w+',  # Python function
        r'function\s+\w+',  # JavaScript function
        r'public\s+\w+',  # Java/C#
        r'import\s+\w+',  # Import statements
        r'#include',  # C includes
        r'```',  # Code fence
    ]

    # Offensive content (basic patterns)
    OFFENSIVE_WORDS = [
        'badword1', 'badword2',  # Add actual offensive words if needed
        # NOTE: In production, use a proper profanity filter library
    ]

    # Spam patterns
    SPAM_PATTERNS = [
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs
        r'(?:check\s+)?(?:this|the)\s+(?:link|site|page)',  # Link spam
        r'(?:click\s+)?(?:here|now)',  # Click bait
        r'(?:buy|sell|free|offer|discount|deal)',  # Commercial spam
    ]

    # Special characters only
    SPECIAL_CHAR_PATTERN = r'^[^a-zA-Z0-9\s]+$'

    # Emoji pattern
    EMOJI_PATTERN = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251\U0001f926-\U0001f937\U00010000-\U0010ffff☀-⭕‍⏏⏩⌚️〰]+'

    def __init__(self):
        """Initialize validator with compiled regex patterns"""
        self.html_regex = [re.compile(p, re.IGNORECASE) for p in self.HTML_PATTERNS]
        self.code_regex = [re.compile(p, re.IGNORECASE) for p in self.CODE_PATTERNS]
        self.spam_regex = [re.compile(p, re.IGNORECASE) for p in self.SPAM_PATTERNS]
        self.emoji_regex = re.compile(self.EMOJI_PATTERN)
        self.special_char_regex = re.compile(self.SPECIAL_CHAR_PATTERN)

    def validate(self, message_text: str) -> Tuple[bool, ValidationError]:
        """
        Validate input message.

        Args:
            message_text: Raw user message

        Returns:
            (is_valid, error_type)
            - is_valid: True if message passed all checks
            - error_type: ValidationError enum indicating what's wrong
        """
        if not message_text:
            return False, ValidationError.BLANK_MESSAGE

        # Check 1: Not blank/whitespace only
        if not message_text or message_text.isspace():
            logger.warning("Validation failed: blank message")
            return False, ValidationError.BLANK_MESSAGE

        # Check 2: Message length (words)
        word_count = len(message_text.split())
        if word_count < self.MIN_MESSAGE_LENGTH:
            logger.warning(f"Validation failed: too short ({word_count} words)")
            return False, ValidationError.TOO_SHORT

        if word_count > self.MAX_MESSAGE_LENGTH:
            logger.warning(f"Validation failed: too long ({word_count} words)")
            return False, ValidationError.TOO_LONG

        # Check 3: Message length (characters)
        if len(message_text) > self.MAX_MESSAGE_CHARS:
            logger.warning(f"Validation failed: too many characters ({len(message_text)})")
            return False, ValidationError.TOO_LONG

        # Check 4: Not only emojis
        if self._is_only_emojis(message_text):
            logger.warning("Validation failed: only emojis")
            return False, ValidationError.ONLY_EMOJIS

        # Check 5: Not only special characters
        if self.special_char_regex.match(message_text):
            logger.warning("Validation failed: only special characters")
            return False, ValidationError.ONLY_SPECIAL_CHARS

        # Check 6: Not HTML/code
        if self._contains_html(message_text):
            logger.warning("Validation failed: HTML detected")
            return False, ValidationError.HTML_DETECTED

        if self._contains_code(message_text):
            logger.warning("Validation failed: Code detected")
            return False, ValidationError.CODE_DETECTED

        # Check 7: Language detection (basic - check for common non-English patterns)
        if self._is_non_english(message_text):
            logger.warning("Validation failed: non-English detected")
            return False, ValidationError.NON_ENGLISH

        # Check 8: Not spam
        if self._is_spam(message_text):
            logger.warning("Validation failed: spam detected")
            return False, ValidationError.SPAM_DETECTED

        # Check 9: Not offensive
        if self._contains_offensive_content(message_text):
            logger.warning("Validation failed: offensive content")
            return False, ValidationError.OFFENSIVE_CONTENT

        logger.info("Validation passed: message is valid")
        return True, ValidationError.VALID

    def _is_only_emojis(self, text: str) -> bool:
        """Check if message contains only emojis and whitespace"""
        # Remove emoji characters
        text_no_emoji = self.emoji_regex.sub('', text).strip()
        # If nothing left, it was only emojis
        return len(text_no_emoji) == 0 and self.emoji_regex.search(text) is not None

    def _contains_html(self, text: str) -> bool:
        """Check if message contains HTML"""
        return any(pattern.search(text) for pattern in self.html_regex)

    def _contains_code(self, text: str) -> bool:
        """Check if message contains code snippets"""
        return any(pattern.search(text) for pattern in self.code_regex)

    def _is_non_english(self, text: str) -> bool:
        """Check if message is primarily non-English"""
        # Basic heuristic: check for common non-Latin scripts
        non_latin_patterns = [
            r'[一-鿿]',  # Chinese
            r'[぀-ゟ゠-ヿ]',  # Japanese
            r'[가-힯]',  # Korean
            r'[؀-ۿ]',  # Arabic
            r'[Ѐ-ӿ]',  # Cyrillic
            r'[฀-๿]',  # Thai
        ]

        for pattern in non_latin_patterns:
            if re.search(pattern, text):
                # Count non-Latin vs Latin characters
                non_latin_chars = len(re.findall(pattern, text))
                latin_chars = len(re.findall(r'[a-zA-Z]', text))

                # If more non-Latin than Latin, consider it non-English
                if non_latin_chars > latin_chars:
                    return True

        return False

    def _is_spam(self, text: str) -> bool:
        """Check if message is spam"""
        spam_score = 0

        # Count spam patterns
        for pattern in self.spam_regex:
            if pattern.search(text):
                spam_score += 1

        # If multiple spam indicators, flag as spam
        return spam_score >= 2

    def _contains_offensive_content(self, text: str) -> bool:
        """Check if message contains offensive words"""
        text_lower = text.lower()
        return any(word in text_lower for word in self.OFFENSIVE_WORDS)

    @staticmethod
    def get_error_message(error_type: ValidationError) -> str:
        """Get user-friendly error message for validation error"""
        standard_response = (
            "I'm sorry, but I couldn't understand your question. "
            "Please rephrase and send it again."
        )

        # Map specific errors to messages (can be customized)
        error_messages = {
            ValidationError.BLANK_MESSAGE: standard_response,
            ValidationError.TOO_SHORT: standard_response,
            ValidationError.TOO_LONG: "Your message is too long. Please break it into smaller questions.",
            ValidationError.HTML_DETECTED: standard_response,
            ValidationError.CODE_DETECTED: standard_response,
            ValidationError.NON_ENGLISH: "Please ask your question in English.",
            ValidationError.SPAM_DETECTED: standard_response,
            ValidationError.OFFENSIVE_CONTENT: "Please keep your message respectful.",
            ValidationError.ONLY_EMOJIS: standard_response,
            ValidationError.ONLY_SPECIAL_CHARS: standard_response,
        }

        return error_messages.get(error_type, standard_response)


# Global validator instance
validator = InputValidator()


def validate_input(message_text: str) -> Tuple[bool, str]:
    """
    Validate user input and return (is_valid, response_if_invalid).

    Args:
        message_text: Raw user message

    Returns:
        (is_valid, response)
        - is_valid: True if message is valid
        - response: Error message if invalid, empty string if valid
    """
    is_valid, error_type = validator.validate(message_text)

    if is_valid:
        return True, ""
    else:
        error_message = InputValidator.get_error_message(error_type)
        return False, error_message
