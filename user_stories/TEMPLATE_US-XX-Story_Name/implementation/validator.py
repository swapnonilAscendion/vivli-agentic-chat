"""
{{US_ID}}: {{US_NAME}}
{{DESCRIPTION}}

This module implements {{GOAL}}
"""

import logging
import re
from typing import Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationError(Enum):
    """Validation error types for {{US_ID}}"""
    {{ERROR_TYPE_1}} = "{{error_type_1}}"
    {{ERROR_TYPE_2}} = "{{error_type_2}}"
    {{ERROR_TYPE_3}} = "{{error_type_3}}"
    VALID = "valid"


class {{VALIDATOR_CLASS_NAME}}:
    """
    Validate {{DESCRIPTION}} per {{US_ID}}.

    Implements the following checks:
    1. {{VALIDATION_RULE_1}}
    2. {{VALIDATION_RULE_2}}
    3. {{VALIDATION_RULE_3}}
    """

    # Configuration
    {{PARAMETER_1}} = {{VALUE_1}}  # Description of parameter
    {{PARAMETER_2}} = {{VALUE_2}}  # Description of parameter
    {{PARAMETER_3}} = {{VALUE_3}}  # Description of parameter

    # Patterns (if needed)
    {{PATTERN_1}} = [
        r'pattern1',
        r'pattern2',
    ]

    def __init__(self):
        """Initialize validator with compiled patterns"""
        # Compile regex patterns if using regex
        self.pattern1_regex = [re.compile(p, re.IGNORECASE) for p in self.{{PATTERN_1}}]

    def validate(self, input_text: str) -> Tuple[bool, ValidationError]:
        """
        Validate input according to {{US_ID}} rules.

        Args:
            input_text: Raw user input to validate

        Returns:
            (is_valid, error_type)
            - is_valid: True if validation passes
            - error_type: ValidationError enum indicating what's wrong (or VALID)

        Validation Flow:
            1. {{VALIDATION_RULE_1}}
            2. {{VALIDATION_RULE_2}}
            3. {{VALIDATION_RULE_3}}
        """

        if not input_text:
            logger.warning("Validation failed: empty input")
            return False, ValidationError.{{ERROR_TYPE_1}}

        # Check 1: {{VALIDATION_RULE_1}}
        if not self._check_rule_1(input_text):
            logger.warning(f"Validation failed: {{VALIDATION_RULE_1}}")
            return False, ValidationError.{{ERROR_TYPE_1}}

        # Check 2: {{VALIDATION_RULE_2}}
        if not self._check_rule_2(input_text):
            logger.warning(f"Validation failed: {{VALIDATION_RULE_2}}")
            return False, ValidationError.{{ERROR_TYPE_2}}

        # Check 3: {{VALIDATION_RULE_3}}
        if not self._check_rule_3(input_text):
            logger.warning(f"Validation failed: {{VALIDATION_RULE_3}}")
            return False, ValidationError.{{ERROR_TYPE_3}}

        logger.info("Validation passed: input is valid")
        return True, ValidationError.VALID

    def _check_rule_1(self, text: str) -> bool:
        """
        Check: {{VALIDATION_RULE_1}}

        Args:
            text: Input to check

        Returns:
            True if check passes, False otherwise
        """
        # Implementation of rule 1
        # Example:
        # if len(text) < self.{{PARAMETER_1}}:
        #     return False
        # return True
        pass

    def _check_rule_2(self, text: str) -> bool:
        """
        Check: {{VALIDATION_RULE_2}}

        Args:
            text: Input to check

        Returns:
            True if check passes, False otherwise
        """
        # Implementation of rule 2
        pass

    def _check_rule_3(self, text: str) -> bool:
        """
        Check: {{VALIDATION_RULE_3}}

        Args:
            text: Input to check

        Returns:
            True if check passes, False otherwise
        """
        # Implementation of rule 3
        pass

    @staticmethod
    def get_error_message(error_type: ValidationError) -> str:
        """
        Get user-friendly error message for validation error.

        Args:
            error_type: The type of validation error

        Returns:
            User-friendly error message string
        """
        error_messages = {
            ValidationError.{{ERROR_TYPE_1}}: "{{ERROR_TYPE_1_MESSAGE}}",
            ValidationError.{{ERROR_TYPE_2}}: "{{ERROR_TYPE_2_MESSAGE}}",
            ValidationError.{{ERROR_TYPE_3}}: "{{ERROR_TYPE_3_MESSAGE}}",
        }

        return error_messages.get(error_type, "I'm sorry, but I couldn't understand your request.")


# Global validator instance
validator = {{VALIDATOR_CLASS_NAME}}()


def validate_input(input_text: str) -> Tuple[bool, str]:
    """
    Validate user input and return (is_valid, error_message).

    This is the main entry point for {{US_ID}} validation.

    Args:
        input_text: Raw user input

    Returns:
        (is_valid, response)
        - is_valid: True if validation passes
        - response: Error message if invalid, empty string if valid

    Example:
        >>> is_valid, error_msg = validate_input("user input")
        >>> if is_valid:
        ...     print("Input is valid!")
        ... else:
        ...     print(f"Error: {error_msg}")
    """
    is_valid, error_type = validator.validate(input_text)

    if is_valid:
        return True, ""
    else:
        error_message = {{VALIDATOR_CLASS_NAME}}.get_error_message(error_type)
        return False, error_message


# Example usage
if __name__ == "__main__":
    # Test with valid input
    valid_input = "example valid input"
    is_valid, error = validate_input(valid_input)
    print(f"Valid input: {is_valid}, Error: {error}")

    # Test with invalid input
    invalid_input = "invalid"
    is_valid, error = validate_input(invalid_input)
    print(f"Invalid input: {is_valid}, Error: {error}")
