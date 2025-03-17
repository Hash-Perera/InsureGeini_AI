from bson import ObjectId
from fastapi import FastAPI, HTTPException
from pipeline_builder import AIModelPipelineBuilder
from inference.ModelFactory import ModelFactory
from utils.PreProcess import PreProcess
from utils.PostProcess import PostProcess
from DB_models.detection_model import DetectionModel
from DTO.DetectionRequest import DetectionRequest
from database import db
from utils.aws import download_image_from_s3, get_image_from_s3
import gc
import requests
from PIL import Image
import io

app = FastAPI()

@app.get("/")
async def check():
    return {"message": "FastAPI Active"}

loaded_models = {
    "detector": ModelFactory.create_model("YoloV8Detector", "../AI_Modles/YoloV8Detection.pt"),
    "segmenter": ModelFactory.create_model("YoloV8Segmenter", "../AI_Modles/YoloV8Segmentation.pt"),
    "classifire": ModelFactory.create_model("VggClassifire", "../AI_Modles/Vgg16Classification.h5")
}

#Maybe add a director to build the pipeline
def get_pipeline():
    return (
        AIModelPipelineBuilder(list(loaded_models.values()))
        .set_preprocessor(PreProcess()) 
        .set_postprocessor(PostProcess()) 
        .build()
    )

@app.post("/predict")
async def predict(request: DetectionRequest):
    #Incude db calls to retrive the image url
    #Most probably the object id will be sent
    claim = await db.claims.find_one({"_id": ObjectId(request.claimId)},{"damageImages":1, "_id": 0})

    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    print(claim)
    
    img_url = claim["damageImages"][0]

    image = get_image_from_s3(img_url)

    # image = download_image_from_s3(img_url)

    # try:
    #     response = requests.get(img_url, timeout=10)  # Fetch image from URL
    #     response.raise_for_status()  # Check for HTTP errors
    #     image_bytes = response.content  # Get image data
    #     image = Image.open(io.BytesIO(image_bytes))  # Open image with PIL
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to fetch image from URL: {str(e)}")

    pipeline = get_pipeline()
    image_path = "C:/Users/user/Desktop/SLIIT/Year 4 Semester 1/Demo Images/detectionTest1.jpg"
    result = pipeline.process_image(image)
    
    detection_docs = []
    for d in result:
        detection_docs.append(
            DetectionModel(
                claimId=None,
                part=d["part"],
                damageType=d["damageType"],
                severity=d["severity"],
                obd_code=d["obd_code"],
                decision=d["decision"],
                reason=d["reason"],
                cost=d["cost"]
            ).model_dump(exclude_unset=True)
            )

    
    inserted_results = await db.detections.insert_many(detection_docs)

    print(inserted_results)

    # Destroying the pipeline object after processing
    del pipeline
    gc.collect()

    return {"message": "Damage Detection Completed"}