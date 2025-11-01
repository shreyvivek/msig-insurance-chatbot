"""
v1 User profile endpoints - Instagram profile fetching
"""
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict
from datetime import datetime
from database import db
from models.user_profile import UserProfile
from services.profile_scraper import ProfileScraper
from services.profile_analyzer import ProfileAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])

profile_scraper = ProfileScraper()
profile_analyzer = ProfileAnalyzer()

@router.post("/fetch-profile")
async def fetch_user_profile(request: Dict):
    """
    Fetch user profile data from Instagram username
    Input: {instagram_username: "username", email: "user@email.com" (optional)}
    Output: {profile_data, adventurous_score, tier_recommendation, analysis}
    """
    instagram_username = request.get("instagram_username", "").strip().lstrip("@")
    email = request.get("email", "").strip()
    
    if not instagram_username:
        raise HTTPException(status_code=400, detail="instagram_username is required")
    
    try:
        # Fetch Instagram profile
        logger.info(f"Fetching Instagram profile for @{instagram_username}")
        instagram_data = await profile_scraper.fetch_instagram_profile(instagram_username)
        
        if instagram_data.get("error"):
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch Instagram profile: {instagram_data.get('error')}"
            )
        
        # Analyze profile
        analysis = await profile_analyzer.analyze_instagram_data(instagram_data)
        
        # Calculate tier
        tier, tier_reason = profile_analyzer.calculate_tier(analysis)
        
        # Create user profile
        profile_data = {
            "instagram_username": instagram_username,
            "email": email if email else None,
            "name": instagram_data.get("full_name"),
            "instagram_bio": instagram_data.get("bio"),
            "instagram_posts_count": instagram_data.get("posts_count", 0),
            "instagram_follower_count": instagram_data.get("follower_count"),
            "instagram_is_private": instagram_data.get("is_private", False),
            "adventurous_score": analysis.get("adventurous_score", 0.0),
            "travel_frequency": analysis.get("travel_frequency", "unknown"),
            "likely_activities": analysis.get("likely_activities", []),
            "detected_interests": analysis.get("detected_interests", []),
            "policy_tier": tier,
            "tier_reason": tier_reason,
            "consent_given": True,
            "consent_timestamp": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Store in MongoDB
        if db.is_connected():
            users_collection = db.get_collection("users")
            # Update or insert
            users_collection.update_one(
                {"instagram_username": instagram_username},
                {"$set": profile_data},
                upsert=True
            )
            logger.info(f"✅ Profile stored for @{instagram_username}")
        
        return {
            "success": True,
            "profile_data": profile_data,
            "analysis": analysis,
            "tier_recommendation": {
                "tier": tier,
                "reason": tier_reason
            },
            "posts_analyzed": len(instagram_data.get("posts_data", [])),
            "is_private": instagram_data.get("is_private", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching profile: {str(e)}")

@router.post("/assign-tier")
async def assign_tier(request: Dict):
    """
    Compute recommended tier based on profile and risk score
    Input: {
        "instagram_username": str,
        "risk_score": float (optional)
    }
    """
    instagram_username = request.get("instagram_username", "").strip().lstrip("@")
    risk_score = request.get("risk_score")
    
    if not instagram_username:
        raise HTTPException(status_code=400, detail="instagram_username is required")
    
    try:
        # Get profile from DB or fetch fresh
        profile_analysis = {}
        if db.is_connected():
            users_collection = db.get_collection("users")
            user = users_collection.find_one({"instagram_username": instagram_username})
            if user:
                profile_analysis = {
                    "adventurous_score": user.get("adventurous_score", 0.0),
                    "travel_frequency": user.get("travel_frequency", "unknown")
                }
        
        # If no profile found, fetch and analyze
        if not profile_analysis:
            instagram_data = await profile_scraper.fetch_instagram_profile(instagram_username)
            profile_analysis = await profile_analyzer.analyze_instagram_data(instagram_data)
        
        # Calculate tier
        tier, reason = profile_analyzer.calculate_tier(profile_analysis, risk_score)
        
        return {
            "tier": tier,
            "reason": reason,
            "adventurous_score": profile_analysis.get("adventurous_score", 0.0),
            "risk_score": risk_score
        }
        
    except Exception as e:
        logger.error(f"Error assigning tier: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error assigning tier: {str(e)}")

