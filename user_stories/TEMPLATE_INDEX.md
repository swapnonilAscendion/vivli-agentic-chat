# User Story Template System - Complete Guide

## What Is This?

A **standardized template system** for creating validators and tests for user stories in the Vivli chatbot. Each new user story gets the same structure, making development consistent and fast.

---

## What's Included

### 1. **TEMPLATE_USER_STORY.md** ← START HERE
Overview and quick reference for the entire template system.
- What's included
- Variables reference table
- How to use the template
- File descriptions

### 2. **TEMPLATE_SETUP_GUIDE.md** ← DETAILED WALKTHROUGH
Step-by-step guide to create new user stories.
- 10-step process
- Real example (US-06 Data Request Validation)
- Common mistakes & solutions
- Checklist

### 3. **TEMPLATE_US-XX-Story_Name/** ← COPY THIS
Actual template directory with all necessary files:

```
TEMPLATE_US-XX-Story_Name/
├── README.md                    # Full documentation
├── ACCEPTANCE_CRITERIA.md       # Definition of done
├── HOW_TO_TEST.md              # Testing procedures
├── QUICK_REFERENCE.md          # Quick lookup
├── implementation/
│   └── validator.py            # Validation logic template
├── tests/
│   └── test_validator.py        # Unit test template
└── test_queries.json            # Integration test template
```

### 4. **Existing Example: US-05-Graceful_Edge_Case_Handling**
Reference implementation you can copy from:
- Fully implemented validator
- Complete unit tests (38 tests)
- Integration test queries (75 queries)
- All documentation

---

## Quick Start (2 Minutes)

### To Create a New User Story:

```bash
# 1. Create directory
mkdir user_stories/US-06-Your_Story_Name
cd user_stories/US-06-Your_Story_Name

# 2. Copy template
cp ../TEMPLATE_US-XX-Story_Name/* .
cp -r ../TEMPLATE_US-XX-Story_Name/{implementation,tests} .

# 3. Replace variables (find & replace {{US_ID}}, {{US_NAME}}, etc.)
# Use your editor's find & replace or sed

# 4. Implement validator logic
# Edit implementation/validator.py

# 5. Add tests
# Edit tests/test_validator.py and test_queries.json

# 6. Run tests
pytest tests/ -v
python test_queries.py
```

---

## Template Variables

All template files use **{{VARIABLE}}** syntax for placeholders.

| Variable | Purpose | Example |
|----------|---------|---------|
| `{{US_ID}}` | User story identifier | US-06 |
| `{{US_NAME}}` | Story name (PascalCase) | Data_Request_Validation |
| `{{DESCRIPTION}}` | What it does | "Validates data requests..." |
| `{{GOAL}}` | The goal/purpose | "Ensure valid requests only" |
| `{{VALIDATION_RULE_1}}` | First check | "Check has required fields" |
| `{{VALIDATION_RULE_2}}` | Second check | "Check format is valid" |
| `{{VALIDATION_RULE_3}}` | Third check | "Check size limit" |
| `{{ERROR_TYPE_1}}` | Error enum | missing_fields |
| `{{ERROR_TYPE_1_MESSAGE}}` | User message | "Please provide all fields" |
| `{{PARAMETER_1}}` | Config parameter | MAX_FIELDS |
| `{{VALUE_1}}` | Parameter value | 10 |
| `{{VALID_QUERY_1}}` | Valid test case | "I need data from study X" |
| `{{INVALID_QUERY_1}}` | Invalid test case | "I need data" |

**Full list** in [TEMPLATE_USER_STORY.md](TEMPLATE_USER_STORY.md)

---

## File Structure

### README.md
Main documentation file covering:
- What the story does
- Goal & importance
- Validation rules explained
- Error messages
- Integration details
- Testing instructions
- Known limitations

### ACCEPTANCE_CRITERIA.md
Definition of "done" including:
- Functional requirements
- Test requirements
- Documentation requirements
- Quality requirements
- Sign-off requirements
- Checklist for completion

### HOW_TO_TEST.md
Complete testing guide with:
- Unit test instructions
- Integration test procedures
- Manual testing examples
- Expected results
- Troubleshooting tips
- Performance testing
- CI/CD integration

### QUICK_REFERENCE.md
One-page lookup containing:
- Validation rules summary
- Error messages table
- Quick test commands
- Configuration reference
- Key files list
- Common issues & fixes

### implementation/validator.py
Python module with:
- ValidationError enum
- Validator class with checks
- Error message mapping
- Main entry point function
- Example usage

### tests/test_validator.py
Unit test suite with:
- Test classes organized by rule
- Valid input tests
- Invalid input tests
- Edge case tests
- Pytest fixtures
- Coverage setup

### test_queries.json
Integration test data with:
- Valid query examples
- Invalid query examples
- Edge case queries
- cURL command examples
- Expected responses
- Test statistics

---

## Example: Creating US-06

### Step 1: Gather Information
```
US_ID = "US-06"
US_NAME = "Data_Request_Validation"
DESCRIPTION = "Validates data requests have required fields and valid format"
GOAL = "Ensure only properly formatted data requests proceed"

Rules:
1. Check request has study ID
2. Check request format is valid
3. Check request size limit

Errors:
1. "missing_study_id" → "Please specify which study"
2. "invalid_format" → "Request format is invalid"
3. "size_limit_exceeded" → "Request is too large"
```

### Step 2: Create & Copy
```bash
mkdir -p user_stories/US-06-Data_Request_Validation
cp -r TEMPLATE_US-XX-Story_Name/* user_stories/US-06-Data_Request_Validation/
```

### Step 3: Replace Variables
```bash
find user_stories/US-06-Data_Request_Validation -type f \
  -exec sed -i 's/{{US_ID}}/US-06/g' {} \;
# ... repeat for all variables
```

### Step 4: Implement
Edit `implementation/validator.py`:
```python
def _check_rule_1(self, text: str) -> bool:
    """Check request has study ID"""
    return bool(re.search(r'study\s+\w+', text))
```

### Step 5: Test
```bash
pytest user_stories/US-06-Data_Request_Validation/tests/ -v
python user_stories/US-06-Data_Request_Validation/test_queries.py
```

---

## What Each File Does

| File | Audience | Purpose | When Modify |
|------|----------|---------|------------|
| README.md | Everyone | Overview & docs | Explain changes |
| ACCEPTANCE_CRITERIA.md | Developer/QA | Definition of done | Clarify requirements |
| HOW_TO_TEST.md | QA/Developers | Testing guide | Add test instructions |
| QUICK_REFERENCE.md | Everyone | Quick lookup | Keep up to date |
| validator.py | Developers | Logic | Implement features |
| test_validator.py | Developers | Unit tests | Write tests |
| test_queries.json | QA/Developers | Integration tests | Add test cases |

---

## Standard Structure for All User Stories

Every user story MUST have:

```
user_stories/US-XX-Story_Name/
├── README.md                          ✅ Required
├── ACCEPTANCE_CRITERIA.md             ✅ Required
├── HOW_TO_TEST.md                     ✅ Required
├── QUICK_REFERENCE.md                 ✅ Required
├── implementation/
│   └── validator.py                   ✅ Required
├── tests/
│   └── test_validator.py              ✅ Required
│       └── (minimum 20 test cases)
└── test_queries.json                  ✅ Required
    └── (minimum 15 test queries)
```

**Optional additions:**
- `docs/` folder for extra documentation
- `examples/` folder for usage examples
- `CHANGELOG.md` for version history

---

## Testing Strategy

Every user story MUST have:

1. **Unit Tests** (pytest)
   - Test each validation rule
   - Test error cases
   - Test edge cases
   - Target: >80% code coverage

2. **Integration Tests** (cURL + test_queries.json)
   - Test via /chat endpoint
   - Valid and invalid cases
   - Real-world scenarios

3. **Manual Testing**
   - Documented procedures
   - Expected results
   - Troubleshooting guide

---

## Validation Best Practices

From the template and existing US-05:

### ✅ DO:
- Keep validation checks simple and focused
- Check in order of performance (fast first)
- Use clear, user-friendly error messages
- Test edge cases thoroughly
- Document all parameters
- Follow PEP 8 style guide
- Use type hints
- Write docstrings

### ❌ DON'T:
- Make error messages too long
- Expose system details in errors
- Have overlapping checks
- Hard-code values (use constants)
- Forget to test edge cases
- Skip documentation
- Duplicate code across checks

---

## Validation Rules Checklist

For any new validation rule, ask:

- [ ] Is it clear and focused?
- [ ] Can it be tested easily?
- [ ] Does it have a good error message?
- [ ] Is it documented?
- [ ] Are there edge cases?
- [ ] Is it performant (<100ms)?
- [ ] Does it conflict with other rules?
- [ ] Is it consistent with other validators?

---

## Common Variable Sets

### For Input Validation (like US-05)
```
VALIDATION_RULE_1: "Check message is not blank"
VALIDATION_RULE_2: "Check message length is within limits"
VALIDATION_RULE_3: "Check message has no malicious content"

ERROR_TYPE_1: blank_message
ERROR_TYPE_2: message_too_long
ERROR_TYPE_3: malicious_content
```

### For Data Request Handling (like US-06)
```
VALIDATION_RULE_1: "Check request has required fields"
VALIDATION_RULE_2: "Check request format is valid"
VALIDATION_RULE_3: "Check request within limits"

ERROR_TYPE_1: missing_fields
ERROR_TYPE_2: invalid_format
ERROR_TYPE_3: exceeds_limit
```

---

## Integration with Main Endpoint

All validators integrate into `/chat` endpoint:

```python
# In main.py
from input_validator import validate_input

@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    # Step 0: Validate input (YOUR_VALIDATOR)
    is_valid, error_message = validate_input(request.query)
    
    if not is_valid:
        return ChatResponse(
            query_id=query_id,
            answer=error_message,
            intent="UNKNOWN",
            confidence_score=0.0,
            metadata={"validation_status": "failed"}
        )
    
    # Continue with normal processing...
```

---

## Continuous Development

### When Adding New Feature:
1. Update ACCEPTANCE_CRITERIA.md
2. Add test cases to test_validator.py
3. Implement feature in validator.py
4. Add integration test queries to test_queries.json
5. Update README.md
6. Run all tests: `pytest tests/ -v && python test_queries.py`

### When Deploying:
1. All tests passing: `pytest tests/ --cov=implementation`
2. Coverage >80%: `coverage report`
3. Documentation updated and reviewed
4. Code reviewed by peer
5. ACCEPTANCE_CRITERIA checklist complete

---

## Files Overview

```
vivli-chatbot/user_stories/
│
├── TEMPLATE_USER_STORY.md           # ← START HERE for overview
├── TEMPLATE_SETUP_GUIDE.md          # ← Detailed walkthrough
├── TEMPLATE_INDEX.md                # ← This file
│
├── TEMPLATE_US-XX-Story_Name/       # ← COPY THIS for new stories
│   ├── README.md
│   ├── ACCEPTANCE_CRITERIA.md
│   ├── HOW_TO_TEST.md
│   ├── QUICK_REFERENCE.md
│   ├── implementation/validator.py
│   ├── tests/test_validator.py
│   └── test_queries.json
│
├── US-05-Graceful_Edge_Case_Handling/  # ← Reference implementation
│   ├── README.md
│   ├── ACCEPTANCE_CRITERIA.md
│   ├── ...
│
└── US-06-Data_Request_Validation/   # ← Your new story
    └── (same structure as template)
```

---

## Key Takeaways

1. **Use the template** - Don't create from scratch
2. **Replace variables** - All {{VARIABLE}} placeholders
3. **Implement logic** - Write validation in validator.py
4. **Write tests** - Minimum 20 unit tests, 15 integration tests
5. **Document** - Update all README, HOW_TO_TEST, ACCEPTANCE_CRITERIA
6. **Verify** - All tests must pass before submitting
7. **Review** - Get code reviewed before merging

---

## Getting Started Right Now

### To create US-06:
```bash
# 1. Read this file (you're doing it!)
# 2. Read TEMPLATE_SETUP_GUIDE.md (detailed walkthrough)
# 3. Run the setup:
cd vivli-chatbot/user_stories
mkdir US-06-Data_Request_Validation
cp -r TEMPLATE_US-XX-Story_Name/* US-06-Data_Request_Validation/
cd US-06-Data_Request_Validation

# 4. Replace variables (use find & replace in editor)
# {{US_ID}} → US-06
# {{US_NAME}} → Data_Request_Validation
# ... etc

# 5. Implement validator
# 6. Run tests
pytest tests/ -v
# 7. Done!
```

---

## Need Help?

| Question | Answer In |
|----------|-----------|
| "How do I start?" | TEMPLATE_SETUP_GUIDE.md |
| "What goes where?" | This file or TEMPLATE_USER_STORY.md |
| "How do I implement?" | US-05 example folder |
| "How do I test?" | HOW_TO_TEST.md template |
| "What's the format?" | README.md template |

---

## Version

**Template Version**: 1.0  
**Last Updated**: 2026-07-03  
**Status**: Ready to use  
**Reference Implementation**: US-05 (Input Validation)

---

## Quick Links

- **START HERE**: [TEMPLATE_USER_STORY.md](TEMPLATE_USER_STORY.md)
- **Detailed Guide**: [TEMPLATE_SETUP_GUIDE.md](TEMPLATE_SETUP_GUIDE.md)
- **Template Files**: [TEMPLATE_US-XX-Story_Name/](TEMPLATE_US-XX-Story_Name/)
- **Reference**: [US-05-Graceful_Edge_Case_Handling/](US-05-Graceful_Edge_Case_Handling/)

---

**Ready to create your first user story?** Go to [TEMPLATE_SETUP_GUIDE.md](TEMPLATE_SETUP_GUIDE.md) → **Step 1: Prepare Your User Story Information**
