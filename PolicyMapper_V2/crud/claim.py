from bson import ObjectId
from core.db import claim_collection


async def get_claim(claim_id: str):
    claim_record = await claim_collection.find_one({"_id": ObjectId(claim_id)})
    return claim_record


async def update_claim_status_start(claim_id):
    result = await claim_collection.update_one(
        {"_id": ObjectId(claim_id)},
        {"$set": {"status": 'Policy Started'}}
    )
    print(f"Claim status updated: {result.modified_count}")
    
# Update the claim status
async def update_claim_status_end(claim_id):
    result = await claim_collection.update_one(
        {"_id": ObjectId(claim_id)},
        {"$set": {"status": 'Completed'}}
    )
    print(f"Claim status updated: {result.modified_count}")