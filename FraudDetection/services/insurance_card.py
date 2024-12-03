import cv2
import easyocr
import re

def read_insurance_card(image_path):
    try:
        # Initialize EasyOCR
        reader = easyocr.Reader(['en'])
        insurance_image = cv2.imread(image_path)

        # Check if the image was loaded successfully
        if insurance_image is None:
            return {
                "status": False,
                "error": f"Image not found at path: {image_path}. Ensure the file exists and is a valid image format.",
                "extracted_data": None
            }

        # Preprocess the image (optional for EasyOCR)
        gray = cv2.cvtColor(insurance_image, cv2.COLOR_BGR2GRAY)

        # Run OCR on the image using EasyOCR
        results = reader.readtext(gray, detail=0)

        # Define keywords and their next stopping keywords
        sections = {
            "Vehicle No": "Vehicle No",
            "Make and Model": "Make & Model",
            "Policy No": "Policy No",
            "Name": "Name",
            "Address": "Address",
            "Coverage Period": "Period of Cover",
            "Engine No": "Engine No",
            "Chassis No": "Chassis No"
        }

        next_keywords = {
            "Vehicle No": ["Make", "Policy"],
            "Make and Model": ["Policy"],
            "Policy No": ["Name"],
            "Name": ["Address"],
            "Address": ["Period"],
            "Coverage Period": ["Engine"],
            "Engine No": ["Chassis"],
            "Chassis No": []
        }

        # Helper function to extract text based on keywords
        def extract_text_after_keyword(results, keyword, next_keywords):
            found = False
            extracted_text = []
            for text in results:
                if keyword.lower() in text.lower():
                    found = True
                    continue
                if found:
                    # Stop if we encounter the next keyword
                    if any(nk.lower() in text.lower() for nk in next_keywords):
                        break
                    extracted_text.append(text)
            return " ".join(extracted_text).strip()

        # Extract information for each section
        extracted_info = {}
        for section, keyword in sections.items():
            try:
                extracted_info[section] = extract_text_after_keyword(results, keyword, next_keywords[section])
            except Exception as e:
                extracted_info[section] = f"Error extracting {section}: {str(e)}"

        # Post-process the extracted data to clean up unwanted text
        extracted_info["Vehicle No"] = re.sub(r"\sMCLH[0-9]+", "", extracted_info.get("Vehicle No", ""))
        extracted_info["Make and Model"] = re.sub(r"\s+", " ", extracted_info.get("Make and Model", "")).strip()
        extracted_info["Chassis No"] = re.sub(r"15JUL.*", "", extracted_info.get("Chassis No", ""))

        # Return the processed results in a consistent format
        return {
            "status": True,
            "error": None,
            "extracted_data": extracted_info
        }

    except Exception as e:
        # Handle any unexpected errors
        return {
            "status": False,
            "error": str(e),
            "extracted_data": None
        }
