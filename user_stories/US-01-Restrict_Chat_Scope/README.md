# US-01: Restrict Chat Scope to Eligible Chats and Stages

## Overview
Validates that the chatbot responds only in appropriate chat contexts and workflow stages.

## Description
The Vivli Agentic Chatbot should only operate within specific communication channels and at appropriate stages of the data request workflow. This user story implements scope-based access control to ensure the chatbot:
- Responds ONLY in the "open chat" channel
- Responds ONLY during draft/revision and form-check stages
- Blocks responses in Contributors, Requestor, and Private Org chats
- Blocks responses after request submission or completion

## Goal
Ensure the chatbot responds only in appropriate chat contexts and workflow stages, preventing confused users and maintaining proper workflow boundaries.

## Validation Rules (Order of Execution)

| # | Rule | Check |
|---|------|-------|
| 1 | Check chat type is eligible | open_chat only |
| 2 | Check request stage is eligible | draft_revision or form_check |
| 3 | Verify chat is not blocked | NOT (contributors, requestor, private) |
| 4 | Verify request not completed | NOT (submitted, approved, rejected) |

## Eligible Conditions (Bot ALLOWS)

✅ **Open chat during draft/revision stage**
- New requests in development
- User can still modify request

✅ **Open chat during form-check stage**
- Vivli form validation in progress
- User may need clarification

✅ **Chat is in active data request**
- Request not yet submitted
- Request not yet completed

✅ **User is in correct workflow stage**
- Before final submission
- Before human review completion

## Ineligible Conditions (Bot DENIES)

❌ **Contributors chat**
- Not intended for this feature

❌ **Requestor chat**
- Not intended for this feature

❌ **Private Organization chat**
- Not intended for this feature

❌ **Stages past form-check**
- After "submitted" - human review started
- After "approved" - access granted
- After "rejected" - request denied

## Error Messages

| Scenario | Error Message |
|----------|---------------|
| Wrong chat type (contributors, requestor, private) | "This feature is only available in the open chat for your data request." |
| Wrong stage (submitted, unknown) | "This feature is only available during the form-check stage of your request." |
| Stage completed (approved, rejected) | "Form-check has been completed. Please contact support for further assistance." |
| Chat not found | "Unable to verify chat context. Please try again." |

## Configuration

```python
ALLOWED_CHAT_TYPES = ["open_chat"]
ALLOWED_STAGES = ["draft_revision", "form_check"]
BLOCKED_CHAT_TYPES = ["contributors_chat", "requestor_chat", "private_org_chat"]
```

## Implementation

### Main Validator
**File:** `implementation/chat_scope_validator.py`

**Functions:**
- `validate_chat_scope(chat_type, request_stage) -> Tuple[bool, str]`
- `get_scope_validation_summary(chat_type, request_stage) -> dict`

### Test Suite
**File:** `tests/test_chat_scope_validator.py`

**Test Coverage:**
- ✅ 2 eligible scenarios
- ✅ 6 ineligible scenarios
- ✅ 6 edge cases
- ✅ 2 summary function tests
- **Total: 16 test cases**

## Integration Points

| Step | Integration |
|------|-------------|
| Step 0 | Role validation (US-02) |
| Step 0.5 | **Chat scope validation (THIS)** |
| Step 1 | Input validation (US-05) |
| Step 2 | Message grouping (US-03) |
| Step 3 | Query decomposition (US-04) |
| Step 4 | Intent classification (US-07) |

## Usage Example

```python
from chat_scope_validator import validate_chat_scope

# Valid case
is_valid, error = validate_chat_scope("open_chat", "draft_revision")
# Returns: (True, "")

# Invalid case - wrong chat
is_valid, error = validate_chat_scope("contributors_chat", "draft_revision")
# Returns: (False, "This feature is only available in the open chat for your data request.")

# Invalid case - wrong stage
is_valid, error = validate_chat_scope("open_chat", "approved")
# Returns: (False, "Form-check has been completed. Please contact support for further assistance.")
```

## Testing

Run the test suite:
```bash
cd user_stories/US-01-Restrict_Chat_Scope/tests
python test_chat_scope_validator.py
```

Expected output:
```
======================================================================
US-01 CHAT SCOPE VALIDATOR - TEST SUITE
======================================================================

[ELIGIBLE SCENARIOS - Should ALLOW]
[PASS] Test 1: Open chat + draft_revision allowed
[PASS] Test 2: Open chat + form_check allowed

[INELIGIBLE SCENARIOS - Should DENY]
[PASS] Test 3: Contributors chat denied
...

======================================================================
ALL TESTS PASSED!
======================================================================
```

## Files

```
US-01-Restrict_Chat_Scope/
├── implementation/
│   └── chat_scope_validator.py    # Main validation logic
├── tests/
│   └── test_chat_scope_validator.py  # Test suite (16 tests)
├── README.md                      # This file
└── ACCEPTANCE_CRITERIA.md         # Acceptance criteria
```

## Status
✅ Implementation Complete
✅ Test Suite Complete
✅ Documentation Complete
📋 Ready for Integration

## Author
Claude Code
Date: 2026-07-03
