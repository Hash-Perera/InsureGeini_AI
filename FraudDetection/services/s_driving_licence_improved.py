import cv2
import re
import io
import torch
from PIL import Image
from deepface import DeepFace
from mtcnn import MTCNN
from fastapi import UploadFile
from concurrent.futures import ThreadPoolExecutor
from services.aws.s3_upload import upload_single_file 

# Load MTCNN detector once (reuse across requests)
face_detector = MTCNN()

# Preload DeepFace models (caching at the start to avoid redownloading)
preloaded_models = {
    model: DeepFace.build_model(model)
    for model in ['VGG-Face', 'Facenet', 'OpenFace', 'DeepID', 'ArcFace']
}


def extract_face_from_license(license_img):
    rgb_img = cv2.cvtColor(license_img, cv2.COLOR_BGR2RGB)
    faces = face_detector.detect_faces(rgb_img)
    if not faces:
        raise ValueError("No face detected in the license image.")
    x, y, w, h = map(abs, faces[0]['box'])
    face = rgb_img[y:y + h, x:x + w]
    return cv2.cvtColor(face, cv2.COLOR_RGB2BGR)


def get_folder_path_from_url(url: str) -> str:
    match = re.search(r"https://.+?amazonaws\.com/(.+)/[^/]+$", url)
    return match.group(1) if match else ''


def save_face_temp(face_image, filename="temp/cropped_face.jpg"):
    cv2.imwrite(filename, face_image)
    with open(filename, "rb") as f:
        return UploadFile(filename="cropped_face.jpg", file=io.BytesIO(f.read()))


def verify_with_model(model_name, face_img, driver_img):
    try:
        return {
            "Model": model_name,
            "result": DeepFace.verify(
                face_img,
                driver_img,
                model_name=model_name,
                enforce_detection=False
            )['verified']
        }
    except Exception as e:
        return {"Model": model_name, "result": False, "error": str(e)}



async def face_compare_improved(license_img_path, driver_img_path, license_original_url, driver_original_url):
    try:
        license_img = cv2.imread(license_img_path)
        driver_img = cv2.imread(driver_img_path)

        if license_img is None or driver_img is None:
            return {
                "status": False,
                "error": "One or both images could not be loaded.",
                "verified": None,
                "model_results": None
            }

        folder_path = get_folder_path_from_url(license_original_url)

        try:
            cropped_face_bgr = extract_face_from_license(license_img)
        except ValueError as e:
            return {
                "status": False,
                "error": str(e),
                "verified": None,
                "model_results": None
            }

        # Save and upload cropped face
        cropped_face_file = save_face_temp(cropped_face_bgr)
        cropped_face_s3url = await upload_single_file(cropped_face_file, folder_path)

        # Run DeepFace verifications in parallel
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(verify_with_model, model, cropped_face_bgr, driver_img)
                for model in preloaded_models
            ]
            ensemble_results = [f.result() for f in futures]

        # Majority voting
        verified_votes = sum(res.get("result", False) for res in ensemble_results)
        verified = verified_votes > len(ensemble_results) / 2

        return {
            "status": True,
            "error": None,
            "verified": verified,
            "images": {
                "license": license_original_url,
                "driver": driver_original_url,
                "cropped_face": cropped_face_s3url
            },
            "model_results": ensemble_results
        }

    except Exception as e:
        return {
            "status": False,
            "error": str(e),
            "verified": None,
            "model_results": None
        }
