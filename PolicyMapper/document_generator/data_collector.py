import json
import os
import ollama
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class DataCollector:
    """Collects and structures all necessary data for the vehicle damage report."""

    def __init__(self, transcript, external_data_path, witness_statements, images):
        self.transcript = transcript
        self.external_data = self.load_external_data(external_data_path)
        self.witness_statements = witness_statements
        self.images = images
        self.llm = Ollama(model="llama3.2")  # Connect to Ollama

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
        prompt_template = PromptTemplate(
            input_variables=["incident", "witnesses"],
            template="""
            You are a professional report generator. Summarize the following accident report concisely:

            Incident Description: {incident}
            Witness Statements: {witnesses}

            Provide a clear, professional summary. Do not include any placeholders or variables in the summary.
            Do not inlude text formattings.
            """
        )

        llm_chain = LLMChain(llm=self.llm, prompt=prompt_template)
        response = llm_chain.run(incident=self.transcript, witnesses=', '.join([w['statement'] for w in self.witness_statements]))

        return response.strip()

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
