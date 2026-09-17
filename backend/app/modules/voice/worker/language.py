"""Map transcript script to Sarvam STT/TTS language codes."""

DEFAULT_LANGUAGE = "en-IN"
STT_LANGUAGE = "unknown"

LANGUAGE_NAMES: dict[str, str] = {
    "bn-IN": "Bengali",
    "en-IN": "English",
    "gu-IN": "Gujarati",
    "hi-IN": "Hindi",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "od-IN": "Odia",
    "pa-IN": "Punjabi",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
}

# (start, end inclusive, BCP-47) — first matching character wins.
_SCRIPT_RANGES: tuple[tuple[int, int, str], ...] = (
    (0x0900, 0x097F, "hi-IN"),  # Devanagari
    (0x0980, 0x09FF, "bn-IN"),  # Bengali
    (0x0A00, 0x0A7F, "pa-IN"),  # Gurmukhi
    (0x0A80, 0x0AFF, "gu-IN"),  # Gujarati
    (0x0B00, 0x0B7F, "od-IN"),  # Odia
    (0x0B80, 0x0BFF, "ta-IN"),  # Tamil
    (0x0C00, 0x0C7F, "te-IN"),  # Telugu
    (0x0C80, 0x0CFF, "kn-IN"),  # Kannada
    (0x0D00, 0x0D7F, "ml-IN"),  # Malayalam
)


def detect_language(text: str) -> str:
    for char in text:
        code = ord(char)
        for start, end, language in _SCRIPT_RANGES:
            if start <= code <= end:
                return language
    return DEFAULT_LANGUAGE


def response_language_instruction(language_code: str) -> str:
    name = LANGUAGE_NAMES.get(language_code, language_code)
    return (
        f"The user spoke {name}. Reply entirely in {name} using the same script as the user. "
        "Do not translate the user's message into English unless they spoke English."
    )
