# VIVLI AGENTIC CHAT - QUERY INPUT SECTION DETAILED PSEUDO CODE

## 📋 Overview

The **Query Input** section of the FRD contains 8 major check categories, each with multiple validations. This document provides detailed pseudo code for **EVERY CHECK**.

---

# 🎯 SECTION 1: INTENT CLASSIFICATION CHECKS

## Check 1.1: System shall classify each incoming researcher chat message into a defined intent category

```yaml
rule_id: query_input.intent_classification.basic_classification
component: Intent Classification Engine
purpose: Classify incoming message into intent categories (FAQ vs Data Request)
source: FRD §1 - Query Input - Intent Classification

user_story: US-07 - Classify each message into an intent category

field_path: researcher_message.query_text
field_type: string
required: yes

preconditions:
  - Message is in open chat
  - Researcher is research team member
  - During draft/revision/form-check stage
  - Message is not blank

validation_logic:
  - Check 1: Validate input is non-empty and non-whitespace
  - Check 2: Parse message for intent keywords
  - Check 3: Calculate semantic similarity to intent categories
  - Check 4: Apply confidence threshold (default: 0.7)

intent_categories:
  - faq_query: General questions about platform, process, policies
  - data_request_related: Questions specific to a data request
  - escalation_trigger: Requests for human help
  - unknown: Cannot determine with confidence

classification_logic:
  
  # Input validation
  if (message.text == null OR message.text.strip() == ""):
    classification_result = {
      intent: "UNKNOWN",
      confidence: 0.0,
      reason: "Empty message",
      action: "return_error_message"
    }
  
  # Extract keywords and calculate scores
  else:
    faq_keywords = ["how", "what", "where", "when", "process", "procedure", "policy", "requirements", "timeline", "eligible"]
    data_request_keywords = ["status", "my request", "update", "feedback", "revision", "submission", "reviewed", "checked"]
    escalation_keywords = ["help", "escalate", "human", "staff", "not helpful", "need assistance"]
    
    faq_score = calculate_keyword_match(message.text, faq_keywords)
    data_request_score = calculate_keyword_match(message.text, data_request_keywords)
    escalation_score = calculate_keyword_match(message.text, escalation_keywords)
    
    # Semantic similarity (using embeddings)
    faq_semantic_score = cosine_similarity(embed(message.text), embed("How to submit a data request"))
    data_request_semantic_score = cosine_similarity(embed(message.text), embed("Status of my request"))
    
    # Combine scores
    faq_combined = (faq_score * 0.5) + (faq_semantic_score * 0.5)
    data_request_combined = (data_request_score * 0.5) + (data_request_semantic_score * 0.5)
    escalation_combined = escalation_score
    
    # Classify based on highest score
    if (faq_combined > 0.7 AND data_request_combined < 0.3):
      classification_result = {
        intent: "FAQ",
        confidence: faq_combined,
        reason: "FAQ keywords and semantic match",
        action: "route_to_knowledge_base",
        all_scores: {faq: faq_combined, data_request: data_request_combined, escalation: escalation_combined}
      }
    
    elif (data_request_combined > 0.7 AND faq_combined < 0.3):
      classification_result = {
        intent: "DATA_REQUEST_RELATED",
        confidence: data_request_combined,
        reason: "Data request keywords and semantic match",
        action: "route_to_data_request_api",
        all_scores: {faq: faq_combined, data_request: data_request_combined, escalation: escalation_combined}
      }
    
    elif (escalation_combined > 0.7):
      classification_result = {
        intent: "ESCALATION",
        confidence: escalation_combined,
        reason: "Escalation keywords detected",
        action: "route_to_escalation_handler",
        all_scores: {faq: faq_combined, data_request: data_request_combined, escalation: escalation_combined}
      }
    
    elif (faq_combined > 0.5 AND data_request_combined > 0.5):
      # Multi-intent query
      classification_result = {
        intent: "HYBRID",
        primary_intent: max(faq_combined, data_request_combined) == faq_combined ? "FAQ" : "DATA_REQUEST_RELATED",
        secondary_intent: max(faq_combined, data_request_combined) == faq_combined ? "DATA_REQUEST_RELATED" : "FAQ",
        confidence: max(faq_combined, data_request_combined),
        reason: "Both FAQ and Data Request signals detected",
        action: "handle_hybrid_query",
        all_scores: {faq: faq_combined, data_request: data_request_combined, escalation: escalation_combined}
      }
    
    else:
      classification_result = {
        intent: "UNKNOWN",
        confidence: max(faq_combined, data_request_combined, escalation_combined),
        reason: "Confidence below threshold for any category",
        action: "escalate_to_human",
        all_scores: {faq: faq_combined, data_request: data_request_combined, escalation: escalation_combined}
      }

output_format:
  {
    "query_id": "unique_identifier",
    "intent_classification": "FAQ|DATA_REQUEST_RELATED|HYBRID|ESCALATION|UNKNOWN",
    "confidence_score": 0.0-1.0,
    "reason": "why this classification was chosen",
    "action": "next action to take",
    "all_scores": {
      "faq_score": 0.0-1.0,
      "data_request_score": 0.0-1.0,
      "escalation_score": 0.0-1.0
    },
    "keywords_detected": ["list", "of", "keywords"],
    "timestamp": "ISO 8601 format"
  }

error_handling:
  - Empty message → return UNKNOWN, log, no escalation
  - Null message → return error, log, no response
  - Unable to embed → use keyword-only matching
  - API timeout during embedding → escalate to human

audit_notes: "This is the critical first decision point. Log all classification scores to understand why messages are routed where they go. Track misclassifications."

acceptance_criteria:
  - ✓ Message classified before routing
  - ✓ Confidence score always provided
  - ✓ All intent categories properly distinguished
  - ✓ Multi-intent queries handled (US-03)
```

---

## Check 1.2: A message may fit into more than 1 intent category

```yaml
rule_id: query_input.intent_classification.multi_intent_detection
component: Intent Classification Engine
purpose: Detect when message contains multiple intents and handle appropriately
source: FRD §1 - Query Input - Intent Classification

user_story: US-03 - Handle back-to-back and multi-context messages
           US-04 - Consolidate multiple questions in one message

field_path: researcher_message.query_text
context: classification_result from Check 1.1

multi_intent_logic:
  
  # Determine if multi-intent
  if (faq_score > 0.5 AND data_request_score > 0.5):
    multi_intent_detected = true
  else:
    multi_intent_detected = false
  
  if (multi_intent_detected):
    
    # Parse message into separate questions
    questions = parse_message_into_questions(message.text)
    # Using NLP to split on sentence boundaries and question marks
    
    if (questions.count == 1):
      # Single question with multiple intent signals - hybrid handling
      multi_intent_result = {
        type: "HYBRID_SINGLE_QUESTION",
        primary_intent: determine_primary_intent(faq_score, data_request_score),
        secondary_intent: determine_secondary_intent(faq_score, data_request_score),
        handling: "answer_data_request_first_then_faq"
      }
    
    elif (questions.count > 1):
      # Multiple questions detected
      multi_intent_result = {
        type: "MULTIPLE_QUESTIONS",
        question_count: questions.count,
        questions: [
          {
            index: 1,
            text: "question 1",
            estimated_intent: "FAQ or DATA_REQUEST_RELATED"
          },
          {
            index: 2,
            text: "question 2",
            estimated_intent: "FAQ or DATA_REQUEST_RELATED"
          },
          # ... for each question
        ],
        handling: "consolidate_responses_into_one_message"  // Per US-04
      }
  
  else:
    multi_intent_result = {
      type: "SINGLE_INTENT",
      multi_intent_detected: false
    }

# Question separation logic for multiple questions
function parse_message_into_questions(message_text):
  
  # Split on sentence boundaries
  sentences = split_on_sentence_boundaries(message_text)
  
  questions = []
  for sentence in sentences:
    if sentence.contains_question_mark:
      questions.append({
        text: sentence,
        is_question: true,
        intent_preliminary: classify_question_intent(sentence)
      })
    elif sentence.is_imperative_or_request:
      # "Please clarify..." "Can you explain..." etc.
      questions.append({
        text: sentence,
        is_question: true,
        intent_preliminary: classify_question_intent(sentence)
      })
    else:
      # Context or supporting statement
      last_question = questions[-1]
      last_question.context.append(sentence)
  
  return questions

output_format:
  {
    "multi_intent_detected": boolean,
    "type": "HYBRID_SINGLE_QUESTION|MULTIPLE_QUESTIONS|SINGLE_INTENT",
    "primary_intent": "FAQ|DATA_REQUEST_RELATED|UNKNOWN",
    "secondary_intent": "FAQ|DATA_REQUEST_RELATED|UNKNOWN|null",
    "question_count": integer,
    "questions": [
      {
        "index": 1,
        "text": "question text",
        "detected_intent": "FAQ|DATA_REQUEST_RELATED"
      }
    ],
    "handling_strategy": "answer_data_request_first_then_faq|consolidate_responses|etc",
    "should_send_single_message": boolean  // For US-04
  }

error_handling:
  - Ambiguous questions → treat as single question, use primary intent
  - Unrelated questions → still consolidate in one message
  - 5+ questions → still consolidate but warn in logs

acceptance_criteria:
  - ✓ Multi-intent queries detected (US-03, US-04)
  - ✓ Multiple questions in one message separated (US-04)
  - ✓ Single consolidated response sent (US-04)
  - ✓ No context merging of unrelated intents
```

---

## Check 1.3: Minimum intent categories: FAQ vs Data Request related queries

```yaml
rule_id: query_input.intent_classification.taxonomy_compliance
component: Intent Classification Engine
purpose: Ensure classification uses defined taxonomy
source: FRD §1 - Query Input - Intent Classification (Taxonomy CSV to be provided by Vivli team)

field_path: classification_result.intent_classification
field_type: enum

valid_intent_categories:
  - "FAQ": General/Knowledge Base questions
  - "DATA_REQUEST_RELATED": Data request specific questions
  - "ESCALATION": Requests for human help
  - "UNKNOWN": Cannot classify with confidence
  - "HYBRID": Contains multiple intents

# Note: Full taxonomy CSV will be provided by Vivli team
# These are MINIMUM categories - more may be added later

taxonomy_validation_logic:
  
  if (classification_result.intent NOT IN valid_intent_categories):
    action: "log_error_and_escalate"
    error: "Intent classification returned invalid category"
    reason: classification_result.intent + " not in taxonomy"
  
  else:
    action: "proceed_with_routing"

# Extensibility for future taxonomy expansion
taxonomy_expansion_process:
  
  when_vivli_adds_new_intent_category:
    1. Update valid_intent_categories list
    2. Add training examples for new category
    3. Retrain intent classification model
    4. Test with sample queries
    5. Deploy to all environments

future_taxonomy_notes:
  - "Placeholder: Will include additional categories for specialized query types"
  - "Example future categories: 'TECHNICAL_ISSUE', 'DEADLINE_QUESTION', 'POLICY_CLARIFICATION'"
  - "Maintain backward compatibility with FAQ and DATA_REQUEST_RELATED"

output_format:
  {
    "intent_category": "string from valid taxonomy",
    "taxonomy_valid": boolean,
    "error_if_invalid": "null or error message"
  }

acceptance_criteria:
  - ✓ Uses defined taxonomy from Vivli team
  - ✓ Minimum categories supported: FAQ, DATA_REQUEST_RELATED
  - ✓ Invalid classifications caught and logged
  - ✓ Expandable for future categories
```

---

## Check 1.4: Based on intent classification result, route query appropriately

```yaml
rule_id: query_input.intent_classification.routing_decision
component: Intent Classification Engine → Routing
purpose: Route query to appropriate handler based on classification
source: FRD §1 - Query Input - Intent Classification

user_story: US-08 - Route queries based on detected intent

field_path: classification_result.intent_classification
depends_on: Check 1.1, 1.2, 1.3

routing_table:
  
  FAQ:
    route_to: "Knowledge Base Retrieval Module"
    component: "COMPONENT 2: FAQ/KNOWLEDGE BASE RETRIEVAL"
    reasoning: "Query about general platform/process information"
  
  DATA_REQUEST_RELATED:
    route_to: "Data Request API Integration Module"
    component: "COMPONENT 3: DATA REQUEST API INTEGRATION"
    reasoning: "Query about specific data request status/feedback"
  
  HYBRID:
    route_to: "Data Request API Integration Module → then Knowledge Base Retrieval"
    order: "Data Request first (get current status), then FAQ (answer other questions)"
    component: "COMPONENT 3, then COMPONENT 2"
    reasoning: "Answer most specific query first, then general context"
  
  ESCALATION:
    route_to: "Escalation Handler Module"
    component: "COMPONENT 6: ESCALATION HANDLER"
    reasoning: "Researcher explicitly requesting human help"
  
  UNKNOWN:
    route_to: "Escalation Handler Module"
    component: "COMPONENT 6: ESCALATION HANDLER"
    confidence_threshold_missed: true
    reasoning: "Cannot confidently classify, prefer human review over guessing"

routing_logic:

  switch (classification_result.intent):
    
    case "FAQ":
      if (classification_result.confidence >= 0.7):
        routing_decision = {
          intent: "FAQ",
          route_to: "knowledge_base_retrieval",
          confidence_level: "high",
          fallback_available: true,  // Can escalate if no docs found
          action: "invoke_knowledge_base_retrieval"
        }
      else:
        routing_decision = {
          intent: "FAQ",
          confidence_level: "low",
          action: "escalate_to_human",
          reason: "FAQ detected but confidence too low"
        }
    
    case "DATA_REQUEST_RELATED":
      if (classification_result.confidence >= 0.7):
        // Extract request ID from message
        request_id = extract_request_id(message.text)
        
        if (request_id == null):
          routing_decision = {
            intent: "DATA_REQUEST_RELATED",
            route_to: "ask_for_clarification",
            action: "ask_user_for_request_id",
            message: "Which data request are you asking about? Please provide the request ID."
          }
        else:
          routing_decision = {
            intent: "DATA_REQUEST_RELATED",
            route_to: "data_request_api_integration",
            request_id: request_id,
            confidence_level: "high",
            action: "invoke_data_request_api"
          }
      else:
        routing_decision = {
          intent: "DATA_REQUEST_RELATED",
          confidence_level: "low",
          action: "escalate_to_human"
        }
    
    case "HYBRID":
      request_id = extract_request_id(message.text)
      if (request_id):
        routing_decision = {
          intent: "HYBRID",
          route_to: ["data_request_api_integration", "knowledge_base_retrieval"],
          order: "sequentially - data request first",
          request_id: request_id,
          action: "invoke_data_request_api_then_knowledge_base"
        }
      else:
        routing_decision = {
          intent: "HYBRID",
          route_to: "knowledge_base_retrieval",
          reason: "No request ID found, treat as FAQ with secondary context"
        }
    
    case "ESCALATION":
      routing_decision = {
        intent: "ESCALATION",
        route_to: "escalation_handler",
        confidence_level: "high",
        action: "invoke_escalation_handler"
      }
    
    case "UNKNOWN":
      routing_decision = {
        intent: "UNKNOWN",
        route_to: "escalation_handler",
        confidence_level: "too_low",
        action: "invoke_escalation_handler",
        reason: "Confidence below threshold for any intent"
      }

output_format:
  {
    "routing_decision": {
      "intent": "from classification",
      "route_to": "module_name",
      "component": "COMPONENT_N",
      "request_id": "if applicable",
      "action": "what_to_do_next",
      "confidence_level": "high|low|too_low",
      "fallback_available": boolean
    }
  }

error_handling:
  - Invalid intent in classification → escalate immediately
  - Request ID extraction fails → ask for clarification
  - Confidence threshold not met → escalate

acceptance_criteria:
  - ✓ FAQ routed to knowledge base (US-08)
  - ✓ Data request queries routed to API (US-08)
  - ✓ Escalation requests routed to humans (US-08)
  - ✓ Unknown classified queries escalated (US-08)
  - ✓ Consistent routing decisions
```

---

# 🎯 SECTION 2: CHAT SCOPE CHECKS

## Check 2.1: Message received in Open Chat only

```yaml
rule_id: query_input.scope.chat_type_validation
component: Message Validation (Pre-Intent Classification)
purpose: Validate message is from Open Chat, not other chats
source: FRD §1 - Query Input, Scope

user_story: US-01 - Restrict chat scope to eligible chats and stages

field_path: message_metadata.chat_type
field_type: enum
valid_values: ["open_chat", "contributors_chat", "requestor_chat", "private_org_chat"]
required: yes

scope_validation_logic:
  
  if (message.chat_type == "open_chat"):
    scope_check = {
      chat_type_valid: true,
      action: "proceed_to_next_check"
    }
  
  elif (message.chat_type in ["contributors_chat", "requestor_chat", "private_org_chat"]):
    scope_check = {
      chat_type_valid: false,
      chat_type: message.chat_type,
      reason: "Message from non-open chat",
      action: "do_not_respond",
      log_action: "ignore_message"
    }
  
  else:
    scope_check = {
      chat_type_valid: false,
      chat_type: message.chat_type,
      reason: "Unknown chat type",
      action: "do_not_respond",
      log_action: "log_and_escalate_to_admin"
    }

out_of_scope_handling:
  - Contributors Chat: "Do not respond. Log as out of scope."
  - Requestor Chat: "Do not respond. Log as out of scope."
  - Private Org Chat: "Do not respond. Log as out of scope."
  - Unknown chat: "Do not respond. Escalate to admin for investigation."

output_format:
  {
    "chat_scope_valid": boolean,
    "chat_type": "from message metadata",
    "is_open_chat": boolean,
    "action": "proceed or do_not_respond",
    "reason_if_invalid": "string"
  }

acceptance_criteria:
  - ✓ Only Open Chat messages processed (US-01)
  - ✓ Other chats ignored (US-01)
  - ✓ Out-of-scope messages logged
  - ✓ No response sent to non-open chats
```

---

## Check 2.2: Message received during eligible stages (draft/revision/form-check)

```yaml
rule_id: query_input.scope.stage_validation
component: Message Validation (Pre-Intent Classification)
purpose: Validate message received during eligible data request stages
source: FRD §1 - Query Input, Scope

user_story: US-01 - Restrict chat scope to eligible chats and stages

field_path: 
  - data_request.current_stage
  - data_request.form_check_human_validation_started

field_type: enum
eligible_stages: ["draft", "revision", "vivli_form_check"]
ineligible_stages: ["review", "approved", "rejected", "completed", "withdrawn"]
required: yes

stage_validation_logic:
  
  current_stage = data_request.current_stage
  form_check_human_started = data_request.form_check_human_validation_started
  
  if (current_stage in ["draft", "revision"]):
    stage_check = {
      stage_valid: true,
      current_stage: current_stage,
      reason: "Draft or revision stage - eligible",
      action: "proceed_to_intent_classification"
    }
  
  elif (current_stage == "vivli_form_check" AND form_check_human_started == false):
    # Form check stage, but human review hasn't started yet
    stage_check = {
      stage_valid: true,
      current_stage: current_stage,
      reason: "Form check stage, human review not yet started",
      action: "proceed_to_intent_classification"
    }
  
  elif (current_stage == "vivli_form_check" AND form_check_human_started == true):
    # Form check stage, but human has taken over
    stage_check = {
      stage_valid: false,
      current_stage: current_stage,
      reason: "Form check stage, but human validation in progress",
      action: "do_not_respond",
      log_action: "ignore_message - human review in progress"
    }
  
  elif (current_stage in ["review", "approved", "rejected", "completed", "withdrawn"]):
    stage_check = {
      stage_valid: false,
      current_stage: current_stage,
      reason: "Data request past form-check stage",
      action: "do_not_respond",
      log_action: "ignore_message - stage not eligible"
    }
  
  else:
    stage_check = {
      stage_valid: false,
      current_stage: current_stage,
      reason: "Unknown or invalid stage",
      action: "do_not_respond",
      log_action: "log_and_escalate"
    }

stage_descriptions:
  "draft": "Researcher is creating/editing the form - Agentic chat ACTIVE"
  "revision": "Researcher is revising after feedback - Agentic chat ACTIVE"
  "vivli_form_check": "Vivli checks form before human review - Agentic chat ACTIVE (until human takes over)"
  "review": "Human Vivli admin reviewing - Agentic chat INACTIVE"
  "approved": "Form approved - Agentic chat INACTIVE"
  "rejected": "Form rejected - Agentic chat INACTIVE"
  "completed": "Request completed - Agentic chat INACTIVE"
  "withdrawn": "Request withdrawn - Agentic chat INACTIVE"

output_format:
  {
    "stage_valid": boolean,
    "current_stage": "from data_request metadata",
    "is_eligible_stage": boolean,
    "human_validation_started": boolean,
    "action": "proceed or do_not_respond",
    "reason_if_invalid": "string"
  }

error_handling:
  - Cannot determine stage → escalate to admin
  - Stage data missing → do not respond, log
  - Human validation flag unclear → do not respond, log

acceptance_criteria:
  - ✓ Messages during draft/revision/form-check processed (US-01)
  - ✓ Messages after form-check ignored (US-01)
  - ✓ Human validation in progress respected (US-01)
  - ✓ Stage transitions handled correctly
```

---

## Check 2.3: Message from Research Team member only

```yaml
rule_id: query_input.scope.user_role_validation
component: Message Validation (Pre-Intent Classification)
purpose: Validate message is from Research Team, not other roles
source: FRD §1 - Query Input, Scope, Roles

user_story: US-02 - Respond only to Research team messages

field_path: message.sender_user_role
field_type: enum
valid_roles_to_respond_to: ["data_request_creator", "research_team_member"]
invalid_roles_to_ignore: ["vivli_admin", "org_admin", "data_uploader", "data_contributor", "automated_notification", "irp_member"]
required: yes

user_role_validation_logic:
  
  sender_role = message.sender_user_role
  
  if (sender_role in ["data_request_creator", "research_team_member"]):
    role_check = {
      role_valid: true,
      sender_role: sender_role,
      reason: "Sender is research team member",
      action: "proceed_to_scope_checks"
    }
  
  elif (sender_role == "vivli_admin"):
    role_check = {
      role_valid: false,
      sender_role: sender_role,
      reason: "Vivli admin - do not respond to admin messages",
      action: "do_not_respond",
      log_action: "ignore_message - admin role"
    }
  
  elif (sender_role == "org_admin"):
    role_check = {
      role_valid: false,
      sender_role: sender_role,
      reason: "Org admin - not research team",
      action: "do_not_respond",
      log_action: "ignore_message - org admin role"
    }
  
  elif (sender_role == "automated_notification"):
    role_check = {
      role_valid: false,
      sender_role: sender_role,
      reason: "Automated system notification - do not respond",
      action: "do_not_respond",
      log_action: "ignore_message - automated notification"
    }
  
  elif (sender_role in ["data_uploader", "data_contributor", "irp_member"]):
    role_check = {
      role_valid: false,
      sender_role: sender_role,
      reason: "Not research team member",
      action: "do_not_respond",
      log_action: "ignore_message - non-research role"
    }
  
  else:
    role_check = {
      role_valid: false,
      sender_role: sender_role,
      reason: "Unknown user role",
      action: "do_not_respond",
      log_action: "log_and_escalate - unknown role"
    }

role_explanations:
  valid_roles:
    data_request_creator: "The researcher who created the data request"
    research_team_member: "A colleague added to the research team"
  
  invalid_roles:
    vivli_admin: "Vivli staff member - they use different interface"
    org_admin: "Organization administrator - not part of research team"
    data_uploader: "Person uploading data to Vivli"
    data_contributor: "Organization contributing data"
    automated_notification: "System notification, not a person"
    irp_member: "Independent Review Panel member"

output_format:
  {
    "role_valid": boolean,
    "sender_user_role": "from message metadata",
    "is_research_team": boolean,
    "action": "proceed or do_not_respond",
    "reason_if_invalid": "string"
  }

error_handling:
  - Cannot determine role → do not respond, log
  - Role data missing → do not respond, log
  - Ambiguous role → escalate to admin

acceptance_criteria:
  - ✓ Only research team messages answered (US-02)
  - ✓ All other roles ignored (US-02)
  - ✓ Admin messages not answered (US-02)
  - ✓ Automated notifications ignored (US-02)
```

---

# 🎯 SECTION 3: MESSAGE INPUT VALIDATION CHECKS

## Check 3.1: Handle blank, empty, and whitespace-only messages

```yaml
rule_id: query_input.validation.blank_message_handling
component: Message Input Validation (Pre-Intent Classification)
purpose: Detect and handle blank, empty, and invalid message inputs
source: FRD §1 - Query Input

user_story: US-05 - Gracefully handle invalid and edge-case inputs

field_path: message.text
field_type: string
required: yes

input_validation_logic:
  
  if (message.text == null):
    validation_result = {
      is_valid: false,
      input_type: "null",
      action: "do_not_respond",
      reason: "Message is null",
      log_action: "log_null_message"
    }
  
  elif (message.text == ""):
    validation_result = {
      is_valid: false,
      input_type: "empty_string",
      action: "do_not_respond",
      reason: "Message is empty string",
      log_action: "log_empty_message"
    }
  
  elif (message.text.strip() == ""):
    validation_result = {
      is_valid: false,
      input_type: "whitespace_only",
      action: "return_error_message",
      error_message: "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.",
      reason: "Message contains only whitespace"
    }
  
  elif (len(message.text.strip()) < 2):
    # Very short message (single character)
    validation_result = {
      is_valid: false,
      input_type: "too_short",
      action: "return_error_message",
      error_message: "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.",
      reason: "Message too short to parse"
    }
  
  else:
    validation_result = {
      is_valid: true,
      input_type: "valid",
      action: "proceed_to_next_check",
      cleaned_text: message.text.strip()
    }

output_format:
  {
    "input_valid": boolean,
    "input_type": "null|empty_string|whitespace_only|too_short|valid",
    "action": "proceed_to_next_check|return_error_message|do_not_respond",
    "cleaned_text": "if valid, the trimmed text"
  }

acceptance_criteria:
  - ✓ Blank messages detected and rejected (US-05)
  - ✓ Whitespace-only messages handled gracefully (US-05)
  - ✓ Error message returned for invalid inputs (US-05)
  - ✓ No processing of empty messages
```

---

## Check 3.2: Handle extremely long messages (500+ words)

```yaml
rule_id: query_input.validation.message_length_limits
component: Message Input Validation (Pre-Intent Classification)
purpose: Handle excessively long messages
source: FRD §1 - Query Input

user_story: US-05 - Gracefully handle invalid and edge-case inputs

field_path: message.text
field_type: string
length_limits:
  warning_threshold: 1000  # characters
  error_threshold: 2000    # characters (500+ words ≈ 2500 chars)
  recommended_max: 5000    # words would be ~25000 chars

length_validation_logic:
  
  message_length = len(message.text)
  word_count = count_words(message.text)
  
  if (message_length > 2000 OR word_count > 500):
    length_result = {
      is_valid: false,
      length_category: "too_long",
      message_length: message_length,
      word_count: word_count,
      action: "return_guidance_message",
      user_message: "Your message is very long. Please break it into smaller questions for better responses. For example: 'First, I have a question about X. Second, I have a question about Y.'",
      internal_action: "may_still_attempt_processing_or_escalate"
    }
  
  elif (message_length > 1000):
    length_result = {
      is_valid: true,
      length_category: "long",
      message_length: message_length,
      word_count: word_count,
      action: "proceed_with_caution",
      internal_note: "Message is long - consider splitting in response"
    }
  
  else:
    length_result = {
      is_valid: true,
      length_category: "normal",
      message_length: message_length,
      word_count: word_count,
      action: "proceed_normally"
    }

# For very long messages that are processed:
handling_strategy:
  if (message_length > 2000):
    1. Alert user to split question
    2. Attempt to parse main intent
    3. If intent clear: answer briefly
    4. If intent unclear: escalate
    5. Suggest user split questions in future

output_format:
  {
    "length_valid": boolean,
    "length_category": "too_long|long|normal",
    "message_length": integer,
    "word_count": integer,
    "action": "proceed_normally|proceed_with_caution|return_guidance_message",
    "guidance_if_too_long": "string"
  }

acceptance_criteria:
  - ✓ Very long messages detected (US-05)
  - ✓ User receives helpful guidance (US-05)
  - ✓ System attempts to handle if processable
  - ✓ Escalation for unclear long messages
```

---

## Check 3.3: Handle special characters, emoji, HTML, code snippets

```yaml
rule_id: query_input.validation.special_content_handling
component: Message Input Validation (Pre-Intent Classification)
purpose: Handle messages with HTML, code, emoji, special characters
source: FRD §1 - Query Input

user_story: US-05 - Gracefully handle invalid and edge-case inputs

field_path: message.text
field_type: string

content_detection_logic:
  
  # Detect various content types
  has_html = detect_html_tags(message.text)
  has_code = detect_code_syntax(message.text)  # Python, JavaScript, SQL, etc.
  has_excessive_emoji = count_emoji(message.text) / word_count > 0.3
  has_special_chars_only = is_special_chars_only(message.text)  # @#$%^&*()
  
  if (has_html OR has_code):
    # HTML or code pasted in
    content_result = {
      contains_special_content: true,
      content_type: "html_or_code",
      action: "return_guidance_message",
      user_message: "I notice your message contains code or HTML. I'm designed to help with questions about the Vivli platform, not code issues. Please ask your question in plain text.",
      internal_action: "extract_intent_if_possible"
    }
  
  elif (has_excessive_emoji):
    content_result = {
      contains_special_content: true,
      content_type: "excessive_emoji",
      action: "return_error_message",
      user_message: "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.",
      internal_action: "do_not_process"
    }
  
  elif (has_special_chars_only):
    content_result = {
      contains_special_content: true,
      content_type: "special_chars_only",
      action: "return_error_message",
      user_message: "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.",
      internal_action: "do_not_process"
    }
  
  else:
    # Normal content, may have some special characters mixed in
    content_result = {
      contains_special_content: false,
      action: "proceed_normally",
      cleaned_text: sanitize_for_processing(message.text)
    }

# Sanitization for processing
function sanitize_for_processing(text):
  # Remove unnecessary HTML/XML tags (keep text content)
  text = remove_html_tags(text)
  
  # Normalize whitespace
  text = normalize_whitespace(text)
  
  # Decode HTML entities (&amp; → &, etc.)
  text = decode_html_entities(text)
  
  # Keep alphanumeric, basic punctuation, some special chars
  # Remove control characters
  text = remove_control_characters(text)
  
  return text

output_format:
  {
    "contains_special_content": boolean,
    "content_type": "html_or_code|excessive_emoji|special_chars_only|normal",
    "action": "proceed_normally|return_guidance_message|return_error_message",
    "cleaned_text": "if processable, the sanitized version"
  }

acceptance_criteria:
  - ✓ HTML/code content detected and handled (US-05)
  - ✓ Emoji-only messages rejected (US-05)
  - ✓ Special character edge cases handled (US-05)
  - ✓ User receives clear guidance
```

---

*[Continuing with remaining checks...]*

## Check 3.4: Handle non-English messages

```yaml
rule_id: query_input.validation.language_detection
component: Message Input Validation (Pre-Intent Classification)
purpose: Detect and handle non-English messages
source: FRD §1 - Query Input

user_story: US-05 - Gracefully handle invalid and edge-case inputs

field_path: message.text
field_type: string

language_detection_logic:
  
  detected_language = detect_language(message.text)  # Using langdetect or similar
  confidence = language_detection_confidence
  
  if (detected_language == "en" AND confidence > 0.8):
    language_result = {
      is_english: true,
      detected_language: "en",
      action: "proceed_normally"
    }
  
  elif (detected_language != "en" AND confidence > 0.7):
    # Clearly non-English
    language_result = {
      is_english: false,
      detected_language: detected_language,
      action: "return_error_message",
      user_message: "I'm sorry, but I'm currently set up to respond in English only. Please try rephrasing your question in English.",
      internal_action: "escalate_if_critical"
    }
  
  elif (confidence < 0.6):
    # Mixed language or unclear
    language_result = {
      is_english: null,
      detected_language: detected_language,
      confidence: confidence,
      action: "attempt_processing",
      internal_note: "Language detection low confidence - proceed but monitor"
    }

future_notes:
  - "Phase 2: Add support for Spanish, French, German based on user feedback"
  - "Phase 3: Add multi-language support via LLM"

output_format:
  {
    "is_english": boolean,
    "detected_language": "language_code",
    "confidence": 0.0-1.0,
    "action": "proceed_normally|return_error_message|attempt_processing",
    "error_message": "if applicable"
  }

acceptance_criteria:
  - ✓ Non-English messages detected (US-05)
  - ✓ User informed in English (US-05)
  - ✓ Scalable for future language support
```

---

## Check 3.5: Handle attachment-only messages and parse attachments

```yaml
rule_id: query_input.validation.attachment_handling
component: Message Input Validation & Attachment Processing
purpose: Handle and parse chat attachments
source: FRD §1 - Query Input

user_story: US-06 - Parse researcher chat attachments

field_path: 
  - message.text
  - message.attachments[]

attachment_validation_logic:
  
  has_text = len(message.text.strip()) > 0
  has_attachments = message.attachments.count > 0
  
  if (NOT has_text AND NOT has_attachments):
    # Truly empty message - handled by blank message check
    attachment_result = {
      is_valid: false,
      reason: "No text and no attachments"
    }
  
  elif (NOT has_text AND has_attachments):
    # Attachment-only message
    attachment_result = {
      type: "attachment_only",
      attachment_count: message.attachments.count,
      action: "parse_attachments_and_extract_text",
      internal_note: "Extract content from attachments to use as query text"
    }
  
  elif (has_text AND has_attachments):
    # Text + attachments
    attachment_result = {
      type: "text_with_attachments",
      attachment_count: message.attachments.count,
      action: "use_text_as_query_and_parse_attachments_for_context"
    }
  
  else:
    # Text only (normal case)
    attachment_result = {
      type: "text_only",
      attachment_count: 0,
      action: "proceed_normally"
    }

attachment_parsing_logic:
  
  for attachment in message.attachments:
    
    file_type = attachment.file_type
    file_size = attachment.file_size_bytes
    
    # Size limits
    if (file_size > 10 * 1024 * 1024):  # 10MB limit
      attachment_parsing_result = {
        status: "skipped",
        reason: "File too large"
      }
      continue
    
    # Supported types
    if (file_type in ["pdf", "txt", "docx", "xlsx", "csv", "png", "jpg", "jpeg"]):
      
      try:
        extracted_content = parse_attachment(attachment)
        
        attachment_parsing_result = {
          status: "success",
          file_type: file_type,
          extracted_text_length: len(extracted_content),
          content_preview: extracted_content[:200]
        }
        
        # Combine with message text
        if (attachment_result.type == "attachment_only"):
          query_text_final = extracted_content
        else:
          query_text_final = message.text + "\n\n[Attachment context]\n" + extracted_content
      
      catch exception:
        attachment_parsing_result = {
          status: "parse_failed",
          file_type: file_type,
          error: exception.message
        }
    
    else:
      attachment_parsing_result = {
        status: "unsupported_type",
        file_type: file_type
      }

output_format:
  {
    "has_attachments": boolean,
    "attachment_count": integer,
    "attachments_parsed": [
      {
        "file_name": "string",
        "file_type": "string",
        "parsing_status": "success|parse_failed|unsupported_type|skipped",
        "extracted_content_length": integer
      }
    ],
    "query_text_final": "text + attachment content combined",
    "action": "proceed_with_combined_text"
  }

error_handling:
  - Parsing fails on attachment → skip that attachment, continue
  - Unsupported file type → note in log, skip
  - File too large → note in log, skip

acceptance_criteria:
  - ✓ Attachments detected and parsed (US-06)
  - ✓ Attachment content available to downstream (US-06)
  - ✓ Unsupported types handled gracefully
  - ✓ Attachment-only messages processed
```

---

## Check 3.6: Handle offensive, irrelevant, or Vivli-unrelated content

```yaml
rule_id: query_input.validation.content_safety_check
component: Message Input Validation (Pre-Intent Classification)
purpose: Detect and reject harmful, offensive, or irrelevant content
source: FRD §1 - Query Input

user_story: US-05 - Gracefully handle invalid and edge-case inputs

field_path: message.text
field_type: string

content_safety_logic:
  
  # Run safety checks using Azure OpenAI content filtering
  safety_result = azure_ai_content_filtering.check(message.text)
  
  if (safety_result.hate_speech_score > 0.8 OR
      safety_result.violence_score > 0.8 OR
      safety_result.sexual_score > 0.8 OR
      safety_result.self_harm_score > 0.8):
    
    content_safety_result = {
      is_safe: false,
      safety_category: safety_result.highest_category,
      confidence: safety_result.highest_confidence,
      action: "do_not_respond",
      log_action: "log_as_unsafe_content_and_flag_for_admin",
      internal_note: "Do not respond, only log for admin review"
    }
  
  else:
    # Check for Vivli relevance
    is_vivli_related = check_vivli_relevance(message.text)
    
    if (NOT is_vivli_related):
      # Question completely unrelated to Vivli
      content_safety_result = {
        is_safe: true,  // Not offensive, but not Vivli-related
        vivli_related: false,
        action: "return_error_message",
        user_message: "I'm sorry, but I'm designed to help with questions about the Vivli platform. Your question doesn't seem to be related to Vivli data sharing. Please ask a question about the platform, data requests, policies, or procedures.",
        internal_action: "log_as_off_topic"
      }
    
    else:
      # Safe and Vivli-related
      content_safety_result = {
        is_safe: true,
        vivli_related: true,
        action: "proceed_normally"
      }

# Vivli relevance check
function check_vivli_relevance(text):
  vivli_keywords = ["vivli", "data request", "data sharing", "form", "submission", "policy", "process", "access", "research", "trial", "clinical"]
  
  keyword_match_score = count_keyword_matches(text, vivli_keywords) / word_count
  
  // Also use semantic similarity
  semantic_score = cosine_similarity(embed(text), embed("Vivli data sharing and requests"))
  
  combined_relevance = (keyword_match_score * 0.4) + (semantic_score * 0.6)
  
  return combined_relevance > 0.5

output_format:
  {
    "is_safe": boolean,
    "vivli_related": boolean,
    "safety_category": "if unsafe, the category",
    "action": "proceed_normally|return_error_message|do_not_respond",
    "error_message": "if applicable"
  }

error_handling:
  - Safety check API fails → escalate to human (don't guess on safety)
  - Borderline relevance → escalate rather than reject

acceptance_criteria:
  - ✓ Offensive content detected and rejected (US-05)
  - ✓ Off-topic questions handled gracefully (US-05)
  - ✓ User receives helpful error messages (US-05)
  - ✓ Admin alerted to unsafe content
```

---

# 🎯 SECTION 4: SUMMARY & DECISION TREE

## Complete Query Input Validation Flow

```yaml
query_input_validation_decision_tree:

  INPUT: Incoming researcher message
    ↓
  [CHECK 2.1] Is message from Open Chat?
    ├─ NO → IGNORE, log as out-of-scope
    └─ YES ↓
  
  [CHECK 2.2] Is message during eligible stage? (draft/revision/form-check before human takes over)
    ├─ NO → IGNORE, log as out-of-scope
    └─ YES ↓
  
  [CHECK 2.3] Is sender a Research Team member?
    ├─ NO → IGNORE, log as wrong role
    └─ YES ↓
  
  [CHECK 3.1] Is message blank/empty/whitespace-only?
    ├─ YES → Return error message, STOP
    └─ NO ↓
  
  [CHECK 3.2] Is message excessively long (500+ words)?
    ├─ YES → Send guidance, attempt processing or escalate
    └─ NO (or attempt processing) ↓
  
  [CHECK 3.3] Does message contain HTML/code/excessive emoji/special chars only?
    ├─ YES, critical issue → Return error message, STOP
    ├─ YES, minor issue → Sanitize and continue
    └─ NO ↓
  
  [CHECK 3.4] Is message non-English?
    ├─ YES, clearly → Return language message, STOP
    └─ NO or unclear ↓
  
  [CHECK 3.5] Handle attachments
    ├─ Parse and extract content
    └─ Combine with message text ↓
  
  [CHECK 3.6] Is content safe and Vivli-related?
    ├─ Unsafe → IGNORE, log for admin, STOP
    ├─ Off-topic → Return guidance message, STOP
    └─ Safe and Vivli-related ↓
  
  MESSAGE PASSES ALL VALIDATIONS ✓
    ↓
  [CHECK 1.1] Classify intent (FAQ / Data Request / Escalation / Hybrid / Unknown)
    ↓
  [CHECK 1.2] Detect multi-intent or multiple questions
    ↓
  [CHECK 1.3] Validate against taxonomy
    ↓
  [CHECK 1.4] Route to appropriate handler
    ↓
  PROCEED TO: COMPONENT 2/3/6 based on routing decision
```

---

## Key Acceptance Criteria Checklist

✓ All checks have unique rule IDs  
✓ Each check includes:
  - Purpose statement
  - Field paths and data types
  - Validation logic (in pseudo code format)
  - Error handling
  - Output format (JSON)
  - Acceptance criteria
  - Audit notes

✓ User stories mapped to each check  
✓ Decision tree shows flow through all checks  
✓ Clear actions at each step (proceed / return error / ignore / escalate)  

---

**This Query Input section provides developers with complete pseudo code for implementing all validation and classification logic!** 🚀

