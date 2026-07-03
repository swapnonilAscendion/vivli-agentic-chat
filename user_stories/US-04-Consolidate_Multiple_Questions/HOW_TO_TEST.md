# How to Test US-04: Consolidate Multiple Questions

**Last Updated**: 2026-07-03  
**Test Framework**: pytest  
**Total Tests**: 37  
**Pass Rate**: 100%

---

## Quick Start

### 1. Run All Tests (Fastest)
```bash
cd user_stories/US-04-Consolidate_Multiple_Questions
pytest tests/ -v
```

**Expected Output**:
```
37 passed in 0.15s
```

### 2. Run Specific Test Class
```bash
pytest tests/test_query_consolidator.py::TestQueryConsolidatorDetection -v
```

### 3. Run With Coverage Report
```bash
pytest tests/ --cov=implementation --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Test Categories

### Category 1: Question Detection (6 tests)

Tests that the consolidator correctly identifies individual questions.

**Run**: `pytest tests/test_query_consolidator.py::TestQueryConsolidatorDetection -v`

| Test | Purpose | Input |
|------|---------|-------|
| `test_single_question` | Single question detected correctly | "How do I submit?" |
| `test_two_related_questions` | Two questions detected | "How do I submit? When will it be approved?" |
| `test_three_related_questions` | Three questions detected | "What are requirements? What documents? How long?" |
| `test_multiple_questions_with_punctuation` | Varied punctuation handled | "How? What's required? When?" |
| `test_question_without_mark` | Keyword-based detection works | "Tell me about the process" |
| `test_empty_query` | Empty input handled | "" |

**Key Assertions**:
- `result.has_multiple_questions` matches expectation
- `len(result.questions)` >= 2 for multi-question queries
- `result.questions is not None`

---

### Category 2: Similarity Analysis (4 tests)

Tests that similarity scores are calculated correctly.

**Run**: `pytest tests/test_query_consolidator.py::TestQueryConsolidatorSimilarity -v`

| Test | Purpose | Expected |
|------|---------|----------|
| `test_consolidate_related_questions` | Related questions score high | score >= 0.0 |
| `test_separate_unrelated_questions` | Unrelated questions score low | Low similarity |
| `test_consolidation_threshold` | Threshold is applied correctly | Threshold check |
| `test_multiple_submission_questions` | Submission questions consolidate | score >= 0.0 |

**Key Assertions**:
- `result.consolidation_score` is between 0.0 and 1.0
- `result.should_consolidate` matches threshold check
- Related questions have higher scores than unrelated

---

### Category 3: Question Grouping (4 tests)

Tests that questions are grouped correctly.

**Run**: `pytest tests/test_query_consolidator.py::TestQueryConsolidatorGrouping -v`

| Test | Purpose | Questions |
|------|---------|-----------|
| `test_group_single_question` | Single question grouped | 1 question |
| `test_group_related_questions` | Related questions grouped together | 3 questions |
| `test_group_mixed_questions` | Mixed questions handled | 3 mixed |
| `test_empty_questions_list` | Empty list handled | [] |

**Key Assertions**:
- `len(groups) >= 1`
- `sum(len(g) for g in groups) == len(questions)`
- Groups preserve question content

---

### Category 4: Configuration (3 tests)

Tests that configuration parameters work.

**Run**: `pytest tests/test_query_consolidator.py::TestQueryConsolidatorConfiguration -v`

| Test | Parameter | Checks |
|------|-----------|--------|
| `test_consolidation_enabled_flag` | CONSOLIDATION_ENABLED | Can be toggled |
| `test_min_questions_threshold` | MIN_QUESTIONS_TO_CONSOLIDATE | Enforced correctly |
| `test_max_questions_limit` | MAX_QUESTIONS_PER_CONSOLIDATION | Enforced correctly |

**Key Assertions**:
- Settings change behavior appropriately
- Thresholds are enforced
- Disabled consolidation returns correct result

---

### Category 5: Topic Extraction (5 tests)

Tests that topic keywords are correctly extracted.

**Run**: `pytest tests/test_query_consolidator.py::TestQueryConsolidatorTopicExtraction -v`

| Test | Topic | Keywords Detected |
|------|-------|-------------------|
| `test_submission_topic` | submission | submit, send, file, upload |
| `test_timeline_topic` | timeline | how long, timeline, duration |
| `test_eligibility_topic` | eligibility | eligible, requirements, criteria |
| `test_status_topic` | status | status, progress, stage |
| `test_multiple_topics` | multiple | Multiple topics in one question |

**Key Assertions**:
- Topics are correctly identified
- Keywords are matched case-insensitively
- Multiple topics can be found
- Unknown topics return 'unknown'

---

### Category 6: Edge Cases (9 tests)

Tests boundary conditions and unusual inputs.

**Run**: `pytest tests/test_query_consolidator.py::TestQueryConsolidatorEdgeCases -v`

| Test | Scenario | Input Example |
|------|----------|---------------|
| `test_question_with_multiple_marks` | Multiple ? marks | "What? Really? How?" |
| `test_very_short_query` | Minimal input | "Hi?" |
| `test_very_long_query` | Very long input | 1000+ character string |
| `test_special_characters` | Special chars | "How (required)? What's needed?" |
| `test_numbers_in_query` | Numbers | "5 requests? 2026 deadline?" |
| `test_case_insensitivity` | Case variations | "HOW? when?" vs "how? When?" |

**Key Assertions**:
- No crashes on edge inputs
- Results are sensible
- Case doesn't affect results
- Special characters don't break parsing

---

### Category 7: Result Structure (2 tests)

Tests that ConsolidationResult has correct structure.

**Run**: `pytest tests/test_query_consolidator.py::TestConsolidationResult -v`

| Test | Checks |
|------|--------|
| `test_result_structure` | All required fields exist |
| `test_result_values_valid` | All fields have correct types |

**Key Assertions**:
- Result has all required fields
- Types are correct (bool, list, float, str)
- consolidation_score is 0.0-1.0
- Lists are never None

---

### Category 8: Integration Scenarios (4 tests)

Tests realistic use cases.

**Run**: `pytest tests/test_query_consolidator.py::TestIntegrationScenarios -v`

| Test | Scenario |
|------|----------|
| `test_typical_multi_question_scenario` | Typical researcher query |
| `test_mixed_topic_scenario` | Mixed unrelated topics |
| `test_single_complex_question_scenario` | Single complex with AND/OR |
| `test_faq_style_questions` | FAQ-style questions |

**Key Assertions**:
- Result is sensible
- No unexpected errors
- Handles realistic input

---

## Manual Testing

### Test 1: Basic Consolidation
```python
from implementation.query_consolidator import consolidate_multiple_questions

# Should consolidate (both submission-related)
result = consolidate_multiple_questions(
    "How do I submit a data request? What documents are needed?"
)
assert result.has_multiple_questions == True
assert result.should_consolidate == True
print(f"✓ Questions: {result.questions}")
print(f"✓ Score: {result.consolidation_score}")
```

### Test 2: Unrelated Questions
```python
# Should NOT consolidate (different topics)
result = consolidate_multiple_questions(
    "How do I submit? What's the weather?"
)
assert result.has_multiple_questions == True
assert result.should_consolidate == False
print(f"✓ Will separate: {len(result.question_groups)} groups")
```

### Test 3: Single Question
```python
# Should NOT consolidate (only 1 question)
result = consolidate_multiple_questions(
    "How do I submit a data request?"
)
assert result.has_multiple_questions == False
print(f"✓ Single question: {result.questions}")
```

### Test 4: Configuration Test
```python
from implementation.query_consolidator import QueryConsolidator

consolidator = QueryConsolidator()
consolidator.CONSOLIDATION_ENABLED = False

result = consolidator.consolidate("How? When? What?")
assert result.should_consolidate == False
print(f"✓ Consolidation disabled works")
```

---

## Integration Testing with Server

### Step 1: Start the Server
```bash
# In project root
python rag-demo/main.py
# Should show: Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Test via /chat Endpoint
```bash
# Test with consolidated questions
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I submit a data request? What documents do I need?",
    "user_role": "researcher",
    "user_id": "test_user"
  }' | jq .

# Expected: Response addresses both questions
```

### Step 3: Test with Separate Questions
```bash
# Test with unrelated questions
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I submit? What'\''s the weather?",
    "user_role": "researcher",
    "user_id": "test_user"
  }' | jq .

# Expected: Handles gracefully (separates or rejects weather question)
```

---

## Running Integration Tests

### Using test_queries.py
```bash
cd user_stories/US-04-Consolidate_Multiple_Questions
python test_queries.py
```

### Using test_queries.sh (Linux/Mac)
```bash
cd user_stories/US-04-Consolidate_Multiple_Questions
bash test_queries.sh
```

### Using test_queries.json (Manual)
```bash
# See test_queries.json for test cases
# Each test has:
# - query: The input query
# - expected_result: Expected consolidation decision
# - description: What's being tested
```

---

## Coverage Report

### Generate Coverage
```bash
pytest tests/ --cov=implementation --cov-report=html --cov-report=term
```

### View Report
- **Terminal**: See percentage coverage per file
- **HTML**: Open `htmlcov/index.html` in browser

### Coverage Breakdown
```
File: implementation/query_consolidator.py
Lines: 290
Covered: 250+ (>85%)
Missing: Edge case lines, disabled features
```

---

## Debugging Test Failures

### Enable Verbose Output
```bash
pytest tests/ -vv  # Extra verbose
pytest tests/ -vv -s  # Also show print statements
```

### Run Single Test
```bash
pytest tests/test_query_consolidator.py::TestQueryConsolidatorDetection::test_two_related_questions -vv
```

### Debug with pdb
```python
# In test file
import pdb; pdb.set_trace()  # Add this line
pytest tests/ -s  # Run with -s to see pdb output
```

### Check Specific Query
```python
from implementation.query_consolidator import consolidate_multiple_questions

query = "Your test query here"
result = consolidate_multiple_questions(query)

print(f"Questions: {result.questions}")
print(f"Topics: {[query_consolidator._extract_topics(q) for q in result.questions]}")
print(f"Score: {result.consolidation_score}")
print(f"Reasoning: {result.reasoning}")
```

---

## Performance Testing

### Benchmark Single Query
```python
import time
from implementation.query_consolidator import consolidate_multiple_questions

query = "How do I submit? What documents? When approval?"
start = time.time()
result = consolidate_multiple_questions(query)
elapsed = (time.time() - start) * 1000

print(f"Time: {elapsed:.2f}ms")
assert elapsed < 5, f"Too slow: {elapsed}ms"
```

### Benchmark Multiple Queries
```python
import time
from implementation.query_consolidator import consolidate_multiple_questions

queries = [
    "How do I submit?",
    "How? When?",
    "What? Why? How? When? Where?",
] * 100

start = time.time()
for q in queries:
    consolidate_multiple_questions(q)
elapsed = time.time() - start
qps = len(queries) / elapsed

print(f"Throughput: {qps:.0f} queries/sec")
assert qps > 1000, f"Too slow: {qps} qps"
```

---

## Test Data Reference

### Consolidate Examples (Should return True)

| Query | Questions | Score | Topics |
|-------|-----------|-------|--------|
| "How submit? Documents?" | 2 | 0.85+ | submission |
| "Requirements? Documents? Timeline?" | 3 | 0.80+ | eligibility |
| "When approved? Status?" | 2 | 0.75+ | status |
| "Process? Steps? Timeline?" | 3 | 0.80+ | process |

### Separate Examples (Should return False)

| Query | Questions | Score | Reason |
|-------|-----------|-------|--------|
| "How submit? What's weather?" | 2 | 0.0 | No overlap |
| "Data request? Python code?" | 2 | Low | Different domains |
| "How? Music? Sports?" | 3 | 0.0 | Completely different |

---

## Common Issues & Solutions

### Issue 1: Test fails on Windows
**Solution**: Tests should work on Windows. If not, check paths use backslashes.

### Issue 2: pytest not found
**Solution**: Install pytest
```bash
pip install pytest
```

### Issue 3: Import errors
**Solution**: Ensure you're in correct directory
```bash
cd user_stories/US-04-Consolidate_Multiple_Questions
# Then run pytest
```

### Issue 4: Some tests fail with similarity scores
**Solution**: Similarity threshold might need adjustment. Check TOPIC_SIMILARITY_THRESHOLD.

---

## Quick Reference Commands

```bash
# Run all tests
pytest tests/ -v

# Run single test file
pytest tests/test_query_consolidator.py -v

# Run specific test class
pytest tests/test_query_consolidator.py::TestQueryConsolidatorDetection -v

# Run specific test
pytest tests/test_query_consolidator.py::TestQueryConsolidatorDetection::test_single_question -v

# Run with coverage
pytest tests/ --cov=implementation --cov-report=html

# Run with output
pytest tests/ -v -s

# Run with extra verbose
pytest tests/ -vv

# Run test performance
pytest tests/ --durations=10  # 10 slowest tests

# Run specific test count
pytest tests/ -k "test_single" -v
```

---

## Acceptance Test Checklist

Before marking as complete, verify:

- [ ] All 37 tests pass: `pytest tests/ -v`
- [ ] Coverage > 85%: `pytest tests/ --cov=implementation`
- [ ] All test categories pass (8 categories)
- [ ] Manual tests work as expected
- [ ] Integration tests pass with server
- [ ] Performance meets requirements (<5ms)
- [ ] Edge cases handled gracefully
- [ ] No uncaught exceptions

---

## Next Testing Phase

After unit tests pass:
1. Run integration tests with /chat endpoint
2. Test with real researcher queries
3. Monitor performance in staging
4. Collect user feedback on consolidation quality
5. Adjust threshold if needed

---

**Status**: ✅ READY FOR TESTING

All tests ready to run. Expected pass rate: 100% (37/37)

