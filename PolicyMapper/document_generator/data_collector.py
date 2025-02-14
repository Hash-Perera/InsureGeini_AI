import json
import os
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

class DataCollector:
    """Collects and structures all necessary data for the vehicle damage report."""

    def __init__(self, transcript, external_data_path, witness_statements, images):
        self.transcript = transcript
        self.external_data = self.load_external_data(external_data_path)
        self.witness_statements = witness_statements
        self.images = images
        self.llm = OllamaLLM(model="llama3.2")  # Updated to latest Ollama integration

    def load_external_data(self, file_path):
        """Loads external API data from a JSON file."""
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading external data: {e}")
            return {}

    def generate_summary(self):
        """Generates a summary using Ollama with LangChain."""
        
        # Define a structured prompt
        prompt_template = PromptTemplate(
            input_variables=["incident", "witnesses"],
            template="""
            You are a professional report generator. Summarize the following accident report concisely:

            Incident Description: {incident}
            Witness Statements: {witnesses}

            Provide a clear, professional summary. Do not include any placeholders or variables in the summary.
            Do not include text formatting.
            """
        )

        # Format the prompt properly
        formatted_prompt = prompt_template.format(
            incident=self.transcript,
            witnesses=', '.join([w['statement'] for w in self.witness_statements])
        )

        # Directly invoke Ollama LLM and process the response
        response = self.llm.invoke(formatted_prompt)

        # Ensure response is a string and clean it up
        if isinstance(response, str):
            return response.strip()
        else:
            print("Error: Unexpected response format from Ollama.")
            return "Summary unavailable due to an error."

    def collect_report_data(self):
        """Aggregates all report data into a structured dictionary."""
        return {
            "vehicle_reg": self.external_data.get("vehicle_reg", "N/A"),
            "vin": self.external_data.get("vin", "N/A"),
            "make_model": self.external_data.get("make_model", "N/A"),
            "report_date": self.external_data.get("report_date", "N/A"),
            "fleet_manager": self.external_data.get("fleet_manager", "N/A"),
            "driver_name": self.external_data.get("driver_name", "N/A"),
            "driver_phone": self.external_data.get("driver_phone", "N/A"),
            "incident_date": self.external_data.get("incident_date", "N/A"),
            "location": self.external_data.get("location", "N/A"),
            "weather": self.external_data.get("weather", "N/A"),
            "damage_severity": self.external_data.get("damage_severity", "N/A"),
            "damage_cause": self.external_data.get("damage_cause", "N/A"),
            "incident_description": self.transcript,
            "other_party": self.external_data.get("other_party", {}),
            "witnesses": [{"name": w["name"], "date": w["date"], "statement": w["statement"]} for w in self.witness_statements],
            "summary": self.generate_summary(),
            "driver_signature": self.external_data.get("driver_signature", "N/A"),
            "driver_date": self.external_data.get("driver_date", "N/A"),
            "fleet_manager_signature": self.external_data.get("fleet_manager_signature", "N/A"),
            "fleet_manager_date": self.external_data.get("fleet_manager_date", "N/A"),
            "photos": self.images
        }

# Example Usage
if __name__ == "__main__":
    transcript = "The car was hit while stopped at a traffic light. The front bumper and headlights were damaged."
    witness_statements = [
        {"name": "Anne Fulton", "date": "03.05.2023", "statement": "I saw the accident happen..."},
        {"name": "Jane Fulton", "date": "03.05.2023", "statement": "The other driver was speeding..."}
    ]
    images = ["sample_images/photo1.jpg", "sample_images/photo2.jpg"]

    collector = DataCollector(transcript, "sample_data/api_mock_data.json", witness_statements, images)
    report_data = collector.collect_report_data()
    print(json.dumps(report_data, indent=4))
