from deep_translator import GoogleTranslator

LANG = {
    "English (US)": "en",
    "English (UK)": "en",
    "Hindi (India)": "hi",
    "Spanish (Spain)": "es",
    "Spanish (Mexico)": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh-CN",
    "Arabic": "ar",
    "Portuguese (Brazil)": "pt",
    "Portuguese (Portugal)": "pt"
}

def translate_text(text, language):
    if not text.strip():
        return ""
    return GoogleTranslator(
        source="auto",
        target=LANG.get(language, "en")
    ).translate(text)
