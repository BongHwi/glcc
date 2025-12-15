from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    tracking_number = Column(String, unique=True, index=True, nullable=False)
    carrier = Column(String, nullable=False)  # e.g., "kr.cj", "global.ups"
    alias = Column(String, nullable=True)  # User-friendly name
    status = Column(String, nullable=True)  # Latest delivery status
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)  # Track only active packages
    notify_enabled = Column(Boolean, default=True)  # Send notifications

    # JSON field for storing full tracking history/details
    tracking_data = Column(String, nullable=True)

    def __repr__(self):
        return f"<Package {self.tracking_number} ({self.carrier})>"
