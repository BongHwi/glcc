from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PackageBase(BaseModel):
    tracking_number: str = Field(..., description="Tracking number")
    carrier: Optional[str] = Field(None, description="Carrier code (e.g., kr.cj, global.ups). If not provided, will be auto-detected.")
    alias: Optional[str] = Field(None, description="User-friendly name for the package")
    notify_enabled: bool = Field(True, description="Enable notifications for this package")

class PackageCreate(PackageBase):
    pass

class PackageUpdate(BaseModel):
    alias: Optional[str] = None
    is_active: Optional[bool] = None
    notify_enabled: Optional[bool] = None

class PackageResponse(PackageBase):
    id: int
    status: Optional[str] = None
    last_updated: datetime
    created_at: datetime
    is_active: bool
    tracking_data: Optional[str] = None

    class Config:
        from_attributes = True

class TrackingResult(BaseModel):
    """Response model for tracking API"""
    tracking_number: str
    carrier: str
    status: str
    details: Optional[dict] = None
    error: Optional[str] = None

class CarrierDetectionRequest(BaseModel):
    """Request model for carrier detection"""
    tracking_number: str = Field(..., description="Tracking number to analyze")

class CarrierDetectionResponse(BaseModel):
    """Response model for carrier detection"""
    carrier: Optional[str] = Field(None, description="Detected carrier code (e.g., global.jppost)")
    confidence: str = Field(..., description="Confidence level: high, medium, low, or none")
    pattern_matched: Optional[str] = Field(None, description="Description of the pattern that was matched")
    tracking_number: str = Field(..., description="Original tracking number")
    error: Optional[str] = Field(None, description="Error message if detection failed")
