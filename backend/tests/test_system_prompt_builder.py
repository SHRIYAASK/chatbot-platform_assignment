from app.shared.llm.message_builder import build_chat_messages
from app.shared.llm.platform_guardrails import PLATFORM_SYSTEM_PROMPT
from app.shared.llm.response_style import GLOBAL_RESPONSE_STYLE
from app.shared.llm.system_prompt_builder import (
    DEFAULT_PROJECT_INSTRUCTIONS,
    build_system_prompt,
)


def test_build_system_prompt_layer_order():
    instructions = "You are an expert Python instructor."
    prompt = build_system_prompt(instructions)

    platform_index = prompt.index("You are an AI assistant operating inside a multi-project AI platform.")
    instructions_index = prompt.index(instructions)
    style_index = prompt.index(GLOBAL_RESPONSE_STYLE)

    assert platform_index < instructions_index < style_index
    assert "INSTRUCTION PRIORITY" in prompt
    assert "PROMPT INJECTION DEFENSE" in prompt


def test_build_system_prompt_uses_default_for_empty_description():
    prompt = build_system_prompt("   ")

    assert DEFAULT_PROJECT_INSTRUCTIONS in prompt
    assert PLATFORM_SYSTEM_PROMPT in prompt
    assert GLOBAL_RESPONSE_STYLE in prompt


def test_build_chat_messages_keeps_history_outside_system_prompt():
    messages = build_chat_messages(
        "You are a nutrition assistant.",
        [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ],
        "What should I eat today?",
    )

    assert messages[0]["role"] == "system"
    assert "You are a nutrition assistant." in messages[0]["content"]
    assert "You are an AI assistant operating inside a multi-project AI platform." in messages[0]["content"]
    assert GLOBAL_RESPONSE_STYLE in messages[0]["content"]
    assert messages[1:] == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
        {"role": "user", "content": "What should I eat today?"},
    ]


def test_build_chat_messages_adds_rag_as_separate_system_message():
    messages = build_chat_messages(
        "You are a legal assistant.",
        [],
        "Explain contracts.",
        rag_context="Use the following project document excerpts.",
    )

    assert messages[0]["role"] == "system"
    assert "You are a legal assistant." in messages[0]["content"]
    assert messages[1] == {
        "role": "system",
        "content": "Use the following project document excerpts.",
    }
    assert messages[2] == {"role": "user", "content": "Explain contracts."}
