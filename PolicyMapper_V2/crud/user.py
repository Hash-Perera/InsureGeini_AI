from bson import ObjectId
from core.db import user_collection

async def get_user(user_id: str):
    user_record = await user_collection.find_one({"_id": ObjectId(user_id)})
    return user_record

