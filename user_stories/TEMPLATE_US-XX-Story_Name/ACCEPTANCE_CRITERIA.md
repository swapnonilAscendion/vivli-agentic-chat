# Acceptance Criteria for {{US_ID}}: {{US_NAME}}

## Definition of Done

This {{US_ID}} is **COMPLETE** when all items below are satisfied.

---

## Functional Requirements

### 1. Validation Logic
- [ ] {{VALIDATION_RULE_1}} is implemented
- [ ] {{VALIDATION_RULE_2}} is implemented
- [ ] {{VALIDATION_RULE_3}} is implemented
- [ ] All rules execute in correct order (1 → 2 → 3)
- [ ] Invalid inputs are rejected gracefully

### 2. Error Messages
- [ ] Error message for {{ERROR_TYPE_1}} is user-friendly
- [ ] Error message for {{ERROR_TYPE_2}} is user-friendly
- [ ] Error message for {{ERROR_TYPE_3}} is user-friendly
- [ ] All error messages are under 140 characters
- [ ] Error messages don't expose system details

### 3. Valid Input Processing
- [ ] Valid inputs pass validation and continue to next step
- [ ] Valid inputs are classified correctly
- [ ] Valid inputs generate appropriate responses

### 4. Integration
- [ ] Integrated into `/chat` endpoint
- [ ] Runs before intent classification
- [ ] Returns proper metadata in response
- [ ] No changes to other user stories

---

## Test Requirements

### Unit Tests
- [ ] Minimum 80% code coverage
- [ ] All validation rules have dedicated tests
- [ ] Edge cases are tested
- [ ] Tests pass locally: `pytest tests/ -v`

### Integration Tests
- [ ] {{TEST_QUERY_VALID_1}} returns `validation_status: "passed"`
- [ ] {{TEST_QUERY_INVALID_1}} returns `validation_status: "failed"`
- [ ] {{TEST_QUERY_EDGE_CASE_1}} returns expected result
- [ ] Test results saved: `test_queries.json`

### Manual Testing
- [ ] Tested valid query via cURL
- [ ] Tested invalid query via cURL
- [ ] Tested edge case via cURL
- [ ] Response times are acceptable (<500ms)

---

## Documentation Requirements

### Code Documentation
- [ ] All functions have docstrings
- [ ] All parameters are documented
- [ ] Return values are documented
- [ ] Examples provided for complex logic

### User Documentation
- [ ] README.md is complete and accurate
- [ ] HOW_TO_TEST.md has clear instructions
- [ ] Error messages are explained
- [ ] Examples are provided

### Developer Documentation
- [ ] QUICK_REFERENCE.md created
- [ ] Configuration options explained
- [ ] Dependencies listed
- [ ] Known limitations documented

---

## Quality Requirements

### Code Quality
- [ ] PEP 8 compliant (run `pylint`)
- [ ] No hardcoded values (use constants)
- [ ] DRY principle followed (no code duplication)
- [ ] Functions are focused and small

### Performance
- [ ] Validation completes in <100ms
- [ ] No memory leaks
- [ ] Handles edge cases efficiently
- [ ] Scales to handle 1000+ queries/second

### Security
- [ ] No SQL injection vulnerabilities
- [ ] No prompt injection risks
- [ ] No sensitive data in logs
- [ ] Input sanitization where needed

### Maintainability
- [ ] Code is self-explanatory
- [ ] Complex logic is commented
- [ ] Easy to add new validation rules
- [ ] Easy to modify error messages

---

## Regression Requirements

- [ ] All existing tests still pass
- [ ] No performance degradation
- [ ] No breaking changes to other user stories
- [ ] Backward compatibility maintained

---

## Documentation Checklist

### In Code
- [ ] `"""Docstrings"""` present on all classes
- [ ] `"""Docstrings"""` present on all functions
- [ ] Parameter types documented
- [ ] Return types documented
- [ ] Examples in docstrings

### In README.md
- [ ] Overview section complete
- [ ] Validation rules explained
- [ ] Error messages documented
- [ ] Examples provided
- [ ] Testing instructions clear

### In HOW_TO_TEST.md
- [ ] Unit test instructions
- [ ] Integration test instructions
- [ ] Manual test examples
- [ ] Expected results documented

### In test_queries.json
- [ ] All queries described
- [ ] Expected outcomes noted
- [ ] Query categories clear

---

## Sign-Off Requirements

Before marking as "Done", verify:

### Code Review
- [ ] Reviewed by: _________________
- [ ] No blocking comments
- [ ] All comments addressed

### Testing
- [ ] All tests pass
- [ ] Coverage is adequate (>80%)
- [ ] Manual testing complete
- [ ] No regressions detected

### Documentation
- [ ] All files created/updated
- [ ] Links are correct
- [ ] Examples work
- [ ] Spelling/grammar checked

---

## Acceptance Criteria Tracking

| Criterion | Status | Verified By | Date |
|-----------|--------|-------------|------|
| {{AC_1}} | ❌ TODO | - | - |
| {{AC_2}} | ❌ TODO | - | - |
| {{AC_3}} | ❌ TODO | - | - |

---

## Notes

- **Started**: 2026-07-03
- **Target Completion**: [DATE]
- **Actual Completion**: [DATE]
- **Comments**: [Any notes about implementation]

---

## Related Issues

- Issue #XXX: [Description]
- Issue #XXX: [Description]

---

## Approved By

- [ ] Developer: _________________ Date: _______
- [ ] Code Reviewer: _________________ Date: _______
- [ ] QA: _________________ Date: _______
- [ ] Product Owner: _________________ Date: _______
