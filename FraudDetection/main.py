from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
from services.driving_license import detect_face_compare, read_id_card
from services.insurance_card import read_insurance_card


app = FastAPI()
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/")
async def ping():
    return "Hello, I am alive!"

@app.post("/detect-face")
async def detect_face(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    try:
        # Save uploaded files
        license_path = os.path.join(TEMP_DIR, file1.filename)
        driver_path = os.path.join(TEMP_DIR, file2.filename)
        with open(license_path, "wb") as buffer:
            buffer.write(file1.file.read())
        with open(driver_path, "wb") as buffer:
            buffer.write(file2.file.read())

        # Call the service function
        result = detect_face_compare(license_path, driver_path)

        # If an error occurred, return it as the response
        if not result["status"]:
            return JSONResponse(content=result, status_code=400)

        # Return success response
        return result

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        # Cleanup temporary files
        for file_path in [license_path, driver_path]:
            if os.path.exists(file_path):
                os.remove(file_path)


@app.post("/read-id-card")
async def read_id_card_endpoint(file1: UploadFile = File(...)):
    image_path = None
    try:
        # Save uploaded file
        image_path = os.path.join(TEMP_DIR, file1.filename)
        with open(image_path, "wb") as buffer:
            buffer.write(file1.file.read())

        # Call the service function
        result = read_id_card(image_path)

        # If an error occurred, return it as the response
        if not result["status"]:
            return JSONResponse(content=result, status_code=400)

        # Return success response
        return result

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        # Cleanup temporary files
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


@app.post("/read-insurance-card")
async def detect_insurance_card(file1: UploadFile = File(...)):
    image_path = None
    try:
        # Save uploaded file
        image_path = os.path.join(TEMP_DIR, file1.filename)
        with open(image_path, "wb") as buffer:
            buffer.write(file1.file.read())

        # Call the service function
        result = read_insurance_card(image_path)

        # Validate the service function's response
        if not result["status"]:
            return JSONResponse(
                content={
                    "status": False,
                    "error": result["error"],
                    "extracted_data": result.get("extracted_data"),
                },
                status_code=400,
            )

        # Return success response
        return JSONResponse(
            content={
                "status": True,
                "error": None,
                "extracted_data": result.get("extracted_data"),
            },
            status_code=200,
        )

    except FileNotFoundError as e:
        # Handle file-related errors
        return JSONResponse(
            content={
                "status": False,
                "error": f"File not found: {str(e)}",
                "extracted_data": None,
            },
            status_code=404,
        )

    except ValueError as e:
        # Handle value-related errors
        return JSONResponse(
            content={
                "status": False,
                "error": f"Value error: {str(e)}",
                "extracted_data": None,
            },
            status_code=422,
        )

    except Exception as e:
        # Handle unexpected errors
        return JSONResponse(
            content={
                "status": False,
                "error": f"An unexpected error occurred: {str(e)}",
                "extracted_data": None,
            },
            status_code=500,
        )

    finally:
        # Cleanup temporary files
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


