import speech_recognition as sr
from speech_to_text.config import SPEECH_RECOGNITION_CONFIG
from speech_to_text.audio_processor import AudioProcessor

class SpeechToText:
    """Handles speech-to-text conversion using SpeechRecognition."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.recognizer = sr.Recognizer()

    def transcribe_audio(self):
        """Converts speech from an audio file into text."""
        audio_processor = AudioProcessor(self.file_path)
        recognizer, audio_data = audio_processor.load_audio()

        try:
            text = recognizer.recognize_google(audio_data, language=SPEECH_RECOGNITION_CONFIG["language"])
            return text
        except sr.UnknownValueError:
            return "Error: Speech was unclear, could not transcribe."
        except sr.RequestError:
            return "Error: Could not reach the speech recognition service."

