from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.database import get_db
from app.api.deps import get_current_user
from app.schemas.scan import (
    ScanRequest, 
    ScanResponse, 
    ScanListResponse, 
    ScanListItem,
    ScanResult
)
from app.services.ultimate_scraper import scrape_website_ultimate
from app.services.ultimate_extractor import extract_contacts_ultimate
from app.services.llm_services import process_with_llm
from app.services.database_services import DatabaseService
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("/", response_model=ScanResponse)
@limiter.limit("5/hour")
def create_scan(
    request: Request,
    scan_request: ScanRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    MAIN ENDPOINT: Ultimate scan pipeline
    """
    try:
        print(f"\n{'='*80}")
        print(f"[API] ULTIMATE SCAN INITIATED")
        print(f"[API] URL: {scan_request.website_url}")
        print(f"{'='*80}\n")
        
        # Step 1: Ultimate scraping
        scraped = scrape_website_ultimate(
            url=str(scan_request.website_url),
            max_pages=10,
            use_selenium=True
        )
        
        if scraped.get('error'):
            raise HTTPException(status_code=400, detail=scraped['error'])
        
        # Step 2: Ultimate extraction
        contacts = extract_contacts_ultimate(scraped)
        
        # Step 3: LLM processing
        structured_result = process_with_llm(
            website_url=scraped['base_url'],
            scraped_text=scraped['combined_text'],
            extracted_contacts=contacts
        )
        
        # Step 4: Save to database
        db_service = DatabaseService(db)
        scan = db_service.create_scan(
            website_url=scraped['base_url'],
            structured_data=structured_result
        )
        
        print(f"\n{'='*80}")
        print(f"[API] SCAN COMPLETE")
        print(f"[API] Scan ID: {scan.id}")
        print(f"[API] Emails: {len(structured_result.emails)}")
        print(f"[API] Phones: {len(structured_result.phone_numbers)}")
        print(f"{'='*80}\n")
        
        return ScanResponse(
            id=scan.id,
            website_url=scan.website_url,
            company_name=scan.company_name,
            summary=scan.summary,
            structured_data=structured_result,
            created_at=scan.created_at
        )
        
    except Exception as e:
        print(f"[API] ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.get("/", response_model=ScanListResponse)
@limiter.limit("60/minute")
def get_scans(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all scan history with pagination"""
    db_service = DatabaseService(db)
    
    offset = (page - 1) * page_size
    scans = db_service.get_all_scans(limit=page_size, offset=offset)
    total = db_service.get_total_count()
    total_pages = (total + page_size - 1) // page_size
    
    scan_items = [
        ScanListItem(
            id=scan.id,
            website_url=scan.website_url,
            company_name=scan.company_name,
            summary=scan.summary,
            created_at=scan.created_at
        )
        for scan in scans
    ]
    
    return ScanListResponse(
        total=total,
        scans=scan_items,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(
    scan_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific scan by ID"""
    db_service = DatabaseService(db)
    scan = db_service.get_scan_by_id(scan_id)
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    structured_data = json.loads(scan.structured_data)
    
    return ScanResponse(
        id=scan.id,
        website_url=scan.website_url,
        company_name=scan.company_name,
        summary=scan.summary,
        structured_data=ScanResult(**structured_data),
        created_at=scan.created_at
    )


@router.delete("/{scan_id}")
def delete_scan(
    scan_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a scan by ID"""
    db_service = DatabaseService(db)
    success = db_service.delete_scan(scan_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {"message": "Scan deleted successfully", "id": scan_id}


@router.post("/debug-ultimate")
def debug_ultimate(
    request: ScanRequest,
    current_user: str = Depends(get_current_user)
):
    """
    DEBUG ENDPOINT: See all extraction details with ultimate system
    """
    try:
        print(f"\n{'='*80}")
        print(f"[DEBUG] Ultimate System Test")
        print(f"[DEBUG] URL: {request.website_url}")
        print(f"{'='*80}\n")
        
        scraped = scrape_website_ultimate(
            url=str(request.website_url),
            max_pages=5,
            use_selenium=True
        )
        
        contacts = extract_contacts_ultimate(scraped)
        
        return {
            "scraping_results": {
                "pages_scraped": scraped['pages_scraped'],
                "total_text_length": len(scraped['combined_text']),
                "contact_forms_found": len(scraped.get('contact_forms', [])),
                "pages": [
                    {
                        "url": p['url'],
                        "title": p['title'],
                        "text_length": p['text_length']
                    }
                    for p in scraped['pages']
                ]
            },
            "extraction_results": {
                "emails": contacts['emails'],
                "phones": contacts['phone_numbers'],
                "socials": contacts['socials'],
                "addresses": contacts['addresses']
            },
            "summary": {
                "emails_found": len(contacts['emails']),
                "phones_found": len(contacts['phone_numbers']),
                "socials_found": len(contacts['socials']),
                "addresses_found": len(contacts['addresses'])
            },
            "contact_forms": scraped.get('contact_forms', [])
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}")
