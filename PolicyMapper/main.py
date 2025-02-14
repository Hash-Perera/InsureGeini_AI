from speech_to_text.speech_to_text import SpeechToText

if __name__ == "__main__":
    audio_file = "sample_audio/harvard.wav"
    stt = SpeechToText(audio_file)
    transcript = stt.transcribe_audio()
    print("Transcription:", transcript)