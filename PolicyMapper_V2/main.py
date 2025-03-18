from fastapi import FastAPI
from audio.audio_pre_processing import process_audio
from audio.speech_to_text import transcribe_audio
from crud.claim import get_claim
from models.policy_mapper import evaluate_claim_using_llma
from models.summary_generator import generate_summary
from helpers.util import download_audio_file, extract_metadata_from_audio_file_url, upload_pdf_to_s3
import aio_pika
import asyncio
import json
from dotenv import load_dotenv
import os
from crud.policy import create_policy
from crud.claim import update_claim_status_start, update_claim_status_end
from contextlib import asynccontextmanager
from core.db import verify_connection
from crud.user import get_user
from crud.vehicle import get_vehicle
from crud.damage_detection import get_damage_detection
from document_generator.data_collector import collect_data
from document_generator.pdf_generator import PDFGenerator
from bson import ObjectId

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME")

async def consume_and_forward():
    try:
        # Try connecting to RabbitMQ
        print("🔄 Attempting to connect to RabbitMQ...")
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        print("✅ Successfully connected to RabbitMQ")
        
        async with connection:
            channel = await connection.channel()
            print("📡 Channel created")
            
            # Declare queue and print queue info
            policy_queue = await channel.declare_queue("policy_queue", durable=True)
            queue_info = await policy_queue.declare()
            print(f"📊 Queue Status:")
            print(f"   - Queue Name: {policy_queue.name}")
            print(f"   - Message Count: {queue_info.message_count}")
            print(f"   - Consumer Count: {queue_info.consumer_count}")

            print("🎯 Starting to consume messages...")
            async for message in policy_queue:
                print(f"📨 Received message: {message.message_id}")
                async with message.process():
                    try:
                        data = json.loads(message.body)
                        claimId = data.get('claimId')

                        print(f"🔍 Processing Policy Mapper for: {claimId}")

                        if not claimId:
                            print("⚠️ Missing claimId in message. Skipping.")
                            continue

                        # Update the claim status to 'Policy Mapper Started'
                        await update_claim_status_start(claimId)

                        result = await main(claimId)
                        
                        if not result:
                            print(f"⚠️ Policy Mapper failed for claimId: {claimId}")
                            continue

                        new_policy_record = await create_policy(result, claimId)
                        
                        print(f"📝 Inserted to fraud collection: {new_policy_record}")
                        
                        # Update the claim status to 'Policy Mapper Completed'
                        await update_claim_status_end(claimId)
                        print("✅ Message processed successfully")

                    except Exception as e:
                        print(f"❌ Error processing message: {e}")
                        continue  # Ensure the loop continues even if an error occurs

    except aio_pika.exceptions.AMQPConnectionError as conn_err:
        print(f"❌ Failed to connect to RabbitMQ: {conn_err}")
        print("⚠️ Please check if RabbitMQ server is running and credentials are correct")
    except Exception as e:
        print(f"❌ Critical Error in consume_and_forward: {e}")

async def start_policy_consumer():
    print("🚀 Starting policy consumer...")
    asyncio.create_task(consume_and_forward())
    print("✅ Policy consumer started successfully")
    
# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles app startup and shutdown events."""
    # Ensure the database connection is verified
    await verify_connection()
    # Start fraud queue consumer in the background
    task = asyncio.create_task(start_policy_consumer())
    yield  # Allow FastAPI to run
    # Cleanup if necessary (optional)
    task.cancel()
from core.logger import Logger

logger = Logger()

app = FastAPI(
    title="Claims Processing API",
    description="API for processing insurance claims",
    version="1.0.0",
   # lifespan=lifespan
)
logger.info("Starting API")

def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

async def main(claim_id: str | ObjectId) -> dict:
    if not ObjectId.is_valid(claim_id):
        logger.error(f"Invalid claim_id: {claim_id}")
        return {"error": "Invalid claim_id"}
    
    logger.info(f"Getting claim record for claim_id: {claim_id}")

    claim_record: dict = await get_claim(claim_id)
    audio_file_url: str = claim_record.get("audio")
    logger.info(f"Extracting metadata from audio file url: {audio_file_url}")
    audio_file_metadata: dict = await extract_metadata_from_audio_file_url(
        audio_file_url
    )
    logger.info(f"Downloading audio file to temp directory")
    audio_file_saved_path: str | None = await download_audio_file(
        audio_file_metadata,
        f"./temp/{audio_file_metadata.get('user_id')}/{audio_file_metadata.get('claim_number')}/{audio_file_metadata.get('audio_file_name')}",
    )
    if audio_file_saved_path is None:
        logger.error(f"Failed to download audio file")
        return {"error": "Failed to download audio file"}
    
    logger.info(f"Processing audio file")
    processed_audio_file_path: str | None = process_audio(
        audio_file_saved_path,
        f"./temp/{audio_file_metadata.get('user_id')}/{audio_file_metadata.get('claim_number')}/{audio_file_metadata.get('audio_file_name')}",
    )
    if processed_audio_file_path is None:
        logger.error(f"Failed to process audio file")
        return {"error": "Failed to process audio file"}
    
    logger.info(f"Audio file processed successfully")

    transcribed_text = transcribe_audio(processed_audio_file_path)
    logger.info(f"Transcribed text: {transcribed_text}")
    
    claim_data = claim_record
    claim_data['audio_to_text'] = transcribed_text
    user_data = await get_user(claim_record.get("userId"))

    print("\n")
    print(f"User data: {user_data}")
    print("\n")

    vehicle_data = await get_vehicle(claim_record.get("vehicleId"))

    print("\n")
    print(f"Vehicle data: {vehicle_data}")
    print("\n")

    damage_detection_data = await get_damage_detection(claim_record.get("_id"))
    incident_summary = generate_summary(user_data, vehicle_data, damage_detection_data, claim_data)
  
    data = collect_data(user_data, vehicle_data, damage_detection_data, claim_data, incident_summary)
    pdf_generator = PDFGenerator()
    pdf_generator.generate_pdf(data, f"{audio_file_metadata.get('user_id')}/{audio_file_metadata.get('claim_number')}/vehicle_damage_report.pdf", "report_template.html")

    # upload the pdf to s3
    if await upload_pdf_to_s3(
        f"temp/{audio_file_metadata.get('user_id')}/{audio_file_metadata.get('claim_number')}/vehicle_damage_report.pdf",
        f"{audio_file_metadata.get('user_id')}/{audio_file_metadata.get('claim_number')}/vehicle_damage_report.pdf"
    ):
        logger.info(f"PDF uploaded to s3 successfully")
    else:
        logger.error(f"Failed to upload PDF to s3")
        return {"error": "Failed to upload PDF to s3"}
    
    result = evaluate_claim_using_llma(claim_data, damage_detection_data, vehicle_data)
    print("\n")
    print(json.dumps(result, indent=4, default=convert_objectid))
    print("\n")


    data = collect_data(user_data, vehicle_data, result, incident_summary)
    pdf_generator = PDFGenerator()
    pdf_generator.generate_pdf(data, f"{audio_file_metadata.get('user_id')}/{audio_file_metadata.get('claim_number')}/decision_report.pdf", "decision_report.html")

    # upload the pdf to s3
    if await upload_pdf_to_s3(
        f"temp/{audio_file_metadata.get('user_id')}/{audio_file_metadata.get('claim_number')}/decision_report.pdf",
        f"{audio_file_metadata.get('user_id')}/{audio_file_metadata.get('claim_number')}/decision_report.pdf"
    ):
        logger.info(f"PDF uploaded to s3 successfully")
    else:
        logger.error(f"Failed to upload PDF to s3")
        
        
        
        
    final_result = {
            "audioToTextConvertedContext": transcribed_text,
            "status": result.get('overall_status'),
            "estimation_requested": result.get('total_cost'),
            "estimation_approved": result.get('approved_costs'),
            "reason": "Rear-ended at a red light",
            "incidentReport": f"https://insure-geini-s3.s3.us-east-1.amazonaws.com/{audio_file_metadata.get('user_id')}/{audio_file_metadata.get('claim_number')}/vehicle_damage_report.pdf",
            "decisionReport": f"https://insure-geini-s3.s3.us-east-1.amazonaws.com/{audio_file_metadata.get('user_id')}/{audio_file_metadata.get('claim_number')}/decision_report.pdf"
    }
        
    new_policy_record = await create_policy(result=final_result, claim_id=claim_id)
    print(f"📝 Inserted to fraud collection: {new_policy_record}")
 
@app.get("/", response_model=None)
async def read_root(claim_id: str = "67a1cacfeace4f9501a8c964") -> dict:
    logger.info(f"Received request for claim_id: {claim_id}")
    await main(claim_id)
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
