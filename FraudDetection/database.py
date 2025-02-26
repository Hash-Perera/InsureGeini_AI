from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB Connection String
MONGO_URI = os.getenv("MONGODB_URI")

# Create a MongoDB client
client = AsyncIOMotorClient(MONGO_URI)

# Access the database
database = client.InsureGeini

# Access the collection
claim_collection = database.get_collection("claims")

# Function to verify connection
async def verify_connection():
    try:
        # Ping the MongoDB server
        await client.admin.command("ping")
        print("MongoDB connection successful!")
    except ServerSelectionTimeoutError as e:
        print("MongoDB connection failed:", str(e))

