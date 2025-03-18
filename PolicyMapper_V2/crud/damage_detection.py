import os
from bson import ObjectId
from core.db import detection_collection

async def get_damage_detection(claim_id: str):

    detection_record = await detection_collection.find({"claimId": ObjectId(claim_id)}).to_list(None)

    return detection_record