import re
from dataclasses import dataclass

from app.shared.guardrails.moderation.categories import get_categories_config


@dataclass(frozen=True)
class CategoryRule:
    category: str
    subcategory: str | None
    risk: str
    decision: str | None
    pattern: re.Pattern[str]


def build_category_rules() -> list[CategoryRule]:
    rules: list[CategoryRule] = []
    categories = get_categories_config()

    for category_name, category_config in categories.items():
        if not category_config.get("enabled", True):
            continue

        if category_name == "SAFE":
            continue

        # Top-level category patterns (e.g. prompt injection)
        for pattern in category_config.get("patterns", []):
            rules.append(
                CategoryRule(
                    category=category_name,
                    subcategory=None,
                    risk=category_config.get("default_risk", "HIGH"),
                    decision=category_config.get("default_decision"),
                    pattern=re.compile(re.escape(pattern.lower())),
                )
            )

        for sub_name, sub_config in category_config.get("subcategories", {}).items():
            for pattern in sub_config.get("patterns", []):
                rules.append(
                    CategoryRule(
                        category=category_name,
                        subcategory=sub_name,
                        risk=sub_config.get("risk", "MEDIUM"),
                        decision=sub_config.get("decision"),
                        pattern=re.compile(re.escape(pattern.lower())),
                    )
                )

    rules.sort(
        key=lambda rule: categories.get(rule.category, {}).get("priority", 0),
        reverse=True,
    )
    return rules
