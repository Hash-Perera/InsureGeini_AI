from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

class DecisionGenerator:
    """Generates a PDF decision document based on claim evaluation results."""

    def __init__(self, template_folder="templates", output_folder="output"):
        self.env = Environment(loader=FileSystemLoader(template_folder))
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

    def generate_decision_pdf(self, report_data, decision, output_filename):
        """Creates a PDF with claim evaluation results."""
        template = self.env.get_template("decision_template.html")
        html_content = template.render(report_data=report_data, decision=decision)

        pdf_path = os.path.join(self.output_folder, output_filename)
        HTML(string=html_content).write_pdf(pdf_path)
        print(f"✅ Decision Document Generated: {pdf_path}")

# Example Usage
if __name__ == "__main__":
    sample_report = {
        "driver_name": "John Smith",
        "vehicle_reg": "NTJ 455",
        "damage_cause": "Collision",
        "incident_date": "01.05.2023",
        "estimated_repair_cost": 8000,
        "insurance_policy": {"policy_number": "POL-2023-24567"}
    }
    decision = {"status": "Accepted", "reason": "Claim meets all policy conditions"}

    decision_gen = DecisionGenerator()
    decision_gen.generate_decision_pdf(sample_report, decision, "output/insurance_decision.pdf")
