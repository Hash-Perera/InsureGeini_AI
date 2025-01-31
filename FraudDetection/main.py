from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import os

# from services.driving_license import detect_face_compare, read_id_card
# from services.insurance_card import read_insurance_card
# from services.damage_compare import damage_compare
from services.s_driving_licence import face_compare, read_license
from services.s_insurance_card import read_insurance_card, read_number_plates
from services.s_damage_compare import damage_compare
from database import claim_collection, verify_connection
from bson import ObjectId
from services.aws import download_file_from_url


app = FastAPI()
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    await verify_connection()
    
@app.get("/")
async def ping():
    return "Hello, I am alive!"

#   claimId = "6794d1984da59d677ddd3ec7"
#!----------- This is the real function that will be called when the script is run ------------//
@app.get("/execute-fraud-detection")
async def execute_fraud_detection():
    claimId = "6794d1984da59d677ddd3ec7"

    try:
        if not ObjectId.is_valid(claimId):
            raise HTTPException(status_code=400, detail="Invalid claim ID format")
        claim = await claim_collection.find_one({"_id": ObjectId(claimId)})
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        # Convert BSON types (like ObjectId) to JSON-serializable types
        claim = convert_bson_to_json(claim)

      
        #? This files should be downloaded from the DB Document. 
        license_path = download_file_from_url("https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/Dad_L.jpg")
        driver_path = download_file_from_url("https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/Dad_S_Cropped.jpg")
        insurance_path = download_file_from_url("https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/IncCard.jpg")
        license_plates = download_file_from_url("https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/V_5.jpg")
        url_set_1 = [
            'https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/DC_1.jpg',
            'https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/NDC_1.jpg',
        ]

        url_set_2 = [
            'https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/DC_1.jpg',
            'https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/NDC_1.jpg',
        ]
        
        #! Detect Face Logic
        faceResult = face_compare(license_path, driver_path)
        if not faceResult["status"]:
            return JSONResponse(content=faceResult, status_code=400)
        
        #! Read License Logic
        readLicenceResult = read_license(license_path)
        if not readLicenceResult["status"]:
            return JSONResponse(content=readLicenceResult, status_code=400)
        
        #! Read Insurance Card Logic
        readInsuranceResult = read_insurance_card(insurance_path)
        if not readInsuranceResult["status"]:
            return JSONResponse(content=readInsuranceResult, status_code=400)
        
        #! Compare Number Plates Logic
        readNumberPlateResult = read_number_plates(license_plates)

        #! compare images
        similarity_score = damage_compare(url_set_1, url_set_2)
        


        #? Return the results
        return { 
            "face_result": faceResult , 
            "read_licence_result": readLicenceResult , 
            "read_insurance_result": readInsuranceResult, 
            "number_plates": readNumberPlateResult,   
            "similarity_score": similarity_score
            }
        

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch claim: {e}")
    
    finally:
        # Cleanup temporary files
        for file_path in [license_path, driver_path, insurance_path, license_plates]:
            if os.path.exists(file_path):
                os.remove(file_path)
    

    

# @app.post("/detect-face")
# async def detect_face(file1: UploadFile = File(...), file2: UploadFile = File(...)):
#     try:
#         # Save uploaded files
#         license_path = os.path.join(TEMP_DIR, file1.filename)
#         driver_path = os.path.join(TEMP_DIR, file2.filename)
#         with open(license_path, "wb") as buffer:
#             buffer.write(file1.file.read())
#         with open(driver_path, "wb") as buffer:
#             buffer.write(file2.file.read())

#         # Call the service function
#         result = detect_face_compare(license_path, driver_path)

#         # If an error occurred, return it as the response
#         if not result["status"]:
#             return JSONResponse(content=result, status_code=400)

#         # Return success response
#         return result

#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)

#     finally:
#         # Cleanup temporary files
#         for file_path in [license_path, driver_path]:
#             if os.path.exists(file_path):
#                 os.remove(file_path)


# @app.post("/read-id-card")
# async def read_id_card_endpoint(file1: UploadFile = File(...)):
#     image_path = None
#     try:
#         # Save uploaded file
#         image_path = os.path.join(TEMP_DIR, file1.filename)
#         with open(image_path, "wb") as buffer:
#             buffer.write(file1.file.read())

#         # Call the service function
#         result = read_id_card(image_path)

#         # If an error occurred, return it as the response
#         if not result["status"]:
#             return JSONResponse(content=result, status_code=400)

#         # Return success response
#         return result

#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)

#     finally:
#         # Cleanup temporary files
#         if image_path and os.path.exists(image_path):
#             os.remove(image_path)


# @app.post("/read-insurance-card")
# async def detect_insurance_card(file1: UploadFile = File(...)):
#     image_path = None
#     try:
#         # Save uploaded file
#         image_path = os.path.join(TEMP_DIR, file1.filename)
#         with open(image_path, "wb") as buffer:
#             buffer.write(file1.file.read())

#         # Call the service function
#         result = read_insurance_card(image_path)

#         # Validate the service function's response
#         if not result["status"]:
#             return JSONResponse(
#                 content={
#                     "status": False,
#                     "error": result["error"],
#                     "extracted_data": result.get("extracted_data"),
#                 },
#                 status_code=400,
#             )

#         # Return success response
#         return JSONResponse(
#             content={
#                 "status": True,
#                 "error": None,
#                 "extracted_data": result.get("extracted_data"),
#             },
#             status_code=200,
#         )

#     except FileNotFoundError as e:
#         # Handle file-related errors
#         return JSONResponse(
#             content={
#                 "status": False,
#                 "error": f"File not found: {str(e)}",
#                 "extracted_data": None,
#             },
#             status_code=404,
#         )

#     except ValueError as e:
#         # Handle value-related errors
#         return JSONResponse(
#             content={
#                 "status": False,
#                 "error": f"Value error: {str(e)}",
#                 "extracted_data": None,
#             },
#             status_code=422,
#         )

#     except Exception as e:
#         # Handle unexpected errors
#         return JSONResponse(
#             content={
#                 "status": False,
#                 "error": f"An unexpected error occurred: {str(e)}",
#                 "extracted_data": None,
#             },
#             status_code=500,
#         )

#     finally:
#         # Cleanup temporary files
#         if image_path and os.path.exists(image_path):
#             os.remove(image_path)
            

# @app.post("/compare-damage")
# async def compare_damage(file1: UploadFile = File(...), file2: UploadFile = File(...)):
#     image_path_1 = None
#     image_path_2 = None
#     try:
#         # Save uploaded files
#         image_path_1 = os.path.join(TEMP_DIR, file1.filename)
#         image_path_2 = os.path.join(TEMP_DIR, file2.filename)
#         with open(image_path_1, "wb") as buffer:
#             buffer.write(file1.file.read())
#         with open(image_path_2, "wb") as buffer:
#             buffer.write(file2.file.read())

#         # Call the service function
#         result = damage_compare(image_path_1, image_path_2)

#         # Validate the service function's response
#         if not result["status"]:
#             return JSONResponse(content=result, status_code=400)

#         # Return success response
#         return JSONResponse(content=result, status_code=200)

#     except Exception as e:
#         # Handle unexpected errors
#         return JSONResponse(
#             content={
#                 "status": False,
#                 "error": f"An unexpected error occurred: {str(e)}",
#                 "similarity_score": None,
#                 "message": None
#             },
#             status_code=500
#         )

#     finally:
#         # Cleanup temporary files
#         for file_path in [image_path_1, image_path_2]:
#             if file_path and os.path.exists(file_path):
#                 os.remove(file_path)


def convert_bson_to_json(document):
    """
    Recursively converts MongoDB BSON types to JSON-serializable types.
    Handles ObjectId and nested structures.
    """
    if isinstance(document, dict):
        return {key: convert_bson_to_json(value) for key, value in document.items()}
    elif isinstance(document, list):
        return [convert_bson_to_json(item) for item in document]
    elif isinstance(document, ObjectId):
        return str(document)  # Convert ObjectId to string
    else:
        return document