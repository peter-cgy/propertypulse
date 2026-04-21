from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

from app.database import get_db
from app.models import User, Property, Report
from app.api.auth import get_current_user
from app.services.report_generator import report_generator
from app.utils.investment import investment_calculator

router = APIRouter()


class ReportGenerateRequest(BaseModel):
    property_data: Dict[str, Any]
    analysis_data: Dict[str, Any]
    market_insights: Dict[str, Any]


@router.post("/generate")
async def generate_report(
    request: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate investment analysis report PDF"""

    if current_user.subscription_plan == "free":
        raise HTTPException(
            status_code=403,
            detail="PDF reports require a paid subscription"
        )

    try:
        pdf_content = report_generator.generate_report(
            property_data=request.property_data,
            analysis_data=request.analysis_data,
            market_insights=request.market_insights,
            user_name=current_user.name or current_user.email
        )

        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=PropertyPulse_Report.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("")
async def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's report list"""
    reports = db.query(Report).filter(Report.user_id == current_user.id).limit(20).all()
    return reports


@router.get("/{report_id}")
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download report PDF"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"message": "Report found", "id": report.id}
