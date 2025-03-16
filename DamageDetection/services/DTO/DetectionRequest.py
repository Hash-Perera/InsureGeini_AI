from pydantic import BaseModel

class DetectionRequest(BaseModel):
    claimId: str