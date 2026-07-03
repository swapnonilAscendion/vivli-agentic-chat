# User Story Template for Vivli Chatbot

## Quick Start

Copy this entire template to create a new user story:

```bash
cp -r user_stories/TEMPLATE_USER_STORY user_stories/US-XX-Your_Story_Name
```

Then customize the variables in each file.

---

## Template Variables Reference

| Variable | Format | Example | File(s) |
|----------|--------|---------|---------|
| `{{US_ID}}` | US-XX (where XX is 2-digit number) | US-06 | All files |
| `{{US_NAME}}` | PascalCase with underscores | Data_Source_Validation | Directory name, README |
| `{{DESCRIPTION}}` | 1-2 sentence description | Validates data sources are legitimate | README, acceptance_criteria.md |
| `{{GOAL}}` | Brief goal statement | Prevent invalid data source references | README |
| `{{ACCEPTANCE_CRITERIA}}` | Bulleted list of AC | User receives error for invalid sources | acceptance_criteria.md |
| `{{VALIDATION_RULES}}` | List of validation checks | Check source exists in database | validator.py |
| `{{ERROR_MESSAGES}}` | User-friendly messages | "Data source not found..." | validator.py |
| `{{TEST_QUERIES}}` | Valid/Invalid test cases | Valid: "data from study XYZ" | test_queries.json |

---

## How to Use This Template

### Step 1: Create Directory
```bash
mkdir user_stories/US-XX-Your_Story_Name
mkdir user_stories/US-XX-Your_Story_Name/{implementation,tests,docs}
```

### Step 2: Copy Template Files
Copy and customize:
- `README.md` → Describe your user story
- `ACCEPTANCE_CRITERIA.md` → Define what "done" means
- `implementation/validator.py` → Implement validation logic
- `test_queries.json` → Create test cases
- `HOW_TO_TEST.md` → Document testing procedures

### Step 3: Variables to Replace
Search and replace these in all files:
- `{{US_ID}}` → Your user story ID (e.g., US-06)
- `{{US_NAME}}` → Your story name (e.g., Data_Source_Validation)
- `{{DESCRIPTION}}` → What your story does
- `{{GOAL}}` → The goal/purpose
- `{{ACCEPTANCE_CRITERIA}}` → List your acceptance criteria
- `{{VALIDATION_RULES}}` → Your validation checks
- `{{ERROR_MESSAGES}}` → Your error messages

### Step 4: Files to Create/Modify

```
user_stories/US-XX-Your_Story_Name/
├── README.md                          # Overview & documentation
├── ACCEPTANCE_CRITERIA.md             # Definition of done
├── HOW_TO_TEST.md                     # Testing procedures
├── implementation/
│   └── validator.py                   # Main validation logic
├── tests/
│   └── test_validator.py              # Unit tests
└── test_queries.json                  # Integration test queries
```

---

## Files Included in Template

### 1. README.md
Main documentation file. Contains:
- What the user story does
- Goal and importance
- Validation rules
- Error messages
- Integration details

**Variables:**
- `{{US_ID}}`, `{{US_NAME}}`, `{{DESCRIPTION}}`, `{{GOAL}}`
- `{{VALIDATION_RULES}}`

### 2. ACCEPTANCE_CRITERIA.md
Defines "done" - success criteria.

**Variables:**
- `{{US_ID}}`, `{{ACCEPTANCE_CRITERIA}}`

### 3. implementation/validator.py
Core validation logic.

**Variables:**
- `{{VALIDATION_RULES}}`
- `{{ERROR_MESSAGES}}`
- Function names, class names, etc.

### 4. tests/test_validator.py
Unit tests for validation logic.

**Variables:**
- `{{US_ID}}`
- Test case names
- Expected results

### 5. test_queries.json
Integration test queries for `/chat` endpoint.

**Variables:**
- `{{US_ID}}`
- `{{TEST_QUERIES}}` (valid and invalid)

### 6. HOW_TO_TEST.md
Testing procedures and examples.

**Variables:**
- `{{US_ID}}`
- Curl commands, test steps

---

## File Templates

Below are the actual template files with placeholder variables.

