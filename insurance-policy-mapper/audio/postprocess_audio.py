# from punctuator import Punctuator
import re

# p = Punctuator('models\Demo-Europarl-EN.pcl')

# def punctuate(transcription):
#     """
#     Punctuates the given transcription text.
#     Args:
#         transcription (str): The text transcription that needs punctuation.
#     Returns:
#         str: The punctuated transcription.
#     """

#     final_transcription = p.transcribe(transcription)
#     return final_transcription


def clean_transcription(text):
    """
    Cleans the given transcription text by removing common filler words.
    Args:
        text (str): The transcription text to be cleaned.
    Returns:
        str: The cleaned transcription text with filler words removed.
    """

    fillers = ["uh", "um", "you know", "like"]
    pattern = r'\b(' + '|'.join(fillers) + r')\b'
    return re.sub(pattern, '', text, flags=re.IGNORECASE)
