from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.scan import Scan
from app.schemas.scan import ScanResult
import json


class DatabaseService:
    """Service for database operations on scans"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_scan(self, website_url: str, structured_data: ScanResult) -> Scan:
        """
        Save a scan result to the database
        """
        # Convert structured_data to dict for storage
        data_dict = structured_data.model_dump()
        
        # Create new scan record
        scan = Scan(
            website_url=website_url,
            company_name=structured_data.company_name,
            summary=structured_data.summary,
            emails=json.dumps(structured_data.emails),
            phone_numbers=json.dumps(structured_data.phone_numbers),
            socials=json.dumps([s.model_dump() for s in structured_data.socials]),
            addresses=json.dumps(structured_data.addresses),
            notes=structured_data.notes,
            sources=json.dumps(structured_data.sources),
            structured_data=json.dumps(data_dict)
        )
        
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)
        
        return scan
    
    def get_scan_by_id(self, scan_id: int) -> Optional[Scan]:
        """Get a specific scan by ID"""
        return self.db.query(Scan).filter(Scan.id == scan_id).first()
    
    def get_all_scans(self, limit: int = 100, offset: int = 0) -> List[Scan]:
        """
        Get all scans with pagination
        Ordered by most recent first
        """
        return (
            self.db.query(Scan)
            .order_by(Scan.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_scans_by_website(self, website_url: str) -> List[Scan]:
        """Get all scans for a specific website"""
        return (
            self.db.query(Scan)
            .filter(Scan.website_url.like(f"%{website_url}%"))
            .order_by(Scan.created_at.desc())
            .all()
        )
    
    def delete_scan(self, scan_id: int) -> bool:
        """Delete a scan by ID"""
        scan = self.get_scan_by_id(scan_id)
        if scan:
            self.db.delete(scan)
            self.db.commit()
            return True
        return False
    
    def get_total_count(self) -> int:
        """Get total number of scans"""
        return self.db.query(Scan).count()


def get_database_service(db: Session) -> DatabaseService:
    """Factory function for database service"""
    return DatabaseService(db)