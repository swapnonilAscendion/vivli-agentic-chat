# Test Queries Guide for US-05: Graceful Edge Case Handling

This guide explains how to use the comprehensive test queries to validate the input validation logic implemented in the `/chat` endpoint.

## Overview

**75 test queries** organized into **10 categories** covering:
- ✅ 15 Valid queries (should PASS)
- ❌ 60 Invalid queries (should FAIL for various reasons)

## Quick Start

### Option 1: Python Test Runner (Recommended)

**Run all tests:**
```bash
python test_queries.py
```

**Run specific category:**
```bash
python test_queries.py --category VALID_QUERIES
python test_queries.py --category INVALID_HTML
```

**Verbose output:**
```bash
python test_queries.py --verbose
```

**Save results to file:**
```bash
python test_queries.py --save results.json
```

**With custom server:**
```bash
python test_queries.py --server http://localhost:8000 --verbose
```

### Option 2: Bash Script

**Run all tests:**
```bash
bash test_queries.sh all http://localhost:8000
```

**Run specific category:**
```bash
bash test_queries.sh VALID_QUERIES http://localhost:8000
bash test_queries.sh INVALID_BLANK http://localhost:8000
bash test_queries.sh INVALID_HTML http://localhost:8000
```

### Option 3: Manual Testing with cURL

**Test a single valid query:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I submit a data request?"}'
```

**Test a blank message:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": ""}'
```

**Test HTML injection:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "<script>alert(1)</script>"}'
```

## Test Categories

### 1. VALID_QUERIES (15 tests)
Queries that should **PASS** validation and be processed normally.

**Examples:**
- `"How do I submit a data request?"`
- `"What is the form check process?"`
- `"When will my request be approved?"`
- `"Can I download the data after approval?"`

**Expected Response:**
- `validation_status: "passed"`
- `intent: "FAQ"` or other classification
- `answer: "..."` (response from knowledge base or LLM)

---

### 2. INVALID_BLANK (5 tests)
Empty or whitespace-only messages - should **FAIL**.

**Examples:**
- `""` (empty string)
- `"   "` (spaces only)
- `"\n\n\n"` (newlines only)
- `"\t\t"` (tabs only)

**Expected Response:**
```json
{
  "validation_status": "failed",
  "error": "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.",
  "intent": "UNKNOWN",
  "confidence_score": 0.0
}
```

---

### 3. INVALID_TOO_LONG (2 tests)
Messages with 500+ words - should **FAIL**.

**Examples:**
- Very long repetitive text (500+ words)
- Lorem Ipsum pasted content

**Expected Response:**
```json
{
  "validation_status": "failed",
  "error": "Your message is too long. Please break it into smaller questions.",
  "intent": "UNKNOWN",
  "confidence_score": 0.0
}
```

---

### 4. INVALID_HTML (6 tests)
HTML/code injection attempts - should **FAIL**.

**Examples:**
- `"<script>alert('xss')</script>"`
- `"Check this <button onclick='alert()'>button</button>"`
- `"<!DOCTYPE html><html><body>Hacked</body></html>"`
- `"<img src=x onerror='alert(1)'>"` 
- `"<div onclick='window.location=\"http://evil.com\"'>Click me</div>"`

**Expected Response:**
```json
{
  "validation_status": "failed",
  "error": "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.",
  "intent": "UNKNOWN",
  "confidence_score": 0.0
}
```

---

### 5. INVALID_CODE (6 tests)
Code snippets - should **FAIL**.

**Examples:**
- `"def my_function(): pass"` (Python)
- `"function test() { return true; }"` (JavaScript)
- `` "```python\ndef hello():\n    print('world')\n```" `` (Code fence)
- `"public class Main { public static void main(String[] args) {} }"` (Java)
- `"#include <stdio.h> int main() { return 0; }"` (C)

**Expected Response:**
```json
{
  "validation_status": "failed",
  "error": "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.",
  "intent": "UNKNOWN",
  "confidence_score": 0.0
}
```

---

### 6. INVALID_SPAM (4 tests)
Spam patterns - should **FAIL**.

**Examples:**
- `"Click here http://malicious-site.com and check this https://another-bad-site.com for amazing deals"`
- `"Buy now! Click here for free offer and get discount today!"`
- `"Check out http://example.com and http://test.com and http://demo.com"`

**Expected Response:**
```json
{
  "validation_status": "failed",
  "error": "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.",
  "intent": "UNKNOWN",
  "confidence_score": 0.0
}
```

---

### 7. INVALID_NON_ENGLISH (4 tests)
Non-English languages - should **FAIL**.

**Examples:**
- `"你好，我想提交数据请求"` (Chinese)
- `"こんにちは、データリクエストを提出したいのですが"` (Japanese)
- `"안녕하세요 데이터 요청을 제출하고 싶습니다"` (Korean)
- `"مرحبا كيف يمكنني تقديم طلب بيانات"` (Arabic)

**Expected Response:**
```json
{
  "validation_status": "failed",
  "error": "Please ask your question in English.",
  "intent": "UNKNOWN",
  "confidence_score": 0.0
}
```

---

### 8. INVALID_EMOJIS_ONLY (3 tests)
Emoji-only messages - should **FAIL**.

**Examples:**
- `"😀😁😂"`
- `"🎉🎊🎈"`
- `"👍👌✌"`

**Expected Response:**
```json
{
  "validation_status": "failed",
  "error": "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.",
  "intent": "UNKNOWN",
  "confidence_score": 0.0
}
```

---

### 9. INVALID_SPECIAL_CHARS (2 tests)
Special characters only - should **FAIL**.

**Examples:**
- `"!@#$%^&*()"`
- `"***???!!!"`

**Expected Response:**
```json
{
  "validation_status": "failed",
  "error": "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.",
  "intent": "UNKNOWN",
  "confidence_score": 0.0
}
```

---

### 10. EDGE_CASES (10 tests)
Edge cases that should **PASS** validation.

**Examples:**
- `"What is the cost? (USD)"` - Special characters in parentheses
- `"Can I request REQ-123456 or REQ-789?"` - Request IDs with hyphens
- `"What's the difference between form check and review?"` - Apostrophes
- `"Is it 100% safe? What about 50% cases?"` - Percentage signs
- `"Do you support data formats like CSV, JSON, and XML?"` - Acronyms
- `"What's the maximum file size allowed for uploads?"` - File size questions

**Expected Response:**
```json
{
  "validation_status": "passed",
  "intent": "FAQ" or other classification
  "answer": "..."
}
```

---

## Understanding the Response

When a query is submitted to the `/chat` endpoint, the response includes:

```json
{
  "query_id": "uuid",
  "answer": "Response text",
  "intent": "FAQ|DATA_REQUEST_RELATED|HYBRID|ESCALATION|UNKNOWN",
  "confidence_score": 0.0-1.0,
  "sources": [...],
  "latency_ms": 123,
  "metadata": {
    "validation_status": "passed|failed",
    "error": "error message if validation failed"
  }
}
```

### Key Fields:
- **validation_status**: `"passed"` or `"failed"` - indicates if input validation passed
- **error**: Error message (only present if validation failed)
- **intent**: Query intent classification
- **answer**: The response text

### Validation Status Mapping:
- ✅ **passed**: Input is valid, proceed with normal processing
- ❌ **failed**: Input validation failed, return error message to user

---

## Running Tests During Development

### Before making changes:
```bash
python test_queries.py --save baseline.json
```

### After making changes:
```bash
python test_queries.py --save updated.json
```

### Compare results:
```bash
# Check if pass rate improved
diff baseline.json updated.json
```

---

## Troubleshooting

### Tests fail with "Cannot connect to server"
- Make sure the chatbot server is running: `python main.py` in `rag-demo/` directory
- Verify the server URL is correct
- Check if the server is listening on the specified port

### Some tests fail unexpectedly
- Review the error message in the response
- Check if the validation logic in `input_validator.py` has been modified
- Run verbose mode to see actual vs expected responses: `python test_queries.py --verbose`

### Slow test execution
- Run a specific category instead of all tests
- Increase the timeout in the test script if needed

---

## Adding New Test Cases

To add new test cases:

1. Open `test_queries.json`
2. Find the appropriate category or create a new one
3. Add a test object with these fields:
   - `id`: Unique test identifier (e.g., "valid_016")
   - `query`: The test query string
   - `expected_status`: `"passed"` or `"failed"`
   - `expected_error`: Error type (if failed)
   - `description`: Human-readable description

Example:
```json
{
  "id": "valid_016",
  "query": "How do I update my research interests?",
  "expected_status": "passed",
  "description": "Update profile question"
}
```

---

## Test Statistics

- **Total Queries**: 75
- **Valid (Pass)**: 20 (includes single-word greetings)
- **Invalid (Fail)**: 55
- **Categories**: 10
- **Coverage**: All validation rules from `input_validator.py`

## Recent Changes

**v1.1 Update (2026-07-03):**
- Changed `MIN_MESSAGE_LENGTH` from 2 to 1 to allow single-word queries like "hi", "hello", "help"
- Removed `INVALID_TOO_SHORT` test category
- Added 5 new valid test cases for single-word greetings to `VALID_QUERIES`
- Updated all test counts and category numbering

---

## Integration with CI/CD

To integrate with CI/CD pipeline:

```bash
# Run tests and fail if any test fails
python test_queries.py --save ci_results.json
if [ $? -ne 0 ]; then exit 1; fi
```

Or use the bash script in a GitHub Actions workflow:
```yaml
- name: Run validation tests
  run: bash test_queries.sh all http://localhost:8000
```

---

## See Also

- [HOW_TO_TEST.md](HOW_TO_TEST.md) - Overall testing guide
- [input_validator.py](implementation/input_validator.py) - Validation logic
- [test_input_validator.py](tests/test_input_validator.py) - Unit tests
- [main.py](../../rag-demo/main.py) - Chat endpoint implementation
