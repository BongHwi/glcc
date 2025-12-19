from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

import crud
import schemas
import models
from database import get_db
from trackers.kr_adapter import track_kr
from trackers.global_scraper import track_global

router = APIRouter(prefix="/packages", tags=["packages"])

@router.post("/", response_model=schemas.PackageResponse, status_code=status.HTTP_201_CREATED)
async def create_package(
    package: schemas.PackageCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new package for tracking

    Automatically performs initial tracking on registration.
    If carrier is not provided, will attempt to auto-detect from tracking number.
    """
    # Auto-detect carrier if not provided
    if not package.carrier:
        from carrier_detector import detect_carrier
        detection = detect_carrier(package.tracking_number)

        if not detection.get("carrier"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not auto-detect carrier from tracking number. Please specify carrier manually."
            )

        package.carrier = detection["carrier"]

    # Check if package already exists
    existing = crud.get_package_by_tracking_number(db, package.tracking_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Package with tracking number {package.tracking_number} already exists"
        )

    # Create package in database
    db_package = crud.create_package(db, package)

    # Perform initial tracking
    try:
        if package.carrier.startswith("kr."):
            result = track_kr(package.carrier, package.tracking_number)
        elif package.carrier.startswith("global."):
            result = track_global(package.carrier, package.tracking_number)
        else:
            result = {"success": False, "error": "Unknown carrier prefix"}

        if result.get("success"):
            db_package = crud.update_package_status(
                db,
                package.tracking_number,
                result.get("status", "Unknown"),
                json.dumps(result)
            )
    except Exception as e:
        # Don't fail package creation if tracking fails
        pass

    return db_package

@router.get("/", response_model=List[schemas.PackageResponse])
async def list_packages(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get list of all packages

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **active_only**: Only return active packages
    """
    packages = crud.get_packages(db, skip=skip, limit=limit, active_only=active_only)
    return packages

@router.get("/{package_id}", response_model=schemas.PackageResponse)
async def get_package(
    package_id: int,
    db: Session = Depends(get_db)
):
    """Get package by ID"""
    package = crud.get_package(db, package_id)
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Package with ID {package_id} not found"
        )
    return package

@router.put("/{package_id}", response_model=schemas.PackageResponse)
async def update_package(
    package_id: int,
    package_update: schemas.PackageUpdate,
    db: Session = Depends(get_db)
):
    """Update package information"""
    package = crud.update_package(db, package_id, package_update)
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Package with ID {package_id} not found"
        )
    return package

@router.delete("/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_package(
    package_id: int,
    db: Session = Depends(get_db)
):
    """Delete package"""
    success = crud.delete_package(db, package_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Package with ID {package_id} not found"
        )
    return None

@router.post("/refresh", response_model=dict)
async def refresh_all_packages(
    db: Session = Depends(get_db)
):
    """
    Refresh tracking status for all active packages

    This is the most important endpoint - updates all package statuses
    """
    packages = crud.get_packages(db, active_only=True, limit=1000)

    results = {
        "total": len(packages),
        "success": 0,
        "failed": 0,
        "errors": []
    }

    for package in packages:
        try:
            if package.carrier.startswith("kr."):
                result = track_kr(package.carrier, package.tracking_number)
            elif package.carrier.startswith("global."):
                result = track_global(package.carrier, package.tracking_number)
            else:
                results["failed"] += 1
                results["errors"].append({
                    "tracking_number": package.tracking_number,
                    "error": "Unknown carrier prefix"
                })
                continue

            if result.get("success"):
                crud.update_package_status(
                    db,
                    package.tracking_number,
                    result.get("status", "Unknown"),
                    json.dumps(result)
                )
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "tracking_number": package.tracking_number,
                    "error": result.get("error", "Unknown error")
                })
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "tracking_number": package.tracking_number,
                "error": str(e)
            })

    return results

@router.post("/{package_id}/track", response_model=schemas.TrackingResult)
async def track_package(
    package_id: int,
    db: Session = Depends(get_db)
):
    """
    Track a specific package and update its status
    """
    package = crud.get_package(db, package_id)
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Package with ID {package_id} not found"
        )

    try:
        if package.carrier.startswith("kr."):
            result = track_kr(package.carrier, package.tracking_number)
        elif package.carrier.startswith("global."):
            result = track_global(package.carrier, package.tracking_number)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown carrier prefix"
            )

        if result.get("success"):
            crud.update_package_status(
                db,
                package.tracking_number,
                result.get("status", "Unknown"),
                json.dumps(result)
            )

        return schemas.TrackingResult(
            tracking_number=package.tracking_number,
            carrier=package.carrier,
            status=result.get("status", "Unknown"),
            details=result.get("raw_data") or result,
            error=result.get("error")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tracking failed: {str(e)}"
        )
