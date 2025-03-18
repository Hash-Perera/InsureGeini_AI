from pydub import AudioSegment
from core.logger import Logger

logger = Logger()

def process_audio(input_path: str, output_path: str):
    try:
        logger.info(f"Processing audio from {input_path} to {output_path}")
        audio = AudioSegment.from_file(input_path)
        logger.info(f"Audio loaded successfully")
        audio = audio.set_channels(1)
        logger.info(f"Audio set to mono")
        audio = audio.set_frame_rate(16000)
        logger.info(f"Audio set to 16000 Hz")
        audio = audio.set_sample_width(2)
        logger.info(f"Audio set to 2 bytes")
        audio.export(output_path, format="wav")
        logger.info(f"Audio exported successfully")
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        return None
    return output_path