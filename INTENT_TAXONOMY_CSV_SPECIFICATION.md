# Intent Taxonomy CSV Specification

## Overview
The Intent Taxonomy CSV defines all possible query types the chatbot can recognize, how to detect them, and where to route them.

---

## CSV Structure & Fields

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **intent_id** | String | Unique identifier for this intent | `INT-001` |
| **intent_name** | String | Human-readable intent name | `FAQ` |
| **category** | String | Grouping category | `general`, `request`, `validation` |
| **keywords** | String | Pipe-separated keywords to detect intent | `how\|what\|where\|process\|guide` |
| **primary_route** | String | Where to send this query | `vector_db`, `vivli_api`, `human`, `form_validator` |
| **fallback_route** | String | Where to send if primary fails | `escalate`, `vector_db`, `human` |
| **confidence_threshold** | Float | Min confidence score to route to primary (0.0-1.0) | `0.5`, `0.6`, `0.3` |
| **min_message_length** | Int | Minimum message length to consider (words) | `3`, `5` |
| **max_message_length** | Int | Maximum message length for this intent | `200`, `500` |

### Optional Fields (Recommended)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **description** | String | What this intent represents | `General platform questions` |
| **response_type** | String | How to format response | `standard`, `structured`, `template` |
| **context_requirement** | String | Does this need request_id, user_role, etc? | `request_id`, `user_id`, `none` |
| **knowledge_base_source** | String | Which KB section to prioritize | `faq`, `how_to`, `policies` | 
| **examples** | String | Sample queries for this intent | `What is a data request?\|How do I submit?` |
| **api_endpoint** | String | If vivli_api route, which endpoint | `/api/requests/{id}`, `/api/users/{id}/requests` |
| **response_template** | String | Template for formatting response | `Your request is at stage: {stage}` |

---

## Real-World Example

### Complete CSV (What Vivli Should Provide)

```csv
intent_id,intent_name,category,keywords,primary_route,fallback_route,confidence_threshold,min_message_length,max_message_length,description,response_type,context_requirement,knowledge_base_source,examples,api_endpoint,response_template
INT-001,General_FAQ,general,how|what|where|process|guide|explain|tutorial|help with|information|learn|understand,vector_db,escalate,0.5,3,500,Questions about Vivli platform features and processes,standard,none,faq|how_to,"What is a data request?|How do I submit a form?|Where can I find guidelines?",/api/knowledge/search,"Based on our knowledge base: {answer}"
INT-002,Request_Status,request,status|my request|request status|update|check|current stage|where is|progress|pending|reviewed,vivli_api,vector_db,0.4,3,200,Questions about a specific data request's status,structured,request_id,none,"What's the status of my request?|Is my form check done?|When will I hear back?",/api/requests/{request_id},"Your request {request_id} is currently at stage: {stage}"
INT-003,Form_Check,request,form check|form validation|field validation|field error|required field|form check status|form review,form_validator,escalate,0.5,3,150,Questions about form check process and field validation,structured,request_id,none,"What does this field mean?|Why is this required?|When is form check done?",/api/requests/{request_id}/form-check,"This field is {field_name}: {field_description}. Status: {status}"
INT-004,Eligibility,general,eligible|qualify|qualification|requirements|criteria|am i eligible|do i qualify|requirements met,vector_db,escalate,0.5,3,200,Questions about researcher eligibility and requirements,standard,user_id,policies|faq,"Am I eligible to request data?|What are the requirements?|Do I meet the criteria?",/api/eligibility/check,"Based on your profile: {eligibility_status}"
INT-005,Data_Request_Process,general,process|steps|how to submit|submission|submit|timeline|approval|researcher form|data sharing|how does,vector_db,escalate,0.5,3,300,Questions about overall data request process and timelines,standard,none,how_to|process,"What are the steps in the data request process?|How long does it take?|What happens after I submit?",/api/knowledge/process,"The process involves these steps: {steps}"
INT-006,Policy_Questions,general,policy|policies|aiml|rules|regulations|compliance|agree to|terms|understand policy,vector_db,escalate,0.6,3,250,Questions about Vivli policies and compliance,standard,none,policies,"What is the AIML policy?|Do I need to agree to terms?|What are the data sharing rules?",/api/knowledge/policies,"According to our {policy_name}: {policy_text}"
INT-007,Account_Issues,general,account|login|password|access|profile|settings|my account|account setup,escalate,escalate,0.0,3,150,Account and login-related issues (escalate to human),standard,user_id,none,"I can't login|Reset my password|Update my account",/api/support/account,"Please contact support for account issues"
INT-008,Technical_Issues,general,bug|error|broken|not working|crash|issue|problem|technical|system error|platform error,escalate,escalate,0.0,3,200,Technical/system issues (escalate to human),standard,none,none,"The platform crashed|I see an error|Something is broken",/api/support/tickets,"Please contact technical support"
INT-009,Contributor_Questions,general,contributor|data provider|share data|provide data|dataset|contributed,escalate,escalate,0.0,3,200,Questions from data contributors (not researchers),standard,none,none,"How do I contribute data?|I'm a contributor",/api/support/contributors,"Contributors should contact support"
INT-010,Out_Of_Scope,general,irrelevant|spam|off topic|not related|random|joke,escalate,escalate,0.0,1,1000,Completely unrelated queries (spam/off-topic),standard,none,none,"Hello bot!|What's the weather?|Tell me a joke",/api/support/escalate,"I'm here to help with data requests"
```

---

## Field Explanations with Examples

### 1. **intent_id** 
Unique identifier. Naming convention: `INT-###`

```
INT-001 (FAQ)
INT-002 (Request Status)
INT-003 (Form Check)
```

### 2. **intent_name**
Clear name for developers. Use underscores.

```
General_FAQ
Request_Status
Form_Check_Questions
```

### 3. **category**
Groups related intents:

```
general    → Platform questions (FAQ, process, policy)
request    → Data request specific (status, form check)
validation → Input validation (spam, edge cases)
account    → User account (login, settings)
support    → Escalation (technical issues, bugs)
```

### 4. **keywords** (CRITICAL)
Pipe-separated (`|`) keywords to detect this intent.

```
For FAQ:           how|what|where|why|when|process|guide|help
For Request Status: status|my request|update|check|stage|progress
For Form Check:    form check|validation|field error|required
For Eligibility:   eligible|qualify|requirements|criteria
```

**How it's used:**
```python
query = "what is the data request process"
keywords = "how|what|where|process|guide"

# Check if any keyword appears in query
if any(kw in query.lower() for kw in keywords.split('|')):
    return this_intent
```

### 5. **primary_route**
Where to send this query if confidence is HIGH:

```
vector_db          → Search knowledge base (for FAQ)
vivli_api          → Call Vivli data request API (for request status)
form_validator     → Special form validation logic
human              → Escalate to human immediately
```

### 6. **fallback_route**
Where to send if primary fails or confidence is LOW:

```
escalate           → Send to human support
vector_kb          → Try knowledge base instead
human              → Always escalate (no fallback)
```

**Example flow:**
```
Query: "What's the status of my request?"

1. Classify: Intent = Request_Status, confidence = 0.45
2. Check threshold: 0.45 < 0.4? NO (0.45 >= 0.4)
3. Use primary_route: vivli_api
4. Try to call API → if fails, use fallback_route: vector_db

Query: "What is a data request?"

1. Classify: Intent = FAQ, confidence = 0.65
2. Check threshold: 0.65 >= 0.5? YES
3. Use primary_route: vector_db
```

### 7. **confidence_threshold**
Minimum confidence score needed to route to PRIMARY route (0.0 - 1.0):

```
0.3 → Very lenient (catch most queries)
0.5 → Moderate (balanced)
0.6 → Strict (high confidence only)
0.8 → Very strict (only clear matches)
```

**Logic:**
```python
if confidence >= threshold:
    use primary_route
else:
    use fallback_route
```

### 8. **min_message_length & max_message_length**
Filter by message length (word count):

```
min_message_length: 3   → Ignore queries like "hi", "ok", "yes"
max_message_length: 500 → Reject pasted documents (500+ words)
```

### 9. **description**
Human-readable explanation (for documentation, not code):

```
"General questions about Vivli platform"
"Questions about researcher's specific data request status"
"Questions that need human support (account, technical issues)"
```

### 10. **response_type**
How to format the response:

```
standard   → Plain text answer from KB
structured → Formatted data (e.g., request status with fields)
template   → Use predefined template with variable substitution
json       → Return JSON structured data
```

### 11. **context_requirement**
What information do we need from the message context?

```
none           → Can answer without extra context
request_id     → Need to extract request ID from query
user_id        → Need user identity
user_role      → Need to know if researcher/admin/contributor
chat_context   → Need chat history
```

### 12. **knowledge_base_source**
Which KB section to prioritize:

```
faq           → FAQ section
how_to        → How-to guides
policies      → AIML policies
process       → Data request process
all           → Search all sections
```

### 13. **examples**
Sample queries for this intent (testing/docs):

```
"What is a data request?|How do I submit?|Where can I find guidelines?"
"What's the status?|Is it done?|When will I hear back?"
```

### 14. **api_endpoint**
If routing to vivli_api, which endpoint to call:

```
/api/requests/{request_id}              → Get request status
/api/requests/{request_id}/form-check   → Get form check status
/api/users/{user_id}/requests           → Get user's requests
/api/eligibility/check                  → Check eligibility
```

### 15. **response_template**
Template for formatting response with variables:

```
"Your request {request_id} is at stage: {stage}"
→ Becomes: "Your request REQ-123 is at stage: form_check"

"The {field_name} field requires: {field_description}"
→ Becomes: "The researcher_name field requires: Full name of lead researcher"
```

---

## What We'll Ask Vivli For

```
Please provide the Intent Taxonomy CSV with these columns:

REQUIRED:
- intent_id (e.g., INT-001)
- intent_name (e.g., General_FAQ)
- category (e.g., general, request, account)
- keywords (e.g., "how|what|where|process")
- primary_route (e.g., vector_db, vivli_api, human)
- fallback_route (e.g., escalate, vector_db)
- confidence_threshold (e.g., 0.5, 0.6, 0.3)

OPTIONAL (but recommended):
- description
- response_type
- context_requirement (if needed for their APIs)
- knowledge_base_source
- examples
- api_endpoint (if using vivli_api)
- response_template

Format: CSV with header row
```

---

## How It Will Be Used in Code

### 1. Loading the CSV
```python
from intent_taxonomy_loader import IntentTaxonomyLoader

loader = IntentTaxonomyLoader('intent_taxonomy.csv')
taxonomy = loader.get_all_intents()
```

### 2. Classifying a Query
```python
intent = classifier.classify("What's the status of my request?")
# Returns:
# {
#   'intent_id': 'INT-002',
#   'intent_name': 'Request_Status',
#   'confidence': 0.75,
#   'keywords_matched': ['status', 'request'],
#   'primary_route': 'vivli_api',
#   'context_required': 'request_id'
# }
```

### 3. Routing the Query
```python
def route_query(intent, confidence):
    taxonomy_entry = taxonomy[intent['intent_id']]
    
    if confidence >= taxonomy_entry['confidence_threshold']:
        route = taxonomy_entry['primary_route']
    else:
        route = taxonomy_entry['fallback_route']
    
    if route == 'vector_db':
        return search_knowledge_base(query)
    elif route == 'vivli_api':
        endpoint = taxonomy_entry['api_endpoint']
        return call_vivli_api(endpoint, request_id)
    elif route == 'human':
        return escalate_to_human(query)
```

### 4. Formatting Response
```python
def format_response(intent_id, response_data):
    taxonomy_entry = taxonomy[intent_id]
    template = taxonomy_entry.get('response_template')
    
    if template:
        # Use template: "Your request {request_id} is at stage: {stage}"
        return template.format(**response_data)
    else:
        # Use standard response
        return response_data
```

---

## Minimal CSV (If Vivli Can't Provide Everything)

At minimum, we need these columns:

```csv
intent_id,intent_name,keywords,primary_route,fallback_route,confidence_threshold
INT-001,FAQ,"how|what|where|process|guide",vector_db,escalate,0.5
INT-002,Request_Status,"status|my request|update|check",vivli_api,escalate,0.4
INT-003,Escalation,"urgent|bug|error|broken",human,human,0.0
```

This is the **absolute minimum**. We can build everything else we need.

---

## Summary: What to Ask Vivli

```
Hi Vivli Team,

We need the Intent Taxonomy CSV file for the chatbot.

Can you provide a CSV with:

REQUIRED COLUMNS:
✓ intent_id (unique ID like INT-001)
✓ intent_name (e.g., General_FAQ, Request_Status)
✓ keywords (pipe-separated, e.g., "how|what|where|process")
✓ primary_route (vector_db, vivli_api, human, form_validator, etc.)
✓ fallback_route (escalate, vector_db, human, etc.)
✓ confidence_threshold (0.0-1.0 decimal)

OPTIONAL COLUMNS (if available):
- category (general, request, validation, account, support)
- description
- response_type
- context_requirement (request_id, user_id, none, etc.)
- api_endpoint (if using vivli_api route)
- response_template
- examples

Format: CSV file with headers
Location: Can send via email/Slack/repo
Deadline: Needed before we complete intent classification work

Thanks!
```

Does this help clarify what should be in the CSV?