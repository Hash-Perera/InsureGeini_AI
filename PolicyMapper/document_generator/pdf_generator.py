from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

class PDFGenerator:
    """Generates a PDF report from an HTML template with dynamic data."""

    def __init__(self, template_folder="templates", output_folder="output"):
        self.env = Environment(loader=FileSystemLoader(template_folder))
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

    def generate_pdf(self, data, output_filename):
        """Generates a PDF with structured report data and ensures images are properly included."""
        
        # Convert all image paths to absolute paths
        for i, img in enumerate(data["photos"]):
            data["photos"][i] = os.path.abspath(img)

        # Render the HTML template
        template = self.env.get_template("report_template.html")
        html_content = template.render(data)

        # Generate PDF
        pdf_path = os.path.join(self.output_folder, output_filename)
        HTML(string=html_content, base_url=".").write_pdf(pdf_path)
        print(f"✅ PDF Generated: {pdf_path}")

# Example Usage
if __name__ == "__main__":
    sample_data = {
        "vehicle_reg": "NTJ 455",
        "vin": "7HGSA1DFGT14554",
        "make_model": "2015 Toyota Prius",
        "report_date": "03.05.2023",
        "summary": "An accident occurred at a red light. The other driver was speeding.",
        "photos": ["images/photo1.jpg", "images/photo2.jpg"]  # Ensure these images exist
    }

    pdf_gen = PDFGenerator()
    pdf_gen.generate_pdf(sample_data, "vehicle_damage_report.pdf")
