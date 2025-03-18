from core.db import report_collection
from datetime import datetime

async def create_policy(result, claim_id):
    policy_record = {
        "claim_id": claim_id,
        "audioToTextConvertedContext": result.get("audioToTextConvertedContext"),
        "status": result.get("status"),
        "estimation_requested": result.get("estimation_requested"),
        "estimation_approved": result.get("estimation_approved"),
        "reason": result.get("reason"),
        "incidentReport": result.get("incidentReport"),
        "decisionReport": result.get("decisionReport"),
        "createdAt": datetime.now(),
    }
    
    await report_collection.insert_one(policy_record)
    print(f"📝 Inserted to report collection: {policy_record}")
    return policy_record
    
    
