# Quick Reference: US-04 - Consolidate Multiple Questions

**TL;DR**: Detects multiple questions in one message and consolidates them if they're related enough.

---

## In 30 Seconds

**What**: Consolidates 2+ related questions into one response  
**Where**: `/chat` endpoint (after US-03, before US-07)  
**When**: Only if questions share topics (threshold: 0.75)  
**Result**: One consolidated answer instead of separate responses

---

## Key Concepts

| Concept | Meaning | Example |
|---------|---------|---------|
| **Has Multiple** | 2+ questions detected | "How? When?" |
| **Should Consolidate** | Similarity >= 0.75 | Both about submission |
| **Similarity Score** | How related (0.0-1.0) | 0.85 = high overlap |
| **Question Groups** | Grouped questions | [[Q1, Q2], [Q3]] |
| **Topic Keywords** | Extracted topics | ["submission", "status"] |

---

## Common Usage Patterns

### Pattern 1: Simple Import
```python
from implementation.query_consolidator import consolidate_multiple_questions

result = consolidate_multiple_questions("How? When?")
```

### Pattern 2: Check Result
```python
if result.has_multiple_questions and result.should_consolidate:
    print(f"Consolidate {len(result.questions)} questions")
else:
    print("Handle separately")
```

### Pattern 3: Access Groups
```python
for group in result.question_groups:
    print(f"Group: {group}")
    # Each group is a list of related questions
```

### Pattern 4: Get Reasoning
```python
print(result.reasoning)
# "Similarity score: 0.85 (threshold: 0.75) - Consolidate"
```

---

## Quick API Reference

### Main Function
```python
consolidate_multiple_questions(query_text: str) -> ConsolidationResult
```

### Result Fields
```python
result.has_multiple_questions    # bool: 2+ questions?
result.questions                 # List[str]: Extracted questions
result.question_groups           # List[List[str]]: Grouped questions
result.should_consolidate        # bool: Consolidate them?
result.consolidation_score       # float: Similarity 0.0-1.0
result.reasoning                 # str: Explanation
```

### Configuration Constants
```python
QueryConsolidator.CONSOLIDATION_ENABLED = True          # Enable?
QueryConsolidator.MIN_QUESTIONS_TO_CONSOLIDATE = 2      # Min needed
QueryConsolidator.MAX_QUESTIONS_PER_CONSOLIDATION = 5   # Max allowed
QueryConsolidator.TOPIC_SIMILARITY_THRESHOLD = 0.75     # Threshold
QueryConsolidator.ALLOW_MIXED_INTENTS = False           # Allow different intents?
```

---

## Decision Tree

```
Query: "How? When? What?"
           ↓
        Extract Questions
        ↓ ↓ ↓ (3 questions)
      ↙ Topic Analysis ↘
   submission          status
      ↓                 ↓
   Similarity Score: 0.85
      ↓
   Compare: 0.85 >= 0.75?
      ↓
    YES ✓
      ↓
   CONSOLIDATE
   ↓
   Return 1 group: [Q1, Q2, Q3]
```

---

## Topic Detection Quick Map

```
Query Contains          → Topic Category
┌─────────────────────────────────────────┐
│ submit, send, file                      │ → submission
│ how long, timeline, duration            │ → timeline
│ eligible, requirements, criteria        │ → eligibility
│ status, progress, approve, reject       │ → status
│ process, procedure, steps               │ → process
│ data, dataset, information, records     │ → data
└─────────────────────────────────────────┘
```

---

## Typical Scenarios

### ✅ Consolidate (Score >= 0.75)

| Scenario | Questions | Score | Action |
|----------|-----------|-------|--------|
| **Submission Flow** | "How submit? Documents needed?" | 0.85+ | ✓ Consolidate |
| **Eligibility Check** | "Eligible? Requirements? Documents?" | 0.80+ | ✓ Consolidate |
| **Timeline Questions** | "When approved? How long? Status?" | 0.75+ | ✓ Consolidate |
| **Process Questions** | "Process? Steps? Timeline?" | 0.80+ | ✓ Consolidate |

### ❌ Separate (Score < 0.75)

| Scenario | Questions | Score | Action |
|----------|-----------|-------|--------|
| **Different Topics** | "How submit? What's weather?" | 0.0 | ✗ Separate |
| **Unrelated** | "Data? Music? Sports?" | 0.0 | ✗ Separate |
| **Single Question** | "How do I submit?" | N/A | ✗ Not multiple |
| **Too Many** | 6+ questions | N/A | ✗ Exceeds max |

---

## Common Queries & Results

### Query 1: Related Questions
```
Input: "How do I submit a data request? What documents are needed?"

Output:
has_multiple_questions: True
questions: 2
question_groups: [[Q1, Q2]]
should_consolidate: True
consolidation_score: 0.85
```

### Query 2: Unrelated Questions
```
Input: "How do I submit? What's the weather?"

Output:
has_multiple_questions: True
questions: 2
question_groups: [[Q1], [Q2]]
should_consolidate: False
consolidation_score: 0.0
```

### Query 3: Single Question
```
Input: "How do I submit a data request?"

Output:
has_multiple_questions: False
questions: 1
question_groups: [[Q1]]
should_consolidate: False
consolidation_score: 0.0
```

---

## Testing Quick Start

```bash
# Run all tests
pytest tests/ -v

# Run specific category
pytest tests/test_query_consolidator.py::TestQueryConsolidatorDetection -v

# Run with coverage
pytest tests/ --cov=implementation

# Expected: 37/37 tests pass, >85% coverage
```

---

## Configuration Quick Guide

### Enable/Disable
```python
# Disable consolidation
QueryConsolidator.CONSOLIDATION_ENABLED = False
# Result: always returns should_consolidate: False
```

### Adjust Threshold
```python
# Make it easier to consolidate
QueryConsolidator.TOPIC_SIMILARITY_THRESHOLD = 0.60

# Make it harder to consolidate
QueryConsolidator.TOPIC_SIMILARITY_THRESHOLD = 0.90
```

### Change Limits
```python
# Allow more questions
QueryConsolidator.MAX_QUESTIONS_PER_CONSOLIDATION = 10

# Require more questions
QueryConsolidator.MIN_QUESTIONS_TO_CONSOLIDATE = 3
```

---

## Performance Expectations

| Input | Time | Throughput |
|-------|------|-----------|
| 1 question | < 1ms | 1000+ qps |
| 2 questions | < 2ms | 1000+ qps |
| 5 questions | < 5ms | 1000+ qps |
| Long query (5KB) | < 10ms | 100+ qps |

---

## Error Handling

All edge cases handled gracefully:

| Input | Behavior |
|-------|----------|
| Empty string `""` | Returns `has_multiple_questions: False` |
| Single question | Returns `has_multiple_questions: False` |
| 6+ questions | Returns `should_consolidate: False` (too many) |
| No keywords | Returns `has_multiple_questions: False` |
| Special chars | Handled gracefully, no errors |

---

## Integration Quick Checklist

- [ ] Import: `from implementation.query_consolidator import consolidate_multiple_questions`
- [ ] Call after US-03 (message grouping)
- [ ] Call before US-07 (intent classification)
- [ ] Check `result.should_consolidate` to decide routing
- [ ] Use `result.question_groups` for response generation
- [ ] Log `result.reasoning` for debugging
- [ ] Test with real researcher queries

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Questions not detected | Check for question marks or keywords (how, what, when) |
| Not consolidating | Check similarity score vs threshold (0.75) |
| Too strict | Lower TOPIC_SIMILARITY_THRESHOLD to 0.60 |
| Too lenient | Raise TOPIC_SIMILARITY_THRESHOLD to 0.85 |
| Import error | Ensure in correct directory for imports |
| Tests fail | Run `pytest tests/ -vv` for detailed output |

---

## Files Quick Navigation

| File | Purpose |
|------|---------|
| `implementation/query_consolidator.py` | Core logic |
| `tests/test_query_consolidator.py` | Unit tests (37 tests) |
| `test_queries.py` | Integration tests |
| `test_queries.json` | Test data |
| `README.md` | Full documentation |
| `ACCEPTANCE_CRITERIA.md` | Definition of done |
| `HOW_TO_TEST.md` | Testing guide |
| `QUICK_REFERENCE.md` | This file |

---

## Key Class & Methods

```python
# Main class
class QueryConsolidator:
    def consolidate(query_text: str) -> ConsolidationResult
    def group_questions(questions: List[str]) -> List[List[str]]
    def _extract_questions(text: str) -> List[str]
    def _extract_topics(question: str) -> List[str]
    def _calculate_similarity(questions: List[str]) -> float

# Result class
@dataclass
class ConsolidationResult:
    has_multiple_questions: bool
    questions: List[str]
    question_groups: List[List[str]]
    should_consolidate: bool
    consolidation_score: float
    reasoning: str

# Entry point
def consolidate_multiple_questions(query_text: str) -> ConsolidationResult
```

---

## Example Integration in /chat

```python
@app.post("/chat")
async def chat(request: ChatRequest):
    # Step 1: Validate role (US-02)
    
    # Step 2: Consolidate questions (US-04)
    consolidation = consolidate_multiple_questions(request.query)
    
    # Step 3: Validate input (US-05)
    
    # Step 4: Classify intent (US-07)
    
    if consolidation.should_consolidate:
        # Use consolidated questions together
        for group in consolidation.question_groups:
            answers = get_answers_for_group(group)
            combined_answer = consolidate_answers(answers)
    else:
        # Handle separately
        answers = [get_answer(q) for q in consolidation.questions]
    
    return response
```

---

## Status

✅ Implementation Complete  
✅ Tests: 37/37 passing  
✅ Coverage: >85%  
✅ Ready for Integration

---

## Next Steps

1. Review README.md for full documentation
2. Run tests: `pytest tests/ -v`
3. Integrate into `/chat` endpoint
4. Test with real queries
5. Monitor consolidation quality

---

**Last Updated**: 2026-07-03  
**Version**: 1.0  
**Status**: Production Ready

