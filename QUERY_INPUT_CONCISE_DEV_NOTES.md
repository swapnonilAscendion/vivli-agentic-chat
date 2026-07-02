# QUERY INPUT - CONCISE DEV NOTES (For FRD)

## INTENT CLASSIFICATION CHECKS

### Check 1.1: Basic Message Classification
**rule_id:** query_input.intent_classification.basic_classification  
**User Story:** US-07

```
Input: researcher_message.query_text (string)

Logic:
  if (message is empty/null):
    return {intent: "UNKNOWN", confidence: 0.0, action: "return_error"}
  
  faq_score = keyword_match(text, ["how", "what", "process", "policy"]) + semantic_similarity(text, "How to submit data request")
  data_request_score = keyword_match(text, ["status", "my request", "feedback"]) + semantic_similarity(text, "Status of my request")
  escalation_score = keyword_match(text, ["help", "escalate", "human"])
  
  if (faq_score > 0.7 && data_request_score < 0.3):
    return {intent: "FAQ", confidence: faq_score, action: "route_to_kb"}
  elif (data_request_score > 0.7 && faq_score < 0.3):
    return {intent: "DATA_REQUEST_RELATED", confidence: data_request_score, action: "route_to_api"}
  elif (escalation_score > 0.7):
    return {intent: "ESCALATION", confidence: escalation_score, action: "escalate"}
  elif (faq_score > 0.5 && data_request_score > 0.5):
    return {intent: "HYBRID", confidence: max(faq_score, data_request_score), action: "api_then_kb"}
  else:
    return {intent: "UNKNOWN", confidence: max(scores), action: "escalate"}

Output: {query_id, intent, confidence_score, all_scores, action}
```

---

### Check 1.2: Multi-Intent Detection
**rule_id:** query_input.intent_classification.multi_intent_detection  
**User Stories:** US-03, US-04

```
Input: classification_result from Check 1.1

Logic:
  if (faq_score > 0.5 && data_request_score > 0.5):
    questions = parse_message_into_separate_questions(message_text)
    return {
      type: "MULTIPLE_QUESTIONS",
      question_count: questions.length,
      handling: "consolidate_into_one_response"
    }
  else:
    return {type: "SINGLE_INTENT"}

Output: {multi_intent_detected, question_count, handling_strategy}
```

---

### Check 1.3: Taxonomy Compliance
**rule_id:** query_input.intent_classification.taxonomy_compliance

```
Valid intent categories: [FAQ, DATA_REQUEST_RELATED, ESCALATION, UNKNOWN, HYBRID]

Logic:
  if (classification_result.intent NOT IN valid_categories):
    return {error: "Invalid intent", action: "escalate"}
  else:
    return {status: "valid", intent: classification_result.intent}
```

---

### Check 1.4: Routing Decision
**rule_id:** query_input.intent_classification.routing_decision  
**User Story:** US-08

```
Input: classification_result.intent

Routing Table:
  FAQ → route_to: "knowledge_base_retrieval"
  DATA_REQUEST_RELATED → route_to: "data_request_api_integration"
  HYBRID → route_to: "api_first_then_kb"
  ESCALATION → route_to: "escalation_handler"
  UNKNOWN → route_to: "escalation_handler"

Output: {routing_decision, component, action}
```

---

## CHAT SCOPE CHECKS

### Check 2.1: Open Chat Validation
**rule_id:** query_input.scope.chat_type_validation  
**User Story:** US-01

```
Input: message_metadata.chat_type

Logic:
  if (chat_type == "open_chat"):
    return {valid: true, action: "proceed"}
  else (chat_type in ["contributors_chat", "requestor_chat", "private_org_chat"]):
    return {valid: false, action: "do_not_respond"}
```

---

### Check 2.2: Eligible Stage Validation
**rule_id:** query_input.scope.stage_validation  
**User Story:** US-01

```
Input: data_request.current_stage, data_request.human_validation_started

Eligible stages: [draft, revision, vivli_form_check (before human takes over)]
Ineligible stages: [review, approved, rejected, completed, withdrawn]

Logic:
  if (stage in [draft, revision]):
    return {valid: true, action: "proceed"}
  elif (stage == vivli_form_check && !human_validation_started):
    return {valid: true, action: "proceed"}
  elif (stage == vivli_form_check && human_validation_started):
    return {valid: false, action: "do_not_respond"}
  else (stage in ineligible_stages):
    return {valid: false, action: "do_not_respond"}
```

---

### Check 2.3: User Role Validation
**rule_id:** query_input.scope.user_role_validation  
**User Story:** US-02

```
Input: message.sender_user_role

Valid roles: [data_request_creator, research_team_member]
Invalid roles: [vivli_admin, org_admin, data_uploader, automated_notification, irp_member]

Logic:
  if (role in valid_roles):
    return {valid: true, action: "proceed"}
  else (role in invalid_roles):
    return {valid: false, action: "do_not_respond"}
```

---

## MESSAGE VALIDATION CHECKS

### Check 3.1: Blank/Empty Messages
**rule_id:** query_input.validation.blank_message_handling  
**User Story:** US-05

```
Input: message.text

Logic:
  if (text == null || text == "" || text.strip() == ""):
    return {valid: false, action: "return_error_message"}
  elif (len(text.strip()) < 2):
    return {valid: false, action: "return_error_message"}
  else:
    return {valid: true, action: "proceed", cleaned_text: text.strip()}
```

---

### Check 3.2: Message Length Limits
**rule_id:** query_input.validation.message_length_limits  
**User Story:** US-05

```
Input: message.text

Length thresholds:
  warning: 1000 chars
  error: 2000 chars (500+ words)

Logic:
  if (len(text) > 2000):
    return {valid: false, action: "return_guidance"}
  elif (len(text) > 1000):
    return {valid: true, action: "proceed_with_caution"}
  else:
    return {valid: true, action: "proceed_normally"}
```

---

### Check 3.3: Special Content (HTML/Code/Emoji)
**rule_id:** query_input.validation.special_content_handling  
**User Story:** US-05

```
Input: message.text

Logic:
  has_html = detect_html_tags(text)
  has_code = detect_code_syntax(text)
  has_excessive_emoji = emoji_count / word_count > 0.3
  has_special_chars_only = is_special_chars_only(text)
  
  if (has_html || has_code):
    return {valid: false, action: "return_guidance"}
  elif (has_excessive_emoji || has_special_chars_only):
    return {valid: false, action: "return_error_message"}
  else:
    return {valid: true, cleaned_text: sanitize(text)}
```

---

### Check 3.4: Non-English Messages
**rule_id:** query_input.validation.language_detection  
**User Story:** US-05

```
Input: message.text

Logic:
  detected_language = detect_language(text)
  confidence = language_detection_confidence
  
  if (detected_language == "en" && confidence > 0.8):
    return {valid: true, action: "proceed"}
  elif (detected_language != "en" && confidence > 0.7):
    return {valid: false, action: "return_language_error"}
  else:
    return {valid: true, action: "proceed", note: "low_confidence"}
```

---

### Check 3.5: Attachment Parsing
**rule_id:** query_input.validation.attachment_handling  
**User Story:** US-06

```
Input: message.text, message.attachments[]

Logic:
  if (no text && has attachments):
    for each attachment:
      if (file_size < 10MB && file_type in [pdf, txt, docx, xlsx, csv]):
        extracted_content = parse_attachment(attachment)
      query_text_final = extracted_content
  elif (has text && has attachments):
    query_text_final = text + extracted_attachment_content
  else:
    query_text_final = text
  
  return {query_text_final, attachments_parsed: []}
```

---

### Check 3.6: Content Safety & Vivli Relevance
**rule_id:** query_input.validation.content_safety_check  
**User Story:** US-05

```
Input: message.text

Logic:
  safety_result = azure_ai_content_filtering.check(text)
  
  if (safety_result.hate_speech > 0.8 || violence > 0.8 || sexual > 0.8 || self_harm > 0.8):
    return {valid: false, action: "do_not_respond", log_for_admin: true}
  
  vivli_relevance_score = keyword_match(text, vivli_keywords) + semantic_similarity(text, "Vivli data sharing")
  
  if (!vivli_related):
    return {valid: false, action: "return_off_topic_message"}
  else:
    return {valid: true, action: "proceed"}
```

---

## VALIDATION FLOW DIAGRAM

```
Message → [Check 2.1: Chat Type] → [Check 2.2: Stage] → [Check 2.3: Role]
  ↓ (all pass)
[Check 3.1: Blank] → [Check 3.2: Length] → [Check 3.3: Special Content]
  ↓ (all pass)
[Check 3.4: Language] → [Check 3.5: Attachments] → [Check 3.6: Safety/Relevance]
  ↓ (all pass)
[Check 1.1: Intent Classification] → [Check 1.2: Multi-Intent] → [Check 1.3: Taxonomy] → [Check 1.4: Routing]
  ↓
Route to appropriate handler (KB, API, or Escalation)
```

---

## CONCISE ACCEPTANCE CRITERIA

✓ All 14 checks implemented  
✓ Confidence scores provided for classification  
✓ Multi-intent queries handled  
✓ All user stories (US-01 to US-06) satisfied  
✓ Error messages returned for invalid inputs  
✓ Scope validation enforced (chat type, stage, role)  
✓ Message sanitization applied  
✓ Attachments parsed  
✓ Content safety checked  
✓ Intent routed to correct handler
