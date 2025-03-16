# ai_model_pipeline/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient

# ✅ MongoDB Configuration
MONGO_URI = "mongodb+srv://vhprabhathperera222:aycSTwnGqfIfHAYZ@clusterhash.fxzh5ya.mongodb.net/InsureGeini?retryWrites=true&w=majority"
DB_NAME = "InsureGeini"

# ✅ Initialize MongoDB Client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]