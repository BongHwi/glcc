from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PackageBase(BaseModel):
    tracking_number: str = Field(..., description="Tracking number")
    carrier: str = Field(..., description="Carrier code (e.g., kr.cj, global.ups)")
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
