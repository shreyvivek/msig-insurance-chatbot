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
        # According to Ancileo documentation: https://www.ancileo.com/insurance-api/
        # Base URL format: https://[base]/v1/travel/front/[endpoint]
        # Try production URL first, fallback to dev
        base_domain = os.getenv("ANCILEO_BASE_URL", "dev.api.ancileo.com")
        self.base_url = f"https://{base_domain}/v1/travel/front"
        
        if not self.api_key or self.api_key == "your_ancileo_api_key_here":
            logger.warning("ANCILEO_API_KEY not set - some features may be limited")
        else:
            logger.info(f"Ancileo API initialized with base URL: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests - according to Ancileo docs, header is X-Api-Key"""
        return {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key  # Capital X as per Ancileo documentation
        }
    
    async def get_quote(
        self,
        market: str = "SG",
        language_code: str = "en",
        channel: str = "white-label",
        device_type: str = "DESKTOP",
        trip_type: str = "RT",  # RT = Round Trip, ST = Single Trip, AN = Annual
        departure_date: str = None,
        return_date: str = None,
        departure_country: str = "SG",
        arrival_country: str = "CN",
        departure_airport: str = None,
        arrival_airport: str = None,
        adults_count: int = 1,
        children_count: int = 0,
        seniors_count: int = 0,
        infants_count: int = 0,
        ticket_price: float = None,
        currency: str = None,
        insureds: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get insurance quotes from Ancileo API
        
        According to Ancileo API documentation:
        - https://www.ancileo.com/insurance-api/
        
        Required fields:
        - market, languageCode, deviceType, touchPoint, channel, context
        - Context must have: tripType, departureDate, departureCountry, arrivalCountry, departureAirport, arrivalAirport
        - At least one age category: seniorsCount, adultsCount, childrenCount, or infantsCount
        
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
        
        # Default airports if not provided (use country code as fallback)
        if not departure_airport:
            # Map common countries to airports
            airport_map = {
                "SG": "SIN", "MY": "KUL", "TH": "BKK", "PH": "MNL",
                "ID": "CGK", "VN": "SGN", "JP": "NRT", "CN": "PEK",
                "IN": "DEL", "AU": "SYD", "US": "LAX", "GB": "LHR"
            }
            departure_airport = airport_map.get(departure_country.upper(), "SIN")
        
        if not arrival_airport:
            airport_map = {
                "SG": "SIN", "MY": "KUL", "TH": "BKK", "PH": "MNL",
                "ID": "CGK", "VN": "SGN", "JP": "NRT", "CN": "PEK",
                "IN": "DEL", "AU": "SYD", "US": "LAX", "GB": "LHR"
            }
            arrival_airport = airport_map.get(arrival_country.upper() if isinstance(arrival_country, str) else arrival_country[0].upper(), "SIN")
        
        # Ensure at least one age category is provided
        if not insureds and seniors_count == 0 and adults_count == 0 and children_count == 0 and infants_count == 0:
            adults_count = 1  # Default to 1 adult
        
        # Build context structure according to API docs
        context = {
            "tripType": trip_type.upper(),  # ST, RT, or AN
            "departureDate": departure_date,
            "departureCountry": departure_country.upper(),
            "arrivalCountry": arrival_country.upper() if isinstance(arrival_country, str) else [c.upper() for c in arrival_country],
            "departureAirport": departure_airport.upper(),
            "arrivalAirport": arrival_airport.upper() if isinstance(arrival_airport, str) else [a.upper() for a in arrival_airport],
            "adultsCount": adults_count,
            "childrenCount": children_count,
            "seniorsCount": seniors_count,
            "infantsCount": infants_count
        }
        
        # Add returnDate for round trips
        if trip_type.upper() == "RT" and return_date:
            context["returnDate"] = return_date
        
        # Add optional fields
        if ticket_price is not None:
            context["ticketPrice"] = float(ticket_price)
        if currency:
            context["currency"] = currency
        
        # Build request body according to Ancileo API documentation
        request_body = {
            "market": market.upper(),
            "languageCode": language_code.lower(),
            "deviceType": device_type.upper(),  # MOBILE, DESKTOP, TABLET, OTHER
            "touchPoint": "details",  # Hardcoded as per API docs
            "channel": channel,
            "context": context
        }
        
        # Add insureds if provided (optional, but if provided, age counts become optional)
        if insureds:
            request_body["insureds"] = insureds
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Log request details for debugging
                logger.debug(f"Ancileo API Request URL: {self.base_url}/pricing")
                logger.debug(f"Ancileo API Request Body: {json.dumps(request_body, indent=2)}")
                
                response = await client.post(
                    f"{self.base_url}/pricing",
                    headers=self._get_headers(),
                    json=request_body
                )
                
                logger.debug(f"Ancileo API Response Status: {response.status_code}")
                logger.debug(f"Ancileo API Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        policies = self._parse_policies_from_response(data)
                        quote_id = data.get("id") or data.get("quoteId") or data.get("quote_id")
                        logger.info(f"Successfully fetched quote from Ancileo API - Quote ID: {quote_id}, Found {len(policies)} policies")
                        return {
                            "success": True,
                            "quote_id": quote_id,
                            "policies": policies,
                            "raw_response": data
                        }
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse Ancileo API response as JSON: {e}")
                        logger.error(f"Response text: {response.text[:500]}")
                        return {
                            "success": False,
                            "error": "Invalid JSON response from Ancileo API",
                            "message": response.text[:500]
                        }
                elif response.status_code == 502:
                    logger.error(f"Ancileo API Gateway Error (502): {response.text[:500]}")
                    return {
                        "success": False,
                        "error": "API Gateway Error (502)",
                        "message": "The Ancileo API gateway encountered an error. This may be a temporary issue. Please try again or check Ancileo service status.",
                        "retryable": True
                    }
                else:
                    logger.error(f"Ancileo API error: {response.status_code} - {response.text[:500]}")
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}",
                        "message": response.text[:500],
                        "retryable": response.status_code in [502, 503, 504]
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
        
        According to Ancileo API documentation, the response structure is:
        {
            "id": "quote_id",
            "offerCategories": [
                {
                    "productType": "travel-insurance",
                    "offers": [
                        {
                            "id": "offer_id",
                            "productCode": "code",
                            "unitPrice": 123.45,
                            "currency": "SGD",
                            "productInformation": {
                                "title": "Product Name",
                                "benefits": "HTML text",
                                "imageURL": "url"
                            },
                            "options": [...]
                        }
                    ]
                }
            ]
        }
        """
        policies = []
        
        try:
            # Log raw response structure for debugging
            logger.debug(f"Ancileo API response keys: {list(response_data.keys())}")
            
            # According to API docs, response has "offerCategories" array
            offer_categories = response_data.get("offerCategories", [])
            
            if not offer_categories:
                logger.warning("No offerCategories found in Ancileo API response")
                logger.debug(f"Response structure: {json.dumps(response_data, indent=2, default=str)[:1000]}")
                return []
            
            # Extract offers from all categories
            for category in offer_categories:
                product_type = category.get("productType", "travel-insurance")
                offers = category.get("offers", [])
                
                logger.debug(f"Found category '{product_type}' with {len(offers)} offers")
                
                for offer in offers:
                    try:
                        # Extract offer details
                        offer_id = offer.get("id")
                        product_code = offer.get("productCode")
                        unit_price = offer.get("unitPrice", 0)
                        currency = offer.get("currency", "SGD")
                        
                        # Extract product information
                        product_info = offer.get("productInformation", {})
                        product_title = product_info.get("title", "Ancileo Policy")
                        benefits_html = product_info.get("benefits", "")
                        image_url = product_info.get("imageURL")
                        
                        # Extract options if available
                        options = offer.get("options", [])
                        
                        # Handle price - ensure it's a float
                        if isinstance(unit_price, str):
                            try:
                                unit_price = float(unit_price.replace(",", ""))
                            except (ValueError, AttributeError):
                                unit_price = 0
                        
                        # Convert HTML benefits to plain text description (strip HTML tags)
                        import re
                        description = re.sub(r'<[^>]+>', '', benefits_html) if benefits_html else "Travel protection"
                        description = description.strip()[:500]  # Limit length
                        
                        policy = {
                            "offer_id": offer_id,
                            "product_code": product_code,
                            "product_name": product_title,
                            "product_type": product_type,
                            "price": float(unit_price) if unit_price else 0,
                            "currency": currency,
                            "description": description,
                            "benefits_html": benefits_html,  # Keep original HTML for display
                            "image_url": image_url,
                            "options": options,
                            "raw_data": offer
                        }
                        policies.append(policy)
                        
                        logger.debug(f"Parsed policy: {product_title} (${unit_price} {currency})")
                        
                    except Exception as e:
                        logger.warning(f"Error parsing individual offer: {e}")
                        logger.debug(f"Problematic offer: {json.dumps(offer, indent=2, default=str)}")
                        continue
                
        except Exception as e:
            logger.error(f"Error parsing policies from Ancileo response: {e}", exc_info=True)
            logger.debug(f"Response data: {json.dumps(response_data, indent=2, default=str)[:1000]}")
        
        logger.info(f"Parsed {len(policies)} policies from Ancileo API response")
        return policies
    
    async def get_available_policies(
        self,
        departure_country: str = "SG",
        arrival_country: str = "CN",
        departure_date: str = None,
        return_date: str = None,
        adults: int = 1,
        children: int = 0,
        retry_count: int = 0,
        max_retries: int = 2
    ) -> List[Dict]:
        """
        Get list of available policies from Ancileo with retry logic
        
        This is a convenience method that fetches quotes and returns policy list.
        Implements exponential backoff for 502/503/504 errors.
        """
        import asyncio
        
        quote_result = await self.get_quote(
            departure_country=departure_country,
            arrival_country=arrival_country,
            departure_date=departure_date,
            return_date=return_date,
            adults_count=adults,
            children_count=children
        )
        
        # Retry logic for gateway/server errors
        if not quote_result.get("success") and quote_result.get("retryable") and retry_count < max_retries:
            wait_time = (2 ** retry_count)  # Exponential backoff: 1s, 2s, 4s
            logger.info(f"Retrying Ancileo API request in {wait_time} seconds (attempt {retry_count + 1}/{max_retries})...")
            await asyncio.sleep(wait_time)
            
            return await self.get_available_policies(
                departure_country=departure_country,
                arrival_country=arrival_country,
                departure_date=departure_date,
                return_date=return_date,
                adults=adults,
                children=children,
                retry_count=retry_count + 1,
                max_retries=max_retries
            )
        
        if quote_result.get("success"):
            policies = quote_result.get("policies", [])
            logger.info(f"Successfully fetched {len(policies)} policies from Ancileo")
            return policies
        else:
            error_msg = quote_result.get("error", "Unknown error")
            logger.warning(f"Failed to fetch Ancileo policies: {error_msg}")
            if quote_result.get("message"):
                logger.warning(f"Error details: {quote_result.get('message')}")
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
        main_contact: Dict,
        emergency_contact: Dict = None,
        payment: Dict = None,
        partner_reference: str = None,
        options: List[str] = None,
        is_send_email: bool = True,
        market: str = "SG",
        language_code: str = "en"
    ) -> Dict[str, Any]:
        """
        Purchase insurance policy through Ancileo API
        
        According to Ancileo API documentation:
        - Required: market, languageCode, quoteId, purchaseOffers, insureds, mainContact
        - Optional: emergencyContact, payment
        
        Note: This should be called after payment processing
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "ANCILEO_API_KEY not configured"
            }
        
        # Build purchase offer structure
        purchase_offer = {
            "productType": product_type,
            "offerId": offer_id,
            "productCode": product_code,
            "unitPrice": float(unit_price),
            "currency": currency,
            "quantity": quantity,
            "totalPrice": float(unit_price) * quantity,
            "isSendEmail": is_send_email
        }
        
        # Add optional fields
        if partner_reference:
            purchase_offer["partnerReference"] = partner_reference
        if options:
            purchase_offer["options"] = options
        
        # Build request body according to API docs
        request_body = {
            "market": market.upper(),
            "languageCode": language_code.lower(),
            "quoteId": quote_id,
            "purchaseOffers": [purchase_offer],
            "insureds": insureds,
            "mainContact": main_contact
        }
        
        # Add optional fields
        if emergency_contact:
            request_body["emergencyContact"] = emergency_contact
        if payment:
            request_body["payment"] = payment
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.debug(f"Ancileo Purchase Request: {json.dumps(request_body, indent=2, default=str)}")
                
                response = await client.post(
                    f"{self.base_url}/purchase",
                    headers=self._get_headers(),
                    json=request_body
                )
                
                logger.debug(f"Ancileo Purchase Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("Successfully processed purchase through Ancileo API")
                    
                    # Extract purchase details according to API docs
                    purchase_id = data.get("id")
                    purchased_offers = data.get("purchasedOffers", [])
                    
                    # Get policy number from first purchased offer
                    policy_number = None
                    if purchased_offers and len(purchased_offers) > 0:
                        policy_number = purchased_offers[0].get("purchasedOfferId")
                    
                    return {
                        "success": True,
                        "purchase_id": purchase_id,
                        "policy_number": policy_number,
                        "purchased_offers": purchased_offers,
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
            logger.error(f"Purchase error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_policy_wordings(
        self,
        policy_id: str,
        email: str,
        market: str = "SG"
    ) -> Dict[str, Any]:
        """
        Get detailed policy wordings/documentation from Ancileo API
        
        According to Ancileo API documentation:
        POST /v1/travel/front/getPolicy
        Requires: market, details (with email and policyId)
        
        policy_id should be the purchasedOfferId from purchase API response
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "ANCILEO_API_KEY not configured"
            }
        
        request_body = {
            "market": market.upper(),
            "details": {
                "email": email,
                "policyId": policy_id
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.debug(f"Ancileo GetPolicy Request: {json.dumps(request_body, indent=2)}")
                
                response = await client.post(
                    f"{self.base_url}/getPolicy",
                    headers=self._get_headers(),
                    json=request_body
                )
                
                logger.debug(f"Ancileo GetPolicy Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("Successfully fetched policy wordings from Ancileo API")
                    
                    # Extract policy details according to API docs
                    return {
                        "success": True,
                        "policy_id": policy_id,
                        "context": data.get("context", {}),
                        "cover": data.get("cover", {}),
                        "purchase": data.get("purchase", {}),
                        "travel_context": data.get("travelContext", {}),
                        "product": data.get("product", {}),
                        "insureds": data.get("insureds", []),
                        "main_contact": data.get("mainContact", {}),
                        "emergency_contact": data.get("emergencyContact", {}),
                        "raw_data": data
                    }
                else:
                    logger.error(f"GetPolicy failed: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}",
                        "message": response.text[:500]
                    }
                
        except Exception as e:
            logger.error(f"Error fetching policy wordings: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

