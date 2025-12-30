"""
Deal Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.deal import DealCreate, DealUpdate
from app.controllers.deal_controller import DealController
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.utils.permissions import has_permission
from app.models.user import User

router = APIRouter()


@router.get("/{company_id}/deals")
async def get_deals(
    company_id: int = Path(..., description="Company ID"),
    search: Optional[str] = Query(None, description="Search in deal name"),
    stage: Optional[str] = Query(None, description="Filter by stage"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all deals in company"""
    try:
        deals = DealController.get_deals(
            company_id, current_user, db, search, stage, status, assigned_to
        )
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_deals = deals[start:end]
        
        total = len(deals)
        pages = (total + per_page - 1) // per_page
        
        return {
            "success": True,
            "data": [deal.to_dict(include_relations=True) for deal in paginated_deals],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages
            },
            "message": "Deals fetched successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{company_id}/deals", status_code=status.HTTP_201_CREATED)
async def create_deal(
    company_id: int = Path(..., description="Company ID"),
    deal_data: DealCreate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new deal
    
    Path Parameters:
    - **company_id**: Company ID
    
    Requires: JWT token, Permission to create deals
    """
    # Check permission to create deal
    if not has_permission(current_user, "deal", "create", company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: create deal"
        )
    
    try:
        deal = DealController.create_deal(company_id, deal_data, current_user, db)
        return success_response(
            data=deal.to_dict(include_relations=True),
            message="Deal created successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================
# IMPORTANT: Static routes MUST come before dynamic {deal_id} routes
# ============================================

@router.get("/{company_id}/deals/forecast")
async def get_sales_forecast_early(
    company_id: int = Path(..., description="Company ID"),
    months: int = Query(3, ge=1, le=12, description="Months to forecast"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get sales forecast based on pipeline and historical data"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    from app.models.deal import Deal
    
    try:
        today = datetime.utcnow().date()
        
        # Get open deals
        open_deals = db.query(Deal).filter(
            Deal.company_id == company_id,
            Deal.status == "open"
        ).all()
        
        # Calculate weighted pipeline
        weighted_value = sum(
            float(d.deal_value or 0) * (d.probability or 0) / 100
            for d in open_deals
        )
        
        # Forecast by category
        forecast_by_category = {
            "best_case": 0,
            "commit": 0,
            "most_likely": 0,
            "worst_case": 0
        }
        
        for deal in open_deals:
            category = deal.forecast_category or "most_likely"
            if category in forecast_by_category:
                forecast_by_category[category] += float(deal.deal_value or 0)
        
        # Monthly projections
        monthly_forecast = []
        for i in range(months):
            month_start = today.replace(day=1) + timedelta(days=32 * i)
            month_start = month_start.replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
            
            month_deals = [
                d for d in open_deals
                if d.expected_close_date and month_start <= d.expected_close_date <= month_end
            ]
            
            month_value = sum(float(d.deal_value or 0) for d in month_deals)
            month_weighted = sum(
                float(d.deal_value or 0) * (d.probability or 0) / 100
                for d in month_deals
            )
            
            monthly_forecast.append({
                "month": month_start.strftime("%B %Y"),
                "deal_count": len(month_deals),
                "total_value": month_value,
                "weighted_value": round(month_weighted, 2),
                "projected_value": round(month_weighted, 2)
            })
        
        # Historical win rate
        six_months_ago = today - timedelta(days=180)
        historical_won = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id,
            Deal.status == "won",
            Deal.actual_close_date >= six_months_ago
        ).scalar() or 0
        
        historical_lost = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id,
            Deal.status == "lost",
            Deal.actual_close_date >= six_months_ago
        ).scalar() or 0
        
        historical_win_rate = (historical_won / (historical_won + historical_lost) * 100) if (historical_won + historical_lost) > 0 else 0
        
        return success_response(
            data={
                "total_pipeline": sum(float(d.deal_value or 0) for d in open_deals),
                "weighted_pipeline": round(weighted_value, 2),
                "by_category": forecast_by_category,
                "monthly_projections": monthly_forecast,
                "win_rate": round(historical_win_rate, 2)
            },
            message="Sales forecast generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating forecast: {str(e)}"
        )


@router.get("/{company_id}/deals/trend-analysis")
async def get_trend_analysis_early(
    company_id: int = Path(..., description="Company ID"),
    months: int = Query(6, ge=1, le=24, description="Months of historical data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get trend analysis based on historical deal data"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    from app.models.deal import Deal
    
    try:
        today = datetime.utcnow().date()
        
        monthly_trends = []
        for i in range(months):
            month_start = today.replace(day=1) - timedelta(days=30 * (months - i - 1))
            month_start = month_start.replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
            
            won_deals = db.query(Deal).filter(
                Deal.company_id == company_id,
                Deal.status == "won",
                Deal.actual_close_date >= month_start,
                Deal.actual_close_date <= month_end
            ).all()
            
            won_value = sum(float(d.deal_value or 0) for d in won_deals)
            
            lost_count = db.query(func.count(Deal.id)).filter(
                Deal.company_id == company_id,
                Deal.status == "lost",
                Deal.actual_close_date >= month_start,
                Deal.actual_close_date <= month_end
            ).scalar() or 0
            
            monthly_trends.append({
                "month": month_start.strftime("%B %Y"),
                "won_count": len(won_deals),
                "won_value": won_value,
                "lost_count": lost_count
            })
        
        # Calculate growth rate
        if len(monthly_trends) >= 2:
            current = monthly_trends[-1]
            prev = monthly_trends[-2]
            growth_rate = ((current["won_value"] - prev["won_value"]) / prev["won_value"] * 100) if prev["won_value"] > 0 else 0
        else:
            growth_rate = 0
        
        total_won = sum(m["won_count"] for m in monthly_trends)
        total_lost = sum(m["lost_count"] for m in monthly_trends)
        
        return success_response(
            data={
                "monthly_trends": monthly_trends,
                "growth_rate": round(growth_rate, 2),
                "total_won": sum(m["won_value"] for m in monthly_trends),
                "deals_won": total_won,
                "win_rate": round((total_won / (total_won + total_lost) * 100), 2) if (total_won + total_lost) > 0 else 0
            },
            message="Trend analysis generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating trend analysis: {str(e)}"
        )


@router.get("/{company_id}/deals/pipeline-view")
async def get_pipeline_view_early(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get pipeline visualization data (Kanban/Funnel view)"""
    from app.models.deal import Deal
    from app.models.user_company import UserCompany
    
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id
    ).first()
    
    if not user_company and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    try:
        stages = ["prospect", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"]
        stages_data = {}
        
        for stage in stages:
            deals = db.query(Deal).filter(
                Deal.company_id == company_id,
                Deal.stage == stage
            ).all()
            
            total_value = sum(float(d.deal_value or 0) for d in deals)
            
            stages_data[stage] = {
                "count": len(deals),
                "total_value": total_value,
                "deals": [
                    {
                        "id": d.id,
                        "deal_name": d.deal_name,
                        "deal_value": float(d.deal_value or 0),
                        "probability": d.probability,
                        "expected_close_date": d.expected_close_date.isoformat() if d.expected_close_date else None,
                        "customer_name": d.customer.name if d.customer else None
                    }
                    for d in deals
                ]
            }
        
        total_deals = sum(s["count"] for s in stages_data.values())
        total_value = sum(s["total_value"] for s in stages_data.values() if s != stages_data.get("closed_lost"))
        weighted_value = sum(
            float(d.deal_value or 0) * (d.probability or 0) / 100
            for stage in ["prospect", "qualified", "proposal", "negotiation"]
            for d in db.query(Deal).filter(Deal.company_id == company_id, Deal.stage == stage).all()
        )
        
        won = stages_data.get("closed_won", {}).get("total_value", 0)
        lost = stages_data.get("closed_lost", {}).get("total_value", 0)
        
        return success_response(
            data={
                "stages": stages_data,
                "summary": {
                    "total_deals": total_deals,
                    "total_value": total_value,
                    "weighted_value": round(weighted_value, 2),
                    "win_rate": round((won / (won + lost) * 100), 2) if (won + lost) > 0 else 0
                }
            },
            message="Pipeline view fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching pipeline view: {str(e)}"
        )


# ============================================
# Dynamic routes with {deal_id} parameter
# ============================================

@router.get("/{company_id}/deals/{deal_id}")
async def get_deal(
    company_id: int = Path(..., description="Company ID"),
    deal_id: int = Path(..., description="Deal ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get deal details"""
    try:
        deal = DealController.get_deal(deal_id, company_id, current_user, db)
        return success_response(
            data=deal.to_dict(include_relations=True),
            message="Deal details fetched successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{company_id}/deals/{deal_id}")
async def update_deal(
    company_id: int = Path(..., description="Company ID"),
    deal_id: int = Path(..., description="Deal ID"),
    deal_data: DealUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update deal
    
    Path Parameters:
    - **company_id**: Company ID
    - **deal_id**: Deal ID
    
    Requires: JWT token, Permission to update deals
    """
    # Check permission to update deal
    if not has_permission(current_user, "deal", "update", company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: update deal"
        )
    
    try:
        deal = DealController.update_deal(deal_id, company_id, deal_data, current_user, db)
        return success_response(
            data=deal.to_dict(include_relations=True),
            message="Deal updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{company_id}/deals/{deal_id}")
async def delete_deal(
    company_id: int = Path(..., description="Company ID"),
    deal_id: int = Path(..., description="Deal ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete deal
    
    Path Parameters:
    - **company_id**: Company ID
    - **deal_id**: Deal ID
    
    Requires: JWT token, Permission to delete deals (admin/manager only)
    """
    # Check permission to delete deal (sales_rep cannot delete deals)
    if not has_permission(current_user, "deal", "delete", company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: delete deal (admin/manager only)"
        )
    
    try:
        DealController.delete_deal(deal_id, company_id, current_user, db)
        return success_response(
            data={},
            message="Deal deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{company_id}/deals-stats")
async def get_deal_stats(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get deal statistics and pipeline"""
    try:
        stats = DealController.get_deal_stats(company_id, db)
        return success_response(
            data=stats,
            message="Deal statistics fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Pipeline Visualization Endpoints

@router.get("/{company_id}/deals/pipeline-view")
async def get_pipeline_view(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get pipeline visualization data (Kanban/Funnel view)
    
    Returns deals grouped by stage with counts and values
    """
    from sqlalchemy import func
    from app.models.deal import Deal
    from app.models.user_company import UserCompany
    
    # Check access
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id
    ).first()
    
    if not user_company and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        stages = ["prospect", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"]
        pipeline_data = []
        
        for stage in stages:
            deals = db.query(Deal).filter(
                Deal.company_id == company_id,
                Deal.stage == stage
            ).all()
            
            total_value = sum(float(d.deal_value or 0) for d in deals)
            
            pipeline_data.append({
                "stage": stage,
                "stage_display": stage.replace("_", " ").title(),
                "count": len(deals),
                "total_value": total_value,
                "deals": [
                    {
                        "id": d.id,
                        "name": d.deal_name,
                        "value": float(d.deal_value or 0),
                        "probability": d.probability,
                        "expected_close_date": d.expected_close_date.isoformat() if d.expected_close_date else None,
                        "account_name": d.customer.name if d.customer else None,
                        "assigned_to": d.assigned_user.email if d.assigned_user else None
                    }
                    for d in deals
                ]
            })
        
        # Calculate totals
        total_deals = sum(p["count"] for p in pipeline_data)
        total_pipeline_value = sum(p["total_value"] for p in pipeline_data if p["stage"] not in ["closed_won", "closed_lost"])
        won_value = next((p["total_value"] for p in pipeline_data if p["stage"] == "closed_won"), 0)
        lost_value = next((p["total_value"] for p in pipeline_data if p["stage"] == "closed_lost"), 0)
        
        return success_response(
            data={
                "pipeline": pipeline_data,
                "summary": {
                    "total_deals": total_deals,
                    "total_pipeline_value": total_pipeline_value,
                    "won_value": won_value,
                    "lost_value": lost_value,
                    "win_rate": round((won_value / (won_value + lost_value) * 100), 2) if (won_value + lost_value) > 0 else 0
                }
            },
            message="Pipeline view fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching pipeline view: {str(e)}"
        )


@router.get("/{company_id}/deals/pipeline-analytics")
async def get_pipeline_analytics(
    company_id: int = Path(..., description="Company ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get pipeline analytics
    
    Returns:
    - Deals per stage
    - Conversion rates between stages
    - Average time in each stage
    - Win/loss rates
    """
    from sqlalchemy import func
    from datetime import datetime, timedelta
    from app.models.deal import Deal
    from app.models.activity import Activity
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        stages = ["prospect", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"]
        
        # Deals by stage
        stage_counts = {}
        stage_values = {}
        for stage in stages:
            count = db.query(func.count(Deal.id)).filter(
                Deal.company_id == company_id,
                Deal.stage == stage
            ).scalar() or 0
            stage_counts[stage] = count
            
            value = db.query(func.sum(Deal.deal_value)).filter(
                Deal.company_id == company_id,
                Deal.stage == stage
            ).scalar() or 0
            stage_values[stage] = float(value)
        
        # Win/Loss in period
        won_count = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id,
            Deal.status == "won",
            Deal.actual_close_date >= start_date
        ).scalar() or 0
        
        lost_count = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id,
            Deal.status == "lost",
            Deal.actual_close_date >= start_date
        ).scalar() or 0
        
        # Average deal value
        avg_deal_value = db.query(func.avg(Deal.deal_value)).filter(
            Deal.company_id == company_id,
            Deal.status == "won"
        ).scalar() or 0
        
        # Deals created in period
        new_deals = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id,
            Deal.created_at >= start_date
        ).scalar() or 0
        
        # Calculate conversion rates (simplified)
        total_open = sum(stage_counts[s] for s in ["prospect", "qualified", "proposal", "negotiation"])
        total_closed = stage_counts["closed_won"] + stage_counts["closed_lost"]
        
        return success_response(
            data={
                "period_days": days,
                "by_stage": {
                    "counts": stage_counts,
                    "values": stage_values
                },
                "performance": {
                    "won_count": won_count,
                    "lost_count": lost_count,
                    "win_rate": round((won_count / (won_count + lost_count) * 100), 2) if (won_count + lost_count) > 0 else 0,
                    "avg_deal_value": round(float(avg_deal_value), 2),
                    "new_deals": new_deals
                },
                "pipeline_health": {
                    "total_open": total_open,
                    "total_closed": total_closed,
                    "pipeline_value": sum(stage_values[s] for s in ["prospect", "qualified", "proposal", "negotiation"])
                }
            },
            message="Pipeline analytics fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching pipeline analytics: {str(e)}"
        )


@router.put("/{company_id}/deals/{deal_id}/move-stage")
async def move_deal_stage(
    company_id: int = Path(..., description="Company ID"),
    deal_id: int = Path(..., description="Deal ID"),
    new_stage: str = Query(..., description="New stage"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Move deal to a new stage (for drag-and-drop)
    
    Valid stages: prospect, qualified, proposal, negotiation, closed_won, closed_lost
    """
    from app.models.deal import Deal
    from app.models.activity import Activity
    from datetime import datetime
    
    valid_stages = ["prospect", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"]
    if new_stage not in valid_stages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid stage. Must be one of: {', '.join(valid_stages)}"
        )
    
    try:
        deal = DealController.get_deal(deal_id, company_id, current_user, db)
        old_stage = deal.stage
        
        # Update stage
        deal.stage = new_stage
        
        # Update status if closed
        if new_stage == "closed_won":
            deal.status = "won"
            deal.actual_close_date = datetime.utcnow().date()
        elif new_stage == "closed_lost":
            deal.status = "lost"
            deal.actual_close_date = datetime.utcnow().date()
        else:
            deal.status = "open"
        
        # Update probability based on stage
        stage_probability = {
            "prospect": 10,
            "qualified": 25,
            "proposal": 50,
            "negotiation": 75,
            "closed_won": 100,
            "closed_lost": 0
        }
        deal.probability = stage_probability.get(new_stage, deal.probability)
        
        # Log activity
        activity = Activity(
            company_id=company_id,
            deal_id=deal.id,
            customer_id=deal.customer_id,
            activity_type="status_change",
            title=f"Deal Stage Changed: {old_stage} → {new_stage}",
            description=f"Deal '{deal.deal_name}' moved from {old_stage} to {new_stage}",
            user_id=current_user.id,
            activity_date=datetime.utcnow()
        )
        db.add(activity)
        
        db.commit()
        db.refresh(deal)
        
        return success_response(
            data={
                "id": deal.id,
                "name": deal.deal_name,
                "old_stage": old_stage,
                "new_stage": new_stage,
                "status": deal.status,
                "probability": deal.probability
            },
            message=f"Deal moved from {old_stage} to {new_stage}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error moving deal stage: {str(e)}"
        )


# Advanced Forecasting Endpoints

@router.get("/{company_id}/deals/forecast")
async def get_sales_forecast(
    company_id: int = Path(..., description="Company ID"),
    months: int = Query(3, ge=1, le=12, description="Months to forecast"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get sales forecast based on pipeline and historical data
    
    Returns:
    - Weighted pipeline value
    - Forecast by category (best_case, commit, most_likely)
    - Monthly projections
    """
    from sqlalchemy import func
    from datetime import datetime, timedelta
    from app.models.deal import Deal
    
    try:
        today = datetime.utcnow().date()
        
        # Get open deals
        open_deals = db.query(Deal).filter(
            Deal.company_id == company_id,
            Deal.status == "open"
        ).all()
        
        # Calculate weighted pipeline
        weighted_value = sum(
            float(d.deal_value or 0) * (d.probability or 0) / 100
            for d in open_deals
        )
        
        # Forecast by category
        forecast_by_category = {
            "best_case": 0,
            "commit": 0,
            "most_likely": 0,
            "worst_case": 0
        }
        
        for deal in open_deals:
            category = deal.forecast_category or "most_likely"
            if category in forecast_by_category:
                forecast_by_category[category] += float(deal.deal_value or 0)
        
        # Monthly projections based on expected close dates
        monthly_forecast = []
        for i in range(months):
            month_start = today.replace(day=1) + timedelta(days=32 * i)
            month_start = month_start.replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
            
            month_deals = [
                d for d in open_deals
                if d.expected_close_date and month_start <= d.expected_close_date <= month_end
            ]
            
            month_value = sum(float(d.deal_value or 0) for d in month_deals)
            month_weighted = sum(
                float(d.deal_value or 0) * (d.probability or 0) / 100
                for d in month_deals
            )
            
            monthly_forecast.append({
                "month": month_start.strftime("%B %Y"),
                "deal_count": len(month_deals),
                "total_value": month_value,
                "weighted_value": round(month_weighted, 2)
            })
        
        # Historical win rate (last 6 months)
        six_months_ago = today - timedelta(days=180)
        historical_won = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id,
            Deal.status == "won",
            Deal.actual_close_date >= six_months_ago
        ).scalar() or 0
        
        historical_lost = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id,
            Deal.status == "lost",
            Deal.actual_close_date >= six_months_ago
        ).scalar() or 0
        
        historical_win_rate = (historical_won / (historical_won + historical_lost) * 100) if (historical_won + historical_lost) > 0 else 0
        
        # Adjusted forecast based on historical win rate
        adjusted_forecast = weighted_value * (historical_win_rate / 100) if historical_win_rate > 0 else weighted_value
        
        return success_response(
            data={
                "pipeline_summary": {
                    "total_open_deals": len(open_deals),
                    "total_pipeline_value": sum(float(d.deal_value or 0) for d in open_deals),
                    "weighted_pipeline_value": round(weighted_value, 2)
                },
                "forecast_by_category": forecast_by_category,
                "monthly_forecast": monthly_forecast,
                "historical_performance": {
                    "win_rate_6m": round(historical_win_rate, 2),
                    "deals_won_6m": historical_won,
                    "deals_lost_6m": historical_lost
                },
                "adjusted_forecast": round(adjusted_forecast, 2),
                "forecast_confidence": "high" if historical_win_rate >= 50 else "medium" if historical_win_rate >= 30 else "low"
            },
            message="Sales forecast generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating forecast: {str(e)}"
        )


@router.get("/{company_id}/deals/trend-analysis")
async def get_trend_analysis(
    company_id: int = Path(..., description="Company ID"),
    months: int = Query(6, ge=1, le=24, description="Months of historical data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get trend analysis based on historical deal data
    
    Returns:
    - Monthly revenue trends
    - Win/loss trends
    - Average deal size trends
    """
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    from app.models.deal import Deal
    
    try:
        today = datetime.utcnow().date()
        start_date = today - timedelta(days=months * 30)
        
        monthly_trends = []
        
        for i in range(months):
            month_start = today.replace(day=1) - timedelta(days=30 * (months - i - 1))
            month_start = month_start.replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
            
            # Won deals in month
            won_deals = db.query(Deal).filter(
                Deal.company_id == company_id,
                Deal.status == "won",
                Deal.actual_close_date >= month_start,
                Deal.actual_close_date <= month_end
            ).all()
            
            won_value = sum(float(d.deal_value or 0) for d in won_deals)
            
            # Lost deals in month
            lost_count = db.query(func.count(Deal.id)).filter(
                Deal.company_id == company_id,
                Deal.status == "lost",
                Deal.actual_close_date >= month_start,
                Deal.actual_close_date <= month_end
            ).scalar() or 0
            
            # New deals created
            new_deals = db.query(func.count(Deal.id)).filter(
                Deal.company_id == company_id,
                Deal.created_at >= datetime.combine(month_start, datetime.min.time()),
                Deal.created_at <= datetime.combine(month_end, datetime.max.time())
            ).scalar() or 0
            
            monthly_trends.append({
                "month": month_start.strftime("%B %Y"),
                "won_count": len(won_deals),
                "won_value": won_value,
                "lost_count": lost_count,
                "new_deals": new_deals,
                "avg_deal_size": round(won_value / len(won_deals), 2) if won_deals else 0
            })
        
        # Calculate growth rates
        if len(monthly_trends) >= 2:
            current_month = monthly_trends[-1]
            prev_month = monthly_trends[-2]
            
            revenue_growth = ((current_month["won_value"] - prev_month["won_value"]) / prev_month["won_value"] * 100) if prev_month["won_value"] > 0 else 0
            deal_growth = ((current_month["won_count"] - prev_month["won_count"]) / prev_month["won_count"] * 100) if prev_month["won_count"] > 0 else 0
        else:
            revenue_growth = 0
            deal_growth = 0
        
        return success_response(
            data={
                "period_months": months,
                "monthly_trends": monthly_trends,
                "growth_rates": {
                    "revenue_growth_mom": round(revenue_growth, 2),
                    "deal_growth_mom": round(deal_growth, 2)
                },
                "totals": {
                    "total_won_value": sum(m["won_value"] for m in monthly_trends),
                    "total_won_count": sum(m["won_count"] for m in monthly_trends),
                    "total_lost_count": sum(m["lost_count"] for m in monthly_trends),
                    "avg_monthly_revenue": round(sum(m["won_value"] for m in monthly_trends) / months, 2)
                }
            },
            message="Trend analysis generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating trend analysis: {str(e)}"
        )

