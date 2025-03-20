from bson import ObjectId
from core.db import vehicle_collection

async def get_vehicle(vehicle_id: str):
    vehicle_record = await vehicle_collection.find_one({"_id": ObjectId(vehicle_id)})
    return vehicle_record
