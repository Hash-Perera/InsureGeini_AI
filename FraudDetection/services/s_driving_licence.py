import cv2
import numpy as np
import easyocr
import matplotlib.pyplot as plt
from deepface import DeepFace
from mtcnn import MTCNN
import re
import io
from fastapi import UploadFile
from services.aws.s3_upload import upload_single_file 

async def face_compare(license_img_path, driver_img_path, license_original_url, driver_original_url):
    try:
        # Load images
        license_img = cv2.imread(license_img_path)
        driver_img = cv2.imread(driver_img_path)


        folder_path = ''
        match = re.search(r"https://.+?amazonaws\.com/(.+)/[^/]+$", license_original_url)
        if match:
            folder_path = match.group(1)  


        if license_img is None:
            return {"status": False, "error": "License image could not be loaded.", "verified": None, "model_results": None}
        if driver_img is None:
            return {"status": False, "error": "Driver image could not be loaded.", "verified": None, "model_results": None}

        # Convert to RGB as MTCNN expects images in RGB format
        license_img_rgb = cv2.cvtColor(license_img, cv2.COLOR_BGR2RGB)

        # Initialize MTCNN detector
        detector = MTCNN()

        # Detect faces in the license image
        results = detector.detect_faces(license_img_rgb)

        if not results:
            return {"status": False, "error": "No face detected in the license image.", "verified": None, "model_results": None}

        # Extract the first detected face
        x, y, width, height = results[0]['box']
        x, y = abs(x), abs(y)  # Ensure no negative values
        cropped_face = license_img_rgb[y:y + height, x:x + width]
        cropped_face_bgr = cv2.cvtColor(cropped_face, cv2.COLOR_RGB2BGR)

        #######################
        # Save the cropped face to a temporary file
        cropped_face_path = "temp/cropped_face.jpg"
        cv2.imwrite(cropped_face_path, cropped_face_bgr)

        # Open the saved image file and read it as bytes
        with open(cropped_face_path, "rb") as file:
            image_bytes = io.BytesIO(file.read())

        # Create an UploadFile object
        cropped_face_file = UploadFile(filename="cropped_face_licence.jpg", file=image_bytes)

        # Upload to S3
        cropped_face_s3url = await upload_single_file(cropped_face_file, folder_path)
        #########################

        # Perform face comparison using DeepFace
        models = ['VGG-Face', 'Facenet', 'OpenFace', 'DeepID', 'ArcFace']
        ensemble_results = []

        for model in models:
            result = DeepFace.verify(cropped_face_bgr, driver_img, model_name=model, enforce_detection=False)
            ensemble_results.append({"Model": model, "result": result['verified']})

        # Majority voting for verification
        verified = sum(res['result'] for res in ensemble_results) > len(ensemble_results) / 2


        # Return structured result
        return {
            "status": True,
            "error": None,
            "verified": verified,
            "images" : {
                "license": license_original_url,
                "driver": driver_original_url,
                "cropped_face": cropped_face_s3url
            },
            "model_results": ensemble_results
        }

    except Exception as e:
        # Catch unexpected errors and return them
        return {"status": False, "error": str(e), "verified": None, "model_results": None}





def read_license(image_path):
    try:
        # Initialize EasyOCR
        reader = easyocr.Reader(['en'])

        # Load the image
        license_image = cv2.imread(image_path)
        if license_image is None:
            return {
                "status": False,
                "error": f"Could not load the image from {image_path}. Ensure the file exists and is a valid image format.",
                "license_data": None,
                
            }

        # Resize the image to a standard size
        standard_size = (1920, 1080)  # Width, Height
        license_image = cv2.resize(license_image, standard_size)

        # Define ROI coordinates in percentages
        roi_coords_percent = {
            "License Number": (0.30, 0.17, 0.65, 0.23),  
            "Name": (0.30, 0.25, 0.70, 0.35),
            "Address": (0.30, 0.36, 0.66, 0.43),
            "Birthdate": (0.30, 0.44, 0.62, 0.50),
            "Issue Date": (0.30, 0.51, 0.62, 0.57),
            "Expire Date": (0.30, 0.58, 0.62, 0.64),
            "NIC Number": (0.7, 0.17, 0.96, 0.24),
            "Blood Group": (0.30, 0.66, 0.62, 0.71),
        }

        # Function to extract text from a specific ROI
        def extract_text_from_roi(image, coords_percent):
            h, w, _ = image.shape
            x1 = int(coords_percent[0] * w)
            y1 = int(coords_percent[1] * h)
            x2 = int(coords_percent[2] * w)
            y2 = int(coords_percent[3] * h)
            roi = image[y1:y2, x1:x2]
            results = reader.readtext(roi)
            extracted_text = " ".join([text for _, text, _ in results])
            return extracted_text.strip(), (x1, y1, x2, y2)

        # Extract text and annotate ROIs
        license_data = {}
        annotated_image = license_image.copy()
        for field, coords_percent in roi_coords_percent.items():
            try:
                text, (x1, y1, x2, y2) = extract_text_from_roi(license_image, coords_percent)
                license_data[field] = text
                # Draw bounding boxes on the annotated image
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(annotated_image, field, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            except Exception as e:
                license_data[field] = f"Error extracting {field}: {str(e)}"

        # Return the processed results
        return {
            "status": True,
            "error": None,
            "license_data": license_data,
           
        }

    except Exception as e:
        # Handle any unexpected errors
        return {
            "status": False,
            "error": str(e),
            "license_data": None,
           
        }


def visualize_results(license_img_path, driver_img_path, results):
    # Load images
    license_img = cv2.imread(license_img_path)
    driver_img = cv2.imread(driver_img_path)

    # Display images
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    ax[0].imshow(cv2.cvtColor(license_img, cv2.COLOR_BGR2RGB))
    ax[0].set_title("License Image")
    ax[0].axis('off')

    ax[1].imshow(cv2.cvtColor(driver_img, cv2.COLOR_BGR2RGB))
    ax[1].set_title("Driver Image")
    ax[1].axis('off')

    plt.show()

    # Display results
    print("Results:")
    print("Verified:", results['verified'])
    print("Model Results:")
    for model_result in results['model_results']:
        print(f"{model_result['Model']}: {model_result['result']}")
