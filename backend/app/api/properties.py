from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import httpx

from app.database import get_db
from app.models import User, Property, SearchHistory
from app.api.auth import get_current_user
from app.config import settings
from app.utils.investment import investment_calculator, InvestmentAnalysis
from app.services.rentcast import rentcast_service

router = APIRouter()


# Pydantic模型
class PropertyResponse(BaseModel):
    id: Optional[int] = None
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    year_built: Optional[int] = None
    price_estimate: Optional[float] = None
    rent_estimate: Optional[float] = None

    class Config:
        from_attributes = True


class InvestmentAnalysisResponse(BaseModel):
    cap_rate: float
    gross_rent_multiplier: float
    monthly_cashflow: float
    annual_cashflow: float
    cash_on_cash_return: float
    price_per_sqft: float
    rent_per_sqft: float
    break_even_ratio: float
    investment_grade: str


class PropertySearchResult(BaseModel):
    property: PropertyResponse
    analysis: InvestmentAnalysisResponse
    market_insights: dict


# US major cities mock data
MOCK_PROPERTIES = {
    "new york": {
        "address": "123 Main St, New York, NY 10001",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "property_type": "Condo",
        "bedrooms": 2,
        "bathrooms": 1.5,
        "square_feet": 1000,
        "year_built": 2010,
        "price_estimate": 850000,
        "rent_estimate": 3500,
    },
    "los angeles": {
        "address": "456 Sunset Blvd, Los Angeles, CA 90028",
        "city": "Los Angeles",
        "state": "CA",
        "zip_code": "90028",
        "property_type": "Single Family",
        "bedrooms": 3,
        "bathrooms": 2.0,
        "square_feet": 1500,
        "year_built": 1995,
        "price_estimate": 750000,
        "rent_estimate": 3200,
    },
    "chicago": {
        "address": "789 Lake Shore Dr, Chicago, IL 60611",
        "city": "Chicago",
        "state": "IL",
        "zip_code": "60611",
        "property_type": "Townhouse",
        "bedrooms": 3,
        "bathrooms": 2.5,
        "square_feet": 1800,
        "year_built": 2005,
        "price_estimate": 450000,
        "rent_estimate": 2400,
    },
    "houston": {
        "address": "321 Texas Ave, Houston, TX 77002",
        "city": "Houston",
        "state": "TX",
        "zip_code": "77002",
        "property_type": "Single Family",
        "bedrooms": 4,
        "bathrooms": 2.5,
        "square_feet": 2200,
        "year_built": 2000,
        "price_estimate": 320000,
        "rent_estimate": 2100,
    },
    "miami": {
        "address": "555 Ocean Dr, Miami, FL 33139",
        "city": "Miami",
        "state": "FL",
        "zip_code": "33139",
        "property_type": "Condo",
        "bedrooms": 2,
        "bathrooms": 2.0,
        "square_feet": 1100,
        "year_built": 2015,
        "price_estimate": 520000,
        "rent_estimate": 2800,
    },
    "seattle": {
        "address": "888 Pike St, Seattle, WA 98101",
        "city": "Seattle",
        "state": "WA",
        "zip_code": "98101",
        "property_type": "Townhouse",
        "bedrooms": 3,
        "bathrooms": 2.0,
        "square_feet": 1400,
        "year_built": 2012,
        "price_estimate": 680000,
        "rent_estimate": 2900,
    },
    "denver": {
        "address": "100 Mountain View Dr, Denver, CO 80202",
        "city": "Denver",
        "state": "CO",
        "zip_code": "80202",
        "property_type": "Single Family",
        "bedrooms": 3,
        "bathrooms": 2.0,
        "square_feet": 1600,
        "year_built": 2008,
        "price_estimate": 520000,
        "rent_estimate": 2500,
    },
    "phoenix": {
        "address": "222 Desert Rose Ln, Phoenix, AZ 85004",
        "city": "Phoenix",
        "state": "AZ",
        "zip_code": "85004",
        "property_type": "Single Family",
        "bedrooms": 4,
        "bathrooms": 2.5,
        "square_feet": 2000,
        "year_built": 2018,
        "price_estimate": 380000,
        "rent_estimate": 2200,
    },
}


def get_mock_property(address: str) -> dict:
    """根据地址返回模拟数据"""
    address_lower = address.lower()

    # 尝试匹配城市
    for key, data in MOCK_PROPERTIES.items():
        if key in address_lower:
            return {**data, "address": address}

    # 默认返回通用数据
    return {
        "address": address,
        "city": "Unknown",
        "state": "XX",
        "zip_code": "00000",
        "property_type": "Single Family",
        "bedrooms": 3,
        "bathrooms": 2.0,
        "square_feet": 1500,
        "year_built": 2000,
        "price_estimate": 400000,
        "rent_estimate": 2000,
    }


def generate_market_insights(property_data: dict, analysis: InvestmentAnalysis) -> dict:
    """Generate market insights"""
    insights = []

    # CAP Rate analysis
    if analysis.cap_rate >= 6:
        insights.append({
            "type": "positive",
            "title": "High Return Rate",
            "description": f"CAP Rate of {analysis.cap_rate}% is above market average, indicating strong return potential"
        })
    elif analysis.cap_rate >= 4:
        insights.append({
            "type": "neutral",
            "title": "Moderate Return Rate",
            "description": f"CAP Rate of {analysis.cap_rate}% is at market average level"
        })
    else:
        insights.append({
            "type": "warning",
            "title": "Low Return Rate",
            "description": f"CAP Rate of {analysis.cap_rate}% is below ideal level, invest with caution"
        })

    # Cash flow analysis
    if analysis.monthly_cashflow > 500:
        insights.append({
            "type": "positive",
            "title": "Strong Cash Flow",
            "description": f"Monthly cash flow of ${analysis.monthly_cashflow:.0f} indicates healthy positive cash flow"
        })
    elif analysis.monthly_cashflow > 0:
        insights.append({
            "type": "neutral",
            "title": "Thin Cash Flow",
            "description": f"Monthly cash flow of ${analysis.monthly_cashflow:.0f}, consider reserving funds for unexpected expenses"
        })
    else:
        insights.append({
            "type": "warning",
            "title": "Negative Cash Flow Risk",
            "description": f"Monthly cash flow of ${analysis.monthly_cashflow:.0f} requires monthly subsidy, invest carefully"
        })

    # Gross Rent Multiplier analysis
    if analysis.gross_rent_multiplier <= 12:
        insights.append({
            "type": "positive",
            "title": "Excellent Price-to-Rent Ratio",
            "description": f"Gross Rent Multiplier of {analysis.gross_rent_multiplier:.1f} years indicates short payback period"
        })

    # Investment grade
    grade_descriptions = {
        "A": "Excellent investment opportunity - Highly recommended",
        "B": "Good investment potential - Worth considering",
        "C": "Fair investment - Requires careful evaluation",
        "D": "High risk investment - Proceed with caution"
    }
    insights.append({
        "type": "info",
        "title": f"Investment Grade: {analysis.investment_grade}",
        "description": grade_descriptions.get(analysis.investment_grade, "")
    })

    return {
        "grade": analysis.investment_grade,
        "insights": insights,
        "recommendation": "Recommended" if analysis.investment_grade in ["A", "B"] and analysis.monthly_cashflow > 0 else "Requires Careful Consideration"
    }


@router.get("/search", response_model=PropertySearchResult)
async def search_property(
    address: str = Query(..., description="房产地址"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """搜索房产信息并返回投资分析"""

    # 检查搜索次数限制（登录用户）
    if current_user:
        if current_user.searches_used >= current_user.searches_limit:
            raise HTTPException(
                status_code=429,
                detail="已达到本月搜索次数上限，请升级订阅计划"
            )

    # 获取房产数据
    property_data = None
    using_real_data = False

    # 尝试调用 RentCast API
    if settings.RENTCAST_API_KEY:
        rentcast_data = await rentcast_service.get_property_by_address(address)
        if rentcast_data:
            property_data = rentcast_service.normalize_property_data(rentcast_data, address)
            using_real_data = True
            print(f"Using real RentCast data for: {address}")

    # 使用模拟数据作为后备
    if not property_data:
        property_data = get_mock_property(address)
        print(f"Using mock data for: {address}")

    # 计算投资分析
    analysis = investment_calculator.calculate(
        price=property_data.get("price_estimate", 0),
        rent=property_data.get("rent_estimate", 0),
        square_feet=property_data.get("square_feet", 1000),
    )

    # 生成市场洞察
    market_insights = generate_market_insights(property_data, analysis)

    # 保存搜索记录
    if current_user:
        search_record = SearchHistory(
            user_id=current_user.id,
            address=address,
        )
        db.add(search_record)
        current_user.searches_used += 1
        db.commit()

    return PropertySearchResult(
        property=PropertyResponse(**property_data),
        analysis=InvestmentAnalysisResponse(
            cap_rate=analysis.cap_rate,
            gross_rent_multiplier=analysis.gross_rent_multiplier,
            monthly_cashflow=analysis.monthly_cashflow,
            annual_cashflow=analysis.annual_cashflow,
            cash_on_cash_return=analysis.cash_on_cash_return,
            price_per_sqft=analysis.price_per_sqft,
            rent_per_sqft=analysis.rent_per_sqft,
            break_even_ratio=analysis.break_even_ratio,
            investment_grade=analysis.investment_grade,
        ),
        market_insights=market_insights,
    )


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: int,
    db: Session = Depends(get_db),
):
    """获取房产详情"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="房产不存在")
    return property_obj
