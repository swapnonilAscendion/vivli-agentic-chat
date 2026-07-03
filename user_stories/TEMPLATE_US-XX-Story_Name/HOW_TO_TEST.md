# How to Test {{US_ID}}: {{US_NAME}}

## Folder Structure

```
{{US_ID}}-{{US_NAME}}/
├── README.md                           # Full documentation
├── ACCEPTANCE_CRITERIA.md              # Definition of done
├── HOW_TO_TEST.md                      # This file
├── implementation/
│   └── validator.py                    # Main validation logic
├── tests/
│   └── test_validator.py               # Unit test suite
└── test_queries.json                   # Integration test queries
```

---

## Quick Start

### Option 1: Run Unit Tests (Fastest)

```bash
cd user_stories/{{US_ID}}-{{US_NAME}}
pytest tests/ -v
```

**Expected Result:**
```
test_validator.py::TestValidator::test_valid_input_1 PASSED
test_validator.py::TestValidator::test_valid_input_2 PASSED
test_validator.py::TestValidator::test_invalid_type_1 PASSED
... (more tests)
===================== XX passed in X.XXs =====================
```

### Option 2: Run Integration Tests

```bash
# Start the server
cd rag-demo
python main.py

# In another terminal, run integration tests
python user_stories/{{US_ID}}-{{US_NAME}}/test_queries.py --verbose

# Or use bash script
bash user_stories/{{US_ID}}-{{US_NAME}}/test_queries.sh all http://localhost:8000
```

### Option 3: Manual Testing with cURL

```bash
# Test valid query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "{{VALID_QUERY_1}}"}'

# Expected: validation_status: "passed"
```

---

## Unit Tests

### What They Test
- `test_valid_input_*`: Valid queries pass validation
- `test_invalid_type_1_*`: {{VALIDATION_RULE_1}} violations are caught
- `test_invalid_type_2_*`: {{VALIDATION_RULE_2}} violations are caught
- `test_invalid_type_3_*`: {{VALIDATION_RULE_3}} violations are caught
- `test_edge_cases_*`: Edge cases are handled correctly

### Run All Tests
```bash
cd user_stories/{{US_ID}}-{{US_NAME}}
pytest tests/test_validator.py -v
```

### Run Specific Test Category
```bash
pytest tests/test_validator.py::TestValidator -k "valid" -v
pytest tests/test_validator.py::TestValidator -k "invalid_type_1" -v
pytest tests/test_validator.py::TestValidator -k "edge_case" -v
```

### Run Single Test
```bash
pytest tests/test_validator.py::TestValidator::test_valid_input_1 -v
```

### With Coverage Report
```bash
pytest tests/ --cov=implementation --cov-report=html --cov-report=term
# Open htmlcov/index.html in browser for detailed report
```

---

## Integration Tests (Full Chatbot)

### Step 1: Start the Server

```bash
cd rag-demo
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 2: Run Test Suite

In another terminal:

```bash
# Python test runner (recommended)
python user_stories/{{US_ID}}-{{US_NAME}}/test_queries.py --verbose

# Or bash script
bash user_stories/{{US_ID}}-{{US_NAME}}/test_queries.sh all http://localhost:8000
```

### Step 3: Check Results

Success output:
```
✓ PASS [valid_001] {{VALID_DESC_1}}
✓ PASS [valid_002] {{VALID_DESC_2}}
✗ FAIL [invalid_001] {{INVALID_DESC_1}} (expected: failed, got: passed)
...
Total Tests: 15
Passed: 14
Failed: 1
Success Rate: 93.3%
```

---

## Test Scenarios & Expected Results

| Scenario | Input | Expected Status | Message |
|----------|-------|-----------------|---------|
| **Valid 1** | {{VALID_QUERY_1}} | ✅ Passed | Process normally |
| **Valid 2** | {{VALID_QUERY_2}} | ✅ Passed | Process normally |
| **Invalid Type 1** | {{INVALID_QUERY_1}} | ❌ Failed | {{ERROR_TYPE_1_MESSAGE}} |
| **Invalid Type 2** | {{INVALID_QUERY_4}} | ❌ Failed | {{ERROR_TYPE_2_MESSAGE}} |
| **Invalid Type 3** | {{INVALID_QUERY_6}} | ❌ Failed | {{ERROR_TYPE_3_MESSAGE}} |
| **Edge Case 1** | {{EDGE_QUERY_1}} | ✅ Passed | Depends on input |

---

## Understanding Test Results

### Test Passed ✅
```
✓ PASS [test_id] Description
```
- Validator behaved as expected
- No issues

### Test Failed ❌
```
✗ FAIL [test_id] Description
  Expected: passed, got: failed
  Query: "..."
```
- Validator returned unexpected result
- Investigate and fix

### Example Failure Investigation
```
Expected: "hi" should PASS (valid single-word greeting)
Got: "hi" returned FAIL (too short)

Fix: Check MIN_MESSAGE_LENGTH setting in validator.py
```

---

## Test Data

### Valid Query Examples
```
{{VALID_QUERY_1}}     → ✅ {{VALID_DESC_1}}
{{VALID_QUERY_2}}     → ✅ {{VALID_DESC_2}}
{{VALID_QUERY_3}}     → ✅ {{VALID_DESC_3}}
```

### Invalid Query Examples
```
{{INVALID_QUERY_1}}   → ❌ {{INVALID_DESC_1}}
{{INVALID_QUERY_4}}   → ❌ {{INVALID_DESC_4}}
{{INVALID_QUERY_6}}   → ❌ {{INVALID_DESC_6}}
```

---

## Manual Testing Examples

### Test Valid Query
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "{{VALID_QUERY_1}}"}'
```

**Expected Response:**
```json
{
  "query_id": "...",
  "answer": "...",
  "intent": "FAQ",
  "confidence_score": 0.XX,
  "metadata": {
    "validation_status": "passed"
  }
}
```

### Test Invalid Query (Type 1)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "{{INVALID_QUERY_1}}"}'
```

**Expected Response:**
```json
{
  "query_id": "...",
  "answer": "{{ERROR_TYPE_1_MESSAGE}}",
  "intent": "UNKNOWN",
  "confidence_score": 0.0,
  "metadata": {
    "validation_status": "failed",
    "error": "{{ERROR_TYPE_1_MESSAGE}}"
  }
}
```

---

## Troubleshooting

### Tests Fail with "Cannot Connect"
**Problem:** Connection error to localhost:8000  
**Solution:**
- Make sure server is running: `python main.py` in `rag-demo/`
- Check port 8000 is available
- Verify server URL is correct

### Unexpected Test Failures
**Problem:** Test expected to pass but failed  
**Solution:**
- Check error message in response
- Review validation logic in `implementation/validator.py`
- Run with verbose flag to see details
- Add debug prints to validator.py

### Slow Test Execution
**Problem:** Tests take too long  
**Solution:**
- Run single test category instead of all
- Increase timeout if network is slow
- Run unit tests instead of integration tests

### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'input_validator'`  
**Solution:**
- Make sure you're in correct directory
- Check `__init__.py` files exist
- Add parent directory to PYTHONPATH

---

## Continuous Testing

### Before Committing
```bash
# Run unit tests
pytest tests/ -v

# Run integration tests
python test_queries.py

# Check code quality
pylint implementation/validator.py
```

### In CI/CD Pipeline
```bash
# Should pass with exit code 0
pytest tests/ --cov=implementation --cov-report=term
python test_queries.py --save results.json
```

---

## Performance Testing

### Check Validation Speed
```bash
# Single query validation should complete in <100ms
time python -c "from implementation.validator import validate_input; validate_input('test')"
```

### Stress Testing
```bash
# Test with 1000 queries
for i in {1..1000}; do
  curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"test query $i\"}" > /dev/null
done
```

---

## Configuration for Testing

### Test Parameters
Edit `implementation/validator.py`:
```python
class {{VALIDATOR_CLASS_NAME}}:
    {{PARAMETER_1}} = value  # Adjust for testing
    {{PARAMETER_2}} = value  # Adjust for testing
```

### Logging
Enable debug logging:
```bash
LOGLEVEL=DEBUG python main.py
```

---

## Next Steps

1. ✅ **Review Code**: Look at `implementation/validator.py`
2. ✅ **Run Unit Tests**: Execute `pytest tests/ -v`
3. ✅ **Test with Chatbot**: Start server and call `/chat` endpoint
4. ✅ **Verify Results**: All tests should pass
5. ⏳ **Next Story**: See [User Stories README](../README.md)

---

## Status

- ✅ **Implementation**: [Status]
- ✅ **Tests**: [X/Y passing]
- ✅ **Integration**: [Status]
- ✅ **Documentation**: [Status]

**Ready to use!**
