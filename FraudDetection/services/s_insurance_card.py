import cv2
import easyocr
import re
import os
from ultralytics import YOLO

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


def read_number_plates(image_path):

    try:

        reader = easyocr.Reader(['en'])
        file_path = "./ML_Models/license_plate_detector.pt"
    
        model = YOLO(file_path)

        def preprocess_image(image):
            # Step 1: Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Step 2: Apply Gaussian Blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            # Step 3: Apply binary thresholding
            _, thresholded = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Step 4: Resize the image for better OCR performance
            resized = cv2.resize(thresholded, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

            return resized
        
        def detect_and_extract_text(image_path):
            # Read the image
            image = cv2.imread(image_path)
            # Detect objects using the trained YOLO model
            results = model(image_path)
            # Extract bounding boxes and confidence scores
            detections = results[0].boxes.data 
            # Ensure at least one detection
            if len(detections) == 0:
                return "No number plate detected", None, None
            
            # Extract the first bounding box (highest confidence score)
            detection = detections[0]  # First detected box
            xmin, ymin, xmax, ymax = map(int, detection[:4].tolist())  # Convert tensor values to integers

            # Draw bounding box on the original image
            annotated_image = image.copy()
            cv2.rectangle(annotated_image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

            # Crop the detected number plate region
            cropped_plate = image[ymin:ymax, xmin:xmax]

            # Preprocess the cropped image for OCR
            preprocessed_image = preprocess_image(cropped_plate)

            # Perform OCR
            ocr_results = reader.readtext(preprocessed_image)

            # Combine detected text
            extracted_text = " ".join([res[1] for res in ocr_results])
            return extracted_text.strip(), cropped_plate, annotated_image
        
        # Function to clean extracted text using regex
        def clean_extracted_text(extracted_text):
            # Remove all non-alphanumeric characters (keep only letters and numbers)
            cleaned_text = re.sub(r'[^A-Za-z0-9]', '', extracted_text)
            # Define the regex pattern for the license plate format
            pattern = r'[A-Z]{2}\d{4}'
            # Search for valid matches in the cleaned text
            matches = re.findall(pattern, cleaned_text)
            # Return the first match if found, else return "No valid license plate detected"
            return matches[0] if matches else "No valid license plate detected"
        
        extracted_text, cropped_plate, annotated_image = detect_and_extract_text(image_path)
        cleaned_text = clean_extracted_text(extracted_text)

        return {
            "status": True,
            "error": None,
            "number_plate": cleaned_text
        }
    
    except Exception as e:
        return {
            "status": False,
            "error": str(e),
            "extracted_data": None
        }
    
def read_VIN_number (image_path):
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
            "VIN": "VIN",
        }

        next_keywords = {
            "VIN": []
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
        extracted_info["VIN"] = re.sub(r"\sMCLH[0-9]+", "", extracted_info.get("VIN", ""))

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