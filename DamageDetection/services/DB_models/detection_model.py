from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List, Optional, Any
from datetime import datetime



class DetectionModel(BaseModel):
    """Schema for AI result data to be stored in MongoDB (matches Node.js model, all fields optional)."""

    
    # claimId: Optional[PyObjectId] = Field(None, description="Claim ID reference")
    part: Optional[str] = Field(None, description="Part of the vehicle that was damaged")
    damageType: Optional[List[str]] = Field(None, description="Types of damages detected")
    severity: Optional[str] = Field(None, description="Severity level of damage")
    obd_code: Optional[bool] = Field(None, description="OBD sensor reading (if applicable)")
    internal: Optional[str] = Field(None, description="Probable cause of damage")
    decision: Optional[str] = Field(None, description="Final decision (Repair or Replace)")
    reason: Optional[str] = Field(None, description="Reason for decision")
    image_url: Optional[str] = Field(None, description="URL of cropped damaged part image")
    cost: Optional[float] = Field(None, description="Estimated repair/replacement cost")
    flag: Optional[str] = Field(None, description="Flag for multiple damages")

    class Config:
        extra = "allow"
    

class DetectionInDB(DetectionModel):
    """Schema for MongoDB document (includes _id)."""
    id: str = Field(..., alias="_id")  # Convert MongoDB _id to string
