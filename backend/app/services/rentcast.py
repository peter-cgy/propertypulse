"""
RentCast API 服务
获取房产估值和租金数据
"""

import httpx
from typing import Optional, Dict, Any
from app.config import settings


class RentCastService:
    """RentCast API 服务类"""

    BASE_URL = "https://api.rentcast.io/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.RENTCAST_API_KEY

    async def get_property_by_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        根据地址获取房产信息

        RentCast API 返回格式：
        {
            "formattedAddress": "123 Main St, New York, NY 10001",
            "addressLine1": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zipCode": "10001",
            "propertyType": "Single Family",
            "bedrooms": 3,
            "bathrooms": 2,
            "squareFootage": 1500,
            "yearBuilt": 1990,
            "price": 450000,
            "pricePerSquareFoot": 300,
            "lastSaleDate": "2023-01-15",
            "lastSalePrice": 420000,
            "rent": 2500,
            "rentPerSquareFoot": 1.67,
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        """
        if not self.api_key:
            print("RentCast API Key not configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/property",
                    headers={
                        "X-Api-Key": self.api_key,
                        "Accept": "application/json"
                    },
                    params={"address": address}
                )

                print(f"RentCast API status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    # RentCast 可能返回单个对象或数组
                    if isinstance(data, list) and len(data) > 0:
                        return data[0]
                    elif isinstance(data, dict) and data:
                        return data
                elif response.status_code == 401:
                    print("RentCast API: Invalid API Key")
                elif response.status_code == 429:
                    print("RentCast API: Rate limit exceeded")
                else:
                    print(f"RentCast API error: {response.text}")

                return None
        except httpx.TimeoutException:
            print("RentCast API timeout")
            return None
        except Exception as e:
            print(f"RentCast API exception: {e}")
            return None

    async def get_rent_estimate(self, address: str) -> Optional[Dict[str, Any]]:
        """
        获取租金估值（单独的租金API端点）
        """
        if not self.api_key:
            return None

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/rent/estimate",
                    headers={
                        "X-Api-Key": self.api_key,
                        "Accept": "application/json"
                    },
                    params={"address": address}
                )

                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"RentCast rent estimate error: {e}")
            return None

    def normalize_property_data(self, data: Dict[str, Any], original_address: str) -> Dict[str, Any]:
        """
        标准化 RentCast 返回的数据格式，使其与我们的 PropertyResponse 兼容
        """
        return {
            "address": data.get("formattedAddress") or original_address,
            "city": data.get("city", ""),
            "state": data.get("state", ""),
            "zip_code": data.get("zipCode", ""),
            "property_type": data.get("propertyType", "Unknown"),
            "bedrooms": data.get("bedrooms"),
            "bathrooms": data.get("bathrooms"),
            "square_feet": data.get("squareFootage"),
            "year_built": data.get("yearBuilt"),
            "price_estimate": data.get("price") or data.get("lastSalePrice"),
            "rent_estimate": data.get("rent"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        }


# 全局实例
rentcast_service = RentCastService()
