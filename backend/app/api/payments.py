"""
LemonSqueezy Payment Integration - Simplified
"""

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models import User
from app.api.auth import get_current_user
from app.config import settings

router = APIRouter()

LEMONSQUEEZY_API_URL = "https://api.lemonsqueezy.com/v1"


class CheckoutRequest(BaseModel):
    plan: str


class CheckoutResponse(BaseModel):
    checkout_url: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_payment_checkout(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a checkout session for subscription"""

    if request.plan not in ["starter", "pro", "team"]:
        raise HTTPException(status_code=400, detail="Invalid plan")

    variant_ids = {
        "starter": settings.LEMONSQUEEZY_STARTER_VARIANT_ID,
        "pro": settings.LEMONSQUEEZY_PRO_VARIANT_ID,
        "team": settings.LEMONSQUEEZY_TEAM_VARIANT_ID,
    }

    variant_id = variant_ids.get(request.plan)
    if not variant_id:
        raise HTTPException(status_code=400, detail="Invalid plan")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LEMONSQUEEZY_API_URL}/checkouts",
                headers={
                    "Authorization": f"Bearer {settings.LEMONSQUEEZY_API_KEY}",
                    "Content-Type": "application/vnd.api+json",
                },
                json={
                    "data": {
                        "type": "checkouts",
                        "attributes": {
                            "checkout_data": {
                                "email": current_user.email,
                                "name": current_user.name or current_user.email,
                                "custom": {
                                    "user_email": current_user.email,
                                    "plan": request.plan
                                }
                            }
                        },
                        "relationships": {
                            "store": {
                                "data": {"type": "stores", "id": str(settings.LEMONSQUEEZY_STORE_ID)}
                            },
                            "variant": {
                                "data": {"type": "variants", "id": str(variant_id)}
                            }
                        }
                    }
                },
                timeout=15.0
            )

            if response.status_code == 201:
                data = response.json()
                return CheckoutResponse(checkout_url=data["data"]["attributes"]["url"])

            raise HTTPException(status_code=500, detail=f"Checkout failed: {response.text[:100]}")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Payment service timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout error: {str(e)}")


@router.get("/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
):
    """Get current subscription status"""
    return {
        "plan": current_user.subscription_plan,
        "searches_used": current_user.searches_used,
        "searches_limit": current_user.searches_limit,
    }
