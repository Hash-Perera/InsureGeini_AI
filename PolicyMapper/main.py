from speech_to_text.speech_to_text import SpeechToText
from document_generator.data_collector import DataCollector
from document_generator.pdf_generator import PDFGenerator

if __name__ == "__main__":
    # Step 1: Convert audio to text
    audio_file = "sample_audio/Colombo.wav"
    stt = SpeechToText(audio_file)
    transcript = stt.transcribe_audio()
    print("🎤 Transcription:", transcript)

    # Step 2: Collect all data (speech, API data, witness statements, images)
    witness_statements = [
        {"name": "Anne Fulton", "date": "03.05.2023", "statement": "I saw the accident happen..."},
        {"name": "Jane Fulton", "date": "03.05.2023", "statement": "The other driver was speeding..."}
    ]
    images = ["sample_images/photo1.jpg", "sample_images/photo2.jpg"]

    # Step 3: Generate summary & format data
    collector = DataCollector(transcript, "sample_data/api_mock_data.json", witness_statements, images)
    report_data = collector.collect_report_data()

    # Step 4: Generate PDF Report
    pdf_gen = PDFGenerator()
    pdf_filename = "vehicle_damage_report.pdf"
    pdf_gen.generate_pdf(report_data, pdf_filename)

    print(f"✅ Report successfully generated: {pdf_filename}")
