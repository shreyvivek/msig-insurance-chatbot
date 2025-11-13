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
    """Handles integration with Ancileo's travel insurance API with support for multiple API keys"""
    
    def __init__(self):
        # Support for multiple API keys (3 keys for 3 different products)
        self.api_keys = {
            1: os.getenv("ANCILEO_API_KEY_1", ""),
            2: os.getenv("ANCILEO_API_KEY_2", ""),
            3: os.getenv("ANCILEO_API_KEY_3", "")
        }
        
        # Fallback to single key for backward compatibility
        if not any(self.api_keys.values()):
            legacy_key = os.getenv("ANCILEO_API_KEY", "")
            if legacy_key and legacy_key != "your_ancileo_api_key_here":
                self.api_keys[1] = legacy_key
                logger.info("Using legacy ANCILEO_API_KEY (single key)")
        
        # Track which keys are configured
        self.available_keys = [k for k, v in self.api_keys.items() if v and v != f"your_ancileo_api_key_{k}_here"]
        self.current_key_index = 0  # For round-robin selection
        
        # Load key mapping from environment (optional)
        self.key_mapping = self._load_key_mapping()
        
        # Base URL configuration
        base_domain = os.getenv("ANCILEO_BASE_URL", "dev.api.ancileo.com")
        self.base_url = f"https://{base_domain}/v1/travel/front"
        
        if not self.available_keys:
            logger.warning("No Ancileo API keys configured - some features may be limited")
        else:
            logger.info(f"Ancileo API initialized with {len(self.available_keys)} API key(s) - Base URL: {self.base_url}")
    
    def _load_key_mapping(self) -> Dict[str, int]:
        """
        Load API key mapping from environment variable
        
        Supports two formats:
        1. Product code mapping: PRODUCT_CODE:KEY_NUMBER
        2. Policy name mapping: POLICY_NAME:KEY_NUMBER
        
        Examples:
        - SG_AXA_SCOOT_COMP:1
        - INTERNATIONAL TRAVEL:1
        - Scootsurance:3
        """
        mapping_str = os.getenv("ANCILEO_KEY_MAPPING", "")
        if not mapping_str:
            return {}
        
        mapping = {}
        for item in mapping_str.split(","):
            item = item.strip()
            if ":" in item:
                identifier, key_num = item.split(":", 1)
                try:
                    key_num = int(key_num.strip())
                    identifier_upper = identifier.strip().upper()
                    mapping[identifier_upper] = key_num
                    # Also create a lowercase version for case-insensitive matching
                    mapping[identifier.strip().lower()] = key_num
                except ValueError:
                    logger.warning(f"Invalid key mapping format: {item}")
        
        return mapping
    
    def _match_policy_to_key(self, product_code: str = None, product_name: str = None) -> Optional[int]:
        """
        Match a policy to an API key based on product code or name
        
        Checks against:
        1. Direct product code match
        2. Product name match (case-insensitive, partial matching)
        3. Policy name keywords (INTERNATIONAL TRAVEL, MHInsure, Scootsurance)
        """
        if not self.key_mapping:
            return None
        
        # Check product code first
        if product_code:
            product_code_upper = product_code.upper()
            if product_code_upper in self.key_mapping:
                return self.key_mapping[product_code_upper]
        
        # Check product name (exact match)
        if product_name:
            product_name_upper = product_name.upper()
            product_name_lower = product_name.lower()
            if product_name_upper in self.key_mapping:
                return self.key_mapping[product_name_upper]
            if product_name_lower in self.key_mapping:
                return self.key_mapping[product_name_lower]
        
        # Check for policy name keywords in product name
        if product_name:
            product_lower = product_name.lower().strip()
            
            # Check for exact matches first (most specific)
            if product_lower == "scoot":
                if "SCOOT" in self.key_mapping or "scoot" in self.key_mapping:
                    return self.key_mapping.get("SCOOT") or self.key_mapping.get("scoot")
            if product_lower == "mag":
                if "MAG" in self.key_mapping or "mag" in self.key_mapping:
                    return self.key_mapping.get("MAG") or self.key_mapping.get("mag")
            if product_lower == "trip":
                if "TRIP" in self.key_mapping or "trip" in self.key_mapping:
                    return self.key_mapping.get("TRIP") or self.key_mapping.get("trip")
            
            # Check for partial matches (less specific)
            if "scootsurance" in product_lower or "scoot" in product_lower:
                if "SCOOTSURANCE" in self.key_mapping or "scootsurance" in self.key_mapping:
                    return self.key_mapping.get("SCOOTSURANCE") or self.key_mapping.get("scootsurance")
                if "SCOOT" in self.key_mapping or "scoot" in self.key_mapping:
                    return self.key_mapping.get("SCOOT") or self.key_mapping.get("scoot")
            
            if "mhinsure" in product_lower or "mh insure" in product_lower or "mag" in product_lower:
                if "MHINSURE TRAVEL" in self.key_mapping or "mhinsure travel" in self.key_mapping:
                    return self.key_mapping.get("MHINSURE TRAVEL") or self.key_mapping.get("mhinsure travel")
                if "MAG" in self.key_mapping or "mag" in self.key_mapping:
                    return self.key_mapping.get("MAG") or self.key_mapping.get("mag")
            
            if "international" in product_lower and "travel" in product_lower:
                if "INTERNATIONAL TRAVEL" in self.key_mapping or "international travel" in self.key_mapping:
                    return self.key_mapping.get("INTERNATIONAL TRAVEL") or self.key_mapping.get("international travel")
                if "TRIP" in self.key_mapping or "trip" in self.key_mapping:
                    return self.key_mapping.get("TRIP") or self.key_mapping.get("trip")
        
        return None
    
    def _get_api_key_for_product(self, product_code: str = None, product_name: str = None) -> str:
        """
        Get the appropriate API key for a product
        
        Priority:
        1. Use key mapping if product_code or product_name matches a mapping
        2. Use round-robin selection across available keys
        3. Fallback to first available key
        """
        if not self.available_keys:
            return ""
        
        # Try to match policy to key
        matched_key = self._match_policy_to_key(product_code, product_name)
        if matched_key and matched_key in self.available_keys:
            logger.debug(f"Using mapped API key {matched_key} for product {product_code or product_name}")
            return self.api_keys[matched_key]
        
        # Round-robin selection
        key_num = self.available_keys[self.current_key_index % len(self.available_keys)]
        self.current_key_index += 1
        logger.debug(f"Using API key {key_num} (round-robin)")
        return self.api_keys[key_num]
    
    @property
    def api_key(self) -> str:
        """Get default API key (for backward compatibility)"""
        return self._get_api_key_for_product()
    
    def _get_headers(self, product_code: str = None) -> Dict[str, str]:
        """Get headers for API requests - according to Ancileo docs, header is X-Api-Key"""
        api_key = self._get_api_key_for_product(product_code)
        return {
            "Content-Type": "application/json",
            "X-Api-Key": api_key  # Capital X as per Ancileo documentation
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
        if not self.available_keys:
            return {
                "success": False,
                "error": "ANCILEO_API_KEY not configured",
                "message": "Please set ANCILEO_API_KEY_1, ANCILEO_API_KEY_2, and/or ANCILEO_API_KEY_3 in .env file"
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
        
        # Build request body according to new Ancileo API documentation format
        request_body = {
            "market": market.upper(),
            "languageCode": language_code.lower(),
            "channel": channel,  # "white-label" as per new docs
            "deviceType": device_type.upper(),  # "DESKTOP" as per new docs
            "context": context
        }
        
        # Add insureds if provided (optional, but if provided, age counts become optional)
        if insureds:
            request_body["insureds"] = insureds
        
        # Try all available API keys to get maximum coverage
        # Start with round-robin, but we'll collect results from all keys
        all_policies = []
        quote_ids = []
        last_error = None
        
        for key_num in self.available_keys:
            api_key = self.api_keys[key_num]
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Log request details for debugging
                    logger.debug(f"Ancileo API Request URL: {self.base_url}/pricing (using key {key_num})")
                    logger.debug(f"Ancileo API Request Body: {json.dumps(request_body, indent=2)}")
                    
                    headers = {
                        "Content-Type": "application/json",
                        "X-Api-Key": api_key
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/pricing",
                        headers=headers,
                        json=request_body
                    )
                    
                    logger.debug(f"Ancileo API Response Status: {response.status_code} (key {key_num})")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            policies = self._parse_policies_from_response(data, api_key_num=key_num)
                            quote_id = data.get("id") or data.get("quoteId") or data.get("quote_id")
                            
                            # Collect policies and quote IDs from all API keys
                            all_policies.extend(policies)
                            if quote_id:
                                quote_ids.append(quote_id)
                            
                            logger.info(f"Successfully fetched quote from Ancileo API (key {key_num}) - Quote ID: {quote_id}, Found {len(policies)} policies")
                            continue  # Try next key
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse Ancileo API response as JSON (key {key_num}): {e}")
                            logger.error(f"Response text: {response.text[:500]}")
                            last_error = f"Invalid JSON response from Ancileo API (key {key_num})"
                            continue  # Try next key
                    elif response.status_code == 502:
                        logger.warning(f"Ancileo API Gateway Error (502) with key {key_num}: {response.text[:500]}")
                        last_error = f"API Gateway Error (502) with key {key_num}"
                        continue  # Try next key
                    else:
                        logger.warning(f"Ancileo API error (key {key_num}): {response.status_code} - {response.text[:500]}")
                        last_error = f"API returned status {response.status_code} with key {key_num}"
                        continue  # Try next key
                        
            except httpx.TimeoutException:
                logger.warning(f"Ancileo API request timed out (key {key_num})")
                last_error = f"Request timeout with key {key_num}"
                continue  # Try next key
            except Exception as e:
                logger.warning(f"Ancileo API error (key {key_num}): {e}")
                last_error = f"Failed to connect with key {key_num}: {str(e)}"
                continue  # Try next key
        
        # Return combined results from all API keys
        if all_policies:
            # Remove duplicates based on product_code
            unique_policies = {}
            for policy in all_policies:
                product_code = policy.get("product_code")
                if product_code and product_code not in unique_policies:
                    unique_policies[product_code] = policy
                elif not product_code:
                    # If no product_code, add it anyway
                    unique_policies[f"policy_{len(unique_policies)}"] = policy
            
            final_policies = list(unique_policies.values())
            primary_quote_id = quote_ids[0] if quote_ids else None
            
            logger.info(f"Successfully fetched quotes from {len(self.available_keys)} API key(s) - Total unique policies: {len(final_policies)}")
            return {
                "success": True,
                "quote_id": primary_quote_id,
                "quote_ids": quote_ids,  # All quote IDs from different keys
                "policies": final_policies,
                "keys_used": len([k for k in self.available_keys if k]),
                "total_policies_found": len(final_policies)
            }
        else:
            # All keys failed
            logger.error(f"All Ancileo API keys failed. Last error: {last_error}")
            return {
                "success": False,
                "error": "All API keys failed",
                "message": last_error or "Failed to fetch quotes from any API key",
                "retryable": True
            }
    
    def _parse_policies_from_response(self, response_data: Dict, api_key_num: int = None) -> List[Dict]:
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
                        
                        # Track which API key was used for this policy
                        policy_api_key = api_key_num
                        if not policy_api_key:
                            # Try to match based on product name or code
                            matched_key = self._match_policy_to_key(product_code, product_title)
                            if matched_key:
                                policy_api_key = matched_key
                                logger.debug(f"Matched policy '{product_title}' (code: {product_code}) to API key {matched_key}")
                        
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
                            "raw_data": offer,
                            "api_key_used": policy_api_key  # Track which key fetched this policy
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
        language_code: str = "en",
        product_name: str = None
    ) -> Dict[str, Any]:
        """
        Purchase insurance policy through Ancileo API
        
        According to Ancileo API documentation:
        - Required: market, languageCode, quoteId, purchaseOffers, insureds, mainContact
        - Optional: emergencyContact, payment
        
        Note: This should be called after payment processing
        """
        if not self.available_keys:
            return {
                "success": False,
                "error": "ANCILEO_API_KEY not configured"
            }
        
        # Get the appropriate API key for this product
        # Use product_code and product_name to find the correct key
        api_key = self._get_api_key_for_product(product_code, product_name)
        if product_name:
            logger.info(f"Purchasing '{product_name}' (code: {product_code}) using mapped API key")
        
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
        
        # Build request body according to new API documentation format
        request_body = {
            "market": market.upper(),
            "languageCode": language_code.lower(),
            "channel": "white-label",  # As per new API docs
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
                
                headers = {
                    "Content-Type": "application/json",
                    "X-Api-Key": api_key  # Use the product-specific API key
                }
                
                response = await client.post(
                    f"{self.base_url}/purchase",
                    headers=headers,
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
        if not self.available_keys:
            return {
                "success": False,
                "error": "ANCILEO_API_KEY not configured"
            }
        
        # Get API key - use product_code if available, otherwise use default
        api_key = self._get_api_key_for_product(None)

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
                
                headers = {
                    "Content-Type": "application/json",
                    "X-Api-Key": api_key
                }
                
                response = await client.post(
                    f"{self.base_url}/getPolicy",
                    headers=headers,
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

