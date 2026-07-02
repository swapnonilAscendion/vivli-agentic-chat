# VIVLI AGENTIC CHAT - PSEUDO CODE SPECIFICATIONS

## 📋 Using Dev Notes Style Format (From Form Validation Project)

---

## 🎯 COMPONENT 1: INTENT CLASSIFICATION ENGINE

### Rule ID: chat.intent.classifier

```
rule_id: chat.intent.classifier
component: Intent Classification Module
purpose: Classify incoming researcher query into defined intent categories

field_path: researcher_message.query_text
field_type: string
required: yes

validation_logic:
  - Check 1: Parse query text for keywords
  - Check 2: Calculate semantic similarity to intent categories
  - Check 3: Apply confidence threshold (default: 0.7)
  - Check 4: Determine if multi-intent query

intent_categories:
  1. faq_query:
     keywords: ["how", "what", "where", "when", "process", "procedure", "policy", "requirements"]
     examples:
       - "How do I submit a data request?"
       - "What documents do I need?"
       - "What is the process timeline?"
  
  2. data_request_related:
     keywords: ["status", "my request", "update", "feedback", "revision", "submission"]
     examples:
       - "What is the status of my request #12345?"
       - "Can I check the status of my submission?"
       - "Have you reviewed my request?"

  3. escalation_trigger:
     keywords: ["help", "escalate", "human", "staff", "not helpful", "need assistance"]
     examples:
       - "I need help"
       - "Escalate this to a human"
       - "This didn't help"

conditional_response:
  - if (intent_score[faq] > 0.7 AND intent_score[data_request] < 0.3):
      intent_classification: "FAQ"
      confidence_score: intent_score[faq]
      route_to: "knowledge_base_retrieval"
  
  - elif (intent_score[data_request] > 0.7 AND intent_score[faq] < 0.3):
      intent_classification: "DATA_REQUEST_RELATED"
      confidence_score: intent_score[data_request]
      route_to: "data_request_api_fetch"
  
  - elif (intent_score[faq] > 0.5 AND intent_score[data_request] > 0.5):
      intent_classification: "HYBRID"
      confidence_score: max(intent_score[faq], intent_score[data_request])
      route_to: "data_request_api_fetch_then_knowledge_base"  // Data request first
  
  - elif (intent_score[escalation] > 0.7):
      intent_classification: "ESCALATION"
      confidence_score: intent_score[escalation]
      route_to: "escalation_handler"
  
  - else:
      intent_classification: "UNKNOWN"
      confidence_score: max(intent_score[*])
      action: "auto_escalate_to_human"
      reason: "Confidence below threshold"

context_dependencies:
  - researcher_id: from session context
  - chat_history: last 3 messages (optional, for conversation context)
  - data_request_id: if query mentions it explicitly

output_format:
  {
    "query_id": "unique_query_identifier",
    "intent_classification": "FAQ|DATA_REQUEST_RELATED|HYBRID|ESCALATION|UNKNOWN",
    "confidence_score": 0.0-1.0,
    "route_to": "next_component",
    "extracted_data": {
      "data_request_id": "if found",
      "keywords_matched": ["list", "of", "keywords"],
      "intent_scores": {
        "faq": 0.0-1.0,
        "data_request": 0.0-1.0,
        "escalation": 0.0-1.0
      }
    }
  }

audit_notes: "This component drives routing decisions. High confidence scores (>0.8) can be used for direct routing without fallback logic."
```

---

## 🎯 COMPONENT 2: FAQ/KNOWLEDGE BASE RETRIEVAL

### Rule ID: chat.knowledge_base.retrieval

```
rule_id: chat.knowledge_base.retrieval
component: Knowledge Base Retrieval Module
purpose: Retrieve relevant knowledge base documents for FAQ queries

field_path: researcher_message.query_text
context_fields:
  - intent_classification: "FAQ"
  - confidence_score: >= 0.7

retrieval_logic:
  - Step 1: Embed query using Azure OpenAI embeddings
  - Step 2: Query vector database (Azure AI Search) for semantic matches
  - Step 3: Retrieve top-K documents (default K=5)
  - Step 4: Calculate relevance scores for each document
  - Step 5: Apply confidence threshold for relevance (default: 0.6)
  - Step 6: Filter by knowledge base source priority

knowledge_base_sources_priority:
  1. Guru templates & cards (PRIORITY_HIGHEST)
  2. Policy documents (PRIORITY_HIGH)
  3. Website FAQs & how-to guides (PRIORITY_MEDIUM)
  4. Historical chat messages (PRIORITY_LOW - training only)

vector_database_config:
  provider: "Azure AI Search"
  index_name: "vivli-knowledge-base"
  embedding_model: "text-embedding-3-large"
  embedding_dimensions: 1536
  similarity_metric: "cosine"
  refresh_schedule: "weekly cron job"
  checksum_validation: "MD5 hash to skip unchanged"

retrieval_logic_detailed:
  - query_embedding = embeddings_client.embed(query_text)
  
  - retrieved_docs = vector_db.search(
      vector=query_embedding,
      top_k=5,
      filters=[
        "source in ('guru_templates', 'guru_cards', 'policy_documents', 'website_faqs', 'howto_guides')"
      ]
    )
  
  - for each doc in retrieved_docs:
      relevance_score = cosine_similarity(query_embedding, doc.embedding)
      
      if (relevance_score >= 0.6):
        if (doc.source == "guru_templates" OR doc.source == "guru_cards"):
          confidence_multiplier = 1.0
        elif (doc.source == "policy_documents"):
          confidence_multiplier = 0.9
        elif (doc.source == "website_faqs" OR doc.source == "howto_guides"):
          confidence_multiplier = 0.8
        
        final_confidence = relevance_score * confidence_multiplier
        
        if (final_confidence >= 0.6):
          add_to_relevant_results(doc, final_confidence)

conflict_resolution:
  - if (multiple documents from same topic with different priorities):
      select: "document with highest priority source"
      action: "log conflict for admin review"

conditional_response:
  - if (relevant_docs.count >= 1 AND max_confidence >= 0.7):
      action: "generate_response_with_llm"
      include_docs: relevant_docs (ordered by confidence)
      
  - elif (relevant_docs.count >= 1 AND max_confidence >= 0.6):
      action: "generate_response_with_llm"
      include_docs: relevant_docs (ordered by confidence)
      confidence_note: "Add disclaimer to response"
      
  - elif (relevant_docs.count >= 1 AND max_confidence >= 0.5):
      action: "manual_escalation"
      reason: "Confidence below minimum threshold for automated response"
      
  - else:
      action: "auto_escalate_to_human"
      reason: "No relevant documents found"

output_format:
  {
    "query_id": "reference to intent classification output",
    "retrieved_documents": [
      {
        "doc_id": "unique_document_id",
        "source": "guru_cards|policy_documents|website_faqs|howto_guides",
        "title": "document title",
        "content": "document text content",
        "relevance_score": 0.0-1.0,
        "confidence": 0.0-1.0,
        "citation_url": "public_facing_url_only",
        "guru_card_url": "if applicable"
      },
      ...
    ],
    "retrieval_metadata": {
      "total_docs_searched": "integer",
      "relevant_docs_found": "integer",
      "max_confidence": 0.0-1.0,
      "retrieval_time_ms": "execution time"
    }
  }

audit_notes: "Document retrieval is critical for answer accuracy. Log all retrieved documents and relevance scores for post-analysis. Track false positives (irrelevant docs with high scores) for model tuning."
```

---

## 🎯 COMPONENT 3: DATA REQUEST API INTEGRATION

### Rule ID: chat.data_request.api

```
rule_id: chat.data_request.api
component: Data Request API Integration Module
purpose: Fetch real-time data request status and metadata from Vivli API

field_path: researcher_message.extracted_data.data_request_id
context_fields:
  - intent_classification: "DATA_REQUEST_RELATED" OR "HYBRID"
  - confidence_score: >= 0.7

api_integration:
  provider: "Vivli Data Request API"
  authentication: "OAuth 2.0 / API Key"
  rate_limit: "100 requests/minute per researcher"
  timeout: "30 seconds"
  retry_logic: "exponential backoff (3 attempts)"

data_request_fetch_logic:
  - Step 1: Extract data_request_id from query (if explicitly mentioned)
  - Step 2: If not found, derive from session context (current data request)
  - Step 3: Call API endpoint: /api/v1/data-requests/{request_id}
  - Step 4: Parse response to extract:
      - request_status (one of: draft, submitted, form_check, review, approved, rejected, completed)
      - current_stage (enum)
      - submission_date (timestamp)
      - last_modified_date (timestamp)
      - form_feedback (array of feedback items)
      - reviewer_notes (string, if available)
  - Step 5: Validate response and handle errors

api_call_pseudo_code:
  
  data_request_id = extract_request_id(query_text)
  
  if (data_request_id is None):
    data_request_id = get_current_request_from_session(researcher_id)
  
  if (data_request_id is None):
    action: "ask_user_for_clarification"
    message: "I don't see which data request you're asking about. Could you provide the request ID?"
  
  try:
    response = api_client.get(
      endpoint=f"/api/v1/data-requests/{data_request_id}",
      headers={
        "Authorization": f"Bearer {session_token}",
        "Content-Type": "application/json"
      },
      timeout=30
    )
    
    if (response.status_code == 200):
      request_data = response.json()
      
      current_stage = request_data.stage
      submission_date = request_data.submitted_at
      status = request_data.status
      
      # Additional enrichment from knowledge base
      action: "fetch_knowledge_base_for_stage_guidance"
      
    elif (response.status_code == 404):
      action: "escalate_to_human"
      message: "I couldn't find this data request. Please verify the request ID and try again."
      
    elif (response.status_code == 403):
      action: "escalate_to_human"
      message: "You don't have permission to view this request. Please contact the Vivli team."
  
  except TimeoutError:
    action: "escalate_to_human"
    message: "I'm having trouble accessing your request information. A Vivli admin will follow up shortly."

conditional_response:
  - if (current_stage == "draft"):
      stage_guidance: "Your application is still in draft. You can make changes and submit when ready."
      suggested_action: "Continue editing and submit"
      knowledge_base_query: "How do I submit a data request?"
  
  - elif (current_stage == "submitted"):
      stage_guidance: "Your application has been submitted. We're reviewing it now."
      suggested_action: "Wait for review feedback"
      knowledge_base_query: "How long does review take?"
  
  - elif (current_stage == "form_check"):
      stage_guidance: "Your application is in form check. You may need to provide additional information."
      feedback_items: request_data.form_feedback[]
      suggested_action: "Check the chat for feedback and revise as needed"
      knowledge_base_query: "How do I respond to form check feedback?"
  
  - elif (current_stage == "review"):
      stage_guidance: "Your application is under review by the Vivli team. No action needed from you."
      suggested_action: "Wait for review to complete"
      knowledge_base_query: "What happens during the review stage?"
  
  - elif (current_stage == "approved"):
      stage_guidance: "Your application has been approved! You can now access the data."
      suggested_action: "Access your data through the platform"
      knowledge_base_query: "How do I access my approved data?"
  
  - elif (current_stage == "rejected"):
      stage_guidance: "Unfortunately, your application was not approved at this time."
      suggested_action: "Review feedback and submit a new request if applicable"
      knowledge_base_query: "Why was my request rejected?"

enrichment_logic:
  # After getting status from API, enrich with knowledge base
  - retrieve_stage_specific_guidance(current_stage)
  - retrieve_faq_for_common_questions(current_stage)
  - include_contact_info_if_escalation_likely: true

output_format:
  {
    "query_id": "reference to intent classification",
    "data_request_info": {
      "request_id": "vivli_id",
      "current_stage": "enum value",
      "submission_date": "timestamp",
      "last_modified": "timestamp",
      "status": "string",
      "stage_guidance": "natural language explanation",
      "form_feedback": [
        {
          "field": "field_name",
          "feedback": "feedback text"
        }
      ]
    },
    "enriched_with_knowledge_base": {
      "stage_specific_guidance": "docs retrieved",
      "relevant_faqs": "docs retrieved",
      "next_steps": "natural language"
    },
    "api_metadata": {
      "api_response_time_ms": "integer",
      "data_accuracy_timestamp": "when data was last updated"
    }
  }

error_handling:
  - API timeout → escalate to human
  - 404 Not Found → escalate to human (request doesn't exist)
  - 403 Forbidden → escalate to human (permission issue)
  - 500 Server Error → escalate to human (retry after delay)
  - Invalid request ID format → ask for clarification

audit_notes: "Every API call must be logged with request ID, researcher ID, timestamp, and response. This enables audit trail and helps identify patterns in researcher questions about status."
```

---

## 🎯 COMPONENT 4: LLM RESPONSE GENERATION

### Rule ID: chat.response.generation

```
rule_id: chat.response.generation
component: LLM Response Generation Module
purpose: Generate natural language responses grounded in retrieved data

field_path: (multiple inputs from previous components)
context_fields:
  - intent_classification: from Component 1
  - retrieved_documents: from Component 2 (if FAQ)
  - data_request_info: from Component 3 (if Data Request)

llm_configuration:
  model: "GPT-4O-mini"
  temperature: 0.7  # Balanced between creativity and consistency
  max_tokens: 500
  top_p: 0.95
  frequency_penalty: 0.0
  presence_penalty: 0.0

response_generation_logic:
  
  if (intent_classification == "FAQ"):
    
    prompt_template = """
    You are a helpful Vivli platform assistant. Answer the researcher's question based ONLY on the provided knowledge base documents.
    
    Researcher Question: {query_text}
    
    Knowledge Base Documents:
    {retrieved_documents}
    
    Requirements:
    1. Answer clearly and in plain language
    2. Reference the source document
    3. Keep response under 3 paragraphs
    4. If information is incomplete, suggest next steps
    5. NEVER fabricate information not in the documents
    """
    
    llm_input = format_prompt(
      query_text=researcher_query,
      retrieved_documents=format_docs_for_llm(relevant_docs),
      role="data sharing assistant"
    )
    
    response = llm_client.generate(
      prompt=prompt_template,
      config=llm_configuration,
      context={
        "researcher_name": researcher_name,
        "retrieved_doc_count": len(relevant_docs),
        "confidence_score": max_confidence_score
      }
    )
    
    # Validate response
    if (contains_fabrication_indicators(response)):
      action: "escalate_to_human"
      reason: "LLM response appears to contain unreliable information"
    
    response_format = FAQ_RESPONSE_TEMPLATE

  elif (intent_classification == "DATA_REQUEST_RELATED"):
    
    prompt_template = """
    You are a Vivli platform support assistant. Provide a status update and guidance based on the researcher's data request information.
    
    Researcher Name: {researcher_name}
    Request ID: {request_id}
    Current Stage: {current_stage}
    Stage Description: {stage_description}
    
    Researcher's Question: {query_text}
    
    Requirements:
    1. Provide stage-specific guidance
    2. Explain what's happening now
    3. Explain what comes next
    4. If action is needed, clearly state it
    5. Be empathetic and professional
    """
    
    llm_input = format_prompt(
      researcher_name=researcher_name,
      request_id=request_id,
      current_stage=data_request_info.stage,
      stage_description=stage_guidance,
      query_text=researcher_query
    )
    
    response = llm_client.generate(
      prompt=prompt_template,
      config=llm_configuration,
      context={
        "data_request_id": request_id,
        "researcher_id": researcher_id,
        "stage": current_stage
      }
    )
    
    response_format = DATA_REQUEST_RESPONSE_TEMPLATE

  elif (intent_classification == "HYBRID"):
    
    # Combine both FAQ and Data Request response logic
    response = combine_responses(
      data_request_response=generate_data_request_response(...),
      faq_response=generate_faq_response(...),
      priority="data_request_first"
    )
    
    response_format = HYBRID_RESPONSE_TEMPLATE

response_validation:
  
  checks = [
    ("hallucination_check", check_for_unsupported_claims(response)),
    ("groundedness_check", check_grounded_in_sources(response, sources)),
    ("relevance_check", check_relevance_to_query(response, query)),
    ("length_check", len(response) <= 500),
    ("safety_check", check_for_harmful_content(response))
  ]
  
  for (check_name, check_result) in checks:
    if (check_result.failed):
      log_validation_failure(check_name, response, reason=check_result.reason)
      if (check_name in ["hallucination_check", "safety_check"]):
        action: "escalate_to_human"
        reason: check_result.reason
        break

output_format:
  {
    "query_id": "reference to intent classification",
    "llm_response": {
      "raw_text": "generated response text",
      "formatted_response": "response with citations and formatting",
      "confidence_score": 0.0-1.0,
      "validation_status": "passed|failed_with_reason"
    },
    "source_documents": [
      {
        "doc_id": "if FAQ",
        "citation": "citation_url"
      }
    ],
    "llm_metadata": {
      "model_used": "GPT-4O-mini",
      "tokens_used": {
        "prompt": integer,
        "completion": integer
      },
      "generation_time_ms": integer,
      "confidence_factors": {
        "source_relevance": 0.0-1.0,
        "response_groundedness": 0.0-1.0,
        "hallucination_risk": "low|medium|high"
      }
    }
  }

audit_notes: "Every LLM generation should be logged with prompt, response, validation results, and confidence metrics. This data is used for model selection and improvement cycles."
```

---

## 🎯 COMPONENT 5: RESPONSE FORMATTING & DELIVERY

### Rule ID: chat.response.format_delivery

```
rule_id: chat.response.format_delivery
component: Response Formatting & Chat API Delivery Module
purpose: Format responses according to Vivli standards and deliver via Chat API

field_path: (output from LLM generation component)
context_fields:
  - intent_classification: from Component 1
  - researcher_name: from session
  - response_type: FAQ|DATA_REQUEST|HYBRID

response_formatting_logic:

  if (response_type == "FAQ"):
    
    formatted_response = """
    Hi {researcher_name},
    
    {llm_generated_answer}
    
    Source: {citation_url}
    
    Was this helpful?
    👍 [Yes, this helped]  |  👎 [No, this didn't help]
    
    ⓘ The information above was generated by an AI system. While reviewed for accuracy, AI can make mistakes. If this answer doesn't resolve your issue, please select "This did not help" to contact our support team.
    """

  elif (response_type == "DATA_REQUEST"):
    
    formatted_response = """
    Hi {researcher_name},
    
    Your data request {request_id} is currently at the following stage: {current_stage}.
    
    {stage_specific_guidance}
    
    {if action_needed: Next steps: {action_description}}
    
    If you have further questions, feel free to ask here.
    
    ⓘ The information above was generated by an AI system. While reviewed for accuracy, AI can make mistakes. If this answer doesn't resolve your issue, please select "This did not help" to contact our support team.
    """

  elif (response_type == "HYBRID"):
    
    formatted_response = """
    Hi {researcher_name},
    
    Regarding your data request {request_id}:
    
    Status: {request_status}
    {stage_specific_guidance}
    
    Regarding your question about {faq_topic}:
    
    {faq_answer}
    
    Source: {citation_url}
    
    If you have further questions, feel free to ask here.
    
    Was this helpful?
    👍 [Yes, this helped]  |  👎 [No, this didn't help]
    
    ⓘ The information above was generated by an AI system. While reviewed for accuracy, AI can make mistakes. If this answer doesn't resolve your issue, please select "This did not help" to contact our support team.
    """

  elif (response_type == "ESCALATION"):
    
    formatted_response = """
    {standard_escalation_message}
    
    I'm sorry, but I couldn't find a reliable answer to your question in our knowledge base.
    
    To make sure you receive the correct information, I've forwarded your question to a Vivli Administrator, who will review it and respond as soon as possible.
    
    Thank you for your patience.
    
    ⓘ The information above was generated by an AI system. While reviewed for accuracy, AI can make mistakes. If this answer doesn't resolve your issue, please select "This did not help" to contact our support team.
    """

  elif (response_type == "MULTIPLE_QUERIES"):
    
    formatted_response = """
    Hi {researcher_name},
    
    I'll address each of your questions:
    
    **Question 1: {q1}**
    {answer_1}
    
    **Question 2: {q2}**
    {answer_2}
    
    [Repeat for each question]
    
    If you need clarification on any of these answers, please let me know.
    
    Was this helpful?
    👍 [Yes, this helped]  |  👎 [No, this didn't help]
    
    ⓘ The information above was generated by an AI system. While reviewed for accuracy, AI can make mistakes. If this answer doesn't resolve your issue, please select "This did not help" to contact our support team.
    """

chat_api_delivery:
  
  try:
    delivery_response = chat_api_client.send_message(
      chat_session_id=session_id,
      message_type="AGENTIC_RESPONSE",
      message_content=formatted_response,
      metadata={
        "query_id": query_id,
        "intent_classification": intent_classification,
        "confidence_score": confidence_score,
        "source_documents": doc_references,
        "ai_generated": true,
        "timestamp": current_timestamp
      }
    )
    
    if (delivery_response.status == "success"):
      message_id = delivery_response.message_id
      action: "log_successful_delivery"
    
    elif (delivery_response.status == "failed"):
      action: "retry_with_exponential_backoff"
      retry_count = 3
      backoff_ms = 1000
  
  except ChatAPIException:
    action: "escalate_to_human"
    reason: "Failed to deliver response via chat API"

output_format:
  {
    "query_id": "reference to original query",
    "message_id": "assigned by chat API",
    "delivery_status": "success|failed",
    "formatted_message": "message sent to chat",
    "delivery_metadata": {
      "timestamp": "when delivered",
      "api_response_time_ms": integer,
      "retry_count": integer
    }
  }

audit_notes: "Delivery status is critical for auditing. Log all messages delivered, failed deliveries, and retry attempts. Track message delivery latency."
```

---

## 🎯 COMPONENT 6: ESCALATION HANDLER

### Rule ID: chat.escalation.handler

```
rule_id: chat.escalation.handler
component: Escalation & Human Review Handler Module
purpose: Route queries to human Vivli admins when AI cannot handle them

trigger_conditions:
  1. Confidence score below threshold (< 0.6)
  2. No relevant documents found
  3. Hallucination detected in LLM response
  4. Researcher manually triggers "This did not help"
  5. Researcher types escalation keywords: "escalate", "human", "help", "staff"
  6. API errors preventing data fetch
  7. Multi-intent query with conflicting routes

escalation_logic:

  if (automatic_escalation_trigger == true):
    
    escalation_reason = determine_reason([
      "low_confidence",
      "no_docs_found",
      "hallucination_detected",
      "api_error",
      "multi_intent_conflict"
    ])
    
    escalation_message = format_escalation_message(
      original_query=researcher_query,
      researcher_id=researcher_id,
      researcher_name=researcher_name,
      reason=escalation_reason,
      timestamp=current_timestamp
    )
    
    escalation_message_formatted = f"""
    [VIVLI-ESCALATION] Researcher {researcher_name} ({researcher_id}) has a question that needs human review.
    
    Original query: '{original_query}'
    
    Reason for escalation: {escalation_reason}
    
    Query ID: {query_id}
    Data Request ID: {if_available}
    
    Timestamp: {timestamp}
    
    Status: Pending Vivli admin response
    """

  elif (manual_escalation_trigger == true):
    
    escalation_reason = "Researcher clicked 'This did not help' button"
    
    escalation_message_formatted = f"""
    [VIVLI-ESCALATION] Researcher {researcher_name} ({researcher_id}) indicated the AI response did not meet their needs.
    
    Original query: '{original_query}'
    AI response provided: '{previous_ai_response}' (first 200 chars)
    
    Query ID: {query_id}
    Data Request ID: {if_available}
    
    Researcher feedback: [if they provided text]
    
    Timestamp: {timestamp}
    
    Status: Pending Vivli admin response
    """

notification_delivery:
  
  # Send escalation notification to Vivli admin email
  email_config = {
    "service": "SendGrid OR Microsoft 365 SMTP",
    "recipient": "vivli-support@vivli.org",
    "subject": f"[ESCALATION] Query from {researcher_name}",
    "body": escalation_message_formatted,
    "priority": "normal"
  }
  
  email_status = email_client.send(email_config)
  
  if (email_status.sent):
    action: "log_escalation_sent"
    log_entry = {
      "escalation_id": generate_uuid(),
      "timestamp": current_timestamp,
      "researcher_id": researcher_id,
      "reason": escalation_reason,
      "email_sent": true
    }
  
  else:
    action: "retry_email_with_backoff"
    retry_attempts = 3

confirmation_message_to_researcher:
  
  message_to_send = """
  Thank you for reaching out. A Vivli Administrator has been notified of your question and will review it shortly.
  
  We typically respond to escalated queries within 24 hours during business days.
  
  Your query ID is: {query_id}
  
  In the meantime, feel free to check out our FAQs or contact us if you have any urgent concerns.
  """
  
  chat_api_client.send_message(
    session_id=session_id,
    message_content=message_to_send,
    message_type="SYSTEM_MESSAGE"
  )

admin_review_workflow:
  
  vivli_admin receives email notification
  
  admin_actions = [
    1. "Read original query in escalation message",
    2. "Access researcher's chat history via existing Vivli chat UI",
    3. "Review data request if applicable",
    4. "Compose response",
    5. "Send response through Vivli chat interface"
  ]
  
  note: "No new admin UI required - use existing Vivli chat interface for responses"

output_format:
  {
    "escalation_id": "unique_escalation_identifier",
    "query_id": "reference to original query",
    "escalation_reason": "reason from trigger conditions",
    "escalation_status": "sent|pending|acknowledged",
    "notification_delivery": {
      "email_sent": boolean,
      "timestamp": "when sent",
      "recipient": "vivli-support@vivli.org",
      "retry_count": integer
    },
    "researcher_confirmation": {
      "message_sent": boolean,
      "confirmation_timestamp": "timestamp"
    }
  }

audit_notes: "Every escalation must be logged with reason, timestamp, and notification status. This data helps identify patterns in query types that require human intervention and informs model improvement strategies."
```

---

## 🎯 COMPONENT 7: FEEDBACK & LOGGING

### Rule ID: chat.feedback.logging

```
rule_id: chat.feedback.logging
component: Feedback Collection & Logging Module
purpose: Capture user feedback and log all interactions for auditing and improvement

field_path: researcher_interaction_data
context_fields:
  - query_id: from intent classification
  - response_id: from response delivery
  - session_id: from session context

feedback_collection_logic:
  
  # Feedback mechanism presented with every response
  feedback_options = {
    "thumbs_up": "Yes, this helped",
    "thumbs_down": "No, this didn't help",
    "escalation_link": "Connect me with Vivli team"
  }
  
  researcher_action = wait_for_user_feedback(timeout_seconds=86400)  // 24 hours
  
  if (researcher_action == "thumbs_up"):
    feedback_record = {
      "feedback_type": "positive",
      "rating": 5,
      "timestamp": current_timestamp,
      "notes": "User found response helpful"
    }
  
  elif (researcher_action == "thumbs_down"):
    feedback_record = {
      "feedback_type": "negative",
      "rating": 1,
      "timestamp": current_timestamp,
      "notes": "User found response unhelpful",
      "auto_action": "trigger_escalation"
    }
  
  elif (researcher_action == "escalation_link"):
    feedback_record = {
      "feedback_type": "escalation_request",
      "rating": 0,
      "timestamp": current_timestamp,
      "notes": "User requested human review",
      "auto_action": "trigger_escalation"
    }
  
  elif (researcher_action == "timeout"):
    feedback_record = {
      "feedback_type": "no_response",
      "rating": null,
      "timestamp": current_timestamp + 86400,
      "notes": "No feedback provided within 24 hours"
    }

logging_data_model:
  
  interaction_log = {
    // Identifiers
    "query_id": "unique identifier for this query",
    "researcher_id": "vivli researcher id",
    "data_request_id": "if applicable",
    "session_id": "chat session identifier",
    
    // Query Information
    "query_text": "full researcher query",
    "query_timestamp": "when query was submitted",
    "query_length_chars": integer,
    "query_language": "detected language",
    
    // Intent & Routing
    "intent_classification": "FAQ|DATA_REQUEST_RELATED|HYBRID|ESCALATION|UNKNOWN",
    "intent_confidence": 0.0-1.0,
    "routing_decision": "knowledge_base|data_request_api|escalation",
    
    // Retrieval (if FAQ)
    "retrieval_metadata": {
      "docs_searched": integer,
      "docs_retrieved": integer,
      "retrieval_time_ms": integer,
      "max_relevance_score": 0.0-1.0
    },
    
    // API Call (if Data Request)
    "api_metadata": {
      "api_endpoint": "string",
      "api_response_time_ms": integer,
      "api_status_code": integer,
      "data_request_stage": "stage returned"
    },
    
    // LLM Generation
    "llm_metadata": {
      "model": "GPT-4O-mini",
      "prompt_tokens": integer,
      "completion_tokens": integer,
      "generation_time_ms": integer,
      "temperature_used": float,
      "confidence_score": 0.0-1.0
    },
    
    // Response Delivery
    "response_text": "full response sent to researcher",
    "response_format_type": "FAQ|DATA_REQUEST|HYBRID|ESCALATION",
    "response_timestamp": "when response was delivered",
    "delivery_status": "success|failed|escalated",
    
    // Feedback
    "feedback_record": feedback_record,
    
    // Performance & Quality
    "total_latency_ms": "full end-to-end time",
    "hallucination_detected": boolean,
    "validation_status": "passed|failed",
    "quality_metrics": {
      "relevance_score": 0.0-1.0,
      "groundedness_score": 0.0-1.0,
      "accuracy_score": 0.0-1.0
    }
  }

database_storage:
  
  storage_system = "Azure Cosmos DB"
  
  // Store in structured format
  cosmos_db.insert(
    container="agentic_chat_interactions",
    document=interaction_log,
    partition_key=researcher_id
  )
  
  // Also store in blob storage for long-term archive
  blob_storage.upload(
    container="chat_interaction_logs",
    filename=f"{query_id}_{timestamp}.json",
    content=json.serialize(interaction_log)
  )

data_retention_policy:
  
  active_retention: "90 days (hot storage)"
  archive_retention: "7 years (cold storage, for compliance)"
  retention_based_on: "researcher_id and data_request_id for audit trail"

analytics_queries:
  
  # These queries support post-analysis
  queries = [
    1. "Query success rate by intent classification",
    2. "Average response latency by component",
    3. "Most frequently escalated query types",
    4. "Feedback sentiment analysis",
    5. "Hallucination rate by model",
    6. "Knowledge base coverage gaps (where escalations happen)",
    7. "Researcher satisfaction trend over time",
    8. "Common question patterns for knowledge base improvement"
  ]

output_format:
  {
    "log_id": "unique log identifier",
    "storage_status": "stored_successfully|failed",
    "stored_at": {
      "database": "cosmos_db_container",
      "blob": "blob_storage_path",
      "timestamp": current_timestamp
    },
    "log_summary": {
      "query_id": "query_id",
      "feedback_received": "thumbs_up|thumbs_down|escalation_request|no_response",
      "latency_ms": integer,
      "success": boolean
    }
  }

audit_notes: "Logging is critical for system improvement. Every interaction must be logged with complete metadata. This data enables retrospective analysis, model selection, knowledge base improvement, and compliance auditing."
```

---

## 📊 INTEGRATION FLOW SUMMARY

```
INPUT: Researcher Message
       ↓
[1] INTENT CLASSIFICATION
    - Analyze query
    - Classify: FAQ | DATA_REQUEST | HYBRID | ESCALATION
    - Confidence score
       ↓
    ├─ If confidence < 0.6 → Escalate to human
    │
    └─ If confidence >= 0.6 → Route to:
       
       ├─ FAQ Path → [2] KNOWLEDGE BASE RETRIEVAL
       │             - Query vector DB
       │             - Get top-K relevant docs
       │             - Confidence check
       │             ↓
       │             ├─ If docs found (conf >= 0.6) → [4] LLM RESPONSE
       │             └─ If no docs (conf < 0.6) → [6] ESCALATION
       │
       └─ DATA REQUEST PATH → [3] API INTEGRATION
                              - Fetch status from API
                              - Get stage & guidance
                              - Enrich with knowledge base
                              ↓
                              ├─ If API succeeds → [4] LLM RESPONSE
                              └─ If API fails → [6] ESCALATION

[4] LLM RESPONSE GENERATION
    - Format prompt
    - Call LLM (GPT-4O-mini)
    - Validate response (no hallucinations)
    ↓
    ├─ If valid → [5] FORMAT & DELIVERY
    └─ If invalid → [6] ESCALATION

[5] RESPONSE FORMATTING & DELIVERY
    - Format message with AI label
    - Include citations
    - Include feedback buttons
    - Send via Chat API
    ↓
    [7] LOGGING & FEEDBACK
    - Log interaction
    - Store in database
    - Wait for feedback

[6] ESCALATION
    - Format escalation message
    - Send to Vivli admin email
    - Notify researcher
    ↓
    [7] LOGGING & FEEDBACK
    - Log escalation
    - Store in database

[7] FEEDBACK COLLECTION
    - Wait for thumbs up/down
    - Log feedback
    - Store in database
    - Use for analytics

OUTPUT: Interaction logged, researcher updated
```

---

## ✅ KEY PRINCIPLES

1. **Clear Rule IDs**: `component.feature.rule_name` (snake_case)
2. **Field Paths**: `parent.child.property` (dot notation)
3. **Conditional Logic**: `if/elif/else` with clear conditions
4. **Actions**: Always specify what to do (route, continue, escalate, log)
5. **Context**: Document dependencies and related fields
6. **Error Handling**: Always have fallback actions
7. **Auditability**: Log everything with timestamps and IDs
8. **Validation**: Check confidence scores and quality metrics
9. **References**: Link to Guru cards and knowledge base sources
10. **Output Format**: Clear JSON structure with metadata

---

**This pseudo code is ready for development!** 🚀

Each component can be implemented independently and integrated together following the flow diagram.
