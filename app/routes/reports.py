"""
Reports Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.schemas.report import (
    ReportCreate, ReportUpdate, ReportResponse, ReportListResponse,
    ReportRunRequest, ReportRunResponse,
    ReportTypeInfo, ReportTypesResponse
)
from app.models.report import Report
from app.models.user import User
from app.models.customer import Customer
from app.models.lead import Lead
from app.models.deal import Deal
from app.models.task import Task
from app.models.activity import Activity
from app.utils.dependencies import get_current_active_user
from app.utils.permissions import require_admin, require_manager
from app.utils.helpers import success_response

router = APIRouter()


@router.get("/reports", response_model=ReportListResponse)
async def get_reports(
    company_id: Optional[int] = Query(None, description="Filter by company"),
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """
    Get all reports accessible to current user
    
    Requires: Manager role or higher
    """
    query = db.query(Report)
    
    # Filter by company or global reports
    if company_id:
        query = query.filter(
            (Report.company_id == company_id) | (Report.company_id.is_(None))
        )
    
    # Filter by type
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    # Filter by access (public or created by user or user has allowed role)
    if current_user.role not in ["super_admin", "admin"]:
        query = query.filter(
            (Report.is_public == True) |
            (Report.created_by == current_user.id)
        )
    
    reports = query.order_by(Report.created_at.desc()).all()
    
    return ReportListResponse(
        reports=[ReportResponse.model_validate(r) for r in reports],
        total=len(reports)
    )


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int = Path(..., description="Report ID"),
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """
    Get report by ID
    
    Requires: Manager role or higher
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check access
    if current_user.role not in ["super_admin", "admin"]:
        if not report.is_public and report.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this report"
            )
    
    return ReportResponse.model_validate(report)


@router.post("/reports", status_code=status.HTTP_201_CREATED, response_model=ReportResponse)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """
    Create a new report
    
    Requires: Manager role or higher
    """
    report = Report(
        name=report_data.name,
        description=report_data.description,
        report_type=report_data.report_type,
        config=report_data.config,
        company_id=report_data.company_id,
        created_by=current_user.id,
        is_public=report_data.is_public,
        allowed_roles=report_data.allowed_roles,
        is_scheduled=report_data.is_scheduled,
        schedule_cron=report_data.schedule_cron
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return ReportResponse.model_validate(report)


@router.put("/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int = Path(..., description="Report ID"),
    report_data: ReportUpdate = ...,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """
    Update a report
    
    Requires: Manager role or higher, must be creator or admin
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check ownership
    if current_user.role not in ["super_admin", "admin"]:
        if report.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the creator or admin can update this report"
            )
    
    # Update fields
    update_data = report_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    report.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(report)
    
    return ReportResponse.model_validate(report)


@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: int = Path(..., description="Report ID"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a report
    
    Requires: Admin role
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    db.delete(report)
    db.commit()
    
    return success_response(
        data={},
        message="Report deleted successfully"
    )


@router.post("/reports/{report_id}/run", response_model=ReportRunResponse)
async def run_report(
    report_id: int = Path(..., description="Report ID"),
    run_request: ReportRunRequest = ReportRunRequest(),
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """
    Execute a report and get results
    
    Requires: Manager role or higher
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check access
    if current_user.role not in ["super_admin", "admin"]:
        if not report.is_public and report.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this report"
            )
    
    # Execute report based on type
    data = []
    row_count = 0
    
    try:
        if report.report_type == "sales":
            # Sales report - deals summary
            query = db.query(Deal)
            if report.company_id:
                query = query.filter(Deal.company_id == report.company_id)
            deals = query.all()
            data = [{"id": d.id, "name": d.name, "value": d.value, "stage": d.stage} for d in deals]
            row_count = len(data)
            
        elif report.report_type == "leads":
            # Leads report
            query = db.query(Lead)
            if report.company_id:
                query = query.filter(Lead.company_id == report.company_id)
            leads = query.all()
            data = [{"id": l.id, "name": f"{l.first_name} {l.last_name}", "status": l.status, "source": l.source} for l in leads]
            row_count = len(data)
            
        elif report.report_type == "activities":
            # Activities report
            query = db.query(Activity)
            if report.company_id:
                query = query.filter(Activity.company_id == report.company_id)
            activities = query.limit(1000).all()
            data = [{"id": a.id, "type": a.activity_type, "subject": a.subject} for a in activities]
            row_count = len(data)
            
        elif report.report_type == "customers":
            # Customers report
            query = db.query(Customer)
            if report.company_id:
                query = query.filter(Customer.company_id == report.company_id)
            customers = query.all()
            data = [{"id": c.id, "name": c.name, "email": c.email, "status": c.status} for c in customers]
            row_count = len(data)
            
        else:
            # Custom report - return empty for now
            data = []
            row_count = 0
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing report: {str(e)}"
        )
    
    # Update last run
    report.last_run = datetime.utcnow()
    db.commit()
    
    return ReportRunResponse(
        report_id=report.id,
        report_name=report.name,
        executed_at=datetime.utcnow(),
        row_count=row_count,
        data=data if run_request.format == "json" else None,
        download_url=None  # Would generate download URL for csv/pdf
    )


@router.get("/reports/types/list", response_model=ReportTypesResponse)
async def get_report_types(
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """
    Get available report types
    
    Requires: Manager role or higher
    """
    types = [
        ReportTypeInfo(
            type="sales",
            name="Sales Report",
            description="Report on deals and revenue",
            available_filters=["date_range", "stage", "owner", "company"]
        ),
        ReportTypeInfo(
            type="leads",
            name="Leads Report",
            description="Report on lead generation and conversion",
            available_filters=["date_range", "status", "source", "owner", "company"]
        ),
        ReportTypeInfo(
            type="activities",
            name="Activities Report",
            description="Report on user activities and engagement",
            available_filters=["date_range", "type", "user", "company"]
        ),
        ReportTypeInfo(
            type="customers",
            name="Customers Report",
            description="Report on customer data",
            available_filters=["date_range", "status", "company"]
        ),
        ReportTypeInfo(
            type="custom",
            name="Custom Report",
            description="Custom report with user-defined configuration",
            available_filters=["custom"]
        )
    ]
    
    return ReportTypesResponse(types=types)
