# Stories We Can Implement NOW (Without CSV/API)

## Quick Analysis

| Story | CSV Needed? | API Needed? | Chat Context Needed? | Can Do Now? | Effort |
|-------|-----------|-----------|----------------------|-----------|--------|
| **US-01** | ❌ No | ❌ No | ✅ YES | ✅ YES | 3-5 days |
| **US-02** | ❌ No | ❌ No | ✅ YES | ✅ YES | 2-3 days |
| **US-03** | ❌ No | ❌ No | ✅ YES | ✅ YES | 3-4 days |
| **US-04** | ❌ No | ❌ No | ❌ No | ✅ YES | 5-7 days |
| **US-05** | ❌ No | ❌ No | ❌ No | ✅ YES | 2-3 days |
| **US-06** | ❌ No | ❌ No | ❌ No | ✅ YES | 5-8 days |
| **US-07** | ✅ YES | ❌ No | ❌ No | ❌ NO | - |
| **US-08** | ✅ YES | ❌ No | ❌ No | ❌ NO | - |
| **US-09** | ❌ No | ✅ YES | ✅ YES | ❌ NO | - |
| **US-10** | ❌ No | ❌ No | ❌ No | ✅ YES (improve) | 1-2 days |
| **US-11** | ❌ No | ❌ No | ❌ No | ✅ YES | 5-7 days |

---

## Stories We CAN Do NOW (7 Stories)

### ✅ **US-01: Restrict Chat Scope** (5 days)
**What**: Only respond in specific chat channels during specific stages

**Why we can do this now**:
- Doesn't need CSV
- Doesn't need API
- Need to understand: What chat metadata is available in the system?

**What we need to ask Vivli**:
```
1. What chat types exist in the system?
   → open_chat, contributors_chat, requestor_chat, private_org_chat, etc.

2. What request stages exist?
   → draft, revision, form_check, approved, rejected, etc.

3. How do we access this info from a message?
   → message.chat_type?
   → message.request_stage?
   → message.metadata?
```

**Implementation approach**:
```python
def should_respond_to_message(message):
    # Check chat type
    if message.chat_type not in ['open_chat']:
        return False, "Chat not eligible"
    
    # Check stage
    if message.request_stage not in ['draft', 'revision', 'form_check']:
        return False, "Request stage not eligible"
    
    return True, "OK to respond"
```

**Files to modify**:
- `main.py` - Add scope check before processing
- `models.py` - Add ChatMessage fields for chat_type, request_stage

---

### ✅ **US-02: Respond Only to Research Team** (2-3 days)
**What**: Ignore messages from admins, bots, contributors, etc. Only answer researchers.

**Why we can do this now**:
- Doesn't need CSV
- Doesn't need API
- Need to understand: What user roles exist?

**What we need to ask Vivli**:
```
1. What user roles exist?
   → researcher, team_member, vivli_admin, data_contributor, org_admin, system, etc.

2. Which roles should get bot responses?
   → Only: researcher, team_member

3. How do we get user role from message?
   → message.sender_role?
   → message.user_id → lookup role?
```

**Implementation approach**:
```python
def is_eligible_user(message):
    eligible_roles = ['researcher', 'team_member', 'data_request_creator']
    return message.sender_role in eligible_roles
```

**Files to modify**:
- `main.py` - Add role check
- `models.py` - Add sender_role field

---

### ✅ **US-03: Handle Back-to-Back Messages** (3-4 days)
**What**: Group consecutive messages sent within 1 minute as same conversation

**Why we can do this now**:
- Doesn't need CSV
- Doesn't need API
- Pure Python logic

**How it works**:
```
User sends at 10:00:00 - "What is a data request?"
User sends at 10:00:30 - "How long does it take?"
User sends at 10:05:00 - "Something else"

GROUP 1 (conversation context):
  - "What is a data request?"
  - "How long does it take?"

GROUP 2 (new conversation):
  - "Something else"
```

**Implementation approach**:
```python
class MessageGrouper:
    def __init__(self, time_window_seconds=60):
        self.time_window = time_window_seconds
    
    def group_messages(self, messages):
        """Group messages by time proximity"""
        groups = []
        current_group = []
        
        for msg in messages:
            if not current_group:
                current_group.append(msg)
            else:
                time_diff = msg.timestamp - current_group[-1].timestamp
                
                if time_diff <= self.time_window:
                    current_group.append(msg)  # Same group
                else:
                    groups.append(current_group)  # New group
                    current_group = [msg]
        
        if current_group:
            groups.append(current_group)
        
        return groups

def combine_group_context(message_group):
    """Combine multiple messages into single context"""
    combined = {
        'original_messages': message_group,
        'combined_text': '\n'.join([m.text for m in message_group]),
        'intent': classify_combined_intent(message_group),
        'context': get_conversation_context(message_group)
    }
    return combined
```

**Files to modify**:
- Create `message_grouper.py` (new)
- Update `main.py` - Group messages before processing
- Update `models.py` - Track message timestamps

---

### ✅ **US-04: Consolidate Multiple Questions** (5-7 days)
**What**: Handle "Q1? Q2? Q3?" in one message and return consolidated answer

**Why we can do this now**:
- Doesn't need CSV
- Doesn't need API
- LLM can decompose questions

**How it works**:
```
User: "What is a data request? How long does it take? What are the steps?"

1. Use LLM to identify 3 separate questions:
   - "What is a data request?"
   - "How long does it take?"
   - "What are the steps?"

2. Answer each separately:
   - "A data request is..."
   - "Typically 2-4 weeks"
   - "The steps are: 1) Submit form 2) Form check 3)..."

3. Consolidate:
   - "Great questions! Here are the answers:\n\n
      1. A data request is...\n\n
      2. Typically 2-4 weeks\n\n
      3. The steps are..."
```

**Implementation approach**:
```python
class QueryDecomposer:
    def decompose_query(self, query):
        """Use LLM to split multiple questions"""
        prompt = f"""
        Identify all separate questions in this query.
        Return one question per line.
        
        Query: {query}
        
        Questions:
        """
        questions = llm.generate(prompt)
        return [q.strip() for q in questions.split('\n') if q.strip()]

class ConsolidatedResponseGenerator:
    def generate(self, original_query, answer_dict):
        """Create one consolidated response"""
        prompt = f"""
        The user asked multiple questions:
        {original_query}
        
        Here are the answers:
        {answer_dict}
        
        Create a single, well-organized response that addresses all questions.
        """
        consolidated = llm.generate(prompt)
        return consolidated
```

**Files to modify**:
- Create `query_decomposer.py` (new)
- Create `response_consolidator.py` (new)
- Update `main.py` - Decompose, answer, consolidate

---

### ✅ **US-05: Graceful Edge Case Handling** (2-3 days)
**What**: Detect invalid inputs and return friendly error instead of answering

**Edge cases to handle**:
```
✗ Blank message: "   "
✗ Too short: "ok"
✗ Too long: 500+ word pasted document
✗ HTML/Code: "<script>alert('hi')</script>"
✗ Non-English: "Hola, ¿qué es esto?"
✗ Spam/Emojis: "😂😂😂🎉🎉🎉"
✗ Offensive: [profanity/hate speech]
✗ Wrong request ID: "What's status of REQ-INVALID?"
✗ Not their request: "What's status of REQ-JOHN-123?" (user is Sarah)
```

**Implementation approach**:
```python
class InputValidator:
    def validate(self, message_text, sender_id):
        errors = []
        
        # Check: Not blank
        if not message_text or message_text.isspace():
            return False, "blank_message"
        
        # Check: Length
        word_count = len(message_text.split())
        if word_count < 2:
            return False, "too_short"
        if word_count > 500:
            return False, "too_long"
        
        # Check: No HTML/code
        if self.contains_html(message_text):
            return False, "html_detected"
        
        # Check: Language (if detectable)
        if self.detect_language(message_text) != 'english':
            return False, "non_english"
        
        # Check: Not spam
        if self.is_spam(message_text):
            return False, "spam_detected"
        
        # Check: Valid request IDs (if mentioned)
        request_ids = self.extract_request_ids(message_text)
        for req_id in request_ids:
            if not self.is_valid_request_id(req_id):
                return False, f"invalid_request_id_{req_id}"
            if not self.user_owns_request(sender_id, req_id):
                return False, f"not_your_request_{req_id}"
        
        return True, None

def handle_validation_error(error_type):
    standard_response = """I'm sorry, but I couldn't understand your question. 
                          Please rephrase and send it again."""
    return standard_response
```

**Files to modify**:
- Create `input_validator.py` (new)
- Update `main.py` - Validate before processing

---

### ✅ **US-06: Parse Chat Attachments** (5-8 days)
**What**: Extract text from PDFs, images, documents uploaded in chat

**Why this takes time**:
- Need to handle different file types
- Need OCR for images
- Need PDF extraction
- Need DOCX/XLSX parsing

**Implementation approach**:
```python
class AttachmentParser:
    def parse_attachment(self, file_path):
        """Extract text from any file type"""
        file_ext = self.get_file_extension(file_path)
        
        if file_ext == 'pdf':
            return self.parse_pdf(file_path)
        elif file_ext in ['png', 'jpg', 'jpeg']:
            return self.parse_image(file_path)
        elif file_ext == 'docx':
            return self.parse_docx(file_path)
        elif file_ext == 'xlsx':
            return self.parse_xlsx(file_path)
        elif file_ext == 'txt':
            return self.parse_text(file_path)
        else:
            return None, "unsupported_file_type"
    
    def parse_pdf(self, file_path):
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    def parse_image(self, file_path):
        import pytesseract
        from PIL import Image
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    
    def parse_docx(self, file_path):
        from docx import Document
        doc = Document(file_path)
        text = '\n'.join([p.text for p in doc.paragraphs])
        return text
```

**Dependencies to install**:
```
pip install PyPDF2
pip install pytesseract pillow
pip install python-docx
pip install openpyxl
```

**Files to modify**:
- Create `attachment_parser.py` (new)
- Update `main.py` - Parse attachments, add to context

---

### ✅ **US-10: Improve FAQ/Knowledge Base Responses** (1-2 days)
**What**: Make knowledge base responses better (already partially working)

**Current status**: ✅ Working but can improve

**Improvements**:
1. Better document ranking (currently just relevance score)
2. Combine multiple documents better
3. Add "related questions" suggestions
4. Improve citation formatting
5. Handle conflicting information from multiple docs

**Implementation approach**:
```python
def improve_faq_response(query, documents):
    # Current: Just search and use top 3 docs
    # Improved: 
    
    # 1. Rank documents by relevance + authority
    ranked = rank_documents_by_quality(documents)
    
    # 2. Extract only relevant sections (not whole doc)
    excerpts = extract_relevant_excerpts(ranked[:3], query)
    
    # 3. Generate answer from excerpts
    answer = llm.generate_faq_response(query, excerpts)
    
    # 4. Add related questions
    related = generate_related_questions(query)
    
    # 5. Better citations with section links
    citations = format_citations_with_links(ranked[:3])
    
    return {
        'answer': answer,
        'citations': citations,
        'related_questions': related,
        'confidence': calculate_response_confidence(ranked)
    }
```

**Files to modify**:
- `retrieval.py` - Improve ranking, excerpt extraction
- `llm.py` - Add related questions generation
- `response_formatter.py` - Better citation formatting

---

### ✅ **US-11: Model Benchmarking (Spike)** (5-7 days)
**What**: Benchmark GPT-4o-mini against alternatives (Phi-4, Mistral, etc.)

**Why we can do this now**:
- Doesn't need CSV
- Doesn't need external API
- We have the infrastructure (Azure OpenAI already set up)

**How benchmarking works**:
```
1. Create Golden Dataset (100+ representative Q&A pairs)
   - Use existing chat transcripts/FAQs as reference
   - Cover all intent types

2. For each LLM candidate:
   - Run all 100 queries
   - Get responses
   - Score on: accuracy, hallucination, relevance

3. Compare metrics:
   - Response quality (0-10 scale)
   - Hallucination score (% false info)
   - Token usage (cost per query)
   - Response time

4. Document findings:
   - Which model is best for FAQ?
   - Which model is best for data request?
   - Which model offers best cost/quality?
```

**Implementation approach**:
```python
class ModelBenchmarker:
    def benchmark_model(self, model_name, golden_dataset):
        """Test model against golden dataset"""
        results = {
            'model': model_name,
            'total_tests': len(golden_dataset),
            'scores': [],
            'hallucination_rate': 0,
            'avg_tokens': 0,
            'avg_latency': 0,
        }
        
        for test_case in golden_dataset:
            query = test_case['query']
            expected = test_case['expected_answer']
            
            # Run test
            response = self.call_model(model_name, query)
            
            # Score response
            accuracy = self.score_accuracy(response, expected)
            hallucination = self.detect_hallucination(response, expected)
            tokens = response['usage']['total_tokens']
            
            results['scores'].append(accuracy)
            results['total_tokens'] += tokens
        
        # Calculate aggregate metrics
        results['accuracy'] = sum(results['scores']) / len(results['scores'])
        results['avg_tokens'] = results['total_tokens'] / len(results['scores'])
        
        return results

def compare_models(benchmark_results):
    """Compare all models and recommend best"""
    # Score on: accuracy + cost + speed
    for result in benchmark_results:
        overall_score = (
            result['accuracy'] * 0.5 +  # Accuracy weight
            (1 - result['hallucination_rate']) * 0.3 +  # Hallucination weight
            (1 - result['avg_tokens']/500) * 0.2  # Cost weight
        )
        result['overall_score'] = overall_score
    
    # Rank by overall score
    sorted_results = sorted(benchmark_results, key=lambda x: x['overall_score'], reverse=True)
    return sorted_results
```

**Files to create**:
- Create `model_benchmarker.py` (new)
- Create `golden_dataset.json` (test data)

---

## Stories We CANNOT Do Yet (4 Stories)

### ❌ **US-07: Classify Intent** - BLOCKED by CSV
Waiting for: Intent Taxonomy CSV from Vivli

### ❌ **US-08: Route Based on Intent** - BLOCKED by US-07
Depends on: US-07 to work first

### ❌ **US-09: Answer Data Request Queries** - BLOCKED by API
Waiting for: 
- Data Request API documentation
- API endpoint details
- Authentication method
- Request/response format

---

## Implementation Roadmap (No CSV/API)

### **Week 1: Core Input Handling**
- **US-01** (3-5 days): Chat scope enforcement
- **US-02** (2-3 days): Role-based access control

### **Week 2: Message Processing**
- **US-03** (3-4 days): Message grouping
- **US-04** (5-7 days): Query decomposition & consolidation
- **US-05** (2-3 days): Input validation

### **Week 3: File & Response Handling**
- **US-06** (5-8 days): Attachment parsing
- **US-10** (1-2 days): Improve FAQ responses

### **Week 4: Technical Work**
- **US-11** (5-7 days): Model benchmarking

---

## Dependencies & Questions for Vivli

### 🔴 CRITICAL - Ask ASAP:

1. **For US-01 & US-03**:
   ```
   - What chat types exist in your system?
   - What request stages exist?
   - How do we get chat_type and request_stage from a message?
   - Sample message JSON structure?
   ```

2. **For US-02**:
   ```
   - What user roles exist?
   - How do we get sender_role from a message?
   - Sample user roles list?
   ```

3. **For US-09** (when ready):
   ```
   - Data Request API endpoint
   - API authentication method
   - Sample request/response JSON
   - Request ID format
   ```

4. **For US-07** (when ready):
   ```
   - Intent Taxonomy CSV
   - Official intent categories
   - Keywords for each intent
   ```

### 🟡 OPTIONAL - Nice to have:
- Sample message data (real or fake) for testing
- Sample request data structure
- Chat metadata fields available
- User permission/role hierarchy

---

## Total Effort (All Implementable Stories)

| Story | Days |
|-------|------|
| US-01 | 3-5 |
| US-02 | 2-3 |
| US-03 | 3-4 |
| US-04 | 5-7 |
| US-05 | 2-3 |
| US-06 | 5-8 |
| US-10 | 1-2 |
| US-11 | 5-7 |
| **Total** | **27-39 days** |

**Estimate: ~4-5 weeks for one developer**

---

## Which Story Should We Start With?

### Recommended Priority Order:

1. **US-05 first** (2-3 days)
   - Quick win
   - Foundational (all other features need good input)
   - Builds confidence

2. **US-01 & US-02** (5-8 days total)
   - Gate logic (must know chat/role before responding)
   - Blocking other features

3. **US-03** (3-4 days)
   - Message grouping infrastructure
   - Needed before decomposition

4. **US-04** (5-7 days)
   - Query decomposition
   - High impact on UX

5. **US-06** (5-8 days)
   - File parsing
   - Good to have but lower priority

6. **US-10** (1-2 days)
   - Improve existing FAQ
   - Quick improvement to current system

7. **US-11** (5-7 days)
   - Model benchmarking
   - Technical work, not user-facing

---

## Ready to Start?

**Which story should we implement first?** I recommend starting with **US-05** (input validation) since it's quick and will make all other features more robust.

Do you want me to start implementing any of these?
