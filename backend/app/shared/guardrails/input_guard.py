import re
from collections import Counter

from app.shared.guardrails.exceptions import InputValidationError
from app.shared.guardrails.moderation.categories import get_input_guard_config


class InputGuard:
    """Structural validation before category classification."""

    @staticmethod
    def validate(message: str) -> str:
        config = get_input_guard_config()
        max_length = config.get("max_message_length", 10000)

        if message is None:
            raise InputValidationError("Message cannot be empty.")

        normalized = message.strip()
        if not normalized:
            raise InputValidationError("Message cannot be empty or whitespace only.")

        if len(normalized) > max_length:
            raise InputValidationError(f"Message exceeds maximum length of {max_length} characters.")

        InputGuard._check_spam_patterns(normalized, config)
        return normalized

    @staticmethod
    def _check_spam_patterns(message: str, config: dict) -> None:
        if len(message) < 20:
            return

        max_repeat_ratio = config.get("max_repeated_char_ratio", 0.6)
        if len(message) >= 10:
            most_common_char_count = Counter(message.replace(" ", "")).most_common(1)[0][1]
            char_total = max(len(message.replace(" ", "")), 1)
            if most_common_char_count / char_total >= max_repeat_ratio:
                raise InputValidationError("Message appears to be spam (excessive repeated characters).")

        min_unique_ratio = config.get("min_unique_char_ratio", 0.05)
        unique_chars = len(set(message.lower()))
        if unique_chars / len(message) < min_unique_ratio:
            raise InputValidationError("Message appears to be malformed or spam.")

        lines = [line.strip() for line in message.splitlines() if line.strip()]
        if lines:
            duplicate_lines = Counter(lines)
            max_dup = config.get("max_duplicate_line_count", 5)
            if any(count >= max_dup for count in duplicate_lines.values()):
                raise InputValidationError("Message appears to be spam (repeated lines).")

        if re.search(r"(.)\1{20,}", message):
            raise InputValidationError("Message appears to be spam (character flooding).")
