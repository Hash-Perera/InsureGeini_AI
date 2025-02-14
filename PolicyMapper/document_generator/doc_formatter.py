import json

class DocumentFormatter:
    """Formats speech-to-text and external data into structured content for the report."""

    def __init__(self, transcript, external_data_path):
        self.transcript = transcript
        self.external_data = self.load_external_data(external_data_path)

    def load_external_data(self, file_path):
        """Loads external API data from a JSON file (currently hardcoded values)."""
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading external data: {e}")
            return {}

    def format_report(self):
        """Generates structured content based on input data."""
        report_content = f"""
        Vehicle Damage Report
        ======================
        
        **Vehicle Information**
        - Registration Number: {self.external_data.get("vehicle_reg", "N/A")}
        - VIN: {self.external_data.get("vin", "N/A")}
        - Make & Model: {self.external_data.get("make_model", "N/A")}
        - Report Date: {self.external_data.get("report_date", "N/A")}
        - Fleet Manager: {self.external_data.get("fleet_manager", "N/A")}

        **Incident Details**
        - Driver: {self.external_data.get("driver_name", "N/A")}
        - Incident Date & Time: {self.external_data.get("incident_date", "N/A")}
        - Location: {self.external_data.get("location", "N/A")}
        - Weather: {self.external_data.get("weather", "N/A")}
        - Damage Severity: {self.external_data.get("damage_severity", "N/A")}
        - Cause of Damage: {self.external_data.get("damage_cause", "N/A")}

        **Incident Summary**
        {self.transcript}

        **Witness Statements**
        - Witness 1: {self.external_data.get("witness1", "N/A")}
        - Witness 2: {self.external_data.get("witness2", "N/A")}

        **Acknowledgment**
        - Driver: {self.external_data.get("driver_signature", "N/A")}
        - Fleet Manager: {self.external_data.get("fleet_manager_signature", "N/A")}
        """
        return report_content.strip()

