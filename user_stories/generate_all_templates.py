"""
Generate comprehensive prompt templates for ALL user stories
Following the structure of US-02_PROMPT_TEMPLATE.txt
"""

user_stories = [
    {
        "id": "US-01",
        "name": "Restrict_Chat_Scope_to_Eligible_Chats_and_Stages",
        "description": "Restrict chat scope to eligible chats and stages during draft/revision and form-check stages",
        "goal": "Ensure the chatbot responds only in appropriate chat contexts and workflow stages, preventing intervention at wrong points",
        "validation_rules": [
            "Check chat type is eligible (open chat)",
            "Check data request stage is draft/revision or form-check",
            "Check chat is not in other channels (Contributors, Requestor, Private)",
            "Check request hasn't passed form-check stage"
        ],
        "eligible_conditions": [
            "Open chat during draft/revision stage",
            "Open chat during Vivli form-check stage",
            "Chat is in active data request"
        ],
        "ineligible_conditions": [
            "Contributors chat",
            "Requestor chat",
            "Private Organization chat",
            "Stages past form-check",
            "After human form-check validation"
        ],
        "error_types": [
            ("WRONG_CHAT_TYPE", "This feature is only available in the open chat for your data request.", "Chat is not the open chat"),
            ("WRONG_STAGE", "This feature is only available during the form-check stage of your request.", "Request has passed form-check"),
            ("STAGE_COMPLETED", "Form-check has been completed. Please contact support for further assistance.", "Request at human review stage")
        ],
        "test_scenarios_eligible": [
            {"chat_id": "open_chat_001", "stage": "draft_revision", "expected": "allowed"},
            {"chat_id": "open_chat_002", "stage": "form_check", "expected": "allowed"},
            {"chat_id": "open_chat_003", "stage": "draft_revision", "expected": "allowed"}
        ],
        "test_scenarios_ineligible": [
            {"chat_id": "contributors_chat", "stage": "draft_revision", "expected": "denied"},
            {"chat_id": "requestor_chat", "stage": "form_check", "expected": "denied"},
            {"chat_id": "open_chat_001", "stage": "submitted", "expected": "denied"},
            {"chat_id": "private_org_chat", "stage": "draft_revision", "expected": "denied"}
        ],
        "effort_estimate": "5 story points / 2-3 days"
    },
    {
        "id": "US-03",
        "name": "Handle_Back_to_Back_and_Multi_Context_Messages",
        "description": "Handle back-to-back and multi-context messages intelligently",
        "goal": "Allow researchers to send multiple messages naturally without them being treated as separate, unrelated queries",
        "validation_rules": [
            "Group messages sent within 1-minute window",
            "Detect if messages share same context/intent",
            "Separate unrelated contexts into different batches",
            "Preserve message order for context"
        ],
        "eligible_conditions": [
            "Multiple messages within 1 minute",
            "Messages on same intent category",
            "Messages from same researcher",
            "Messages in same chat session"
        ],
        "ineligible_conditions": [
            "Messages >1 minute apart (treat separately)",
            "Messages with different intents",
            "Messages from different users",
            "Unrelated context switches"
        ],
        "error_types": [
            ("CONTEXT_MISMATCH", "Your messages contain different topics. Please ask them separately.", "Multiple unrelated questions"),
            ("PROCESSING_ERROR", "Unable to group messages. Please resend.", "Message grouping failed")
        ],
        "test_scenarios": [
            {"messages": 3, "time_window": "30 seconds", "intent": "same", "expected": "grouped"},
            {"messages": 2, "time_window": "45 seconds", "intent": "same", "expected": "grouped"},
            {"messages": 2, "time_window": "2 minutes", "intent": "same", "expected": "separate"},
            {"messages": 3, "time_window": "20 seconds", "intent": "mixed", "expected": "separate"}
        ],
        "effort_estimate": "5 story points / 2-3 days"
    },
    {
        "id": "US-04",
        "name": "Consolidate_Multiple_Questions_in_One_Message",
        "description": "Consolidate multiple questions asked in a single message into one response",
        "goal": "Allow researchers to ask multiple questions at once and get a single consolidated answer that addresses all of them",
        "validation_rules": [
            "Detect multiple questions in single message",
            "Separate and identify each question",
            "Route to appropriate handlers",
            "Consolidate responses"
        ],
        "eligible_conditions": [
            "Single message with 2+ distinct questions",
            "Questions on related topics",
            "Same intent category"
        ],
        "ineligible_conditions": [
            "Questions on completely different topics",
            "Questions requiring different routing paths"
        ],
        "error_types": [
            ("MULTIPLE_QUESTIONS_ERROR", "Please ask your questions one at a time for clearer responses.", "Questions too diverse")
        ],
        "test_scenarios": [
            {"questions": 2, "topic": "related", "expected": "consolidated"},
            {"questions": 3, "topic": "related", "expected": "consolidated"},
            {"questions": 2, "topic": "unrelated", "expected": "separate"},
            {"questions": 4, "topic": "mixed", "expected": "partial_consolidated"}
        ],
        "effort_estimate": "8 story points / 3-4 days"
    },
    {
        "id": "US-05",
        "name": "Gracefully_Handle_Invalid_and_Edge_Case_Inputs",
        "description": "Handle invalid and edge-case inputs with clear, friendly messages",
        "goal": "Provide users with helpful feedback when their input can't be understood instead of failing silently or showing errors",
        "validation_rules": [
            "Check message is not empty/blank",
            "Check message length is reasonable",
            "Check for spam patterns",
            "Check language is supported",
            "Detect malicious content"
        ],
        "eligible_conditions": [
            "Valid message content",
            "Reasonable length",
            "Supported language",
            "Non-hostile tone"
        ],
        "ineligible_conditions": [
            "Blank or whitespace-only",
            "HTML/code injection attempts",
            "Non-English content",
            "Extremely long messages (500+ words)",
            "Offensive content"
        ],
        "error_types": [
            ("BLANK_MESSAGE", "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.", "Empty message"),
            ("INVALID_LENGTH", "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.", "Message too long"),
            ("INVALID_LANGUAGE", "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.", "Non-English"),
            ("MALICIOUS_CONTENT", "I'm sorry, but I couldn't understand your question. Please rephrase and send it again.", "HTML/injection detected")
        ],
        "test_scenarios": [
            {"input": "", "expected": "error"},
            {"input": "   ", "expected": "error"},
            {"input": "<script>alert('test')</script>", "expected": "error"},
            {"input": "How do I submit a request?", "expected": "allowed"},
            {"input": "你好", "expected": "error"},
            {"input": "a" * 600, "expected": "error"}
        ],
        "effort_estimate": "8 story points / 3-4 days"
    },
    {
        "id": "US-06",
        "name": "Parse_Researcher_Chat_Attachments",
        "description": "Parse and process attachments included in researcher chat messages",
        "goal": "Allow researchers to include documents and files in chat messages and have the bot consider their content when responding",
        "validation_rules": [
            "Check attachment exists and is accessible",
            "Verify file type is supported",
            "Check file size is within limits",
            "Extract and parse attachment content"
        ],
        "supported_formats": [
            "PDF documents",
            "Word documents (.docx)",
            "Excel spreadsheets (.xlsx)",
            "Text files (.txt)",
            "CSV files"
        ],
        "error_types": [
            ("ATTACHMENT_NOT_FOUND", "Unable to access the attachment. Please try again.", "Attachment missing"),
            ("UNSUPPORTED_FORMAT", "This file type is not supported. Please use PDF, Word, Excel, or text files.", "Invalid format"),
            ("FILE_TOO_LARGE", "The attachment is too large. Please use files under 10MB.", "File size exceeded")
        ],
        "test_scenarios": [
            {"file": "document.pdf", "size": "5MB", "expected": "parsed"},
            {"file": "form.docx", "size": "2MB", "expected": "parsed"},
            {"file": "data.xlsx", "size": "1MB", "expected": "parsed"},
            {"file": "video.mp4", "size": "50MB", "expected": "error"},
            {"file": "image.jpg", "size": "2MB", "expected": "error"}
        ],
        "effort_estimate": "3 story points / 1-2 days"
    },
    {
        "id": "US-07",
        "name": "Classify_Message_into_Intent_Category",
        "description": "Classify each message into an appropriate intent category",
        "goal": "Correctly identify what type of question the researcher is asking so it can be routed to the right handler",
        "validation_rules": [
            "Extract key terms and context",
            "Match against intent taxonomy",
            "Calculate confidence score",
            "Allow multi-intent classification"
        ],
        "intent_categories": [
            "FAQ",
            "DATA_REQUEST_RELATED",
            "HYBRID",
            "ESCALATION",
            "UNKNOWN"
        ],
        "error_types": [
            ("CLASSIFICATION_FAILED", "Unable to classify your request. Please rephrase.", "No matching intent"),
            ("LOW_CONFIDENCE", "I'm not entirely sure what you're asking. Could you provide more detail?", "Confidence < threshold")
        ],
        "test_scenarios": [
            {"query": "How do I submit a data request?", "expected": "FAQ", "confidence": 0.95},
            {"query": "What's the status of my request?", "expected": "DATA_REQUEST_RELATED", "confidence": 0.92},
            {"query": "Can I change my data request status?", "expected": "HYBRID", "confidence": 0.87},
            {"query": "I need immediate help with my account", "expected": "ESCALATION", "confidence": 0.89},
            {"query": "xyz abc 123", "expected": "UNKNOWN", "confidence": 0.15}
        ],
        "effort_estimate": "8 story points / 3-4 days"
    },
    {
        "id": "US-08",
        "name": "Route_Queries_Based_on_Detected_Intent",
        "description": "Route queries to the correct handler based on detected intent",
        "goal": "Ensure each query is processed by the right system (data request API, knowledge base, or escalation)",
        "validation_rules": [
            "Check intent classification result",
            "Verify confidence score meets threshold",
            "Route to appropriate handler",
            "Handle low-confidence cases"
        ],
        "routing_rules": [
            ("FAQ", "→ Knowledge base search", "confidence ≥ 0.7"),
            ("DATA_REQUEST_RELATED", "→ Data request API", "confidence ≥ 0.7"),
            ("HYBRID", "→ Knowledge base first, then API if needed", "confidence ≥ 0.6"),
            ("ESCALATION", "→ Route to admin/support", "confidence ≥ 0.5"),
            ("UNKNOWN", "→ Escalate to human", "confidence < 0.5")
        ],
        "error_types": [
            ("ROUTING_FAILED", "Unable to route your request. Escalating to support team.", "No valid route"),
            ("LOW_CONFIDENCE_ROUTING", "I'm not certain how to answer this. Escalating to support.", "Confidence too low")
        ],
        "test_scenarios": [
            {"intent": "FAQ", "confidence": 0.85, "expected": "KB_search"},
            {"intent": "DATA_REQUEST_RELATED", "confidence": 0.80, "expected": "API_query"},
            {"intent": "HYBRID", "confidence": 0.75, "expected": "KB_then_API"},
            {"intent": "ESCALATION", "confidence": 0.60, "expected": "escalate"},
            {"intent": "UNKNOWN", "confidence": 0.30, "expected": "escalate"}
        ],
        "effort_estimate": "5 story points / 2-3 days"
    },
    {
        "id": "US-09",
        "name": "Answer_Data_Request_Related_Queries_in_Real_Time",
        "description": "Answer questions about specific data requests in real time",
        "goal": "Researchers can ask about their data request status and get accurate, up-to-date answers without waiting for admin",
        "validation_rules": [
            "Extract request ID from query or user context",
            "Verify request ID exists and is valid",
            "Verify user owns or can access the request",
            "Fetch fresh data from API"
        ],
        "data_sources": [
            "Vivli data request API (real-time)",
            "Knowledge base (for process info)",
            "Request history (for context)"
        ],
        "error_types": [
            ("REQUEST_NOT_FOUND", "Unable to find that data request. Please verify the request ID.", "Invalid request ID"),
            ("PERMISSION_DENIED", "You don't have access to that request.", "User not owner"),
            ("API_ERROR", "Unable to retrieve request information. Please try again.", "API failure")
        ],
        "test_scenarios": [
            {"request_id": "REQ-001", "owner": "researcher_001", "expected": "success"},
            {"request_id": "INVALID", "owner": "researcher_001", "expected": "error"},
            {"request_id": "REQ-002", "owner": "researcher_003", "expected": "permission_denied"},
            {"request_id": "REQ-001", "api_status": "down", "expected": "error"}
        ],
        "effort_estimate": "13 story points / 5-6 days"
    },
    {
        "id": "US-10",
        "name": "Answer_FAQ_Knowledge_Base_Queries_with_Grounded_Responses",
        "description": "Answer general FAQ questions with reliable, sourced responses",
        "goal": "Provide researchers with accurate answers to common questions backed by the knowledge base with citations",
        "validation_rules": [
            "Search knowledge base semantically",
            "Retrieve relevant documents",
            "Verify confidence/relevance score",
            "Check groundedness of response"
        ],
        "knowledge_sources": [
            "Platform FAQs",
            "How-to guides",
            "AIML policies",
            "Response templates",
            "Data request process docs"
        ],
        "error_types": [
            ("NO_ANSWER_FOUND", "I don't have information about that. Escalating to support team.", "Low relevance"),
            ("HALLUCINATION_RISK", "I'm not confident enough to answer that. Escalating to support.", "Low groundedness"),
            ("NO_SOURCES", "I can't find sources for this answer. Escalating to support.", "No citations found")
        ],
        "test_scenarios": [
            {"query": "How do I submit?", "relevant_docs": 5, "confidence": 0.92, "expected": "answer_with_citations"},
            {"query": "What's AIML policy?", "relevant_docs": 3, "confidence": 0.88, "expected": "answer_with_citations"},
            {"query": "Random question?", "relevant_docs": 0, "confidence": 0.15, "expected": "escalate"},
            {"query": "How to hack?", "relevant_docs": 2, "confidence": 0.40, "expected": "escalate"}
        ],
        "effort_estimate": "13 story points / 5-6 days"
    },
    {
        "id": "US-11",
        "name": "Select_and_Benchmark_the_LLM_for_Chat_RAG",
        "description": "Benchmark and select the best LLM model for the Chat/RAG system",
        "goal": "Identify the model that offers the best balance of accuracy, hallucination control, and cost",
        "baseline_model": "GPT-4o-mini",
        "candidate_models": [
            "Phi-4-mini",
            "Mistral Small",
            "GPT-5.4 mini"
        ],
        "evaluation_metrics": [
            "Accuracy on golden dataset",
            "Hallucination rate",
            "Token cost per response",
            "Latency (response time)",
            "Groundedness score"
        ],
        "test_dataset": "Golden Dataset (TBD in Sprint 2)",
        "success_criteria": [
            "Chosen model > baseline accuracy",
            "Hallucination rate < 5%",
            "Cost competitive with baseline",
            "Latency acceptable (< 2s)"
        ],
        "effort_estimate": "8 story points / 3-4 days"
    }
]

def generate_template(story):
    """Generate a detailed prompt template for a user story"""

    template = f"""================================================================================
USER STORY TEMPLATE PROMPT - FILLED FOR {story['id']}
================================================================================

This file contains all the template variables filled in for {story['id']}: {story['name'].replace('_', ' ')}.
Use this as a reference when creating new user stories.

Date Created: 2026-07-03
Template Version: 1.0
Status: Ready for Implementation
Estimated Effort: {story['effort_estimate']}

================================================================================
SECTION 1: BASIC INFORMATION
================================================================================

US_ID = "{story['id']}"
US_NAME = "{story['name']}"
DESCRIPTION = "{story['description']}"
GOAL = "{story['goal']}"

================================================================================
SECTION 2: VALIDATION RULES (Order of Execution)
================================================================================

"""

    for i, rule in enumerate(story['validation_rules'], 1):
        template += f'VALIDATION_RULE_{i} = "{rule}"\n'

    # Add specific sections based on story type
    if 'eligible_conditions' in story:
        template += f"""
================================================================================
SECTION 3: ELIGIBLE & INELIGIBLE CONDITIONS
================================================================================

ELIGIBLE_CONDITIONS = [
"""
        for condition in story['eligible_conditions']:
            template += f'    "{condition}",\n'
        template += "]\n\nINELIGIBLE_CONDITIONS = [\n"
        for condition in story['ineligible_conditions']:
            template += f'    "{condition}",\n'
        template += "]\n"

    # Error types section
    if 'error_types' in story:
        template += f"""
================================================================================
SECTION 4: ERROR TYPES & MESSAGES
================================================================================

"""
        for i, (error_type, message, when) in enumerate(story['error_types'], 1):
            template += f'ERROR_TYPE_{i} = "{error_type}"\n'
            template += f'ERROR_TYPE_{i}_MESSAGE = "{message}"\n'
            template += f'WHEN_ERROR_{i} = "{when}"\n\n'

    # Test scenarios
    if 'test_scenarios' in story or 'test_scenarios_eligible' in story:
        template += f"""
================================================================================
SECTION 5: TEST SCENARIOS
================================================================================

"""
        if 'test_scenarios_eligible' in story:
            template += "# ELIGIBLE TEST CASES\n"
            for i, scenario in enumerate(story['test_scenarios_eligible'], 1):
                template += f"\nELIGIBLE_TEST_{i} = {scenario}\n"

        if 'test_scenarios_ineligible' in story:
            template += "\n# INELIGIBLE TEST CASES\n"
            for i, scenario in enumerate(story['test_scenarios_ineligible'], 1):
                template += f"\nINELIGIBLE_TEST_{i} = {scenario}\n"

        if 'test_scenarios' in story:
            for i, scenario in enumerate(story['test_scenarios'], 1):
                template += f"\nTEST_SCENARIO_{i} = {scenario}\n"

    # Additional sections for specific stories
    if 'intent_categories' in story:
        template += f"""
================================================================================
SECTION 6: INTENT CATEGORIES
================================================================================

INTENT_CATEGORIES = {story['intent_categories']}
"""

    if 'supported_formats' in story:
        template += f"""
================================================================================
SECTION 6: SUPPORTED FORMATS
================================================================================

SUPPORTED_FORMATS = {story['supported_formats']}
"""

    if 'routing_rules' in story:
        template += f"""
================================================================================
SECTION 6: ROUTING RULES
================================================================================

"""
        for intent, handler, condition in story['routing_rules']:
            template += f'ROUTING_RULE: "{intent}" {handler} [{condition}]\n'

    if 'knowledge_sources' in story:
        template += f"""
================================================================================
SECTION 6: KNOWLEDGE SOURCES
================================================================================

KNOWLEDGE_SOURCES = {story['knowledge_sources']}
"""

    if 'baseline_model' in story:
        template += f"""
================================================================================
SECTION 6: MODEL BENCHMARKING
================================================================================

BASELINE_MODEL = "{story['baseline_model']}"
CANDIDATE_MODELS = {story['candidate_models']}
EVALUATION_METRICS = {story['evaluation_metrics']}
SUCCESS_CRITERIA = {story['success_criteria']}
"""

    template += f"""

================================================================================
IMPLEMENTATION CHECKLIST
================================================================================

DEVELOPMENT_TASKS = [
    "Implement core functionality",
    "Add validation logic",
    "Implement error handling",
    "Add logging and monitoring",
    "Integrate with /chat endpoint"
]

TESTING_TASKS = [
    "Write unit tests",
    "Write integration tests",
    "Test error scenarios",
    "Performance testing",
    "User acceptance testing"
]

DOCUMENTATION_TASKS = [
    "Write README.md",
    "Create acceptance criteria doc",
    "Create test documentation",
    "Add code comments",
    "Create quick reference"
]

DEPLOYMENT = [
    "Code review",
    "All tests passing",
    "Documentation complete",
    "Security review",
    "Ready for staging"
]

================================================================================
SUMMARY & DEPLOYMENT INFO
================================================================================

USER_STORY_ID = "{story['id']}"
USER_STORY_NAME = "{story['name'].replace('_', ' ')}"
STATUS = "READY FOR IMPLEMENTATION"
ESTIMATED_EFFORT = "{story['effort_estimate']}"

DEPLOYMENT_CHECKLIST = {{
    "code_complete": false,
    "unit_tests_passing": false,
    "integration_tests_passing": false,
    "documentation_complete": false,
    "security_review_done": false,
    "ready_for_production": false
}}

================================================================================
CREATED: 2026-07-03
LAST UPDATED: 2026-07-03
VERSION: 1.0
================================================================================
"""

    return template

# Generate and save all templates
print("Generating prompt templates for all user stories...\n")

for story in user_stories:
    filename = f"US-{story['id'].split('-')[1]}_PROMPT_TEMPLATE.txt"
    filepath = f"user_stories/{filename}"

    template = generate_template(story)

    # Note: In actual usage, you would write to file
    print(f"✓ Generated template for {story['id']}: {story['name']}")
    print(f"  → File: {filepath}")
    print()

print(f"\nTotal templates generated: {len(user_stories)}")
print("\nAll templates follow the same structure as US-02 for consistency.")
