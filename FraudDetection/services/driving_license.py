import cv2
import numpy as np
from deepface import DeepFace
import matplotlib.pyplot as plt
from mtcnn import MTCNN


# def detect_face_compare(license_img_path, driver_img_Path):

#     license_img = cv2.imread(license_img_path)
#     driver_img = cv2.imread(driver_img_Path)

#     #! Convert to RGB as MTCNN expects images in RGB format
#     license_img_rgb = cv2.cvtColor(license_img, cv2.COLOR_BGR2RGB)

#     #! Initialize MTCNN detector
#     detector = MTCNN()

#     # Detect faces in the image
#     results = detector.detect_faces(license_img_rgb)

#     # Check if any faces are detected
#     if results:
#         # Get the first detected face's bounding box
#         x, y, width, height = results[0]['box']
#         x, y = abs(x), abs(y)  # Ensuring no negative values
#         cropped_face = license_img_rgb[y:y + height, x:x + width]

#         # Convert the cropped face back to BGR for saving and comparison
#         cropped_face_bgr = cv2.cvtColor(cropped_face, cv2.COLOR_RGB2BGR)
#         cv2.imwrite('cropped_face.jpg', cropped_face_bgr)

#     else:
#         print("No face detected in the license image, please adjust the image quality.")


#     # Perform face comparison using DeepFace with multiple models
#     try:
#     # Define models for ensemble verification
#         models = ['VGG-Face', 'Facenet', 'OpenFace', 'DeepID', 'ArcFace']
#         threshold = 0.5  # Set a confidence threshold for verification

#         # Perform verification with multiple models and aggregate results
#         ensemble_results = []
#         for model in models:
#             result = DeepFace.verify(cropped_face_bgr, driver_img, model_name=model, enforce_detection=False)
#             ensemble_results.append({"Model": model, "result": result['verified']})
#             print(f"Model: {model}, Verified: {result['verified']}, Distance: {result['distance']}")

#         # Decision based on majority voting
#         verified = sum(res['result'] for res in ensemble_results) > len(ensemble_results) / 2
#         print(f"\nOverall Verification Result: {'Verified' if verified else 'Not Verified'}")
#         return verified, ensemble_results

#     except Exception as e:
#         print(f"Error during verification: {e}")
#         raise

def detect_face_compare(license_img_path, driver_img_path):
    try:
        # Load images
        license_img = cv2.imread(license_img_path)
        driver_img = cv2.imread(driver_img_path)

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
            "model_results": ensemble_results
        }

    except Exception as e:
        # Catch unexpected errors and return them
        return {"status": False, "error": str(e), "verified": None, "model_results": None}
