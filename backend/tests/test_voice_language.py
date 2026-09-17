from app.modules.voice.worker.language import (
    detect_language,
    response_language_instruction,
)


def test_detect_language_tamil():
    assert detect_language("என்ன பிரச்சனை உனக்கு") == "ta-IN"


def test_detect_language_hindi():
    assert detect_language("आपकी समस्या क्या है") == "hi-IN"


def test_detect_language_english():
    assert detect_language("What is the problem, sir?") == "en-IN"


def test_detect_language_mixed_uses_first_indic_script():
    assert detect_language("Hello என்ன problem") == "ta-IN"


def test_response_language_instruction_tamil():
    instruction = response_language_instruction("ta-IN")
    assert "Tamil" in instruction
    assert "English" in instruction
