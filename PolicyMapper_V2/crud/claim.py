from bson import ObjectId
from core.db import claim_collection


async def get_claim(claim_id: str):
    claim_record = await claim_collection.find_one({"_id": ObjectId(claim_id)})
    return claim_record