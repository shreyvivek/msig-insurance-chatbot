"""
User Profile Manager - Mock MSIG Database Integration
Handles existing users, profile retrieval, and dynamic data collection
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class UserProfileManager:
    """Manages user profiles with mock MSIG database integration"""
    
    def __init__(self):
        # Mock MSIG database - simulate existing users
        self.mock_database = {
            # Existing user 1 - Has travel history
            "john.doe@example.com": {
                "user_id": "msig_user_001",
                "email": "john.doe@example.com",
                "phone": "+65 9123 4567",
                "firstName": "John",
                "lastName": "Doe",
                "dateOfBirth": "1985-03-15",
                "nationality": "SG",
                "passport": "K12345678",
                "cardId": "S1234567A",
                "preferences": {
                    "preferred_coverage": "comprehensive",
                    "price_sensitivity": "medium",
                    "preferred_destinations": ["Japan", "Thailand", "Australia"]
                },
                "travel_history": [
                    {
                        "destination": "Japan",
                        "date": "2024-01-15",
                        "policy": "TravelEasy",
                        "claim_filed": False
                    },
                    {
                        "destination": "Thailand",
                        "date": "2023-11-20",
                        "policy": "Scootsurance",
                        "claim_filed": False
                    }
                ],
                "insurance_profile": {
                    "risk_level": "low",
                    "loyalty_tier": "silver",
                    "last_purchase_date": "2024-01-10"
                }
            },
            # Existing user 2 - Frequent traveler
            "sarah.chen@example.com": {
                "user_id": "msig_user_002",
                "email": "sarah.chen@example.com",
                "phone": "+65 8765 4321",
                "firstName": "Sarah",
                "lastName": "Chen",
                "dateOfBirth": "1990-07-22",
                "nationality": "SG",
                "passport": "K98765432",
                "cardId": "S9876543B",
                "preferences": {
                    "preferred_coverage": "premium",
                    "price_sensitivity": "low",
                    "preferred_destinations": ["Europe", "USA", "Japan"]
                },
                "travel_history": [
                    {
                        "destination": "Europe",
                        "date": "2024-02-01",
                        "policy": "TravelEasy",
                        "claim_filed": True
                    },
                    {
                        "destination": "USA",
                        "date": "2023-12-10",
                        "policy": "TravelEasy",
                        "claim_filed": False
                    },
                    {
                        "destination": "Japan",
                        "date": "2023-10-05",
                        "policy": "Scootsurance",
                        "claim_filed": False
                    }
                ],
                "insurance_profile": {
                    "risk_level": "medium",
                    "loyalty_tier": "gold",
                    "last_purchase_date": "2024-02-01"
                }
            },
            # Existing user 3 - New user
            "mike.tan@example.com": {
                "user_id": "msig_user_003",
                "email": "mike.tan@example.com",
                "phone": "+65 8123 4567",
                "firstName": "Mike",
                "lastName": "Tan",
                "dateOfBirth": "1992-11-08",
                "nationality": "SG",
                "passport": None,  # Not provided yet
                "cardId": "S7654321C",
                "preferences": {
                    "preferred_coverage": "basic",
                    "price_sensitivity": "high"
                },
                "travel_history": [],
                "insurance_profile": {
                    "risk_level": "unknown",
                    "loyalty_tier": "bronze",
                    "last_purchase_date": None
                }
            }
        }
        
        # In-memory session storage for new users
        self.session_profiles = {}
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Check if user exists in MSIG database"""
        if not email:
            return None
        
        email_lower = email.lower().strip()
        return self.mock_database.get(email_lower)
    
    def get_user_by_phone(self, phone: str) -> Optional[Dict]:
        """Check if user exists by phone number"""
        if not phone:
            return None
        
        # Normalize phone number
        phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")
        
        for user in self.mock_database.values():
            user_phone_clean = user.get("phone", "").replace(" ", "").replace("-", "").replace("+", "")
            if user_phone_clean.endswith(phone_clean[-8:]) or phone_clean.endswith(user_phone_clean[-8:]):
                return user
        
        return None
    
    def get_user_by_session(self, session_id: str) -> Optional[Dict]:
        """Get user profile from session (new users)"""
        return self.session_profiles.get(session_id)
    
    def create_or_update_profile(self, session_id: str, user_data: Dict) -> Dict:
        """Create or update user profile (for new users or partial data)"""
        if session_id not in self.session_profiles:
            self.session_profiles[session_id] = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "is_new_user": True
            }
        
        # Merge new data
        self.session_profiles[session_id].update(user_data)
        self.session_profiles[session_id]["updated_at"] = datetime.now().isoformat()
        
        return self.session_profiles[session_id]
    
    def identify_user(self, email: str = None, phone: str = None, session_id: str = None) -> Dict:
        """
        Try to identify existing user, return profile if found
        Returns: {
            "found": bool,
            "user": Dict or None,
            "needs_data": List[str] - missing fields if partial match
        }
        """
        user = None
        
        # Try email first
        if email:
            user = self.get_user_by_email(email)
            if user:
                return {
                    "found": True,
                    "user": user,
                    "needs_data": [],
                    "identification_method": "email"
                }
        
        # Try phone
        if phone:
            user = self.get_user_by_phone(phone)
            if user:
                return {
                    "found": True,
                    "user": user,
                    "needs_data": [],
                    "identification_method": "phone"
                }
        
        # Check session
        if session_id:
            user = self.get_user_by_session(session_id)
            if user:
                missing = self._check_missing_fields(user)
                return {
                    "found": True,
                    "user": user,
                    "needs_data": missing,
                    "identification_method": "session"
                }
        
        return {
            "found": False,
            "user": None,
            "needs_data": ["email", "phone", "firstName", "lastName", "dateOfBirth"],
            "identification_method": None
        }
    
    def _check_missing_fields(self, user: Dict) -> List[str]:
        """Check what fields are missing from user profile"""
        required_fields = {
            "email": user.get("email"),
            "phone": user.get("phone"),
            "firstName": user.get("firstName"),
            "lastName": user.get("lastName"),
            "dateOfBirth": user.get("dateOfBirth"),
            "nationality": user.get("nationality")
        }
        
        return [field for field, value in required_fields.items() if not value]
    
    def get_travel_context(self, user: Dict) -> Dict:
        """Extract travel-related context from user profile"""
        return {
            "travel_history": user.get("travel_history", []),
            "preferred_destinations": user.get("preferences", {}).get("preferred_destinations", []),
            "preferred_coverage": user.get("preferences", {}).get("preferred_coverage", "comprehensive"),
            "loyalty_tier": user.get("insurance_profile", {}).get("loyalty_tier", "bronze"),
            "risk_level": user.get("insurance_profile", {}).get("risk_level", "unknown"),
            "has_claim_history": any(t.get("claim_filed", False) for t in user.get("travel_history", []))
        }
    
    def enrich_user_data(self, user: Dict, additional_data: Dict) -> Dict:
        """Enrich user profile with additional data from conversations/documents"""
        enriched = user.copy()
        
        # Smart merging - don't overwrite existing data unless new data is more complete
        for key, value in additional_data.items():
            if not enriched.get(key) or (value and len(str(value)) > len(str(enriched.get(key, "")))):
                enriched[key] = value
        
        return enriched

