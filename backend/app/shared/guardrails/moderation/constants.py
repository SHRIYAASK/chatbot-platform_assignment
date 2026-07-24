from enum import StrEnum


class ModerationCategory(StrEnum):
    SAFE = "SAFE"
    SEXUAL_CONTENT = "SEXUAL_CONTENT"
    VIOLENCE = "VIOLENCE"
    SELF_HARM = "SELF_HARM"
    HATE_HARASSMENT = "HATE_HARASSMENT"
    CYBERSECURITY = "CYBERSECURITY"
    ILLEGAL_ACTIVITIES = "ILLEGAL_ACTIVITIES"
    PRIVACY = "PRIVACY"
    PROMPT_INJECTION = "PROMPT_INJECTION"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ModerationDecision(StrEnum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


BLOCKED_USER_MESSAGE = (
    "I'm sorry, but I can't assist with requests involving harmful, illegal, "
    "abusive, or unsafe activities. If you have another question on a safe topic, "
    "I'd be happy to help."
)
