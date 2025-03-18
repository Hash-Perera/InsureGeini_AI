from fastapi import  HTTPException
from fastapi.responses import JSONResponse
from database import claim_collection, get_detections_images_current_claim, get_similar_claims,get_detections_images_similar_claims, verify_connection
from bson import ObjectId
from services.s_damage_compare import damage_compare
from services.s_driving_licence import face_compare
from services.aws.aws_download import download_file_from_url
import time
from dotenv import load_dotenv
from openai import OpenAI 
import re
import os

load_dotenv()

async def excute_fraud_detector(claimId):
   
    try:
        # Find the claim in the database
        if not ObjectId.is_valid(claimId):
            raise HTTPException(status_code=400, detail="Invalid claim ID format")
        claimMongo = await claim_collection.find_one({"_id": ObjectId(claimId)})
        
        if not claimMongo:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        # Convert BSON to Json
        claim =  convert_bson_to_json(claimMongo)


        try:
            license_path = download_file_from_url(claim["drivingLicenseFront"])
            driver_path = download_file_from_url(claim["driverFace"])
            #! Detect Face Logic
            faceResult = await face_compare(license_path, driver_path, claim["drivingLicenseFront"] , claim["driverFace"])
        except Exception as e:
            faceResult = {
                "status": False, 
                "error": str(e), 
                "verified": None, 
                "model_results": None
            }

        try:
            #! Car model
            carModelResult = identify_car_model(claim["vehicleFront"])
        except Exception as e:
            carModelResult = {
                "status": False, 
                "error": str(e), 
                "model": 'N/A'
            }

        try:
            #! Read Licence
            readLicenceResult  = extract_driving_license_text(claim["drivingLicenseFront"])
        except Exception as e:
            readLicenceResult = {
                "status": False, 
                "error": str(e), 
                "licence_Details": 'N/A'
            }  

        try:
            #! Read Insurance
            readInsuranceResult = extract_insurance_card_text(claim["insuranceFront"])
        except Exception as e:
            readInsuranceResult = {
                "status": False, 
                "error": str(e), 
                "insurace_Details": 'N/A'
            }

        try:
            #! Read Number Plate
            print(claim["frontLicencePlate"]);
            readNumberPlateResult = extract_number_plates(claim["frontLicencePlate"])
        except Exception as e:
            readNumberPlateResult = {
                "status": False, 
                "error": str(e), 
                "number_plate": 'N/A'
            }

        #! Read VIN number
        try:
            vinNumberResult = exraction_vin_number(claim["vehicleFront"])
        except Exception as e:
            vinNumberResult = {
                "status": False, 
                "error": str(e), 
                "vin_number": 'N/A'
            }

        #! Read Color
        try:
            colorResult = exraction_color(claim["vehicleFront"])
        except Exception as e:
            colorResult = {
                "status": False, 
                "error": str(e), 
                "color": 'N/A'
            }


        # #! Compare Damage Images
        # try:

        #     # #######################################################################################

        #     # # Ensure vehicleId is an ObjectId before querying
        #     # vehicle_id = claim["vehicleId"]
        #     # if isinstance(vehicle_id, dict) and "$oid" in vehicle_id:
        #     #     vehicle_id = ObjectId(vehicle_id["$oid"])
        #     # elif isinstance(vehicle_id, str):
        #     #     vehicle_id = ObjectId(vehicle_id)

        #     # # Ensure claimId is an ObjectId before excluding it
        #     # current_claim_id = claim["_id"]
        #     # if isinstance(current_claim_id, dict) and "$oid" in current_claim_id:
        #     #     current_claim_id = ObjectId(current_claim_id["$oid"])
        #     # elif isinstance(current_claim_id, str):
        #     #     current_claim_id = ObjectId(current_claim_id)

        #     # # Find the claims that have damage Areas in the current claim
        #     # current_damage_areas = claim["damagedAreas"] or []
        #     # query = {
        #     #     "damagedAreas": {
        #     #         "$in": current_damage_areas  
        #     #     },
        #     #     "vehicleId" : vehicle_id,
        #     #     "_id": { "$ne": current_claim_id }
        #     # }

            
        #     # # Fetch claims with similar damage areas and same vehicleId
        #     # similar_claims = await claim_collection.find(query, {"_id": 1, "damagedAreas": 1, "damageImages": 1}).to_list(length=None)
        #     # # Convert BSON ObjectIds to JSON format
        #     # # similar_claims_formatted = []
        #     # # if len(similar_claims) > 0: 
        #     # #     similar_claims_formatted = [convert_bson_to_json(claim) for claim in similar_claims]

            
        
            
        #     # # Push Damage images of all similar claims to a new array
        #     # similar_damage_images = []
        #     # for claim in similar_claims:
        #     #     similar_damage_images.extend(claim["damageImages"])

        #     # # Pass Similer images list to compare images function
        #     # ###########################################################################################

        #     #! compare images
        #     url_set_1 = claim["damageImages"]

        #     url_set_2 = [
        #         'https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/DC_1.jpg',
        #         'https://insure-geini-s3.s3.us-east-1.amazonaws.com/6748472eae0fb7cdbf7190fa/CLM-1/NDC_1.jpg',
        #     ]
        #     similarity_score = damage_compare(url_set_1, url_set_2)

        # except Exception as e:
        #     similarity_score =   {
        #         "status": False,
        #         "error": str(e),
        #         "results": None
        #     }

        try:
            #! Verify the connection
            current_damageurl = await get_detections_images_current_claim(claimId)
            similer_claims = await get_similar_claims(claimId, claim["vehicleId"], claim["damagedAreas"])
            similer_damageurl = await get_detections_images_similar_claims(similer_claims)

            similarity_score = damage_compare(current_damageurl, similer_damageurl)

           
        except Exception as e:
            similarity_score =   {
                "status": False,
                "error": str(e),
                "results": None
            }    


        #? Return the results
        return {
            "model_result": carModelResult,  
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
    


def convert_bson_to_json(document):
    if isinstance(document, dict):
        return {key: convert_bson_to_json(value) for key, value in document.items()}
    elif isinstance(document, list):
        return [convert_bson_to_json(item) for item in document]
    elif isinstance(document, ObjectId):
        return str(document)  # Convert ObjectId to string
    else:
        return document
    
#################################################################################################################
#################################################################################################################

# Initialize client
secret_key = os.getenv("SECRET_KEY")
client = OpenAI(api_key=secret_key)

def identify_car_model(image_url):
    try:
        # Create assistant
        assistant = client.beta.assistants.create(
            name="Car Model Identifier",
            instructions="You are a car expert. Analyze images. Out of this values give me the answer car model. [Vezel, WagonR, Fit, KDH, Alto, Axio] No explanations. Response type example: Alto",
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}]
        )

        # Create thread
        thread = client.beta.threads.create()

        # Add message with image
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=[
                {"type": "text", "text": "Identify this car:"},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        )

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Wait for completion with a timeout mechanism
        MAX_RETRIES = 30  # Set a limit on retries
        retry_count = 0

        while run.status not in ["completed", "failed", "cancelled"]:
            if retry_count >= MAX_RETRIES:
                return {
                    "status": False, 
                    "error": "The car model identification process took too long.", 
                    "model": 'N/A'
                }

            time.sleep(2)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            retry_count += 1

        if run.status == "failed":
            return {
                    "status": False, 
                    "error": "The function failed to complete the request.", 
                    "model": 'N/A'
            }

        # Get response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        return {
            "status": True,
            "error": None,
            "model": messages.data[0].content[0].text.value
        }
        

    except Exception as e:  
        return {
            "status": False, 
            "error":  str(e), 
            "model": 'N/A'
        }


def extract_insurance_card_text(image_url):
    try:
        # Create assistant
        assistant = client.beta.assistants.create(
            name="Insurance Card OCR",
            instructions="You are an OCR expert. Extract all readable text from the insurance card image. Provide only the extracted text in a structured format with fields like Vehicle No, Model, Make, Policy No, Name, Address, Period Cover, Engine No, Chassis No Only. no explanations only output",
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}]
        )

        # Create thread
        thread = client.beta.threads.create()

        # Add message with image
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=[
                {"type": "text", "text": "Extract text from this insurance card:"},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        )

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Wait for completion with a timeout mechanism
        MAX_RETRIES = 30
        retry_count = 0

        while run.status not in ["completed", "failed", "cancelled"]:
            if retry_count >= MAX_RETRIES:
                return {
                    "status": False, 
                    "error": "The text extraction process took too long.", 
                    "insurace_Details": 'N/A'
                }
                

            time.sleep(2)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            retry_count += 1

        if run.status == "failed":
            return {
                "status": False, 
                "error": "The function failed to complete the request.", 
                "insurace_Details": 'N/A'
            }

        # Get response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        extracted_text = messages.data[0].content[0].text.value

        # Parsing the extracted text into JSON format
        insurance_details = {}
        lines = extracted_text.split("\n")
        for line in lines:
            match = re.match(r"(.+?):\s(.+)", line)
            if match:
                key = match.group(1).strip().replace(" ", "_").lower()
                value = match.group(2).strip()
                insurance_details[key] = value

        # Return structured JSON
        return {
            "status": True,
            "error": None,
            "insurance_Details": insurance_details
        }
        

    except Exception as e:
        return {
            "status": False, 
            "error":  str(e), 
            "insurace_Details": 'N/A'
        }


def extract_driving_license_text(image_url):
    try:

        # Create assistant
        assistant = client.beta.assistants.create(
            name="Driving License OCR",
            instructions="You are an OCR expert. Extract all readable text from the driving license image. Provide only the extracted text in a structured format with fields like License Number, Name, Address, Date of Birth, Issue Date, Expiry Date, Blood Group, NIC number only. no explanations only output",
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}]
        )

        # Create thread
        thread = client.beta.threads.create()

        # Add message with image
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=[
                {"type": "text", "text": "Extract text from this driving license:"},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        )

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Wait for completion with a timeout mechanism
        MAX_RETRIES = 30
        retry_count = 0

        while run.status not in ["completed", "failed", "cancelled"]:
            if retry_count >= MAX_RETRIES:
                return {
                    "status": False, 
                    "error": "The text extraction process took too long.", 
                    "licence_Details": 'N/A'
                }
                

            time.sleep(2)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            retry_count += 1

        if run.status == "failed":
            return {
                "status": False, 
                "error": "The text extraction process took too long.", 
                "licence_Details": 'N/A'
            }
            

        # Get response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        extracted_text = messages.data[0].content[0].text.value

        # Parsing the extracted text into JSON format
        license_details = {}
        lines = extracted_text.split("\n")
        for line in lines:
            match = re.match(r"(.+?):\s(.+)", line)
            if match:
                key = match.group(1).strip().replace(" ", "_").lower()
                value = match.group(2).strip()
                license_details[key] = value

        # Return structured JSON
        return {
            "status": True,
            "error": None,
            "licence_Details": license_details
        }

    except Exception as e:
        return {
            "status": False, 
            "error":  str(e), 
            "licence_Details": 'N/A'
        }
    
def extract_number_plates(image_url):
    try:
       
        # Create assistant
        assistant = client.beta.assistants.create(
            name="Vehicle Licemce Plate OCR",
            instructions="You are an OCR expert. Read license plate number. No explanation. response format is XXXXXXX or XXXXXX",
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}]
        )

        # Create thread
        thread = client.beta.threads.create()

        # Add message with image
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=[
                {"type": "text", "text": "Extract text from this license plate"},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        )

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Wait for completion with a timeout mechanism
        MAX_RETRIES = 30
        retry_count = 0

        while run.status not in ["completed", "failed", "cancelled"]:
            if retry_count >= MAX_RETRIES:
                return {
                    "status": False, 
                    "error": "The text extraction process took too long.", 
                    "number_plate": 'N/A'
                }
                

            time.sleep(2)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            retry_count += 1

        if run.status == "failed":
            return {
                "status": False, 
                "error": "The text extraction process took too long.", 
                "number_plate": 'N/A'
            }
            

        # Get response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        extracted_text = messages.data[0].content[0].text.value

        return {
            "status": True, 
            "error":  None, 
            "number_plate": extracted_text
        }


    except Exception as e:
        return {
            "status": False, 
            "error":  str(e), 
            "number_plate": 'N/A'
        }

def exraction_vin_number(image_url):
    try:
       
        # Create assistant
        assistant = client.beta.assistants.create(
            name="Vehicle VIN number OCR",
            instructions="You are an OCR expert. Read the VIN number of the image and provide the extracted text. No explanations. Response format is XXXXXXXXXXXXXXXXX",
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}]
        )

        # Create thread
        thread = client.beta.threads.create()

        # Add message with image
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=[
                {"type": "text", "text": "Extract text from this VIN number image"},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        )

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Wait for completion with a timeout mechanism
        MAX_RETRIES = 30
        retry_count = 0

        while run.status not in ["completed", "failed", "cancelled"]:
            if retry_count >= MAX_RETRIES:
                return {
                    "status": False, 
                    "error": "The text extraction process took too long.", 
                    "vin_number": 'N/A'
                }
                

            time.sleep(2)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            retry_count += 1

        if run.status == "failed":
            return {
                "status": False, 
                "error": "The text extraction process took too long.", 
                "vin_number": 'N/A'
            }
            

        # Get response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        extracted_text = messages.data[0].content[0].text.value

        return {
            "status": True, 
            "error":  str(e), 
            "vin_number": extracted_text
        }


    except Exception as e:
        return {
            "status": False, 
            "error":  str(e), 
            "vin_number": 'N/A'
        }



def exraction_color(image_url):
    try:

        # Create assistant once (outside function)
        assistant = client.beta.assistants.create(
        name="Vehicle color",
        instructions="You are an OCR expert. Detect the vehicle color. No explanations. Response format is [Red, Blue, Black, White, Silver, Grey, Green, Yellow, Orange, Brown]",
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}]
        )

        # Create thread
        thread = client.beta.threads.create()

        # Add message with image
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=[
                {"type": "text", "text": "Find the color of the vehicle in the image"},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        )

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Wait for completion with a timeout mechanism
        MAX_RETRIES = 30
        retry_count = 0

        while run.status not in ["completed", "failed", "cancelled"]:
            if retry_count >= MAX_RETRIES:
                return {
                    "status": False, 
                    "error": "The color extraction process took too long.", 
                    "color": 'N/A'
                }

            time.sleep(2)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            retry_count += 1

        if run.status == "failed":
            return {
                "status": False, 
                "error": "The color extraction process failed.", 
                "color": 'N/A'
            }

        # Get response
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        # Ensure we have valid message content
        extracted_text = "N/A"
        if messages.data and messages.data[0].content:
            extracted_text = messages.data[0].content[0].text.value  # Fix: Access .text directly

        return {
            "status": True, 
            "error": None,  # Fix: Error should be None if success
            "color": extracted_text
        }

    except Exception as e:
        return {
            "status": False, 
            "error": str(e),  # Fix: Convert exception to string for readability
            "color": 'N/A'
        }
    