from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

# MongoDB Connection String
MONGO_URI = "mongodb+srv://vhprabhathperera222:aycSTwnGqfIfHAYZ@clusterhash.fxzh5ya.mongodb.net/InsureGeini?retryWrites=true&w=majority"

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

