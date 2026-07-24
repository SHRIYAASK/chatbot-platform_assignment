import json
from functools import lru_cache
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parent / "moderation_config.json"


@lru_cache(maxsize=1)
def load_moderation_config() -> dict[str, Any]:
    with open(CONFIG_PATH, encoding="utf-8") as config_file:
        return json.load(config_file)


def reload_moderation_config() -> dict[str, Any]:
    load_moderation_config.cache_clear()
    return load_moderation_config()


def get_blocked_user_message() -> str:
    return load_moderation_config().get("blocked_user_message", "")


def get_decision_matrix() -> dict[str, str]:
    return load_moderation_config().get("decision_matrix", {})


def get_categories_config() -> dict[str, Any]:
    return load_moderation_config().get("categories", {})


def get_input_guard_config() -> dict[str, Any]:
    return load_moderation_config().get("input_guard", {})


def get_output_guard_config() -> dict[str, Any]:
    return load_moderation_config().get("output_guard", {})
