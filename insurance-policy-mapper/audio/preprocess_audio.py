import noisereduce as nr
import torch

def normalize_audio(waveform):
    """
    Normalize the audio waveform.
    This function takes an audio waveform and normalizes it by dividing 
    each sample by the maximum absolute value of the waveform. This 
    ensures that the waveform's values are scaled between -1 and 1.
    Parameters:
    waveform (torch.Tensor): A 1D tensor representing the audio waveform.
    Returns:
    torch.Tensor: The normalized audio waveform.
    """

    return waveform / waveform.abs().max()



def reduce_noise(waveform, sample_rate):
    """
    Reduces noise from an audio waveform.
    Args:
        waveform (torch.Tensor): The input audio waveform as a PyTorch tensor.
        sample_rate (int): The sample rate of the audio waveform.
    Returns:
        torch.Tensor: The denoised audio waveform as a PyTorch tensor.
    """

    waveform_np = waveform.numpy()
    reduced_waveform = nr.reduce_noise(y=waveform_np.flatten(), sr=sample_rate)
    return torch.tensor(reduced_waveform).unsqueeze(0)

