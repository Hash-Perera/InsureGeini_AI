import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Final
from pymongo.errors import ServerSelectionTimeoutError

load_dotenv()

MONGODB_URI: Final = os.getenv("MONGODB_URI")

client = AsyncIOMotorClient(MONGODB_URI)
db = client.InsureGeini

claim_collection = db.get_collection("claims")
detection_collection = db.get_collection("detections")
feedback_collection = db.get_collection("feedbacks")
fraud_collection = db.get_collection("frauds")
report_collection = db.get_collection("reports")
reporttest_collection = db.get_collection("reporttests")
role_collection = db.get_collection("roles")
user_collection = db.get_collection("users")
vehicle_collection = db.get_collection("vehicles")

# Function to verify connection
async def verify_connection():
    try:
        # Ping the MongoDB server
        await client.admin.command("ping")
        print("MongoDB connection successful!")
    except ServerSelectionTimeoutError as e:
        print("MongoDB connection failed:", str(e))