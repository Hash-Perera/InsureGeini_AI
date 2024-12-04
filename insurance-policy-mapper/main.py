from audio.load_audio import load_audio
from audio.preprocess_audio import normalize_audio, reduce_noise
from audio.transcribe_audio import transcribe_audio
# from punctuate.punctuate import punctuate
from audio.postprocess_audio import clean_transcription
from core.logger import safe_execution
from llm.llm import populate_report, save_report_to_yaml
import logging

logging.basicConfig(filename="stt_system.log", level=logging.INFO, format="%(asctime)s - %(message)s")

test_audio_path = "data/Colombo.wav"
data = {
    "registration_number": "XYZ1234",
    "vin": "1HGBH41JXMN109186",
    "year_make_model": "2020 Honda Civic",
    "report_date_time": "2024-12-01T18:45:00",
    "fleet_manager_name": "Alice Johnson",

    "driver_name": "John Doe",
    "driver_license_photo": "https://example.com/driver_license.jpg",
    "driver_phone": "123-456-7890",

    "incident_date_time": "2024-12-01T18:45:00",
    "incident_location": {
        "address": "Main Street, City, Country",
        "latitude": "37.7749",
        "longitude": "-122.4194"
    },
    "weather_condition": "Rainy",
    "damage_severity": "Moderate",
    "damage_cause": "Slippery roads",

    "witnesses": [
        {"name": "Jane Doe", "statement": "I saw the car sliding due to rain.", "phone": "987-654-3210"},
        {"name": "Mark Smith", "statement": "The road was very slippery.", "phone": "123-789-4560"}
    ],

    "comments": "The driver was not injured and was immediately able to report the incident.",
    "driver_signature": "John Doe, 2024-12-01T19:00:00",
    "fleet_manager_signature": "Alice Johnson, 2024-12-01T19:05:00"
}


@safe_execution
def safe_audio_load(test_audio_path):
    return load_audio(test_audio_path)

@safe_execution
def safe_normalize_audio(waveform):
    return normalize_audio(waveform)

@safe_execution
def safe_reduce_noise(waveform, target_sample_rate):
    return reduce_noise(waveform, target_sample_rate)

@safe_execution
def safe_transcribe_audio(waveform, target_sample_rate):
    return transcribe_audio(waveform, target_sample_rate)

@safe_execution
def safe_clean_transcription(transcription):
    return clean_transcription(transcription)


def process_audio(test_audio_path):
    waveform, target_sample_rate = safe_audio_load(test_audio_path)
    print(f'{waveform} loaded with sample rate  {target_sample_rate}')
    waveform = safe_normalize_audio(waveform)
    print(f' Normalized waveform : {waveform} ')
    waveform = safe_reduce_noise(waveform, target_sample_rate)
    print(f' Reduced noise waveform : {waveform} ')
    transcription = safe_transcribe_audio(waveform, target_sample_rate)
    print(f'Transcription : {transcription}')

    # punctuated_transcription = punctuate(transcription)
    # print(punctuated_transcription)

    cleaned_transcription = safe_clean_transcription(transcription)
    print(f'Cleaned Transcription : {cleaned_transcription}')
    return cleaned_transcription

def main():
    transcription = process_audio(test_audio_path)
    # Example of usage
    report_data = populate_report(data, transcription, len(transcription))
    save_report_to_yaml(report_data)


if __name__ == "__main__":
    main()