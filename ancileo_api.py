"""
Ancileo API Integration
Connects to Ancileo's travel insurance API to fetch policies and quotes
"""

import os
import json
import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class AncileoAPI:
    """Handles integration with Ancileo's travel insurance API"""
    
    def __init__(self):
        self.api_key = os.getenv("ANCILEO_API_KEY", "")
        self.base_url = "https://dev.api.ancileo.com/v1/travel/front"
        
        if not self.api_key or self.api_key == "your_ancileo_api_key_here":
            logger.warning("ANCILEO_API_KEY not set - some features may be limited")
        else:
            logger.info("Ancileo API initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
    
    async def get_quote(
        self,
        market: str = "SG",
        language_code: str = "en",
        channel: str = "white-label",
        device_type: str = "DESKTOP",
        trip_type: str = "RT",  # RT = Round Trip, ST = Single Trip
        departure_date: str = None,
        return_date: str = None,
        departure_country: str = "SG",
        arrival_country: str = "CN",
        adults_count: int = 1,
        children_count: int = 0
    ) -> Dict[str, Any]:
        """
        Get insurance quotes from Ancileo API
        
        Returns available policies with pricing and details
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "ANCILEO_API_KEY not configured",
                "message": "Please set ANCILEO_API_KEY in .env file"
            }
        
        # Validate dates
        if not departure_date:
            departure_date = datetime.now().strftime("%Y-%m-%d")
        if trip_type == "RT" and not return_date:
            # Default to 7 days after departure
            from datetime import timedelta
            departure_dt = datetime.strptime(departure_date, "%Y-%m-%d")
            return_date = (departure_dt + timedelta(days=7)).strftime("%Y-%m-%d")
        
        request_body = {
            "market": market,
            "languageCode": language_code,
            "channel": channel,
            "deviceType": device_type,
            "context": {
                "tripType": trip_type,
                "departureDate": departure_date,
                "departureCountry": departure_country,
                "arrivalCountry": arrival_country,
                "adultsCount": adults_count,
                "childrenCount": children_count
            }
        }
        
        # Add returnDate for round trips
        if trip_type == "RT" and return_date:
            request_body["context"]["returnDate"] = return_date
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/pricing",
                    headers=self._get_headers(),
                    json=request_body
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Successfully fetched quote from Ancileo API")
                    return {
                        "success": True,
                        "quote_id": data.get("quoteId"),
                        "policies": self._parse_policies_from_response(data),
                        "raw_response": data
                    }
                else:
                    logger.error(f"Ancileo API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}",
                        "message": response.text[:500]
                    }
                    
        except httpx.TimeoutException:
            logger.error("Ancileo API request timed out")
            return {
                "success": False,
                "error": "Request timeout",
                "message": "Ancileo API did not respond in time"
            }
        except Exception as e:
            logger.error(f"Ancileo API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to connect to Ancileo API"
            }
    
    def _parse_policies_from_response(self, response_data: Dict) -> List[Dict]:
        """
        Parse policy information from Ancileo API response
        
        The response structure may vary - this extracts available policies/offers
        """
        policies = []
        
        try:
            # Try different possible response structures
            offers = response_data.get("offers", [])
            products = response_data.get("products", [])
            plans = response_data.get("plans", [])
            
            # Check all possible keys
            policy_list = offers or products or plans or []
            
            for item in policy_list:
                policy = {
                    "offer_id": item.get("offerId") or item.get("id"),
                    "product_code": item.get("productCode") or item.get("code"),
                    "product_name": item.get("productName") or item.get("name") or item.get("productCode", "Unknown"),
                    "product_type": item.get("productType", "travel-insurance"),
                    "price": item.get("unitPrice") or item.get("price"),
                    "currency": item.get("currency", "SGD"),
                    "description": item.get("description") or item.get("summary"),
                    "coverage": item.get("coverage", {}),
                    "features": item.get("features", []),
                    "terms": item.get("terms", {}),
                    "raw_data": item
                }
                policies.append(policy)
                
        except Exception as e:
            logger.error(f"Error parsing policies from response: {e}")
        
        return policies
    
    async def get_available_policies(
        self,
        departure_country: str = "SG",
        arrival_country: str = "CN",
        departure_date: str = None,
        return_date: str = None,
        adults: int = 1,
        children: int = 0
    ) -> List[Dict]:
        """
        Get list of available policies from Ancileo
        
        This is a convenience method that fetches quotes and returns policy list
        """
        quote_result = await self.get_quote(
            departure_country=departure_country,
            arrival_country=arrival_country,
            departure_date=departure_date,
            return_date=return_date,
            adults_count=adults,
            children_count=children
        )
        
        if quote_result.get("success"):
            return quote_result.get("policies", [])
        else:
            logger.warning(f"Failed to fetch policies: {quote_result.get('error')}")
            return []
    
    async def purchase_policy(
        self,
        quote_id: str,
        offer_id: str,
        product_code: str,
        product_type: str,
        unit_price: float,
        currency: str,
        quantity: int,
        insureds: List[Dict],
        is_send_email: bool = True,
        market: str = "SG",
        language_code: str = "en",
        channel: str = "white-label"
    ) -> Dict[str, Any]:
        """
        Purchase insurance policy through Ancileo API
        
        Note: This should be called after payment processing
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "ANCILEO_API_KEY not configured"
            }
        
        request_body = {
            "market": market,
            "languageCode": language_code,
            "channel": channel,
            "quoteId": quote_id,
            "purchaseOffers": [
                {
                    "productType": product_type,
                    "offerId": offer_id,
                    "productCode": product_code,
                    "unitPrice": unit_price,
                    "currency": currency,
                    "quantity": quantity,
                    "totalPrice": unit_price * quantity,
                    "isSendEmail": is_send_email
                }
            ],
            "insureds": insureds
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/purchase",
                    headers=self._get_headers(),
                    json=request_body
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("Successfully processed purchase through Ancileo API")
                    return {
                        "success": True,
                        "purchase_id": data.get("purchaseId") or data.get("id"),
                        "policy_number": data.get("policyNumber"),
                        "confirmation": data,
                        "raw_response": data
                    }
                else:
                    logger.error(f"Purchase failed: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}",
                        "message": response.text[:500]
                    }
                    
        except Exception as e:
            logger.error(f"Purchase error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

