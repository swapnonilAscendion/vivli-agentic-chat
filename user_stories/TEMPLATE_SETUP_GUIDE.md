# User Story Template Setup Guide

## Overview

This guide explains how to use the standardized templates to create new user stories for the Vivli chatbot.

**Templates include:**
- README.md (documentation)
- ACCEPTANCE_CRITERIA.md (definition of done)
- implementation/validator.py (validation logic)
- tests/test_validator.py (unit tests)
- test_queries.json (integration tests)
- HOW_TO_TEST.md (testing guide)
- QUICK_REFERENCE.md (quick lookup)

---

## Step-by-Step Setup

### Step 1: Prepare Your User Story Information

Before creating the story, gather:

```
US_ID:              US-06, US-07, etc. (2-digit number)
US_NAME:            PascalCase_With_Underscores (e.g., Data_Request_Handler)
DESCRIPTION:        1-2 sentences describing what it does
GOAL:               The goal/purpose (e.g., "Prevent invalid data requests")

VALIDATION_RULE_1:  First check (e.g., "Check message is not blank")
VALIDATION_RULE_2:  Second check (e.g., "Check message is English")
VALIDATION_RULE_3:  Third check (e.g., "Check message has no code")

ERROR_TYPE_1:       blank_message, non_english, code_detected, etc.
ERROR_TYPE_1_MSG:   "User-friendly error message for check 1"
ERROR_TYPE_2:       (similar to above)
ERROR_TYPE_2_MSG:   
ERROR_TYPE_3:       
ERROR_TYPE_3_MSG:   

ACCEPTANCE_CRITERIA_1:  "Validation logic is implemented"
ACCEPTANCE_CRITERIA_2:  "All tests pass"
(... more criteria)
```

### Step 2: Create Directory Structure

```bash
# Create the user story directory
mkdir -p user_stories/{{US_ID}}-{{US_NAME}}/implementation
mkdir -p user_stories/{{US_ID}}-{{US_NAME}}/tests
mkdir -p user_stories/{{US_ID}}-{{US_NAME}}/docs

# Navigate there
cd user_stories/{{US_ID}}-{{US_NAME}}
```

### Step 3: Copy Template Files

Copy the template files to your new user story:

```bash
# Copy from template
cp ../TEMPLATE_US-XX-Story_Name/README.md .
cp ../TEMPLATE_US-XX-Story_Name/ACCEPTANCE_CRITERIA.md .
cp ../TEMPLATE_US-XX-Story_Name/HOW_TO_TEST.md .
cp ../TEMPLATE_US-XX-Story_Name/QUICK_REFERENCE.md ./docs/
cp ../TEMPLATE_US-XX-Story_Name/implementation/validator.py ./implementation/
cp ../TEMPLATE_US-XX-Story_Name/tests/test_validator.py ./tests/
cp ../TEMPLATE_US-XX-Story_Name/test_queries.json .
```

### Step 4: Search and Replace Variables

Replace all template variables in every file. Use your editor's find-and-replace:

#### Variables to Replace (in all files)

```
{{US_ID}}                    → US-06
{{US_NAME}}                  → Data_Request_Handler
{{DESCRIPTION}}              → "Validates data requests are properly formatted..."
{{GOAL}}                     → "Ensure only valid data requests are processed"
{{VALIDATION_RULE_1}}        → "Check request has required fields"
{{VALIDATION_RULE_2}}        → "Check request format is valid"
{{VALIDATION_RULE_3}}        → "Check request doesn't exceed limits"
{{ERROR_TYPE_1}}             → missing_fields
{{ERROR_TYPE_1_MESSAGE}}     → "Please provide all required fields..."
{{ERROR_TYPE_2}}             → invalid_format
{{ERROR_TYPE_2_MESSAGE}}     → "Request format is invalid..."
{{ERROR_TYPE_3}}             → limit_exceeded
{{ERROR_TYPE_3_MESSAGE}}     → "Request exceeds maximum size..."
{{PARAMETER_1}}              → MAX_FIELDS
{{VALUE_1}}                  → 10
{{PARAMETER_2}}              → MIN_FIELDS
{{VALUE_2}}                  → 3
```

#### Quick Replace Commands (Bash)

```bash
# Replace all instances in all files
find . -type f \( -name "*.md" -o -name "*.py" -o -name "*.json" \) -exec sed -i \
  -e "s/{{US_ID}}/US-06/g" \
  -e "s/{{US_NAME}}/Data_Request_Handler/g" \
  -e "s/{{DESCRIPTION}}/Your description here/g" \
  {} \;
```

#### Or Do It Manually

1. Open README.md
2. Use Find & Replace (Ctrl+H in VS Code)
3. Replace {{US_ID}} with your US ID
4. Repeat for each variable
5. Do the same for all other files

### Step 5: Customize Implementation

Edit `implementation/validator.py`:

```python
class DataRequestValidator:  # Rename from {{VALIDATOR_CLASS_NAME}}
    """Validate data requests are properly formatted"""
    
    # Update parameters
    MAX_FIELDS = 10
    MIN_FIELDS = 3
    
    # Update validation rules
    def _check_rule_1(self, text: str) -> bool:
        """Check request has required fields"""
        # Your implementation here
        pass
    
    def _check_rule_2(self, text: str) -> bool:
        """Check request format is valid"""
        # Your implementation here
        pass
    
    def _check_rule_3(self, text: str) -> bool:
        """Check request doesn't exceed limits"""
        # Your implementation here
        pass
```

### Step 6: Create Unit Tests

Edit `tests/test_validator.py`:

```python
import pytest
from implementation.validator import validate_input

class TestDataRequestValidator:
    """Test suite for US-06: Data Request Handler"""
    
    def test_valid_request_1(self):
        """Test valid data request with all fields"""
        is_valid, error = validate_input("valid request data")
        assert is_valid is True
        assert error == ""
    
    def test_invalid_missing_fields(self):
        """Test request missing required fields"""
        is_valid, error = validate_input("incomplete")
        assert is_valid is False
        assert "required" in error.lower()
    
    # Add more test cases...
```

### Step 7: Create Test Queries

Edit `test_queries.json`:

```json
{
  "description": "Test queries for US-06: Data Request Handler",
  "categories": {
    "VALID_QUERIES": {
      "tests": [
        {
          "id": "valid_001",
          "query": "I want data from study ABC-123",
          "expected_status": "passed",
          "description": "Valid data request with study ID"
        }
      ]
    },
    "INVALID_MISSING_FIELDS": {
      "tests": [
        {
          "id": "invalid_001",
          "query": "I want data",
          "expected_status": "failed",
          "expected_error": "missing_fields",
          "description": "Missing study ID"
        }
      ]
    }
  }
}
```

### Step 8: Document Testing

Edit `HOW_TO_TEST.md` with actual test examples:

```markdown
## Manual Testing Examples

### Test Valid Request
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "I want data from study ABC-123"}'
```

### Test Invalid Request (Missing Fields)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "I want data"}'
```
```

### Step 9: Run Tests

```bash
# Unit tests
pytest tests/ -v

# Integration tests
python test_queries.py --verbose

# Coverage
pytest tests/ --cov=implementation --cov-report=html
```

### Step 10: Review Documentation

- [ ] README.md is complete and accurate
- [ ] ACCEPTANCE_CRITERIA.md is comprehensive
- [ ] HOW_TO_TEST.md has clear instructions
- [ ] QUICK_REFERENCE.md is concise
- [ ] All examples are correct
- [ ] All variables are replaced

---

## Real Example: Creating US-06 Data Request Validation

### Information Gathered

```
US_ID:           US-06
US_NAME:         Data_Request_Validation
DESCRIPTION:     Validates data requests have all required fields and valid format
GOAL:            Ensure only properly formatted data requests are processed

VALIDATION_RULE_1:  Check request has study ID
VALIDATION_RULE_2:  Check request has valid format
VALIDATION_RULE_3:  Check request doesn't exceed size limits

ERROR_TYPE_1:    missing_study_id
ERROR_TYPE_1_MSG: "Please specify which study data you need"
ERROR_TYPE_2:    invalid_format
ERROR_TYPE_2_MSG: "Data request format is invalid"
ERROR_TYPE_3:    request_too_large
ERROR_TYPE_3_MSG: "Your request is too large. Please be more specific"

VALID_QUERY_1:   "I need data from study ABC-123"
VALID_QUERY_2:   "Can I get data for the diabetes study?"
INVALID_QUERY_1: "I need data"
INVALID_QUERY_2: "Show me every study's data"
```

### Create Directory

```bash
mkdir -p user_stories/US-06-Data_Request_Validation/{implementation,tests}
cd user_stories/US-06-Data_Request_Validation
```

### Copy and Customize

```bash
# Copy files
cp ../TEMPLATE_US-XX-Story_Name/* .
cp ../TEMPLATE_US-XX-Story_Name/implementation/* ./implementation/
cp ../TEMPLATE_US-XX-Story_Name/tests/* ./tests/

# Replace variables
sed -i 's/{{US_ID}}/US-06/g' README.md ACCEPTANCE_CRITERIA.md HOW_TO_TEST.md
sed -i 's/{{US_NAME}}/Data_Request_Validation/g' README.md ACCEPTANCE_CRITERIA.md
# ... (continue for all variables)
```

### Implement Validator

Edit `implementation/validator.py`:

```python
def _check_rule_1(self, text: str) -> bool:
    """Check request has study ID"""
    # Look for patterns like "study ABC-123" or "diabetes study"
    return bool(re.search(r'study\s+\w+', text, re.IGNORECASE))

def _check_rule_2(self, text: str) -> bool:
    """Check request has valid format"""
    # Check for keywords like "data", "need", "get"
    return bool(re.search(r'\b(data|need|get|request)\b', text, re.IGNORECASE))

def _check_rule_3(self, text: str) -> bool:
    """Check request doesn't exceed size limits"""
    return len(text) <= 500
```

### Create Tests

```python
def test_valid_with_study_id(self):
    is_valid, _ = validate_input("I need data from study ABC-123")
    assert is_valid is True

def test_invalid_missing_study(self):
    is_valid, error = validate_input("I need data")
    assert is_valid is False
    assert "study" in error.lower()
```

### Run Tests

```bash
pytest tests/ -v
# Expected: 15 tests pass
```

---

## Checklist for Creating New User Story

- [ ] User story ID and name decided
- [ ] Description and goal written
- [ ] Validation rules defined (3+)
- [ ] Error messages written (user-friendly)
- [ ] Acceptance criteria listed
- [ ] Directory structure created
- [ ] Template files copied
- [ ] All variables replaced
- [ ] Validator logic implemented
- [ ] Unit tests written
- [ ] Integration test queries added
- [ ] Testing documentation updated
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation reviewed

---

## Common Mistakes to Avoid

| Mistake | Solution |
|---------|----------|
| Incomplete variable replacement | Search for {{ in all files |
| Validator returns wrong tuple | Must return (bool, ValidationError) |
| Tests don't import correctly | Check __init__.py files exist |
| Error messages too long | Keep under 140 characters |
| No edge cases tested | Add at least 5-10 edge cases |
| Documentation out of sync | Update docs when code changes |

---

## File Locations Quick Reference

```
vivli-chatbot/
├── user_stories/
│   ├── TEMPLATE_USER_STORY.md          ← Start here
│   ├── TEMPLATE_US-XX-Story_Name/      ← Copy this
│   │   ├── README.md
│   │   ├── ACCEPTANCE_CRITERIA.md
│   │   ├── HOW_TO_TEST.md
│   │   ├── QUICK_REFERENCE.md
│   │   ├── implementation/
│   │   │   └── validator.py
│   │   ├── tests/
│   │   │   └── test_validator.py
│   │   └── test_queries.json
│   │
│   └── US-06-Data_Request_Validation/  ← Create your story here
│       └── (same structure)
│
├── rag-demo/
│   └── (your server code)
```

---

## Next Steps

1. ✅ Create directory and copy files
2. ✅ Replace all variables
3. ✅ Implement validation logic
4. ✅ Write unit tests
5. ✅ Create integration test queries
6. ✅ Run and verify all tests pass
7. ✅ Update documentation
8. ✅ Code review
9. ✅ Merge to main branch

---

## Need Help?

- **Template Questions**: See TEMPLATE_USER_STORY.md
- **Implementation Questions**: See existing US-05 example
- **Testing Questions**: See HOW_TO_TEST.md
- **Documentation**: See README.md examples

---

**Last Updated**: 2026-07-03  
**Template Version**: 1.0
