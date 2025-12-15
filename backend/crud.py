from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas

def get_package(db: Session, package_id: int) -> Optional[models.Package]:
    """Get package by ID"""
    return db.query(models.Package).filter(models.Package.id == package_id).first()

def get_package_by_tracking_number(db: Session, tracking_number: str) -> Optional[models.Package]:
    """Get package by tracking number"""
    return db.query(models.Package).filter(models.Package.tracking_number == tracking_number).first()

def get_packages(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[models.Package]:
    """Get all packages"""
    query = db.query(models.Package)
    if active_only:
        query = query.filter(models.Package.is_active == True)
    return query.offset(skip).limit(limit).all()

def create_package(db: Session, package: schemas.PackageCreate) -> models.Package:
    """Create new package"""
    db_package = models.Package(
        tracking_number=package.tracking_number,
        carrier=package.carrier,
        alias=package.alias,
        notify_enabled=package.notify_enabled
    )
    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package

def update_package(db: Session, package_id: int, package_update: schemas.PackageUpdate) -> Optional[models.Package]:
    """Update package"""
    db_package = get_package(db, package_id)
    if not db_package:
        return None

    update_data = package_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_package, field, value)

    db.commit()
    db.refresh(db_package)
    return db_package

def update_package_status(db: Session, tracking_number: str, status: str, tracking_data: Optional[str] = None) -> Optional[models.Package]:
    """Update package tracking status"""
    db_package = get_package_by_tracking_number(db, tracking_number)
    if not db_package:
        return None

    db_package.status = status
    if tracking_data:
        db_package.tracking_data = tracking_data

    db.commit()
    db.refresh(db_package)
    return db_package

def delete_package(db: Session, package_id: int) -> bool:
    """Delete package"""
    db_package = get_package(db, package_id)
    if not db_package:
        return False

    db.delete(db_package)
    db.commit()
    return True
