from app.modules.chat.services.llm_service import LLMService, LLMServiceError
from app.shared.validators import validate_project_description

REWRITE_SYSTEM_PROMPT = """You rewrite project instructions for an AI assistant.

Improve clarity, structure, and specificity while preserving the user's intent.
Write concise instruction-style text suitable as a system prompt for a chatbot.
Do not use markdown tables, blog-style headings, or decorative formatting.
Output only the rewritten instructions with no preamble or explanation.
Stay within 500 characters."""


class DescriptionRewriteService:
    @staticmethod
    async def rewrite_description(description: str) -> str:
        normalized = validate_project_description(description)
        messages = [
            {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
            {"role": "user", "content": normalized},
        ]

        try:
            result = await LLMService.generate_reply(messages)
        except LLMServiceError:
            raise

        rewritten = result.content.strip()
        if len(rewritten) > 500:
            rewritten = rewritten[:500].rstrip()

        return validate_project_description(rewritten)
