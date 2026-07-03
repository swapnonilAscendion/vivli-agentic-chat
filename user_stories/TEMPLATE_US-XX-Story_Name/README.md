# {{US_ID}}: {{US_NAME}}

**Status:** In Development  
**Version:** 1.0  
**Last Updated:** 2026-07-03

---

## Overview

### What It Does
{{DESCRIPTION}}

### Goal
{{GOAL}}

### Importance
- Improves user experience by [benefit]
- Prevents [problem] from occurring
- Ensures [compliance/quality/security]

---

## Validation Rules

The following checks are performed on user input:

{{VALIDATION_RULES}}

### Rule Priority (Order of Execution)
1. **Check 1**: Description
2. **Check 2**: Description
3. **Check 3**: Description

---

## Error Messages

| Error Type | Message | When Triggered |
|-----------|---------|-----------------|
| Error_1 | "{{ERROR_1_MESSAGE}}" | When [condition] |
| Error_2 | "{{ERROR_2_MESSAGE}}" | When [condition] |
| Error_3 | "{{ERROR_3_MESSAGE}}" | When [condition] |

---

## How It Works

### Flow Diagram
```
User Input
    ↓
[Validation Rule 1]
    ↓
[Validation Rule 2]
    ↓
[Validation Rule 3]
    ↓
✅ Valid / ❌ Invalid
```

### Example: Valid Input
```
Query: "..."
Checks:
  ✓ Rule 1 passed
  ✓ Rule 2 passed
  ✓ Rule 3 passed
Result: PASS → Process normally
```

### Example: Invalid Input
```
Query: "..."
Checks:
  ✓ Rule 1 passed
  ✓ Rule 2 passed
  ✗ Rule 3 failed
Result: FAIL → Return error message
```

---

## Integration

### Where It's Used
- **Endpoint**: `/chat`
- **Step**: Before intent classification
- **Module**: `input_validator.py`

### Import
```python
from input_validator import validate_{{variable}}

is_valid, error_message = validate_{{variable}}(user_input)
```

### Response Format (Valid)
```json
{
  "validation_status": "passed",
  "intent": "FAQ",
  "answer": "..."
}
```

### Response Format (Invalid)
```json
{
  "validation_status": "failed",
  "error": "{{ERROR_MESSAGE}}",
  "intent": "UNKNOWN",
  "confidence_score": 0.0
}
```

---

## Testing

### Quick Test
```bash
cd user_stories/{{US_ID}}-{{US_NAME}}
pytest tests/ -v
```

### Integration Test
```bash
# Start server
python main.py

# In another terminal, test with curl
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "valid input here"}'
```

### Full Testing Guide
See [HOW_TO_TEST.md](HOW_TO_TEST.md)

---

## Test Results

| Category | Count | Status |
|----------|-------|--------|
| Valid Queries | XX | ✅ Pass |
| Invalid Queries | XX | ✅ Pass |
| Edge Cases | XX | ✅ Pass |
| **Total** | **XX** | **✅ Pass** |

---

## Files

### Implementation
- `implementation/validator.py` - Main validation logic (XX lines)

### Tests
- `tests/test_validator.py` - Unit tests (XX test cases)
- `test_queries.json` - Integration test queries (XX queries)

### Documentation
- `README.md` - This file
- `ACCEPTANCE_CRITERIA.md` - Definition of done
- `HOW_TO_TEST.md` - Testing procedures
- `QUICK_REFERENCE.md` - Quick lookup

---

## Configuration

### Parameters
```python
PARAMETER_1 = value  # Description
PARAMETER_2 = value  # Description
PARAMETER_3 = value  # Description
```

### Customization
To modify validation behavior, edit `implementation/validator.py`:
```python
class {{VALIDATOR_CLASS}}:
    PARAMETER_1 = new_value
```

---

## Acceptance Criteria

All items must be completed for "done":

- [ ] {{ACCEPTANCE_CRITERIA_1}}
- [ ] {{ACCEPTANCE_CRITERIA_2}}
- [ ] {{ACCEPTANCE_CRITERIA_3}}

See [ACCEPTANCE_CRITERIA.md](ACCEPTANCE_CRITERIA.md) for full details.

---

## Dependencies

- Python 3.8+
- pytest
- [Other dependencies]

---

## Known Limitations

- [Limitation 1]
- [Limitation 2]
- [Future enhancement item]

---

## Future Enhancements

- [ ] Enhancement 1
- [ ] Enhancement 2
- [ ] Enhancement 3

---

## References

- Related User Stories: [Links]
- External Documentation: [Links]
- Issue Tracker: [Links]

---

## Contact

**Owner**: [Team/Person]  
**Questions**: [Slack channel or email]  
**Status**: {{STATUS}}
