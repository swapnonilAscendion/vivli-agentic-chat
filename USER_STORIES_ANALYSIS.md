# Vivli Chatbot - User Stories Analysis

## Overview
11 user stories + 1 technical spike define the chatbot's functionality. These stories describe what the system MUST do from user and technical perspectives.

---

## User Stories Breakdown

### TIER 1: INPUT HANDLING & SCOPE (Stories 1-6)
These stories focus on **controlling WHEN and FROM WHOM the bot responds**.

#### US-01: Restrict Chat Scope
**Story**: Respond only in specific chat channels at specific stages
- **Scope**: Open chat during DRAFT/REVISION or FORM-CHECK stages only
- **NOT in**: Contributors chat, Requestor chat, Private Org chat
- **NOT after**: Form-check completion
- **Impact**: Bot must know context of chat and data request stage
- **Current Status**: ❌ NOT IMPLEMENTED

#### US-02: Respond Only to Research Team
**Story**: Ignore non-research-team users (admins, bots, contributors, etc.)
- **Must identify**: Research team members vs. others
- **Must ignore**: Vivli Admins, automated notifications, data contributors, org admins, IRP
- **Impact**: Bot needs role/permission validation
- **Current Status**: ❌ NOT IMPLEMENTED

#### US-03: Handle Back-to-Back & Multi-Context Messages
**Story**: Treat consecutive messages as context + separate unrelated topics
- **Group**: Multiple messages within 1 minute as one context
- **Separate**: Messages with different intents
- **Impact**: Need message grouping + context awareness
- **Current Status**: ❌ NOT IMPLEMENTED (single-message handling only)

#### US-04: Consolidate Multiple Questions
**Story**: Handle "Question 1? Question 2?" in one message
- **Process**: Query rewriting to separate questions
- **Output**: Single consolidated answer addressing each question
- **Impact**: Need query decomposition + multi-answer consolidation
- **Current Status**: ❌ NOT IMPLEMENTED

#### US-05: Graceful Edge Case Handling
**Story**: Handle invalid/unusual inputs without fabricating answers
- **Edge cases**: Blank messages, HTML/code pasting, non-English, emojis, spam, long messages (500+ words), wrong request IDs, form validation questions, etc.
- **Response**: Standard error: "I'm sorry, but I couldn't understand your question. Please rephrase and send it again."
- **Critical**: NEVER fabricate answers
- **Current Status**: ⚠️ PARTIALLY IMPLEMENTED (basic error handling exists, but not comprehensive)

#### US-06: Parse Chat Attachments
**Story**: Extract content from researcher-uploaded files
- **Actions**: Parse PDFs, images, documents in chat
- **Usage**: Use attachment content in response
- **Impact**: Need file parser integration
- **Current Status**: ❌ NOT IMPLEMENTED

---

### TIER 2: INTENT & ROUTING (Stories 7-8)
These stories focus on **UNDERSTANDING and ROUTING queries**.

#### US-07: Classify Intent
**Story**: Detect what type of question the researcher is asking
- **Minimum categories**:
  - FAQ / General queries
  - Data request related queries
  - (May be more in Intent Taxonomy)
- **Multiple intents**: Single message can have multiple intents
- **Reference**: Vivli Intent Taxonomy (CSV to be provided)
- **Current Status**: ⚠️ PARTIALLY IMPLEMENTED
  - Have basic intent classification (FAQ, DATA_REQUEST, HYBRID, ESCALATION)
  - But not comprehensive per Taxonomy
  - Needs alignment with official taxonomy

#### US-08: Route Based on Intent
**Story**: Send each query to the right source
- **FAQ queries** → Vector database (knowledge base)
- **Data request queries** → Vivli data request API
- **Low confidence** → Escalate to human
- **Consistency**: Routing matches classification result
- **Current Status**: ⚠️ PARTIALLY IMPLEMENTED
  - Routing exists but may not handle all intent types correctly
  - No actual API integration (US-09 requirement)

---

### TIER 3: RESPONSE GENERATION (Stories 9-10)
These stories focus on **ANSWERING queries correctly**.

#### US-09: Answer Data Request Queries in Real Time
**Story**: Answer questions about the researcher's specific data request
- **Integration**: Connect to Vivli data request API
- **Process**:
  1. Correlate by request ID
  2. Fetch current data request form in real time
  3. Generate natural-language response
  4. Search knowledge base for context
- **Fallback**: If no KB answer → escalate to admin
- **Important**: NO message memory (fresh data on every query)
- **Example questions**:
  - "What's the status of my request?"
  - "When will my request be reviewed?"
  - "What stage is my form check at?"
- **Current Status**: ❌ NOT IMPLEMENTED
  - No API integration
  - No request ID handling
  - No real-time data request retrieval

#### US-10: Answer FAQ/Knowledge Base Queries
**Story**: Answer general questions with cited responses
- **Sources**: Platform FAQs, how-tos, AIML policies, templates, process guides
- **Search method**: Semantic search on vector database
- **Response quality**: 
  - Relevant and accurate
  - Plain language
  - Grounded in documents
  - NO fabrication
- **Citations**: Public URLs only (no internal Guru card links)
- **Confidence threshold**: Has minimum relevance requirement
- **Fallback**: No relevant doc → escalate to admin (not fabricate)
- **Current Status**: ✅ PARTIALLY WORKING (but needs improvement)
  - Vector DB has documents indexed
  - Semantic search working
  - Citations included
  - But document quality/relevance may need improvement

---

### TIER 4: TECHNICAL INFRASTRUCTURE (Story 11)
This is a technical spike for model selection.

#### US-11: Select & Benchmark LLM
**Story**: Choose the best LLM for Chat/RAG use case
- **Current baseline**: GPT-4o-mini (selected for accuracy + cost balance)
- **Sprint 2 work**:
  - Build Golden Dataset (representative Q&A)
  - Ingest into Azure AI Search
  - Benchmark candidates: Phi-4-mini, Mistral Small, GPT-5.4 mini
  - Evaluate on: hallucination, token economics
- **Outcome**: Document model selection decision
- **Current Status**: ✅ IN PROGRESS
  - Currently using GPT-4o-mini
  - Not yet benchmarked against alternatives

---

## Implementation Status Summary

| Story | Category | Title | Status | Notes |
|-------|----------|-------|--------|-------|
| US-01 | Input | Restrict scope to eligible chats/stages | ❌ Not done | Need chat context, stage awareness |
| US-02 | Input | Respond only to research team | ❌ Not done | Need role/permission validation |
| US-03 | Input | Handle back-to-back messages | ❌ Not done | Need message grouping, context tracking |
| US-04 | Input | Consolidate multiple questions | ❌ Not done | Need query decomposition |
| US-05 | Input | Graceful edge case handling | ⚠️ Partial | Basic error handling, needs expansion |
| US-06 | Input | Parse chat attachments | ❌ Not done | Need file parser |
| US-07 | Intent | Classify intent | ⚠️ Partial | Basic classification, needs Taxonomy alignment |
| US-08 | Routing | Route based on intent | ⚠️ Partial | Routes exist but incomplete |
| US-09 | Response | Answer data request queries | ❌ Not done | **CRITICAL** - Need API integration |
| US-10 | Response | Answer FAQ queries | ✅ Partial | Working but can improve |
| US-11 | Tech | Select/benchmark LLM | ✅ In progress | Currently GPT-4o-mini, needs benchmarking |

---

## Critical Gaps

### 🔴 BLOCKING (Must implement before production)
1. **US-01**: No chat scope enforcement (bot responds everywhere)
2. **US-02**: No role/permission checking (bot answers admins, bots)
3. **US-09**: NO API integration (can't answer data request status)
4. **US-07**: Intent classification not aligned with official Taxonomy

### 🟡 IMPORTANT (Should implement soon)
1. **US-03**: No back-to-back message handling
2. **US-04**: Can't consolidate multiple questions
3. **US-06**: No attachment parsing
4. **US-05**: Limited edge case handling

### 🟢 WORKING (Acceptable for MVP)
1. **US-10**: FAQ/KB responses working (with improvements)
2. **US-08**: Basic routing exists
3. **US-11**: Using reasonable baseline model

---

## What Needs to Change in Chatbot Code

### Priority 1: CRITICAL (Do First)
```
1. Add Vivli API integration (US-09)
   - Connect to data request API
   - Retrieve current request status by ID
   - Handle request validation

2. Add context/scope enforcement (US-01, US-02)
   - Know which chat the message is from
   - Know which stage the request is at
   - Know who is sending the message (role)
   - Only respond to eligible chats/users

3. Implement Intent Taxonomy (US-07)
   - Update classifier to use official taxonomy
   - Align all intent categories
```

### Priority 2: IMPORTANT (Do Next)
```
4. Message grouping & context (US-03)
   - Group back-to-back messages
   - Track context across messages
   - Separate unrelated intents

5. Query decomposition (US-04)
   - Split multiple questions
   - Answer each separately
   - Consolidate response

6. Attachment parsing (US-06)
   - Support PDF, images, docs
   - Extract text/data
   - Use in responses
```

### Priority 3: NICE-TO-HAVE (Do Later)
```
7. Comprehensive edge case handling (US-05)
   - Detect spam/offensive content
   - Handle non-English gracefully
   - Improve error messages

8. Model benchmarking (US-11)
   - Compare alternatives
   - Document findings
```

---

## Key Questions for Vivli Team

1. **Intent Taxonomy**: Where is the CSV with all intent categories?
2. **Chat Integration**: How do we get chat_id, stage_id, user_role from the platform?
3. **Data Request API**: What's the endpoint? Authentication? Request ID format?
4. **Knowledge Base**: Should we add more documents specific to data request process?
5. **Attachment Types**: Which file types should we support initially?
6. **Compliance**: Any data privacy/security requirements for storing request info?

---

## Recommendations

### ✅ What's Working Well
- Knowledge base (vector DB) indexed correctly
- FAQ responses generating answers
- Basic intent classification exists
- Error handling framework in place

### 🔧 What Needs Work
- **Missing**: Data request API integration (highest priority)
- **Missing**: Context/scope enforcement
- **Incomplete**: Intent classification (vs. official taxonomy)
- **Incomplete**: Query decomposition
- **Missing**: Attachment parsing

### 📊 Effort Estimate

| Story | Complexity | Days |
|-------|-----------|------|
| US-01 | Medium | 3-5 |
| US-02 | Medium | 2-3 |
| US-03 | Medium | 3-4 |
| US-04 | High | 5-7 |
| US-05 | Low | 2-3 |
| US-06 | High | 5-8 |
| US-07 | Medium | 3-4 |
| US-08 | Low | 1-2 |
| US-09 | High | 8-10 |
| US-10 | Low | 1-2 |
| US-11 | Medium | 5-7 |

**Total**: ~40-50 days for full implementation (~2 months with team)

---

## Next Steps

1. **Get Intent Taxonomy CSV** - Essential for US-07
2. **Get API Documentation** - Essential for US-09
3. **Get Chat Integration Details** - Essential for US-01, US-02, US-03
4. **Prioritize stories** with Vivli team based on MVP scope
5. **Start with US-09** (data request API) as it's highest impact
