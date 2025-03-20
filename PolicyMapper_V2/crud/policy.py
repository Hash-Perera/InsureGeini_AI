from core.db import report_collection
from datetime import datetime
from bson import ObjectId

async def create_policy(result, claim_id):
    print(result.get("evaluation"))
    policy_record = {
        "claimId": ObjectId(claim_id),
        "audioToTextConvertedContext": result.get("audioToTextConvertedContext"),
        "status": result.get("status"),
        "estimation_requested": result.get("estimation_requested"),
        "estimation_approved": result.get("estimation_approved"),
        "reason": result.get("reason"),
        "incidentReport": result.get("incidentReport"),
        "decisionReport": result.get("decisionReport"),
        "evaluation": result.get("evaluation"),
        "createdAt": datetime.now(),
    }
    
    await report_collection.insert_one(policy_record)
    print(f"📝 Inserted to report collection: {policy_record}")
    return policy_record
    
    
