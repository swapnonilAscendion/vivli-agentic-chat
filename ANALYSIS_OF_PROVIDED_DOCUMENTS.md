# Complete Analysis: FRD + Intent Taxonomy + Classification Rules

## Executive Summary

✅ **YES, these documents SOLVE ALL my problems!**

The three documents provide:
1. **Intent Taxonomy CSV Data** - 13 intent categories with scope, standard responses, and rules
2. **Development Rules & Logic** - Specific rule IDs and implementation notes
3. **Classification Rules** - 40+ example queries mapped to intent categories
4. **Scope Enforcement Logic** - Exactly which chats/stages/roles should be handled

---

## What I Now Understand

### **The Intent Taxonomy (13 Categories)**

From the metadata document, here are the **13 official Vivli Intent Categories**:

| ID | Category Name | In/Out | Purpose | Scope |
|----|----|------|----|-------|
| 1 | **study_selection_and_enquiry_handling** | IN | Questions about studies, enquiries, study selection | FAQ answers from Guru cards |
| 2 | **revision_followup_resubmit_nudge** | OUT | Auto messages pushing resubmit | Not for AI to respond |
| 3 | **specialized_form_check_meddra_safety** | IN | MedDRA certification questions | FAQ about MedDRA requirements |
| 4 | **form_check_revisions_requested** | IN | Form check feedback - what to fix | FAQ with revision instructions |
| 5 | **data_contributor_revisions_relayed** | OUT | Data contributor requests | Not for AI to respond |
| 6 | **dua_initiation_and_signing_instructions** | OUT | DUA signing process (post form-check) | Not for AI (future stages) |
| 7 | **request_withdrawn_for_inactivity** | IN | After 4 months of inactivity | Standard response for withdrawal |
| 8 | **draft_request_completion_nudge** | OUT | Auto message for incomplete draft | Not for AI to respond |
| 9 | **short_acknowledgment_confirmation** | IN | "Has form check been received?" "What's status?" | Short confirmation responses |
| 10 | **vivli_admin_edits_for_approval** | IN | "Vivli made edits, review and approve" | Standard response + deadline |
| 11 | **request_status_update_in_review** | IN | "What's the status of my request?" | Status + timeline info |
| 12 | **login_difficulties** | OUT | Account/login issues | Escalate to human |
| 13 | **documents_uploaded_to_chat** | IN | File uploads (MedDRA cert, etc.) | Parse and track documents |

---

## What This Means for Implementation

### **AI Agent Scope (CLEAR NOW)**

**The AI agent ONLY responds to:**
✅ **"IN" categories** (1, 3, 4, 7, 9, 10, 11, 13)
- These have standard Guru card responses
- These are FAQ/knowledge-based

✅ **In Open Chat only**
✅ **During Draft/Revision/Form-Check stages ONLY**
✅ **From Research Team members ONLY**

**The AI agent DOES NOT respond to:**
❌ **"OUT" categories** (2, 5, 6, 8, 12)
- These are automated messages or outside scope
- Escalate or ignore

❌ **Other chats** (Contributors, Requestor, Private Org)
❌ **Other stages** (DUA, Approved, Rejected, In Review)
❌ **Other users** (Admins, automated systems)

---

## FRD Rules & Dev Notes (IMPLEMENTATION DETAILS)

The FRD document includes **specific rule IDs** for developers:

```
For Intent Classification:
  rule_id: intent.classify
  rule_id: intent.min_categories  (FAQ vs Data Request)
  rule_id: intent.route

For Data Request Queries:
  rule_id: drq.fetch_realtime     (Call API with request_id)
  rule_id: drq.generate_response  (Use KB for context)
  rule_id: drq.no_answer_escalate (If no answer found)
  rule_id: drq.stateless          (No message memory)

For FAQ/KB Queries:
  rule_id: faq.all_sources        (All Guru cards)
  rule_id: faq.semantic_search    (Vector search)
  rule_id: faq.generate           (LLM generation)
  rule_id: faq.citations_public_only (Only public links)
  rule_id: faq.no_fabrication     (Never make up answers)
```

---

## Intent Classification Examples (From Excel)

Here are **REAL queries** mapped to intent categories:

### **Category 1: study_selection_and_enquiry_handling**
```
- "How to add a Vivli member study not listed on the platform?"
- "How to submit an enquiry for an unlisted study?"
- "How to add a J&J study not listed on the platform?"
- "When will my enquiry be approved?"
- "What's the status of my enquiry?"
- "How do I download a full list of studies?"
- "Can I download the data?" (if studies NOT downloadable)
- "Can studies be added at a later stage?"
- "Can an enquiry and data request be submitted at the same time?"
```
→ **Response**: Link to Guru card "How-to-enquire-about-a-study-not-listed-on-the-platform"

### **Category 3: specialized_form_check_meddra_safety**
```
- "Is [certification] sufficient for MedDRA training?"
- "I can't register for MedDRA course"
- "What are MedDRA requirements for safety analysis?"
```
→ **Response**: Guru card "MedDRA-requirements"

### **Category 4: form_check_revisions_requested**
```
- "What changes do I need to make following form check failure?"
- "Can I download the data?" (if studies ARE downloadable)
- "One or more studies are NOT set to downloadable"
```
→ **Response**: Guru cards with specific revision instructions

### **Category 7: request_withdrawn_for_inactivity**
```
- "I want to withdraw my request"
- "I want to cancel my request"
```
→ **Response**: Standard template with PI name

### **Category 9: short_acknowledgment_confirmation**
```
- "Has my form check submission been received?"
- "What's the status of my form check?"
- "When will I hear back?" (during active review)
- "I'm submitting revision responses via chat" (redirect to platform)
- "What's the status?" (while in Draft stage)
```
→ **Response**: "We have received your submission" + timeline

### **Category 10: vivli_admin_edits_for_approval**
```
- "Vivli has made edits to my request"
- "Vivli is sending standard edits-on-behalf message"
- "Can AI make edits on my behalf?"
```
→ **Response**: Standard response + "Review by [deadline]"

### **Category 11: request_status_update_in_review**
```
- "How long does the review process take?"
- "What's the general timeline for data access?"
- "I can't submit my request" (role not admin / form incomplete)
- "Can I reset my request to Draft?"
- "Is AI agent managing my data request?"
```
→ **Response**: Status + timeline + instructions

### **Category 13: documents_uploaded_to_chat**
```
- "Any file upload event detected"
- "Uploaded document is MedDRA certificate"
- "Mark MedDRA requirement as fulfilled"
- "Uploaded file is not MedDRA"
```
→ **Response**: Parse file + update status

---

## Critical Implementation Rules (From FRD)

### **Scope Enforcement (CRITICAL)**

```python
# Only respond if ALL conditions are met:
if (chat_type == 'open_chat'                                    # ✓ Right chat
    and request_stage in ['draft', 'revision', 'form_check']    # ✓ Right stage
    and sender_role in ['researcher', 'team_member']             # ✓ Right user
    and intent_category in ['in_scope_categories']):             # ✓ Right intent
    
    # Process and respond
    response = generate_response(query)
else:
    # Ignore message (don't respond)
    return None
```

### **Intent Classification (From FRD)**

```
Minimum categories:
  - FAQ / General queries
  - Data Request related queries
  
Reference taxonomy: Use the 13 categories from metadata doc
Rule_id: intent.classify
```

### **Intent Routing (From FRD)**

```
if intent.confidence >= threshold:
    use primary_route
else:
    use fallback_route

FAQ queries           → primary: vector_db  | fallback: escalate
Data Request queries  → primary: vivli_api  | fallback: escalate
Out-of-scope          → escalate to human
```

### **Data Request API Integration (CRITICAL FOR US-09)**

```
rule_id: drq.fetch_realtime
  1. Extract request_id from query
  2. Call Vivli data request API
  3. Get current form data
  
rule_id: drq.generate_response
  1. Fetch fresh data from API (no caching)
  2. Search KB for context
  3. Generate response
  
rule_id: drq.stateless
  NO message history stored
  Fresh API call on every query
  
rule_id: drq.no_answer_escalate
  If API returns empty/no answer
  → Escalate to human
```

### **FAQ Response Requirements (CRITICAL FOR US-10)**

```
rule_id: faq.all_sources
  Search: Guru cards, policies, FAQs, how-tos
  
rule_id: faq.semantic_search
  Vector search on embeddings
  
rule_id: faq.generate
  LLM generates grounded response
  
rule_id: faq.citations_public_only
  ONLY public URLs allowed (no Guru card links)
  Public: website FAQ, policy pages, how-to guides
  
rule_id: faq.no_fabrication
  If confidence < threshold → escalate
  NEVER make up answers
```

---

## How This Changes My Recommendations

### **BEFORE (Without documents):**
- 7 stories potentially implementable
- 4 stories blocked (waiting for CSV/API)
- Unclear intent taxonomy
- Unclear scope rules

### **AFTER (With documents):**
- ✅ **We have complete Intent Taxonomy** (13 categories)
- ✅ **We have classification examples** (40+ queries)
- ✅ **We have scope rules** (chats, stages, roles)
- ✅ **We have implementation rules** (rule IDs, logic)
- ✅ **We have standard responses** (Guru card links)

---

## New Implementation Roadmap

### **PHASE 1: FOUNDATION (Critical - Do First)**

#### **US-01 & US-02: Scope Enforcement** (5-8 days) 🔴 CRITICAL
What we now know:
- Must restrict to: `open_chat` only
- Must check stage: `draft`, `revision`, `form_check` only  
- Must check role: `researcher`, `team_member` only
- Must check intent: Only "IN" categories (1,3,4,7,9,10,11,13)

Implementation:
```python
def should_respond(message):
    checks = [
        message.chat_type == 'open_chat',
        message.request_stage in ['draft', 'revision', 'form_check'],
        message.sender_role in ['researcher', 'team_member'],
        intent_category in IN_SCOPE_CATEGORIES
    ]
    return all(checks)
```

#### **Create Intent Taxonomy Data Structure** (2-3 days) 🔴 CRITICAL
Convert metadata doc into code:
```python
INTENT_CATEGORIES = {
    'study_selection_and_enquiry_handling': {
        'in_scope': True,
        'standard_response': 'https://...',
        'examples': ['How to add study...', '...'],
    },
    'form_check_revisions_requested': {
        'in_scope': True,
        'standard_response': 'https://...',
        'examples': ['What changes...', '...'],
    },
    # ... 13 total categories
}
```

---

### **PHASE 2: INTENT CLASSIFICATION & ROUTING** (8-12 days)

#### **US-07: Implement Intent Classifier** (5-8 days) 🟡 IMPORTANT
Now we know:
- Exact 13 categories to classify into
- Specific queries for each category (40+ examples)
- Classification rules from Excel
- Confidence thresholds from FRD

Implementation:
```python
class IntentClassifier:
    def __init__(self):
        self.taxonomy = INTENT_CATEGORIES
        self.rules = CLASSIFICATION_RULES  # From Excel
    
    def classify(self, query):
        # Match against 13 categories
        for category, rules in self.rules.items():
            if self.matches_rules(query, rules['queries']):
                return category, confidence_score
        
        return 'unknown', 0
```

#### **US-08: Implement Intent Router** (3-4 days) 🟡 IMPORTANT
Now we know:
- FAQ routes → `vector_db` (search Guru cards)
- Data Request routes → `vivli_api` (fetch request status)
- Out-of-scope → `escalate` (send to human)
- Fallback routes if primary fails

Implementation:
```python
def route_query(intent, confidence):
    category = INTENT_CATEGORIES[intent]
    
    if not category['in_scope']:
        return escalate_to_human(query)
    
    if confidence >= category['threshold']:
        return route_to_primary(category['primary_route'])
    else:
        return route_to_fallback(category['fallback_route'])
```

---

### **PHASE 3: RESPONSE GENERATION** (10-15 days)

#### **US-10: Improve FAQ Responses** (5-7 days) 🟢 GOOD
Now we know:
- Must search all Guru cards
- Must use semantic search (vector embeddings)
- Must cite ONLY public URLs (not internal Guru links)
- Must NEVER fabricate if confidence low

#### **US-09: Implement Data Request API** (5-8 days) 🔴 CRITICAL
**Now we know from FRD:**
```
rule_id: drq.fetch_realtime
  1. Extract request_id from query
  2. Call /api/requests/{request_id}
  3. Get current status, stage, form data

rule_id: drq.generate_response
  1. Use KB documents for context
  2. Generate response mentioning status
  3. Include timeline if available

rule_id: drq.stateless
  No message memory!
  Fresh API call every time

rule_id: drq.no_answer_escalate
  If API has no info → escalate
```

**What we need from Vivli:**
```
1. API endpoint for fetching request status
2. Authentication method
3. Sample request/response JSON
4. Request ID format (REQ-XXXXX?)
5. What fields are available in response
```

---

### **PHASE 4: REMAINING USER STORIES** (12-18 days)

#### **US-03: Back-to-Back Message Grouping** (3-4 days)
#### **US-04: Query Decomposition** (5-7 days)
#### **US-05: Input Validation** (2-3 days)
#### **US-06: File Attachment Parsing** (5-8 days)

---

## What We Have vs. What We Need

### ✅ **We NOW HAVE (From Documents)**

1. **Complete Intent Taxonomy** (13 categories with scope)
2. **Classification Rules** (40+ example queries)
3. **Standard Responses** (Guru card links)
4. **Scope Enforcement Rules** (chats, stages, roles)
5. **Development Rule IDs** (faq.*, drq.*, intent.*)
6. **Response Format Requirements** (citations, no fabrication)
7. **Priority Order** (IN vs OUT scope)

### 🔴 **We STILL NEED (From Vivli)**

1. **Data Request API Documentation**
   - Endpoint URL
   - Authentication method
   - Request/response format
   - Sample data

2. **Chat Context Metadata**
   - How to get chat_type, request_stage, sender_role
   - Sample message JSON structure
   - What fields are available

3. **Access to Guru Cards** (for knowledge base)
   - Full dump of Guru cards in JSON format
   - For ingesting into vector DB

4. **Request ID Format & Parsing**
   - How request IDs look (REQ-12345?)
   - How to extract from natural language queries

---

## Complete Implementation Checklist

### **Ready to Start NOW** ✅

- [ ] **Phase 1a** - Create Intent Taxonomy data structure (code version of metadata doc)
- [ ] **Phase 1b** - Implement scope enforcement (chat/stage/role checks)
- [ ] **Phase 2a** - Build intent classifier (using 13 categories + 40+ rules)
- [ ] **Phase 2b** - Build intent router (routing logic)
- [ ] **Phase 4** - Implement remaining stories (US-03,04,05,06)

### **Blocked Until Vivli Provides** 🔴

- [ ] **Phase 3** - Data Request API integration (need API docs)
- [ ] **Phase 3** - Knowledge base ingestion (need Guru card access)

---

## My Revised Recommendation

### **START THIS WEEK**

1. **Create Intent Taxonomy Module** (Day 1-2)
   - Convert metadata doc into Python data structure
   - 13 categories with all fields

2. **Implement Scope Enforcement** (Day 3-4)
   - Check chat_type, request_stage, sender_role
   - Use mock data initially; wire to real data later

3. **Build Intent Classifier** (Day 5-8)
   - Implement classification for 13 categories
   - Test with 40+ examples from Excel

4. **Build Intent Router** (Day 9-10)
   - Route based on category and confidence
   - Test routing logic

**By end of week**: Core routing infrastructure ready ✅

**Then wait for**:
- API documentation → Phase 3 (Data Request API)
- Guru card access → Phase 3 (Knowledge base)
- Chat metadata details → Wire up real chat context

---

## Summary Table: What We Know Now

| Component | Before | After | Status |
|-----------|--------|-------|--------|
| Intent Taxonomy | ❌ Unknown | ✅ 13 categories defined | **READY** |
| Classification Rules | ❌ Unknown | ✅ 40+ examples mapped | **READY** |
| Scope Rules | ❌ Unclear | ✅ Chats/stages/roles defined | **READY** |
| Standard Responses | ❌ Unknown | ✅ Guru card links provided | **READY** |
| Dev Rule IDs | ❌ None | ✅ faq.*, drq.*, intent.* defined | **READY** |
| API Documentation | ❌ Missing | ❌ Still missing | **BLOCKED** |
| Chat Metadata Details | ❌ Unclear | ✅ Partially clear (need verification) | **PARTIALLY READY** |
| Guru Card Access | ❌ Unknown | ✅ Needed (bulk export) | **BLOCKED** |

---

## Questions for Vivli (Ask ASAP)

```
1. Data Request API:
   - What's the endpoint URL for fetching request status?
   - How do we authenticate?
   - Sample request/response JSON?
   - What fields are available in response?

2. Chat Context:
   - Can messages include chat_type, request_stage, sender_role?
   - Sample message JSON structure?
   - How do we know which chat a message is from?

3. Knowledge Base:
   - Can you provide a full Guru card dump (JSON export)?
   - All cards or only ones marked for public use?
   - Format for ingestion into vector DB?

4. Request ID Handling:
   - Request ID format? (REQ-12345?)
   - How are they generated?
   - How to extract from natural language?
```

---

## Next Steps (Specific Actions)

### **TODAY/THIS WEEK:**
1. ✅ Read and understand all three documents (DONE)
2. ✅ Create Intent Taxonomy Python data structure
3. ✅ Implement scope enforcement module  
4. ✅ Implement intent classifier (13 categories)
5. ✅ Implement intent router
6. ✅ Write unit tests for each

### **NEXT WEEK:**
7. Send questions to Vivli (API, metadata, Guru access)
8. Start Phase 4 stories (if time)
9. Mock the API responses (don't wait for real API)
10. Set up integration test harness

---

## Conclusion

**These documents are GOLD.** They provide everything needed to implement a production-ready intent classification system. The only missing pieces are:
- API endpoint details (will come from Vivli)
- Live Guru card content (will come from Vivli)
- Real chat metadata (will come from platform integration)

**But we can start building the core logic TODAY without any of those!**
