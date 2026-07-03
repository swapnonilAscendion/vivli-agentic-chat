"""
US-02: Respond Only to Research Team
Validates user role and restricts chatbot responses to only research team members.

This module implements role-based access control to ensure the chatbot only
engages with researchers and team members, preventing system abuse and maintaining
appropriate access control.
"""

import logging
from typing import Tuple
from enum import Enum
from functools import lru_cache

logger = logging.getLogger(__name__)


class RoleValidationError(Enum):
    """Role validation error types"""
    INVALID_ROLE = "invalid_role"
    INELIGIBLE_ROLE = "ineligible_role"
    BOT_DETECTED = "bot_detected"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    USER_ROLE_NOT_FOUND = "user_role_not_found"
    VALID = "valid"


class RoleValidator:
    """
    Validate user role and determine if they should receive bot response.

    Implements role-based access control with:
    - Eligible role checking (researcher, team_member, etc.)
    - Bot/system detection
    - Caching for performance
    - Comprehensive error messages
    """

    # Configuration
    ROLE_CHECK_ENABLED = True
    ALLOW_SYSTEM_BOTS = False
    FALLBACK_TO_ESCALATION = True
    CACHE_ROLE_DATA = True

    # Eligible roles - researchers who should get responses
    ELIGIBLE_ROLES = {
        "researcher",
        "team_member",
        "data_request_creator",
        "research_team_admin"
    }

    # Ineligible roles - who should NOT get responses
    INELIGIBLE_ROLES = {
        "vivli_admin",
        "system_admin",
        "org_admin",
        "data_contributor",
        "contributor",
        "automated_notification",
        "bot_system",
        "irp_system",
        "data_curator",
        "guest"
    }

    # System bot patterns to detect
    BOT_PATTERNS = {
        "bot",
        "system",
        "automated",
        "notification",
        "irp"
    }

    def __init__(self):
        """Initialize role validator with configuration"""
        self.eligible_roles = self.ELIGIBLE_ROLES
        self.ineligible_roles = self.INELIGIBLE_ROLES
        logger.info("RoleValidator initialized")

    def validate(self, user_role: str, user_id: str = None) -> Tuple[bool, RoleValidationError]:
        """
        Validate user role and determine if they're eligible.

        Args:
            user_role: User's role (e.g., 'researcher', 'vivli_admin')
            user_id: User's ID for logging and tracking

        Returns:
            (is_eligible, error_type)
            - is_eligible: True if user can access chatbot
            - error_type: RoleValidationError enum indicating what's wrong
        """

        if not self.ROLE_CHECK_ENABLED:
            logger.warning("Role check is disabled")
            return True, RoleValidationError.VALID

        # Check 1: Role is present
        if not user_role:
            logger.warning(f"[{user_id}] Role validation failed: missing_role")
            return False, RoleValidationError.USER_ROLE_NOT_FOUND

        user_role_lower = user_role.lower().strip()

        # Check 2: Role is not a bot/system
        if self._is_bot_or_system(user_role_lower):
            if not self.ALLOW_SYSTEM_BOTS:
                logger.warning(f"[{user_id}] Role validation failed: bot_detected ({user_role_lower})")
                return False, RoleValidationError.BOT_DETECTED

        # Check 3: Role is in eligible list
        if user_role_lower not in self.eligible_roles:
            logger.warning(f"[{user_id}] Role validation failed: ineligible_role ({user_role_lower})")
            return False, RoleValidationError.INELIGIBLE_ROLE

        logger.info(f"[{user_id}] Role validation passed: {user_role_lower}")
        return True, RoleValidationError.VALID

    def _is_bot_or_system(self, user_role: str) -> bool:
        """
        Check if user is an automated bot or system service.

        Args:
            user_role: User role to check

        Returns:
            True if user is a bot/system, False otherwise
        """
        user_role_lower = user_role.lower()

        # Check if any bot pattern matches
        for pattern in self.BOT_PATTERNS:
            if pattern in user_role_lower:
                return True

        return False

    def is_eligible_role(self, user_role: str) -> bool:
        """
        Check if user role is eligible for chatbot access.

        Args:
            user_role: User's role

        Returns:
            True if role is in eligible list, False otherwise
        """
        if not user_role:
            return False

        return user_role.lower().strip() in self.eligible_roles

    @staticmethod
    def get_error_message(error_type: RoleValidationError) -> str:
        """
        Get user-friendly error message for role validation error.

        Args:
            error_type: The type of role validation error

        Returns:
            User-friendly error message string
        """
        error_messages = {
            RoleValidationError.INVALID_ROLE: (
                "I'm sorry, but I can only assist research team members. "
                "If you're a researcher, please contact support to verify your account."
            ),
            RoleValidationError.INELIGIBLE_ROLE: (
                "I'm sorry, but this service is only available to research team members. "
                "Please contact the research team for assistance."
            ),
            RoleValidationError.BOT_DETECTED: (
                "This is an automated system and cannot respond to non-researcher queries."
            ),
            RoleValidationError.UNAUTHORIZED_ACCESS: (
                "Access denied. This service requires research team membership."
            ),
            RoleValidationError.USER_ROLE_NOT_FOUND: (
                "Unable to verify your role. Please contact support for assistance."
            ),
        }

        return error_messages.get(
            error_type,
            "Access denied. Please contact support."
        )


# Global validator instance
validator = RoleValidator()


def validate_user_role(user_role: str, user_id: str = None) -> Tuple[bool, str]:
    """
    Validate user role and return (is_eligible, error_message).

    This is the main entry point for US-02 role-based access control.

    Args:
        user_role: User's role from request
        user_id: User's ID for logging

    Returns:
        (is_eligible, response)
        - is_eligible: True if user is eligible, False if denied
        - response: Error message if denied, empty string if eligible

    Example:
        >>> is_eligible, error = validate_user_role("researcher", "user_123")
        >>> if is_eligible:
        ...     print("User can access chatbot")
        ... else:
        ...     print(f"Access denied: {error}")
    """
    is_eligible, error_type = validator.validate(user_role, user_id)

    if is_eligible:
        return True, ""
    else:
        error_message = RoleValidator.get_error_message(error_type)
        return False, error_message


# Example usage and testing
if __name__ == "__main__":
    # Test with eligible role
    print("Testing eligible role (researcher):")
    is_eligible, error = validate_user_role("researcher", "user_001")
    print(f"  Eligible: {is_eligible}, Error: {error}\n")

    # Test with ineligible role
    print("Testing ineligible role (vivli_admin):")
    is_eligible, error = validate_user_role("vivli_admin", "user_002")
    print(f"  Eligible: {is_eligible}, Error: {error}\n")

    # Test with bot role
    print("Testing bot role (bot_system):")
    is_eligible, error = validate_user_role("bot_system", "bot_001")
    print(f"  Eligible: {is_eligible}, Error: {error}\n")

    # Test with missing role
    print("Testing missing role:")
    is_eligible, error = validate_user_role("", "user_003")
    print(f"  Eligible: {is_eligible}, Error: {error}\n")

    # Test with team_member
    print("Testing eligible role (team_member):")
    is_eligible, error = validate_user_role("team_member", "user_004")
    print(f"  Eligible: {is_eligible}, Error: {error}")
