from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import os

class PDFGenerator:
    """Generates a PDF report from an HTML template with external CSS support."""

    def __init__(self, template_folder="templates", output_folder="temp"):
        self.env = Environment(loader=FileSystemLoader(template_folder))
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

    def generate_pdf(self, data, output_filename, template_name):
        """Generates a PDF report and includes external CSS styling."""
        
        # Ensure image paths are absolute
        for i, img in enumerate(data["photos"]):
            data["photos"][i] = os.path.abspath(img)

        # Render the HTML template
        template = self.env.get_template(template_name)
        html_content = template.render(data)

        # Define paths
        pdf_path = os.path.join(self.output_folder, output_filename)
        css_path = os.path.abspath("templates/report.css")  # Ensure the CSS file exists

        # Generate PDF with external CSS
        HTML(string=html_content, base_url=".").write_pdf(pdf_path, stylesheets=[CSS(css_path)])
        
        print(f"✅ PDF Generated: {pdf_path}")

# Example Usage of the PDFGenerator class
if __name__ == "__main__":
    sample_incident_data = {
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
      
    decision_report_sample_data = {
  "vehicle_number_plate": "KM7537",
  "vehicle_vin": "345610",
  "vehicle_make_model": "Alto",
  "report_date": "19.03.2025",
  "fleet_manager": "Hashan",
  "driver_name": "Hashan",
  "driver_phone": "0775538374",
  "incident_date": "19.03.2025 - 22:21",
  "incident_location": "N/A",
  "weather": "N/A",
  "damage_cause": "Rear-ended at a red light",
  "fraud_verification": {
    "model_verified": "false",
    "face_verified": "true",
    "license_verified": "true",
    "insurance_verified": "true",
    "number_plates_verified": "true",
    "prev_damage_verified": "true",
    "vin_number_verified": "true",
    "color_verified": "true",
    "location_verified": "true",
    "fraud_verified": "true"
  },
  "damage_parts": [
    {
      "part": "damaged-door",
      "cost": "$6000.0",
      "severity": "Moderate",
      "decision": "Repair",
      "reason": "The claim is for a moderate dent to the vehicle's door, which is covered under the comprehensive insurance policy. There are no indications of fraud or excluded perils. The damage does not involve internal components or excluded parts, and the cost is reasonable for the repair.",
      "status": "approved"
    },
    {
      "part": "damaged-door",
      "cost": "$93000.0",
      "severity": "Severe",
      "decision": "Replace",
      "reason": "The claim is covered under the comprehensive insurance policy as the damage to the vehicle's door, despite being severe, falls within the covered sections and does not fall under any exclusions.",
      "status": "approved"
    },
    {
      "part": "damaged-door",
      "cost": "$93000.0",
      "severity": "Severe",
      "decision": "Replace",
      "reason": "The claim is approved as the severe dent and internal damages fall under the comprehensive coverage without applicable exclusions. The OBD code is valid, and no fraud is detected.",
      "status": "approved"
    },
    {
      "part": "damaged-door",
      "cost": "$93000.0",
      "severity": "Severe",
      "decision": "Replace",
      "reason": "The claim is covered under the comprehensive insurance policy, and the damage severity warrants replacement. No exclusions apply, and fraud check is negative.",
      "status": "approved"
    }
  ],
  "incident_description": "Accident Report for Insurance ID: id1\n\nIntroduction:\nThis report summarizes the key facts and details of an accident involving the vehicle with Number Plate KM7537, an Alto model with ash color, insured under Comprehensive Insurance policy.\n\nVehicle Details:\nThe vehicle involved in the accident is an Alto model with ash color, bearing Number Plate KM7537, Engine No 103004-b78, and Chassis No 3624672323-09.\n\nAccident Circumstances:\nThe accident occurred at location WV97+629 Colombo, Sri Lanka, under weather conditions of clouds and scattered clouds. The claim status is currently Policy Mapper Started.\n\nDamage Details:\nThe damage detection data indicates a total of 4 damaged parts. The damage areas are the Front and Right Side of the vehicle. The damaged parts include damaged-door with varying severity levels and damage types, including dent and crack.\n\nDamage Severity:\nThe severity of the damage ranges from moderate to severe, with multiple instances of severe damage, including dents and cracks on the damaged-door.\n\nClaim Information:\nThe insurance claim ID for this accident is insuregeni-126735. The claim is currently being processed.\n\nConclusion:\nIn conclusion, the accident involved the vehicle with Number Plate KM7537, resulting in damage to the Front and Right Side, with a total of 4 damaged parts. The damage severity ranges from moderate to severe. This report provides a factual summary of the accident based on the damage detection data and claim details.",
  "photos": [
    "https://test-bucket-chathura.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/67d0532009cadf38a9976547/1741706022378-buildform-studio-vaishali-nagar-jaipur-architects-9o7ua2tq5o.png",
    "https://test-bucket-chathura.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/67d0532009cadf38a9976547/1741706023748-buildform-studio-vaishali-nagar-jaipur-architects-9o7ua2tq5o.png",
    "https://test-bucket-chathura.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/67d0532009cadf38a9976547/1741706025032-buildform-studio-vaishali-nagar-jaipur-architects-9o7ua2tq5o.png",
    "https://test-bucket-chathura.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/67d0532009cadf38a9976547/1741706026040-buildform-studio-vaishali-nagar-jaipur-architects-9o7ua2tq5o.png"
  ],
  "total_estimation": "$285000.0",
  "approved_amount": "$285000.0",
  "status_summary": "Approved"
}


    pdf_gen = PDFGenerator()
    pdf_gen.generate_pdf(sample_incident_data, "incident_report.pdf", "report_template.html")
