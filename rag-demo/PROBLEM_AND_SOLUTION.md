# Problem Analysis & Solution Report

## Executive Summary

**Problem**: Chatbot returned "couldn't find a reliable answer" error for ALL queries, despite having indexed documents.

**Root Causes**: 4 cascading issues in confidence thresholds, intent classification, response logic, and context sizing.

**Solution**: Applied targeted fixes to each layer. **System now works correctly.**

---

## Problem Details

### User Report
> "Whatever I write it gives error messages"

### Example Query & Response
```
INPUT:  "what are the things you can answer"

OUTPUT: "I'm sorry, but I couldn't find a reliable answer to your question 
         in our knowledge base. I've forwarded your question to a Vivli 
         Administrator..."
         
STATUS: ❌ Escalation message (wrong!)
```

### What Was Wrong
- Documents **WERE being retrieved** (5 documents with relevance score 38+)
- LLM **COULD have generated** an answer
- But system returned generic escalation message instead

---

## Root Cause Analysis

### Issue #1: Overly Strict Confidence Thresholds
**Location**: `config.py`

**The Problem**:
```python
CONFIDENCE_THRESHOLD = 0.6        # Too strict
INTENT_HIGH_CONFIDENCE = 0.25     # Too strict
```

**Impact**: 
- Query gets marked as HYBRID intent (confidence = 0.19)
- Threshold check: 0.19 > 0.3? NO
- Result: Documents ignored, escalation returned

**The Fix**:
```python
CONFIDENCE_THRESHOLD = 0.3        # More realistic
INTENT_HIGH_CONFIDENCE = 0.15     # More realistic
```

---

### Issue #2: Brittle Keyword Intent Classifier
**Location**: `intent_classifier.py`

**The Problem**:
Query: "what are the things you can answer"
- "what" keyword exists? YES
- "things" keyword exists? NO
- "answer" keyword exists? NO
- Score: 1/43 keywords = very low

Result: HYBRID intent with low confidence (0.19)

**The Fix**:
```python
# Added minimum baseline score for real queries
if len(text) > 15:  # Meaningful question
    score = max(score, 0.12)  # Minimum FAQ score
```

Now: Query length > 15 chars → score ≥ 0.12 = caught as FAQ

---

### Issue #3: Confidence Gate in Hybrid Handler
**Location**: `main.py` line 275

**The Problem**:
```python
# In _handle_hybrid():
if documents and classification_confidence > CONFIDENCE_THRESHOLD:  # 0.19 > 0.3? NO!
    # Use knowledge base...
else:
    return format_escalation_response()  # This runs!
```

**Impact**:
- Documents retrieved ✓
- But confidence (0.19) < threshold (0.3)
- → Escalation response returned (wrong!)

**The Fix**:
```python
# Changed to:
if documents:  # If we have documents, USE THEM
    context = retrieval.format_for_llm(documents)
    result = await llm_client.generate_faq_response(query, context)
    # ...
```

**Rationale**: If documents can answer the question, confidence score shouldn't block using them.

---

### Issue #4: Context Too Large for LLM
**Location**: `retrieval.py` - `format_for_llm()`

**The Problem**:
Documents being formatted included:
- 18MB JSON file (full chat export)
- 380-row CSV file (all rows)
- Multiple large DOCX files (full content)

Total: **54MB of text** passed to LLM

**Error from Azure OpenAI**:
```
400 Bad Request
"string too long. Expected maximum 10485760 bytes, got 54319633"
```

**The Fix**:
```python
def format_for_llm(self, documents, max_tokens: int = 2000):
    """Format documents with size limits"""
    max_chars = max_tokens * 250  # ~500KB total
    
    for doc in documents:
        # Truncate each document
        content = doc.content[:2000]  # Max 2000 chars per doc
        if len(doc.content) > 2000:
            content += "\n[Content truncated...]"
        
        # Stop adding if we exceed limit
        if current_size + len(doc_text) > max_chars:
            break
```

**Result**: Manageable context (~500KB) sent to LLM

---

## Solution Applied

### Configuration Changes
```python
# config.py
CONFIDENCE_THRESHOLD = 0.3          # was 0.6
RELEVANCE_THRESHOLD = 0.1           # was 0.2
INTENT_HIGH_CONFIDENCE = 0.15       # was 0.25
INTENT_LOW_CONFIDENCE = 0.05        # was 0.1
INTENT_MULTI_THRESHOLD = 0.08       # was 0.2
```

### Code Changes
| File | Change | Impact |
|------|--------|--------|
| `config.py` | Lower thresholds | Documents no longer filtered out |
| `intent_classifier.py` | Add minimum score | Non-keyword queries recognized |
| `main.py` | Remove confidence gate | Documents used when available |
| `retrieval.py` | Add truncation | LLM gets manageable context |

---

## Verification

### Test Case 1: Original Failing Query ✅
```
Query: "what are the things you can answer"

BEFORE:
- Answer: Escalation message (generic)
- Sources: 3 documents (ignored)
- Confidence: 0.18

AFTER:
- Answer: "As your Vivli platform assistant, I can help answer 
           questions related to the data request process..."
- Sources: 3 relevant documents (used)
- Confidence: 0.19
```

### Test Case 2: Domain-Specific Question ✅
```
Query: "what is data request"

Response: "A data request on the Vivli platform refers to a proposal 
          submitted by researchers seeking access to specific datasets 
          for their research purposes..."
```

### Test Case 3: Process Question ✅
```
Query: "how do I submit a data request"

Response: "You should fill out a detailed form that outlines the 
          objectives of the research, the data needed, and any 
          relevant information about the research team..."
```

---

## System Flow (Fixed)

```
User Query
    ↓
1. Classify Intent (keyword-based)
    ↓
2. Embed Query & Retrieve Documents (keyword search)
    ↓
3. Filter by Relevance (threshold 0.1)
    ↓
4. Format for LLM (truncated to ~500KB)
    ↓
5. Generate Response (via gpt-4o-mini)
    ├─ If documents found → Use knowledge base ✓
    └─ If no documents → Escalate or LLM fallback
    ↓
6. Format Response (with sources & disclaimer)
    ↓
Response to User
```

---

## Key Takeaways

| Issue | Severity | Status |
|-------|----------|--------|
| Confidence thresholds too strict | 🔴 Critical | ✅ Fixed |
| Intent classifier brittle | 🟡 Medium | ✅ Fixed |
| Hybrid handler confidence gate | 🔴 Critical | ✅ Fixed |
| Context too large for LLM | 🔴 Critical | ✅ Fixed |

**Result**: System now properly answers questions using indexed knowledge base.

---

## Remaining Limitations

1. **No semantic search** - Still keyword-based (Azure Search SDK limitation)
2. **No conversation history** - Each query independent
3. **Document truncation** - Large documents limited to 2000 chars
4. **Keyword-based intent** - Could use LLM for better classification

---

## Next Steps

1. ✅ System operational - queries answered correctly
2. 🔄 (Optional) Implement semantic/vector search for better matching
3. 🔄 (Optional) Add LLM-based intent classification
4. 🔄 (Optional) Implement conversation history tracking

---

**Status**: 🟢 **FIXED** - Chatbot now properly answers questions using knowledge base
