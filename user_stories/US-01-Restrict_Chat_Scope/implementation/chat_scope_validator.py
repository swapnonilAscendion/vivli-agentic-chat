"""
US-01: Restrict Chat Scope to Eligible Chats and Stages

Validates that the chatbot is being used in appropriate chat contexts and workflow stages.
Restricts bot responses to:
- Chat type: open_chat only
- Request stages: draft_revision or form_check only

Configuration:
- ALLOWED_CHAT_TYPES: ["open_chat"]
- ALLOWED_STAGES: ["draft_revision", "form_check"]
- BLOCKED_CHAT_TYPES: ["contributors_chat", "requestor_chat", "private_org_chat"]
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Validation configuration - Order of execution matters
ALLOWED_CHAT_TYPES = ["open_chat"]
ALLOWED_STAGES = ["draft_revision", "form_check"]
BLOCKED_CHAT_TYPES = ["contributors_chat", "requestor_chat", "private_org_chat"]


def validate_chat_scope(
    chat_type: str,
    request_stage: str
) -> Tuple[bool, str]:
    """
    Validate chat type and request stage before allowing bot response.

    Rule 1: Check chat type is eligible (open chat only)
    Rule 2: Check data request stage is draft/revision or form-check
    Rule 3: Verify chat is not in other channels (Contributors, Requestor, Private)
    Rule 4: Verify request hasn't passed form-check validation stage

    Args:
        chat_type: Type of chat where query originated
                  (open_chat, contributors_chat, requestor_chat, private_org_chat)
        request_stage: Current stage of data request
                      (draft_revision, form_check, submitted, approved, rejected)

    Returns:
        Tuple of (is_valid: bool, error_message: str)
        - is_valid: True if chat scope is eligible, False otherwise
        - error_message: User-friendly error message if validation fails

    Eligible Conditions (Bot ALLOWS response):
    1. Open chat during draft/revision stage
    2. Open chat during Vivli form-check stage
    3. Chat is in active data request
    4. User is in correct workflow stage

    Ineligible Conditions (Bot DENIES response):
    1. Contributors chat
    2. Requestor chat
    3. Private Organization chat
    4. Stages past form-check
    5. After human form-check validation started
    """

    # Normalize inputs
    chat_type = (chat_type or "").lower().strip()
    request_stage = (request_stage or "").lower().strip()

    # Rule 1: Check if chat type is eligible
    if chat_type not in ALLOWED_CHAT_TYPES:
        if chat_type in BLOCKED_CHAT_TYPES:
            logger.warning(f"[US-01] Scope validation failed: Chat type '{chat_type}' not allowed")
            return (
                False,
                "This feature is only available in the open chat for your data request."
            )
        else:
            logger.warning(f"[US-01] Scope validation failed: Unknown chat type '{chat_type}'")
            return (
                False,
                "Unable to verify chat context. Please try again."
            )

    # Rule 2: Check if request stage is eligible
    if request_stage not in ALLOWED_STAGES:
        if request_stage == "submitted":
            logger.warning(f"[US-01] Scope validation failed: Stage '{request_stage}' - form-check not completed")
            return (
                False,
                "This feature is only available during the form-check stage of your request."
            )
        elif request_stage in ["approved", "rejected"]:
            logger.warning(f"[US-01] Scope validation failed: Stage '{request_stage}' - request completed")
            return (
                False,
                "Form-check has been completed. Please contact support for further assistance."
            )
        else:
            logger.warning(f"[US-01] Scope validation failed: Invalid stage '{request_stage}'")
            return (
                False,
                "This feature is only available during the form-check stage of your request."
            )

    # All checks passed
    logger.info(f"[US-01] Chat scope validation passed: chat_type='{chat_type}', stage='{request_stage}'")
    return (True, "")


def get_scope_validation_summary(chat_type: str, request_stage: str) -> dict:
    """
    Get a summary of scope validation results for debugging/logging.

    Args:
        chat_type: Type of chat
        request_stage: Current request stage

    Returns:
        Dictionary with validation details including:
        - is_valid: bool
        - chat_type: str
        - request_stage: str
        - allowed_chats: list
        - allowed_stages: list
        - error_message: str or None
    """
    is_valid, error_message = validate_chat_scope(chat_type, request_stage)

    return {
        "is_valid": is_valid,
        "chat_type": chat_type,
        "request_stage": request_stage,
        "allowed_chats": ALLOWED_CHAT_TYPES,
        "allowed_stages": ALLOWED_STAGES,
        "blocked_chats": BLOCKED_CHAT_TYPES,
        "error_message": error_message if not is_valid else None
    }
