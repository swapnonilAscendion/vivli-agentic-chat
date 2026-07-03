# Quick Reference: {{US_ID}}: {{US_NAME}}

## One-Liner
{{DESCRIPTION}}

---

## Validation Rules (Order of Execution)

1. **{{VALIDATION_RULE_1}}**
2. **{{VALIDATION_RULE_2}}**
3. **{{VALIDATION_RULE_3}}**

---

## Error Messages

| Error | When | Message |
|-------|------|---------|
| {{ERROR_TYPE_1}} | {{WHEN_ERROR_1}} | "{{ERROR_TYPE_1_MESSAGE}}" |
| {{ERROR_TYPE_2}} | {{WHEN_ERROR_2}} | "{{ERROR_TYPE_2_MESSAGE}}" |
| {{ERROR_TYPE_3}} | {{WHEN_ERROR_3}} | "{{ERROR_TYPE_3_MESSAGE}}" |

---

## Quick Tests

### Valid
```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"query": "{{VALID_QUERY_1}}"}'
# Expected: validation_status: "passed"
```

### Invalid (Type 1)
```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"query": "{{INVALID_QUERY_1}}"}'
# Expected: validation_status: "failed"
```

### Invalid (Type 2)
```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"query": "{{INVALID_QUERY_4}}"}'
# Expected: validation_status: "failed"
```

### Invalid (Type 3)
```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"query": "{{INVALID_QUERY_6}}"}'
# Expected: validation_status: "failed"
```

---

## Commands

### Unit Tests
```bash
pytest tests/ -v
```

### Integration Tests
```bash
python test_queries.py --verbose
bash test_queries.sh all http://localhost:8000
```

### Coverage
```bash
pytest tests/ --cov=implementation --cov-report=html
```

### Specific Category
```bash
pytest tests/ -k "{{VALIDATION_RULE_1}}" -v
```

---

## Configuration

### File: `implementation/validator.py`
```python
{{PARAMETER_1}} = {{VALUE_1}}  # {{PARAM_DESC_1}}
{{PARAMETER_2}} = {{VALUE_2}}  # {{PARAM_DESC_2}}
{{PARAMETER_3}} = {{VALUE_3}}  # {{PARAM_DESC_3}}
```

---

## Key Files

| File | Purpose |
|------|---------|
| `validator.py` | Validation logic |
| `test_validator.py` | Unit tests |
| `test_queries.json` | Integration tests |
| `README.md` | Full documentation |
| `ACCEPTANCE_CRITERIA.md` | Definition of done |
| `HOW_TO_TEST.md` | Testing guide |

---

## Test Statistics

- **Total**: XX tests
- **Valid**: XX tests
- **Invalid**: XX tests
- **Pass Rate**: XX%

---

## Integration

**Endpoint**: `/chat`  
**Step**: Before intent classification  
**Import**: `from input_validator import validate_input`

---

## Status

✅ **Implementation**: Complete  
✅ **Tests**: XX/XX passing  
✅ **Integration**: Complete  
✅ **Documentation**: Complete  

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Tests fail with "Cannot connect" | Start server: `python main.py` |
| Import error | Check PYTHONPATH and `__init__.py` |
| Slow tests | Run unit tests only, not integration |
| Different results | Make sure server is restarted |

---

## Helpful Regex

If using regex patterns:

```python
# {{PATTERN_1}}
{{PATTERN_1_REGEX}}

# {{PATTERN_2}}
{{PATTERN_2_REGEX}}
```

---

## Performance Targets

- Validation: <100ms per query
- Throughput: 1000+ queries/second
- Memory: <50MB
- Coverage: >80%

---

## Related Stories

- [US-01: Story Name](../US-01-Story_Name/)
- [US-XX: Other Story](../US-XX-Other_Story/)

---

**Last Updated**: 2026-07-03
