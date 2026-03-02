from gtts import gTTS
import uuid
import os

def speak(text, lang="en"):
    if not text.strip():
        return None

    os.makedirs("static/tts", exist_ok=True)
    filename = f"static/tts/{uuid.uuid4().hex}.mp3"

    gTTS(text=text[:300], lang=lang).save(filename)
    return "/" + filename
