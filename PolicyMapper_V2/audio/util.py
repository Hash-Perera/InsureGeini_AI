from pydub import AudioSegment
import whisper
import os

def convert_mp3_to_wav(mp3_file_path):
    """
    Converts an MP3 file to WAV format.

    :param mp3_file_path: Path to the input MP3 file.
    :param wav_file_path: Path to save the output WAV file.
    """
    
    path = os.path.dirname(mp3_file_path)
    output = os.path.join(path, 'wav_output.wav')
    audio = AudioSegment.from_mp3(mp3_file_path)
    audio.export(output, format="wav")
    print("✔️ WAV exported")


def transcribe_audio_to_text(mp3_file_path, model_size="base"):
    """
    Transcribes audio from a WAV file to text using OpenAI's Whisper model.

    :param wav_file_path: Path to the input WAV file.
    :param model_size: Size of the Whisper model to use (e.g., 'tiny', 'base', 'small', 'medium', 'large').
    :return: Transcribed text.
    """

    path = os.path.dirname(mp3_file_path)
    output = os.path.join(path, 'wav_output.wav')
    model = whisper.load_model("turbo")
    result = model.transcribe(output)
    print("✔️ Transcribed audio")
    return result['text']




def process_audio_file(mp3_file_path, model_size="base"):
    """
    Converts an MP3 file to WAV format and transcribes the audio to text.

    :param mp3_file_path: Path to the input MP3 file.
    :param model_size: Size of the Whisper model to use for transcription.
    :return: Transcribed text.
    """

    try:
        convert_mp3_to_wav(mp3_file_path)
        # Transcribe the WAV audio to text
        transcription = transcribe_audio_to_text(mp3_file_path, model_size)



    finally:
        # Clean up the temporary WAV file
        path = os.path.dirname(mp3_file_path)
        output = os.path.join(path, 'wav_output.wav')
        if os.path.exists(output):
            os.remove(output)

    return transcription