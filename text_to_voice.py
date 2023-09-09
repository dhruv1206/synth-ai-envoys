from gtts import gTTS
import pyttsx3
from googletrans import Translator


def convert_to_speech_in_multiple_languages(prId,phrase, languages):
    translator = Translator()

    for lang in languages:
        try:
            # Translate the input phrase to the target language
            translated_phrase = translator.translate(phrase, dest=lang).text

            # Use gTTS for other languages
            tts = gTTS(text=translated_phrase, lang=lang, )
            tts.save(f"{prId}_output_{lang}.mp3")
            # Play the audio here using a library like pygame or subprocess
            print(f"Saved and played audio for {lang}.")
        except Exception as e:
            print(f"Error :{e} for language:{lang}")
            continue


if __name__ == "__main__":
    # Example usage:
    phrase_to_convert = "Hello, how are you?"
    languages_to_convert = ["en", "hi", "bn", "te", "mr", "ta", "ur", "gu", "ml", "kn"]
    convert_to_speech_in_multiple_languages("sdfg",phrase_to_convert, languages_to_convert)
