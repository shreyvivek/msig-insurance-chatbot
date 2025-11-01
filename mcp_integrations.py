"""
MCP Integrations - Gmail, Instagram, Stripe
Uses Model Context Protocol for seamless data access
"""

import os
import logging
from typing import Dict, List, Optional, Any
import json
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPGmailIntegration:
    """Gmail MCP Integration - Extract user data from Gmail"""
    
    def __init__(self):
        self.mcp_server_url = os.getenv("MCP_GMAIL_SERVER_URL", "http://localhost:8003/mcp/gmail")
        self.api_key = os.getenv("GMAIL_API_KEY", "")
    
    async def get_user_profile(self, email: str) -> Dict:
        """
        Get user profile data from Gmail using MCP
        Returns: name, date_of_birth, address, phone, etc.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.mcp_server_url}/profile",
                    json={"email": email},
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Gmail profile retrieved for {email}")
                    return {
                        "success": True,
                        "name": data.get("name", ""),
                        "date_of_birth": data.get("date_of_birth"),
                        "address": data.get("address", {}),
                        "phone": data.get("phone", ""),
                        "email": email,
                        "profile_data": data
                    }
                else:
                    logger.warning(f"Gmail MCP returned {response.status_code}")
                    return self._get_fallback_profile(email)
        
        except Exception as e:
            logger.error(f"Gmail MCP integration failed: {e}")
            return self._get_fallback_profile(email)
    
    def _get_fallback_profile(self, email: str) -> Dict:
        """Fallback: Extract basic info from email"""
        return {
            "success": True,
            "email": email,
            "name": email.split("@")[0].replace(".", " ").title(),
            "date_of_birth": None,
            "address": {},
            "phone": "",
            "source": "fallback"
        }


class MCPInstagramIntegration:
    """Instagram MCP Integration - Analyze user interests from Instagram profile"""
    
    def __init__(self):
        self.mcp_server_url = os.getenv("MCP_INSTAGRAM_SERVER_URL", "http://localhost:8004/mcp/instagram")
        self.api_key = os.getenv("INSTAGRAM_API_KEY", "")
    
    async def analyze_profile(self, username: str) -> Dict:
        """
        Analyze Instagram profile to understand user interests
        Returns: interests, activity_types, travel_preferences, lifestyle
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.mcp_server_url}/analyze",
                    json={"username": username},
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Instagram profile analyzed for {username}")
                    return {
                        "success": True,
                        "username": username,
                        "interests": data.get("interests", []),
                        "activity_types": data.get("activity_types", []),
                        "travel_preferences": data.get("travel_preferences", {}),
                        "lifestyle": data.get("lifestyle", "balanced"),
                        "adventure_level": data.get("adventure_level", "moderate"),
                        "posts_analysis": data.get("posts_analysis", {})
                    }
                else:
                    logger.warning(f"Instagram MCP returned {response.status_code}")
                    return self._get_fallback_interests()
        
        except Exception as e:
            logger.error(f"Instagram MCP integration failed: {e}")
            return self._get_fallback_interests()
    
    def _get_fallback_interests(self) -> Dict:
        """Fallback: Default interests"""
        return {
            "success": True,
            "interests": ["travel", "adventure"],
            "activity_types": ["sightseeing", "photography"],
            "travel_preferences": {"style": "balanced"},
            "lifestyle": "balanced",
            "adventure_level": "moderate",
            "source": "fallback"
        }


class MCPStripeIntegration:
    """Stripe MCP Integration - One-click payments"""
    
    def __init__(self):
        self.mcp_server_url = os.getenv("MCP_STRIPE_SERVER_URL", "http://localhost:8005/mcp/stripe")
        self.stripe_api_key = os.getenv("STRIPE_SECRET_KEY", os.getenv("STRIPE_SECRET_KEY_SANDBOX", ""))
    
    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "sgd",
        policy_id: str = None,
        user_email: str = None
    ) -> Dict:
        """
        Create payment intent via Stripe MCP
        Returns: client_secret, payment_intent_id
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.mcp_server_url}/create_intent",
                    json={
                        "amount": int(amount * 100),  # Stripe uses cents
                        "currency": currency.lower(),
                        "policy_id": policy_id,
                        "user_email": user_email,
                        "metadata": {
                            "policy_id": policy_id,
                            "payment_type": "travel_insurance"
                        }
                    },
                    headers={"Authorization": f"Bearer {self.stripe_api_key}"} if self.stripe_api_key else {}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Stripe payment intent created: {data.get('id')}")
                    return {
                        "success": True,
                        "client_secret": data.get("client_secret"),
                        "payment_intent_id": data.get("id"),
                        "amount": amount,
                        "currency": currency
                    }
                else:
                    logger.error(f"Stripe MCP returned {response.status_code}: {response.text}")
                    return {"success": False, "error": f"Stripe API error: {response.status_code}"}
        
        except Exception as e:
            logger.error(f"Stripe MCP integration failed: {e}")
            # Fallback to direct Stripe API
            return await self._direct_stripe_payment(amount, currency, policy_id, user_email)
    
    async def _direct_stripe_payment(
        self,
        amount: float,
        currency: str,
        policy_id: str,
        user_email: str
    ) -> Dict:
        """Fallback: Direct Stripe API call"""
        try:
            import stripe
            stripe.api_key = self.stripe_api_key or os.getenv("STRIPE_SECRET_KEY_SANDBOX", "")
            
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency=currency.lower(),
                metadata={
                    "policy_id": policy_id or "unknown",
                    "user_email": user_email or "unknown"
                }
            )
            
            return {
                "success": True,
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": amount,
                "currency": currency,
                "source": "direct_api"
            }
        except Exception as e:
            logger.error(f"Direct Stripe payment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def confirm_payment(self, payment_intent_id: str) -> Dict:
        """Confirm payment completion"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.mcp_server_url}/confirm",
                    json={"payment_intent_id": payment_intent_id},
                    headers={"Authorization": f"Bearer {self.stripe_api_key}"} if self.stripe_api_key else {}
                )
                
                if response.status_code == 200:
                    return {"success": True, **response.json()}
                else:
                    return {"success": False, "error": f"Payment confirmation failed: {response.status_code}"}
        
        except Exception as e:
            logger.error(f"Payment confirmation failed: {e}")
            return {"success": False, "error": str(e)}


class MCPIntegrations:
    """Main MCP Integration Manager"""
    
    def __init__(self):
        self.gmail = MCPGmailIntegration()
        self.instagram = MCPInstagramIntegration()
        self.stripe = MCPStripeIntegration()
    
    async def get_comprehensive_profile(
        self,
        email: str,
        instagram_username: str = None
    ) -> Dict:
        """
        Get comprehensive user profile combining Gmail and Instagram data
        Determines policy tier based on profile analysis
        """
        try:
            profile = {
                "email": email,
                "policy_tier": "free",  # free, medium, premium
                "profile_complete": False
            }
            
            # Get Gmail data (with fallback)
            try:
                gmail_data = await self.gmail.get_user_profile(email)
                profile.update(gmail_data)
            except Exception as e:
                logger.warning(f"Gmail profile fetch failed: {e}, using fallback")
                # Fallback profile
                profile["name"] = email.split("@")[0].replace(".", " ").title()
                profile["success"] = True
                profile["source"] = "fallback"
            
            # Get Instagram data if provided
            if instagram_username:
                try:
                    # Remove @ if present
                    clean_username = instagram_username.lstrip('@')
                    instagram_data = await self.instagram.analyze_profile(clean_username)
                    profile["instagram"] = instagram_data
                    profile["interests"] = instagram_data.get("interests", [])
                    profile["activity_types"] = instagram_data.get("activity_types", [])
                    profile["adventure_level"] = instagram_data.get("adventure_level", "moderate")
                except Exception as e:
                    logger.warning(f"Instagram profile fetch failed: {e}, continuing without it")
                    profile["instagram"] = None
                    profile["interests"] = []
                    profile["activity_types"] = []
                    profile["adventure_level"] = "moderate"
            else:
                profile["instagram"] = None
                profile["interests"] = []
                profile["activity_types"] = []
                profile["adventure_level"] = "moderate"
            
            # Determine policy tier
            profile["policy_tier"] = self._determine_policy_tier(profile)
            profile["profile_complete"] = bool(profile.get("name") and profile.get("email"))
            
            logger.info(f"✅ Comprehensive profile created: tier={profile['policy_tier']}, name={profile.get('name')}")
            
            return profile
        except Exception as e:
            logger.error(f"Failed to get comprehensive profile: {e}", exc_info=True)
            # Return a basic profile even on error
            return {
                "email": email,
                "name": email.split("@")[0].replace(".", " ").title(),
                "policy_tier": "free",
                "profile_complete": True,
                "success": True,
                "source": "fallback",
                "error": None
            }
    
    def _determine_policy_tier(self, profile: Dict) -> str:
        """
        Determine policy tier based on profile analysis
        Logic: Adventure level, travel frequency, interests complexity
        """
        # Check adventure level
        adventure_level = profile.get("adventure_level", "moderate")
        activity_types = profile.get("activity_types", [])
        interests = profile.get("interests", [])
        
        # Premium indicators
        high_risk_activities = ["skiing", "scuba", "mountaineering", "paragliding", "skydiving", "bungee"]
        has_high_risk = any(act in str(activity_types).lower() for act in high_risk_activities)
        
        if adventure_level == "high" or has_high_risk or len(interests) > 8:
            return "premium"
        elif adventure_level == "moderate" or len(interests) > 4:
            return "medium"
        else:
            return "free"

