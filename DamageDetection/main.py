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


@app.post("/predict")
async def predict(request: DetectionRequest):
    print("call received")
    await damage_Detector(request.claimId)
    print(f"🔍 Processing damage detection for: {request.claimId}")