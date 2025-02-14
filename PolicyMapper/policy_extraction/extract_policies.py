import json
import pdfplumber
import docx
import re
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

class PolicyExtractor:
    """Extracts structured insurance policies from a policy document using Ollama 3.2."""

    def __init__(self, model="llama3.2"):
        self.llm = OllamaLLM(model=model)

    def extract_text_from_pdf(self, pdf_path):
        """Extracts text from a PDF document."""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()

    def extract_text_from_docx(self, docx_path):
        """Extracts text from a DOCX document."""
        doc = docx.Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()

    def extract_policies(self, document_text):
        """Uses Ollama 3.2 to extract all structured policies dynamically from document text."""

        prompt_template = PromptTemplate(
            input_variables=["policy_text"],
            template="""
            Extract all structured insurance policy rules from the following text:

            {policy_text}

            Provide **only a valid JSON output** in this format:
            ```json
            {{
                "policies": [
                    {{
                        "policy_number": "string",
                        "coverage": "string",
                        "max_coverage_amount": int,
                        "covered_damage_types": ["string"],
                        "deductible": int,
                        "exclusions": ["string"]
                    }}
                ]
            }}
            ```

            Ensure **strict JSON formatting** and dynamically include all policies found in the document.
            Extract **all** available policies, no matter how many are present.
            """
        )

        formatted_prompt = prompt_template.format(policy_text=document_text)
        response = self.llm.invoke(formatted_prompt)

        # Ensure response is properly formatted
        if not response or response.strip() == "":
            print("Error: Ollama returned an empty response.")
            return []

        # Extract JSON using regex
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if not json_match:
            print("Error: No valid JSON found in Ollama response.")
            return []

        response_text = json_match.group(0).strip()

        # Convert response to JSON
        try:
            policies = json.loads(response_text)
            if "policies" in policies:
                print(f"✅ Extracted {len(policies['policies'])} policies.")
                return policies["policies"]
            else:
                print("Error: Expected 'policies' key missing from response.")
                return []
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse extracted policy data. {e}")
            return []

    def process_policy_document(self, policy_file):
        """Reads a policy document, extracts multiple policies dynamically, and saves them to a JSON file."""
        if policy_file.endswith(".pdf"):
            document_text = self.extract_text_from_pdf(policy_file)
        elif policy_file.endswith(".docx"):
            document_text = self.extract_text_from_docx(policy_file)
        else:
            raise ValueError("Unsupported file format. Please use PDF or DOCX.")

        extracted_policies = self.extract_policies(document_text)

        if extracted_policies:
            with open("policies.json", "w") as json_file:
                json.dump(extracted_policies, json_file, indent=4)
            print(f"✅ Extracted {len(extracted_policies)} insurance policies and saved to policies.json.")
        else:
            print("⚠️ No policies extracted.")

# Example Usage
if __name__ == "__main__":
    policy_extractor = PolicyExtractor()
    policy_extractor.process_policy_document("policies/motor-english-policy-book-2023.pdf")  # Use actual file path
