from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch

processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")
model.eval()


def transcribe_audio(waveform, sample_rate):
    """
    Transcribes the given audio waveform into text.
    Args:
        waveform (torch.Tensor): The audio waveform to transcribe.
        sample_rate (int): The sample rate of the audio waveform.
    Returns:
        str: The transcribed text from the audio waveform.
    """

    inputs = processor(waveform.squeeze(), sampling_rate=sample_rate, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(inputs.input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)
    return transcription[0]