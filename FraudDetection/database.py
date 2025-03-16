import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv
from bson import ObjectId


load_dotenv()

# MongoDB Connection String
MONGO_URI = os.getenv("MONGODB_URI")

# Create a MongoDB client
client = AsyncIOMotorClient(MONGO_URI)

# Access the database
database = client.InsureGeini

# Access the collection
claim_collection = database.get_collection("claims")
fraud_collection = database.get_collection("frauds")

# Function to verify connection
async def verify_connection():
    try:
        # Ping the MongoDB server
        await client.admin.command("ping")
        print("MongoDB connection successful!")
    except ServerSelectionTimeoutError as e:
        print("MongoDB connection failed:", str(e))

# Function to insert a document
async def insert_to_fraud_collection(result, claim_id):
    fraud_record = {
        "claim": ObjectId(claim_id),
        "model_result": result.get("model_result", {}),
        "face_result": result.get("face_result", {}),
        "read_licence_result": result.get("read_licence_result", {}),
        "read_insurance_result": result.get("read_insurance_result", {}),
        "number_plates": result.get("number_plates", "N/A"),
        "similarity_score": result.get("similarity_score", {}),
        "vin_number": result.get("vin_number", {}),
        "color": result.get("color", {}),
    }
    
    result = await fraud_collection.insert_one(fraud_record)
    print(f"Document inserted with ID: {result.inserted_id}")
    return result.inserted_id;

# Update the claim status
async def update_claim_status_start(claim_id):
    result = await claim_collection.update_one(
        {"_id": ObjectId(claim_id)},
        {"$set": {"status": 'Fraud Detection Started'}}
    )
    print(f"Claim status updated: {result.modified_count}")
# Update the claim status
async def update_claim_status_end(claim_id):
    result = await claim_collection.update_one(
        {"_id": ObjectId(claim_id)},
        {"$set": {"status": 'Fraud Detection Completed'}}
    )
    print(f"Claim status updated: {result.modified_count}")

