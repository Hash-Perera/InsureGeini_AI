import torchaudio


def load_audio(file_path, target_sample_rate=16000):
    """
    Load an audio file and resample it to the target sample rate if necessary.
    Args:
        file_path (str): Path to the audio file to be loaded.
        target_sample_rate (int, optional): The desired sample rate for the audio. Defaults to 16000.
    Returns:
        tuple: A tuple containing the waveform tensor and the sample rate.
    """

    waveform, sample_rate = torchaudio.load(file_path)
    if sample_rate != target_sample_rate:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
        waveform = resampler(waveform)
    return waveform, target_sample_rate