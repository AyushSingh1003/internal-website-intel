from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base
import json
from datetime import datetime, timezone


class Scan(Base):
    """Stores website scan results"""
    
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    website_url = Column(String, nullable=False, index=True)
    
    # Structured data (stored as JSON string)
    company_name = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    emails = Column(Text, nullable=True)  # JSON array as string
    phone_numbers = Column(Text, nullable=True)  # JSON array as string
    socials = Column(Text, nullable=True)  # JSON array as string
    addresses = Column(Text, nullable=True)  # JSON array as string
    notes = Column(Text, nullable=True)
    sources = Column(Text, nullable=True)  # JSON array as string
    
    # Full structured JSON for easy retrieval
    structured_data = Column(Text, nullable=False)  # Complete JSON
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        """Convert model to dictionary with parsed JSON fields"""
        return {
            "id": self.id,
            "website_url": self.website_url,
            "company_name": self.company_name,
            "summary": self.summary,
            "structured_data": json.loads(self.structured_data) if self.structured_data else {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
