import asyncio
from contextlib import asynccontextmanager
from services.damage_detector import damage_Detector
from services.queue_service import start_damage_consumer
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from services.pipeline_builder import AIModelPipelineBuilder
from services.inference.ModelFactory import ModelFactory
from services.utils.PreProcess import PreProcess
from services.utils.PostProcess import PostProcess
from services.DB_models.detection_model import DetectionModel
from services.DTO.DetectionRequest import DetectionRequest
from services.database import db
from services.utils.aws import download_image_from_s3, get_image_from_s3
import gc
import requests
from PIL import Image
import io


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles app startup and shutdown events."""
    # Ensure the database connection is verified
    # await verify_connection()
    # Start fraud queue consumer in the background
    task = asyncio.create_task(start_damage_consumer())
    yield  # Allow FastAPI to run
    # Cleanup if necessary (optional)
    task.cancel()


# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def check():
    return {"message": "FastAPI Active"}

# loaded_models = {
#     "detector": ModelFactory.create_model("YoloV8Detector", "./AI_Modles/YoloV8Detection.pt"),
#     "segmenter": ModelFactory.create_model("YoloV8Segmenter", "./AI_Modles/YoloV8Segmentation.pt"),
#     "classifire": ModelFactory.create_model("VggClassifire", "./AI_Modles/Vgg16Classification.h5")
# }

# #Maybe add a director to build the pipeline
# def get_pipeline():
#     return (
#         AIModelPipelineBuilder(list(loaded_models.values()))
#         .set_preprocessor(PreProcess()) 
#         .set_postprocessor(PostProcess()) 
#         .build()
#     )

# @app.post("/predict")
async def predict(claimId):
    await damage_Detector(claimId)
    print(f"🔍 Processing damage detection for: {claimId}")

    # #Add db calls to get the obd codes from claims collection
    # claim = await db.claims.find_one({"_id": ObjectId(claimId)},{"damageImages":1, "_id": 0})
    # obd_codes = ["B3108","B0050"]

    # if not claim:
    #     raise HTTPException(status_code=404, detail="Claim not found")
    
    # print(claim)
    
    # img_url = claim["damageImages"][0]

    # image = get_image_from_s3(img_url)

    # # image = download_image_from_s3(img_url)

    # # try:
    # #     response = requests.get(img_url, timeout=10)  # Fetch image from URL
    # #     response.raise_for_status()  # Check for HTTP errors
    # #     image_bytes = response.content  # Get image data
    # #     image = Image.open(io.BytesIO(image_bytes))  # Open image with PIL
    # # except Exception as e:
    # #     raise HTTPException(status_code=500, detail=f"Failed to fetch image from URL: {str(e)}")

    # pipeline = get_pipeline()
    # image_path = "C:/Users/user/Desktop/SLIIT/Year 4 Semester 1/Demo Images/detectionTest1.jpg"
    
    # #send the obd codes too
    # result = await pipeline.process_image(image,obd_codes,claimId)
    
    # detection_docs = []
    # for d in result:
    #     detection_docs.append(
    #         DetectionModel(
    #             claimId=ObjectId(claimId),
    #             part=d["part"],
    #             damageType=d["damageType"],
    #             severity=d["severity"],
    #             obd_code=d["obd_code"],
    #             internal=d["internal"],
    #             decision=d["decision"],
    #             reason=d["reason"],
    #             image_url=d["image_url"],
    #             cost=d["cost"],
    #             flag=d["flag"]
    #         ).model_dump(exclude_unset=True)
    #         )

    
    # inserted_results = await db.detections.insert_many(detection_docs)

    # print(inserted_results)

    # # Destroying the pipeline object after processing
    # del pipeline
    # gc.collect()

    # return {"message": "Damage Detection Completed"}