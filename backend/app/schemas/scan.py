from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime


class SocialMedia(BaseModel):
    """Social media platform info"""
    platform: str
    url: str


class ScanResult(BaseModel):
    """Structured output from LLM"""
    company_name: str
    website: str
    summary: str = Field(..., max_length=500)
    emails: List[str] = []
    phone_numbers: List[str] = []
    socials: List[SocialMedia] = []
    addresses: List[str] = []
    notes: Optional[str] = None
    sources: List[str] = []


class ScanRequest(BaseModel):
    """Request to scan a website"""
    website_url: HttpUrl


class ScanResponse(BaseModel):
    """Response with scan results"""
    id: int
    website_url: str
    company_name: Optional[str]
    summary: Optional[str]
    structured_data: ScanResult
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScanListItem(BaseModel):
    """Scan item for history list (minimal info)"""
    id: int
    website_url: str
    company_name: Optional[str]
    summary: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScanListResponse(BaseModel):
    """Response for list of scans with pagination"""
    total: int
    scans: List[ScanListItem]
    page: int
    page_size: int
    total_pages: int