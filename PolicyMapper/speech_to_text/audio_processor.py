import os
import speech_recognition as sr
from pydub import AudioSegment

class AudioProcessor:
    """Handles loading and preprocessing of audio files for speech recognition."""

    def __init__(self, file_path):
        self.file_path = file_path

    def convert_to_wav(self):
        """Converts audio to WAV format (if needed) for compatibility."""
        if self.file_path.endswith('.wav'):
            return self.file_path  # Already in WAV format
        
        audio = AudioSegment.from_file(self.file_path)
        wav_path = self.file_path.rsplit(".", 1)[0] + ".wav"
        audio.export(wav_path, format="wav")
        return wav_path

    def load_audio(self):
        """Loads an audio file and returns a SpeechRecognition AudioFile object."""
        wav_path = self.convert_to_wav()
        recognizer = sr.Recognizer()

        with sr.AudioFile(wav_path) as source:
            recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
            audio_data = recognizer.record(source)  # Read entire audio file
        
        return recognizer, audio_data
