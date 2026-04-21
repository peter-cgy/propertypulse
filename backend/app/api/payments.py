"""
LemonSqueezy Payment Integration
"""

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json
import hmac
import hashlib

from app.database import get_db
from app.models import User
from app.api.auth import get_current_user
from app.config import settings

router = APIRouter()

LEMONSQUEEZY_API_URL = "https://api.lemonsqueezy.com/v1"


class CheckoutRequest(BaseModel):
    plan: str  # starter, pro, team


class CheckoutResponse(BaseModel):
    checkout_url: str


async def create_checkout(user_email: str, user_name: str, plan: str) -> Optional[str]:
    """Create a LemonSqueezy checkout session"""

    # Map plan to variant ID
    variant_ids = {
        "starter": settings.LEMONSQUEEZY_STARTER_VARIANT_ID,
        "pro": settings.LEMONSQUEEZY_PRO_VARIANT_ID,
        "team": settings.LEMONSQUEEZY_TEAM_VARIANT_ID,
    }

    variant_id = variant_ids.get(plan)
    if not variant_id:
        return None

    try:
        async with httpx.AsyncClient() as client:
            print(f"Creating checkout for: {user_email}, plan: {plan}")
            print(f"Store ID: {settings.LEMONSQUEEZY_STORE_ID}, Variant ID: {variant_id}")

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
                                "email": user_email,
                                "name": user_name,
                                "custom": {
                                    "user_email": user_email,
                                    "plan": plan
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

            print(f"LemonSqueezy response status: {response.status_code}")

            if response.status_code == 201:
                data = response.json()
                return data["data"]["attributes"]["url"]

            print(f"Checkout creation failed: {response.text}")
            return None

    except Exception as e:
        print(f"Checkout error: {e}")
        import traceback
        traceback.print_exc()
        return None


@router.post("/checkout", response_model=CheckoutResponse)
async def create_payment_checkout(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a checkout session for subscription"""

    if request.plan not in ["starter", "pro", "team"]:
        raise HTTPException(status_code=400, detail="Invalid plan")

    checkout_url = await create_checkout(
        user_email=current_user.email,
        user_name=current_user.name or current_user.email,
        plan=request.plan
    )

    if not checkout_url:
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

    return CheckoutResponse(checkout_url=checkout_url)


@router.post("/webhook")
async def lemon_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Handle LemonSqueezy webhooks"""

    # Get raw body
    body = await request.body()
    payload = body.decode()

    # Verify signature
    signature = request.headers.get("X-Signature")
    if settings.LEMONSQUEEZY_WEBHOOK_SECRET and signature:
        expected_sig = hmac.new(
            settings.LEMONSQUEEZY_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        data = json.loads(payload)
        event_type = data.get("meta", {}).get("event_name")

        if event_type == "order_created":
            # Extract order info
            order_data = data.get("data", {})
            attributes = order_data.get("attributes", {})
            custom_data = attributes.get("first_order_item", {}).get("custom_data", {})

            user_email = custom_data.get("user_email")
            plan = custom_data.get("plan")

            if user_email and plan:
                # Update user subscription
                user = db.query(User).filter(User.email == user_email).first()
                if user:
                    user.subscription_plan = plan
                    user.searches_limit = {
                        "starter": 30,
                        "pro": 100,
                        "team": 999
                    }.get(plan, 30)
                    db.commit()
                    print(f"Updated subscription for {user_email} to {plan}")

        return {"status": "ok"}

    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.get("/status")
async def get_subscription_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current subscription status"""
    return {
        "plan": current_user.subscription_plan,
        "searches_used": current_user.searches_used,
        "searches_limit": current_user.searches_limit,
    }
