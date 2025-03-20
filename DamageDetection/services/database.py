# ai_model_pipeline/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# ✅ MongoDB Configuration
MONGO_URI = "mongodb+srv://vhprabhathperera222:aycSTwnGqfIfHAYZ@clusterhash.fxzh5ya.mongodb.net/InsureGeini?retryWrites=true&w=majority"
DB_NAME = "InsureGeini"

# ✅ Initialize MongoDB Client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

claim_collection = db.get_collection("claims")

# Update the claim status
async def update_claim_status_start(claim_id):
    result = await claim_collection.update_one(
        {"_id": ObjectId(claim_id)},
        {"$set": {"status": 'Damage Detection Started'}}
    )
    print(f"Claim status updated: {result.modified_count}")

# Update the claim status
async def update_claim_status_end(claim_id):
    result = await claim_collection.update_one(
        {"_id": ObjectId(claim_id)},
        {"$set": {"status": 'Damage Detection Completed'}}
    )
    print(f"Claim status updated: {result.modified_count}")