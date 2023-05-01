import tempfile
from gtts import gTTS


def text_to_audio(text, lang):
    tts = gTTS(text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        temp_file = fp.name
    tts.save(temp_file)
    return temp_file