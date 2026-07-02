import time
import logging
from typing import Optional
from openai import AzureOpenAI
from httpx import Client
from config import AzureConfig
from models import LLMGenerationResult

logger = logging.getLogger(__name__)


class LLMClient:
    """Azure OpenAI LLM response generation"""

    # System prompts for different intent types
    FAQ_SYSTEM_PROMPT = """You are a helpful Vivli platform assistant. Answer the researcher's question based ONLY on the provided knowledge base documents.

Requirements:
1. Answer clearly and in plain language
2. Reference the source document
3. Keep response under 3 paragraphs
4. If information is incomplete, suggest next steps
5. NEVER fabricate information not in the documents"""

    DATA_REQUEST_SYSTEM_PROMPT = """You are a Vivli platform support assistant. Provide a status update and guidance based on the researcher's data request information.

Requirements:
1. Provide stage-specific guidance
2. Explain what's happening now
3. Explain what comes next
4. If action is needed, clearly state it
5. Be empathetic and professional"""

    def __init__(self):
        # For corporate environments with SSL inspection, bypass verification
        # NOTE: Only for development/testing - DO NOT use in production!
        try:
            http_client = Client(verify=False)
            self.client = AzureOpenAI(
                api_key=AzureConfig.OPENAI_API_KEY,
                api_version=AzureConfig.OPENAI_API_VERSION,
                azure_endpoint=AzureConfig.OPENAI_ENDPOINT,
                http_client=http_client,
            )
        except Exception:
            # Fallback to standard client if SSL bypass fails
            self.client = AzureOpenAI(
                api_key=AzureConfig.OPENAI_API_KEY,
                api_version=AzureConfig.OPENAI_API_VERSION,
                azure_endpoint=AzureConfig.OPENAI_ENDPOINT,
            )
        self.deployment = AzureConfig.LLM_DEPLOYMENT

    async def generate_faq_response(
        self, query: str, context: str, researcher_name: Optional[str] = None
    ) -> LLMGenerationResult:
        """
        Generate FAQ response using retrieved documents.

        Args:
            query: User's question
            context: Formatted retrieved documents
            researcher_name: Optional researcher name for personalization

        Returns:
            LLMGenerationResult with generated answer
        """
        prompt = f"""Knowledge Base Documents:
{context}

Researcher Question: {query}

Answer:"""

        return await self._generate(
            system_prompt=self.FAQ_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

    async def generate_data_request_response(
        self,
        query: str,
        request_id: str,
        current_stage: str,
        stage_description: str,
        researcher_name: Optional[str] = None,
    ) -> LLMGenerationResult:
        """
        Generate data request status response.

        Args:
            query: User's question
            request_id: Data request ID
            current_stage: Current stage of request
            stage_description: Description of current stage
            researcher_name: Optional researcher name

        Returns:
            LLMGenerationResult with generated answer
        """
        prompt = f"""Researcher Name: {researcher_name or 'Researcher'}
Request ID: {request_id}
Current Stage: {current_stage}
Stage Description: {stage_description}

Researcher's Question: {query}

Status Update:"""

        return await self._generate(
            system_prompt=self.DATA_REQUEST_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

    async def _generate(
        self, system_prompt: str, user_prompt: str
    ) -> LLMGenerationResult:
        """
        Generate response using Azure OpenAI.

        Args:
            system_prompt: System message for the LLM
            user_prompt: User prompt with context

        Returns:
            LLMGenerationResult with generated text
        """
        try:
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=AzureConfig.TEMPERATURE,
                max_tokens=AzureConfig.MAX_TOKENS,
                top_p=0.95,
            )

            answer = response.choices[0].message.content.strip()
            elapsed_ms = int((time.time() - start_time) * 1000)

            # Basic validation
            validation_status = "passed"
            if len(answer) < 10:
                validation_status = "failed_with_reason"
                logger.warning("Generated answer too short")

            tokens_used = {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
            }

            logger.info(f"Generated response in {elapsed_ms}ms (tokens: {tokens_used})")

            return LLMGenerationResult(
                answer=answer,
                confidence_score=0.8,  # Default confidence for LLM responses
                validation_status=validation_status,
                tokens_used=tokens_used,
                generation_time_ms=elapsed_ms,
            )

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return LLMGenerationResult(
                answer="",
                confidence_score=0.0,
                validation_status="failed_with_reason",
                generation_time_ms=0,
            )
