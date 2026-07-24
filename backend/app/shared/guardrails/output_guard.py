import re

from app.shared.guardrails.moderation.categories import get_output_guard_config


class OutputGuard:
    """Sanitize LLM responses before returning to clients."""

    UNSAFE_HTML_PATTERN = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)

    @classmethod
    def sanitize(cls, content: str) -> str:
        if not content:
            return content

        config = get_output_guard_config()
        sanitized = content

        sanitized = cls.UNSAFE_HTML_PATTERN.sub("[removed]", sanitized)

        for pattern in config.get("redact_patterns", []):
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)

        sanitized = cls._fix_broken_markdown_fences(sanitized)

        max_length = config.get("max_response_length", 50000)
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "\n\n[Response truncated for length.]"

        return sanitized

    @staticmethod
    def _fix_broken_markdown_fences(content: str) -> str:
        fence_count = content.count("```")
        if fence_count % 2 != 0:
            return content + "\n```"
        return content
