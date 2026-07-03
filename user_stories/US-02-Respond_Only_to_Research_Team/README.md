# US-02: Respond Only to Research Team

**Status:** Implemented  
**Version:** 1.0  
**Last Updated:** 2026-07-03  
**Effort:** 2-3 days  
**Priority:** HIGH (blocks other features)

---

## Overview

### What It Does
Validates user role and restricts chatbot responses to only research team members, ignoring admin, bot, and contributor requests.

### Goal
Ensure the chatbot only engages with researchers and team members, preventing system abuse and maintaining appropriate access control.

### Importance
- Prevents unauthorized access to the chatbot
- Protects against system abuse by admins/bots
- Maintains confidentiality of research data
- Ensures only intended users can access the service

---

## Validation Rules

The following checks are performed in order:

### 1. Check User Role is Present and Valid
- Validates that user_role field exists in request
- Rejects empty, null, or whitespace-only roles
- **Error if fails:** `USER_ROLE_NOT_FOUND`

### 2. Check User Role is Eligible
- Validates role is in the ELIGIBLE_ROLES list
- Checks against: researcher, team_member, data_request_creator, research_team_admin
- **Error if fails:** `INELIGIBLE_ROLE`

### 3. Check User is Not a Bot/System
- Detects automated systems (bot, system, automated, notification, irp)
- Prevents system bots from consuming chatbot resources
- **Error if fails:** `BOT_DETECTED`

---

## Roles

### ✅ ELIGIBLE ROLES (Allow Access)

| Role | Description |
|------|-------------|
| `researcher` | Primary research user who submits data requests |
| `team_member` | Member of research team assisting with requests |
| `data_request_creator` | User who created an active data request |
| `research_team_admin` | Administrator of research team |

### ❌ INELIGIBLE ROLES (Deny Access)

| Role | Description | Category |
|------|-------------|----------|
| `vivli_admin` | Vivli platform administrator | Admin |
| `system_admin` | System/infrastructure administrator | Admin |
| `org_admin` | Organization administrator | Admin |
| `data_contributor` | Entity that contributes data | Data |
| `data_curator` | Data management specialist | Data |
| `contributor` | General contributor role | Data |
| `bot_system` | Automated system bot | System |
| `automated_notification` | Automated notification service | System |
| `irp_system` | Institutional Repository system | System |
| `guest` | Guest or unauthenticated user | Other |

---

## Error Messages

| Error Type | Message | When Triggered |
|-----------|---------|-----------------|
| **INVALID_ROLE** | "I'm sorry, but I can only assist research team members. If you're a researcher, please contact support to verify your account." | Role cannot be determined or is not in system |
| **INELIGIBLE_ROLE** | "I'm sorry, but this service is only available to research team members. Please contact the research team for assistance." | User role is admin, bot, contributor, or other ineligible role |
| **BOT_DETECTED** | "This is an automated system and cannot respond to non-researcher queries." | User is identified as automated bot or system process |
| **USER_ROLE_NOT_FOUND** | "Unable to verify your role. Please contact support for assistance." | User information cannot be retrieved |
| **UNAUTHORIZED_ACCESS** | "Access denied. This service requires research team membership." | User attempts to access with insufficient permissions |

---

## How It Works

### Flow Diagram
```
User Request (with user_role)
    ↓
Step 1: Check role is present?
    ├─ NO  → DENY (USER_ROLE_NOT_FOUND)
    └─ YES → Step 2
         ↓
Step 2: Check role is eligible?
    ├─ NO  → Check if bot
    │       ├─ YES (bot) → DENY (BOT_DETECTED)
    │       └─ NO → DENY (INELIGIBLE_ROLE)
    └─ YES → ALLOW ✓
```

### Example: Valid Request (Researcher)
```
Input: {"query": "How do I submit?", "user_role": "researcher", "user_id": "user_001"}
Step 1: Role present? YES
Step 2: Role eligible (researcher)? YES
Result: ✅ PASS → Continue to intent classification
```

### Example: Invalid Request (Admin)
```
Input: {"query": "How do I submit?", "user_role": "vivli_admin", "user_id": "admin_001"}
Step 1: Role present? YES
Step 2: Role eligible (vivli_admin)? NO
Step 3: Is bot? NO
Result: ❌ FAIL → Return "research team only" message
```

---

## Integration

### Where It's Used
- **Endpoint**: `/chat`
- **Step**: Step 1 (First check - BEFORE input validation)
- **Module**: `implementation/role_validator.py`

### Import
```python
from implementation.role_validator import validate_user_role

is_eligible, error_message = validate_user_role(user_role, user_id)
```

### Response Format (Eligible)
```json
{
  "validation_status": "passed",
  "user_role_valid": true,
  "access_granted": true,
  "continue_processing": true
}
```

### Response Format (Ineligible)
```json
{
  "validation_status": "failed",
  "user_role_valid": false,
  "access_granted": false,
  "error_type": "ineligible_role",
  "error_message": "I'm sorry, but this service is only available to research team members...",
  "continue_processing": false
}
```

---

## Testing

### Quick Test
```bash
cd user_stories/US-02-Respond_Only_to_Research_Team
pytest tests/ -v
```

### Integration Test
```bash
# Start server
python rag-demo/main.py

# In another terminal
python user_stories/US-02-Respond_Only_to_Research_Team/test_queries.py --verbose
```

### Manual Test (Eligible)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-User-Role: researcher" \
  -d '{"query": "How do I submit a data request?"}'
```

**Expected:** validation_status: "passed", normal response

### Manual Test (Ineligible)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-User-Role: vivli_admin" \
  -d '{"query": "How do I submit a data request?"}'
```

**Expected:** validation_status: "failed", "research team only" message

---

## Test Results

| Category | Count | Status |
|----------|-------|--------|
| Eligible Roles Tests | 5 | ✅ Pass |
| Ineligible Admins Tests | 3 | ✅ Pass |
| Ineligible Bots Tests | 3 | ✅ Pass |
| Ineligible Contributors Tests | 3 | ✅ Pass |
| Ineligible Guests Tests | 1 | ✅ Pass |
| Edge Cases Tests | 5 | ✅ Pass |
| **Total** | **20** | **✅ Pass** |

---

## Configuration

### Parameters
```python
ROLE_CHECK_ENABLED = True  # Enable/disable role-based access control
ALLOW_SYSTEM_BOTS = False  # Whether to allow responses to system bots
FALLBACK_TO_ESCALATION = True  # Send ineligible users to support
CACHE_ROLE_DATA = True  # Cache user role data for performance
```

### Customization
To modify validation behavior, edit `implementation/role_validator.py`:

```python
class RoleValidator:
    ELIGIBLE_ROLES = {
        "researcher",
        "team_member",
        # Add new roles here
    }
```

---

## Acceptance Criteria

All items must be completed for "done":

- [x] Role validation logic is implemented and tested
- [x] All eligible roles grant access
- [x] All ineligible roles deny access
- [x] Users with no role are denied access
- [x] Bot/system users are properly detected and denied
- [x] Error messages are user-friendly and don't expose details
- [x] Role data caching works appropriately
- [x] Integration into `/chat` endpoint works correctly
- [x] Role validation runs BEFORE input validation (Step 1)
- [x] Unit tests cover all eligible and ineligible roles
- [x] Integration tests verify role-based access control
- [x] Documentation is complete with role mapping

---

## Files

### Implementation
- `implementation/role_validator.py` - Main validation logic (150+ lines)

### Tests
- `tests/test_role_validator.py` - Unit test suite (50+ test cases)
- `test_queries.json` - Integration test queries (15+ test cases)

### Documentation
- `README.md` - This file
- `ACCEPTANCE_CRITERIA.md` - Definition of done
- `HOW_TO_TEST.md` - Testing procedures
- `QUICK_REFERENCE.md` - Quick lookup

---

## Key Differences from US-05

| Aspect | US-05 | US-02 |
|--------|-------|-------|
| **Focus** | Input validation (WHAT) | Access control (WHO) |
| **Validates** | Message content | User role/identity |
| **Checks** | Format, length, spam, language | Role, permissions, eligibility |
| **Step** | 2 (after role check) | 1 (first check) |

---

## Known Limitations

- Requires user_role field in request (must be populated by authentication system)
- Does not validate user identity (assumes authentication is already done)
- Caching may cause delays if role changes mid-session (1 hour default TTL)
- Bot detection based on role name patterns (may need refinement)

---

## Future Enhancements

- [ ] Add role inheritance/hierarchy support
- [ ] Implement dynamic role loading from database
- [ ] Add role expiration/time-based access
- [ ] Enhance bot detection with ML-based analysis
- [ ] Add fine-grained permission scopes per role
- [ ] Implement role audit logging and analytics

---

## Dependencies

- Python 3.8+
- pytest (for testing)
- No external dependencies for core functionality

---

## Contact

**Owner**: Development Team  
**Status**: ✅ COMPLETE & TESTED  
**Ready for Integration**: YES

---

## References

- [TEMPLATE_SETUP_GUIDE.md](../TEMPLATE_SETUP_GUIDE.md) - How to create user stories
- [US-05](../US-05-Graceful_Edge_Case_Handling/) - Reference implementation
- [HOW_TO_TEST.md](../HOW_TO_TEST.md) - Master testing guide
