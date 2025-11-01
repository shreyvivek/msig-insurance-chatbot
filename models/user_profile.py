"""
User profile and chat history data models
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
from datetime import datetime

# Try to import bson, but don't fail if not available
try:
    from bson import ObjectId
    BSON_AVAILABLE = True
except ImportError:
    BSON_AVAILABLE = False
    # Create a dummy ObjectId class
    class ObjectId:
        @staticmethod
        def is_valid(v):
            return isinstance(v, str)

if BSON_AVAILABLE:
    class PyObjectId(ObjectId):
        """Custom ObjectId for Pydantic"""
        @classmethod
        def __get_validators__(cls):
            yield cls.validate
        
        @classmethod
        def validate(cls, v):
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid ObjectId")
            return ObjectId(v)
        
        @classmethod
        def __modify_schema__(cls, field_schema):
            field_schema.update(type="string")
else:
    # Fallback for when bson is not available
    PyObjectId = str

class UserProfile(BaseModel):
    """User profile with Instagram-derived insights"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    instagram_username: str
    name: Optional[str] = None
    
    # Instagram-derived data
    instagram_bio: Optional[str] = None
    instagram_posts_count: int = 0
    instagram_follower_count: Optional[int] = None
    instagram_is_private: bool = False
    
    # Analysis results
    adventurous_score: float = 0.0  # 0-1
    travel_frequency: str = "unknown"  # low, medium, high, unknown
    likely_activities: List[str] = []  # e.g., ["skiing", "hiking", "scuba"]
    detected_interests: List[str] = []  # General interests from posts
    
    # Tier assignment
    policy_tier: str = "free"  # free, medium, premium
    tier_reason: Optional[str] = None
    
    # Metadata
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    consent_given: bool = False
    consent_timestamp: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        if BSON_AVAILABLE:
            json_encoders[ObjectId] = str

class ChatMessage(BaseModel):
    """Single chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()
    metadata: Optional[Dict] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ChatSession(BaseModel):
    """Chat session with history"""
    session_id: str
    user_id: Optional[str] = None
    messages: List[ChatMessage] = []
    summary: Optional[str] = None
    created_at: datetime = datetime.now()
    archived_at: Optional[datetime] = None
    language: str = "en"  # Selected language
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

