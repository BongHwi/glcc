"""
Carriers Router

API endpoints for carrier detection and carrier information.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import schemas
from carrier_detector import detect_carrier, get_supported_carriers_with_patterns


router = APIRouter(prefix="/carriers", tags=["carriers"])


@router.post("/detect", response_model=schemas.CarrierDetectionResponse)
async def detect_carrier_from_tracking_number(
    request: schemas.CarrierDetectionRequest
) -> schemas.CarrierDetectionResponse:
    """
    Detect carrier from tracking number pattern

    Automatically identifies the most likely carrier based on tracking number format.

    Args:
        request: CarrierDetectionRequest with tracking_number

    Returns:
        CarrierDetectionResponse with detected carrier and confidence level

    Example:
        Request: {"tracking_number": "EN387436585JP"}
        Response: {
            "carrier": "global.jppost",
            "confidence": "high",
            "pattern_matched": "Ends with JP (e.g., EN123456789JP)",
            "tracking_number": "EN387436585JP"
        }
    """
    if not request.tracking_number or not request.tracking_number.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tracking number is required"
        )

    # Detect carrier using pattern matching
    result = detect_carrier(request.tracking_number)

    return schemas.CarrierDetectionResponse(**result)


@router.get("/", response_model=Dict[str, Any])
async def list_supported_carriers() -> Dict[str, Any]:
    """
    Get list of all supported carriers with their pattern information

    Returns a list of carriers sorted by detection priority (highest first).

    Returns:
        Dictionary with carriers list and total count

    Example Response:
        {
            "carriers": [
                {
                    "id": "global.jppost",
                    "name": "Japan Post",
                    "patterns": ["Ends with JP (e.g., EN123456789JP)"],
                    "priority": 10
                },
                ...
            ],
            "count": 15
        }
    """
    return get_supported_carriers_with_patterns()
