from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import os

class PDFGenerator:
    """Generates a PDF report from an HTML template with external CSS support."""

    def __init__(self, template_folder="templates", output_folder="temp"):
        self.env = Environment(loader=FileSystemLoader(template_folder))
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

    def generate_pdf(self, data, output_filename):
        """Generates a PDF report and includes external CSS styling."""
        
        # Ensure image paths are absolute
        for i, img in enumerate(data["photos"]):
            data["photos"][i] = os.path.abspath(img)

        # Render the HTML template
        template = self.env.get_template("report_template.html")
        html_content = template.render(data)

        # Define paths
        pdf_path = os.path.join(self.output_folder, output_filename)
        css_path = os.path.abspath("templates/report.css")  # Ensure the CSS file exists

        # Generate PDF with external CSS
        HTML(string=html_content, base_url=".").write_pdf(pdf_path, stylesheets=[CSS(css_path)])
        
        print(f"✅ PDF Generated: {pdf_path}")

# Example Usage
if __name__ == "__main__":
    sample_data = {
    "vehicle_number_plate": "NTJ 455",
    "vehicle_vin": "7HGSA1DFGT14554",
    "vehicle_make_model": "2015 Toyota Prius",
    "report_date": "03.05.2023",
    "fleet_manager": "John Doe",
    
    "driver_name": "Ian Lee",
    "driver_phone": "+1 (555) 123-4567",

    "incident_date": "02.05.2023 - 14:30",
    "incident_location": "Downtown Main Street, Cityville",
    "weather": "Clear Sky",
    "damage_cause": "Rear-ended at a red light",
    
    "damage_parts": [
        {"part": "Front Bumper", "cost": "$1,200", "severity": "Severe"},
        {"part": "Left Headlight", "cost": "$450", "severity": "Moderate"},
        {"part": "Hood", "cost": "$900", "severity": "Minor"}
    ],
    
    "incident_description": "A distracted driver failed to brake in time at a red light and collided with the rear of the insured vehicle. The impact resulted in a broken front bumper, minor dents on the hood, and a cracked left headlight.",
    
    "photos": [
        "images/damage_front_bumper.jpg",
        "images/damage_headlight.jpg",
        "images/damage_hood.jpg"
    ],

    "incident_summary": "The vehicle sustained moderate damage. Repair costs are estimated at approximately $2,550. No injuries were reported, and both parties exchanged insurance information."
}


    pdf_gen = PDFGenerator()
    pdf_gen.generate_pdf(sample_data, "vehicle_damage_report.pdf")
