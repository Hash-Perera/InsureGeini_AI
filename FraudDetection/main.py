import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import os
from PIL import Image

from services.s_driving_licence import face_compare, read_license
from services.s_insurance_card import read_insurance_card, read_number_plates, read_VIN_number
from services.s_damage_compare import damage_compare
from services.s_color_verification import detect_vehicle_color
from services.z_detector import excute_fraud_detector
from services.s_vehicle_model_detection import predict_vehicle_class

from database import claim_collection, verify_connection
from bson import ObjectId
from services.aws.aws_download import download_file_from_url

from services.queue_service import start_fraud_consumer



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

# Create temp directory
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles app startup and shutdown events."""
    # Ensure the database connection is verified
    await verify_connection()
    # Start fraud queue consumer in the background
    task = asyncio.create_task(start_fraud_consumer())
    yield  # Allow FastAPI to run
    # Cleanup if necessary (optional)
    task.cancel()

# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)
    
@app.get("/")
async def healthCheck():
    return "Hello, Fraud Detection Server is running!"

#!----------- This is the real function that will be called when the script is run ------------//
@app.get("/execute-fraud-detection")
async def execute_fraud_detection():
    claimId = "67a1cacfeace4f9501a8c964"

    try:
        # Find the claim in the database
        if not ObjectId.is_valid(claimId):
            raise HTTPException(status_code=400, detail="Invalid claim ID format")
        claim = await claim_collection.find_one({"_id": ObjectId(claimId)})
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        # Convert BSON types (like ObjectId) to JSON-serializable types
        claim = convert_bson_to_json(claim)

      
        # #? This files should be downloaded from the DB Document. 
        # license_path = download_file_from_url("https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/Dad_L.jpg")
        # driver_path = download_file_from_url("https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/Dad_S_Cropped.jpg")
        # insurance_path = download_file_from_url("https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/IncCard.jpg")
        # license_plates = download_file_from_url("https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/V_5.jpg")
        # url_set_1 = [
        #     'https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/DC_1.jpg',
        #     'https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/NDC_1.jpg',
        # ]

        # url_set_2 = [
        #     'https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/DC_1.jpg',
        #     'https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/NDC_1.jpg',
        # ]

        license_path = download_file_from_url(claim["drivingLicenseFront"])
        driver_path = download_file_from_url(claim["driverFace"])
        insurance_path = download_file_from_url(claim["insuranceFront"])
        license_plates = download_file_from_url(claim["backLicencePlate"])
        color_detect_path = download_file_from_url(claim["frontLicencePlate"])
        vin_number_path = download_file_from_url(claim["vinNumber"])
        url_set_1 = claim["damageImages"]

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

        #! Car Model result
        carModelResult = predict_vehicle_class(Image.open(license_path))

        #! VIN Number
        vinNumberResult = read_VIN_number(vin_number_path)

        #! Color Detection
        colorResult = detect_vehicle_color(color_detect_path)
        
        #? Return the results
        return { 
            "model_result" : carModelResult,
            "face_result": faceResult , 
            "read_licence_result": readLicenceResult , 
            "read_insurance_result": readInsuranceResult, 
            "number_plates": readNumberPlateResult,   
            "similarity_score": similarity_score,
            "vin_number": vinNumberResult,
            "color": colorResult
        }
        

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch claim: {e}")
    
    finally:
        print("Cleaning up")
        # Cleanup temporary files
        for file_path in [license_path, driver_path, insurance_path, license_plates]:
            if os.path.exists(file_path):
                os.remove(file_path)

@app.get("/excute-fraud-detection")
async def excute_fraud_detection():
    claimId = "67a1cacfeace4f9501a8c964"
    return await excute_fraud_detector(claimId);

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
    # uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
