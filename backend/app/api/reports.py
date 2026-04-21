from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import json

from app.database import get_db
from app.models import User, Property, Report
from app.api.auth import get_current_user
from app.services.report_generator import report_generator
from app.utils.investment import investment_calculator

router = APIRouter()


class ReportGenerateRequest(BaseModel):
    # 直接传递房产数据，无需预先保存
    property_data: Dict[str, Any]
    analysis_data: Dict[str, Any]
    market_insights: Dict[str, Any]


class ReportResponse(BaseModel):
    id: int
    user_id: int
    property_address: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/generate")
async def generate_report(
    request: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """生成投资分析报告PDF"""

    # 检查用户订阅（只有付费用户可以生成报告）
    if current_user.subscription_plan == "free":
        raise HTTPException(
            status_code=403,
            detail="PDF报告功能需要升级到付费计划"
        )

    try:
        # 生成PDF
        pdf_content = report_generator.generate_report(
            property_data=request.property_data,
            analysis_data=request.analysis_data,
            market_insights=request.market_insights,
            user_name=current_user.name or current_user.email
        )

        # 保存房产记录
        property_obj = Property(
            address=request.property_data.get('address', ''),
            city=request.property_data.get('city'),
            state=request.property_data.get('state'),
            zip_code=request.property_data.get('zip_code'),
            property_type=request.property_data.get('property_type'),
            bedrooms=request.property_data.get('bedrooms'),
            bathrooms=request.property_data.get('bathrooms'),
            square_feet=request.property_data.get('square_feet'),
            year_built=request.property_data.get('year_built'),
            price_estimate=request.property_data.get('price_estimate'),
            rent_estimate=request.property_data.get('rent_estimate'),
        )
        db.add(property_obj)
        db.flush()  # 获取ID

        # 保存报告记录
        report_obj = Report(
            user_id=current_user.id,
            property_id=property_obj.id,
            pdf_url=f"/api/reports/{property_obj.id}/download",
            status="generated",
        )
        db.add(report_obj)
        db.commit()

        # 返回PDF文件
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=PropertyPulse_Report_{property_obj.id}.pdf"
            }
        )

    except Exception as e:
        print(f"Report generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="报告生成失败，请稍后重试"
        )


@router.get("", response_model=list[ReportResponse])
async def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取用户的报告列表"""
    reports = db.query(Report).filter(Report.user_id == current_user.id).order_by(Report.created_at.desc()).limit(20).all()
    return reports


@router.get("/{report_id}")
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """下载报告PDF"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    # 获取房产数据
    property_obj = db.query(Property).filter(Property.id == report.property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="房产数据不存在")

    # 重新生成PDF（实际项目中应该保存PDF文件）
    property_data = {
        'address': property_obj.address,
        'city': property_obj.city,
        'state': property_obj.state,
        'property_type': property_obj.property_type,
        'bedrooms': property_obj.bedrooms,
        'bathrooms': property_obj.bathrooms,
        'square_feet': property_obj.square_feet,
        'year_built': property_obj.year_built,
        'price_estimate': property_obj.price_estimate,
        'rent_estimate': property_obj.rent_estimate,
    }

    analysis = investment_calculator.calculate(
        price=property_obj.price_estimate or 0,
        rent=property_obj.rent_estimate or 0,
        square_feet=property_obj.square_feet or 1000
    )

    pdf_content = report_generator.generate_report(
        property_data=property_data,
        analysis_data={
            'cap_rate': analysis.cap_rate,
            'gross_rent_multiplier': analysis.gross_rent_multiplier,
            'monthly_cashflow': analysis.monthly_cashflow,
            'annual_cashflow': analysis.annual_cashflow,
            'cash_on_cash_return': analysis.cash_on_cash_return,
            'price_per_sqft': analysis.price_per_sqft,
            'rent_per_sqft': analysis.rent_per_sqft,
            'break_even_ratio': analysis.break_even_ratio,
            'investment_grade': analysis.investment_grade,
        },
        market_insights={
            'grade': analysis.investment_grade,
            'insights': [],
            'recommendation': 'Generated Report'
        },
        user_name=current_user.name or current_user.email
    )

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=PropertyPulse_Report_{report_id}.pdf"
        }
    )
