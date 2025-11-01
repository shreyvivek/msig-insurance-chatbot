# WanderSure Advanced Personalization - Implementation Plan

## Overview
Comprehensive implementation plan for 8 major features: destination-first itinerary analysis, quantitative policy comparison, multilingual support, Gmail/Instagram profile fetching (web scraping), Stripe MCP payments, simplified policy wording, empathetic responses, and chat history management.

## Architecture Decisions
- **API Versioning**: Add `/v1/` endpoints alongside existing `/api/` endpoints (backward compatible)
- **Database**: Add MongoDB for persistent storage (user profiles, chat history, claims cache)
- **Claims Source**: Use existing PostgreSQL RDS + parse PDF for enrichment
- **Profile Data**: Users provide Gmail email and Instagram username; system scrapes/fetches public data from web for any user

## Prerequisites & Environment Variables

### Required Environment Variables (`.env`)
```bash
# LLM/AI
GROQ_API_KEY=gsk_... (or OPENAI_API_KEY)
GROQ_MODEL=llama-3.3-70b-versatile

# MCP Configuration
MCP_API_KEY=... (if using MCP for LLM proxy)
MCP_TOOL_CONFIG=... (JSON config for MCP tools)

# Stripe Sandbox
STRIPE_TEST_SECRET=sk_test_...
STRIPE_TEST_PUBLISHABLE=pk_test_...
STRIPE_WEBHOOK_SECRET_TEST=whsec_...

# Web Scraping / Data Fetching (for Gmail/Instagram public data)
# No OAuth required - users provide their email/username, system fetches public data
SCRAPING_API_KEY=... (optional, for services like ScraperAPI)
PROXY_ENABLED=false (optional, for scraping)

# MongoDB
MONGO_URI=mongodb://localhost:27017/wandersure (or Atlas URI)

# Claims Database
CLAIMS_DB_PATH=./Claims_Data_DB.pdf

# Voice Services
TTS_API_KEY=... (optional, uses OpenAI if available)
STT_API_KEY=... (optional, uses OpenAI if available)

# Email
EMAIL_SENDER=noreply@wandersure.com

# AWS (if using S3)
S3_BUCKET=wandersure-data
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-southeast-1

# GitHub (for PR)
GIT_REPO_URL=https://github.com/user/msig-insurance-chatbot
GITHUB_TOKEN=...
```

## Implementation Phases

### Phase 1: Database & Infrastructure Setup

#### 1.1 MongoDB Integration
**File**: `database.py` (new)
```python
"""
MongoDB connection and models
"""
import os
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/wandersure")
        self.client = MongoClient(mongo_uri)
        self.db = self.client.wandersure
        
        # Collections
        self.users = self.db.users
        self.chat_history = self.db.chat_history
        self.claims_cache = self.db.claims_cache
        self.consent_records = self.db.consent_records
        
        # Indexes
        self._create_indexes()
    
    def _create_indexes(self):
        self.users.create_index("email", unique=True)
        self.chat_history.create_index([("user_id", 1), ("created_at", -1)])
        self.claims_cache.create_index([("destination", 1), ("updated_at", -1)])
```

**File**: `models/user_profile.py` (new)
```python
"""
User profile data models with encryption support
"""
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class UserProfile(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    date_of_birth: Optional[str] = None  # YYYY-MM-DD
    phone: Optional[str] = None
    address: Optional[Dict] = None
    nationality: Optional[str] = None
    
    # Instagram-derived
    adventurous_score: float = 0.0  # 0-1
    travel_frequency: str = "unknown"  # low, medium, high
    likely_activities: List[str] = []
    
    # Tier assignment
    policy_tier: str = "free"  # free, medium, premium
    tier_reason: Optional[str] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    consent_records: List[str] = []  # consent record IDs
```

**File**: `models/chat_history.py` (new)
```python
"""
Chat history data models
"""
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # user or assistant
    content: str
    timestamp: datetime
    metadata: Optional[Dict] = None

class ChatSession(BaseModel):
    session_id: str
    user_id: str
    messages: List[ChatMessage]
    summary: Optional[str] = None
    created_at: datetime
    archived_at: Optional[datetime] = None
```

#### 1.2 Update Requirements
**File**: `requirements.txt` (modify)
```python
# Add to existing requirements:
pymongo>=4.6.0
pymongo-encryption>=2.0.0  # For field-level encryption
beautifulsoup4>=4.12.0  # Web scraping
selenium>=4.15.0  # For dynamic content scraping
instaloader>=4.10.0  # Instagram scraping
email-validator>=2.1.0  # Email validation
python-social-media-scraper>=1.0.0  # Social media data fetching
camelot-py[cv]>=0.11.0  # PDF table extraction
tabula-py>=2.5.1  # Alternative PDF extraction
pydantic>=2.5.0
python-multipart>=0.0.6
```

### Phase 2: Claims Database Enhancement

#### 2.1 Claims Loader Service
**File**: `services/claims_loader.py` (new)
```python
"""
Loads and processes Claims_Data_DB.pdf into structured MongoDB collection
"""
import os
import logging
from pathlib import Path
import pandas as pd
import pdfplumber
from typing import Dict, List
from datetime import datetime
from database import Database

logger = logging.getLogger(__name__)

class ClaimsLoader:
    def __init__(self):
        self.db = Database()
        self.pdf_path = os.getenv("CLAIMS_DB_PATH", "./Claims_Data_DB.pdf")
    
    async def load_claims_from_pdf(self):
        """Extract claims data from PDF and store in MongoDB"""
        # Implementation:
        # 1. Use pdfplumber to extract tables
        # 2. Normalize destination names
        # 3. Aggregate by destination + activity
        # 4. Calculate: claim_count, avg_amount, median_amount, seasonality
        # 5. Store in MongoDB claims_cache collection
        pass
    
    def _normalize_destination(self, dest: str) -> str:
        """Normalize destination names"""
        # Map: "Tokyo" -> "Japan", "Bangkok" -> "Thailand", etc.
        pass
```

#### 2.2 Risk Scorer Service
**File**: `services/risk_scorer.py` (new)
```python
"""
Combines Claims DB signals and user profile for risk scoring
"""
import math
from typing import Dict
from database import Database
from claims_database import ClaimsDatabase

class RiskScorer:
    def __init__(self):
        self.db = Database()
        self.claims_db = ClaimsDatabase()
        
        # Activity risk weights
        self.activity_weights = {
            "skiing": 1.8,
            "scuba": 2.0,
            "hiking": 1.3,
            "mountaineering": 2.2,
            "bungee": 1.9,
            "paragliding": 2.1
        }
    
    def predict(self, trip_features: Dict, user_profile: Dict = None) -> Dict:
        """
        Calculate risk score and recommended coverage
        Inputs: destination, start_date, end_date, activities, age, adventurous_score, trip_duration_days
        Returns: {risk_prob, category, recommended_medical, recommended_coverage_upgrades}
        """
        # Implementation per algorithm specified
        pass
    
    def _normalize_claim_count(self, count: int, max_count: int = 1000) -> float:
        """Normalize claim count to 0-1 scale"""
        return min(count / max_count, 1.0)
    
    def _sigmoid(self, x: float) -> float:
        """Sigmoid function for probability"""
        return 1 / (1 + math.exp(-x))
```

### Phase 3: Policy Comparison Enhancement

#### 3.1 Policy Comparator Service
**File**: `services/policy_comparator.py` (new)
```python
"""
Quantitative policy comparison for specific scenarios
"""
from typing import Dict, List
from policy_intelligence import PolicyIntelligence
from groq import Groq
import json
import os

class PolicyComparator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.policy_intel = PolicyIntelligence()
    
    async def compare(self, policyA_id: str, policyB_id: str, scenario: Dict) -> Dict:
        """
        Compare two policies quantitatively
        Returns: {benefit_comparison_table, composite_scores, best_policy, justification, citations}
        """
        # 1. Get normalized policy data
        # 2. Extract relevant benefits for scenario
        # 3. Calculate scores per benefit with relevance weights
        # 4. Generate composite scores
        # 5. Use LLM to generate justification with citations
        pass
    
    def _calculate_benefit_score(self, value: float, relevance_weight: float, normalized_max: float) -> float:
        """Calculate normalized benefit score"""
        normalized_value = value / normalized_max if normalized_max > 0 else 0
        return normalized_value * relevance_weight
```

#### 3.2 Enhanced Policy Parser
**File**: `services/policy_parser.py` (new - enhance existing policy_intelligence.py)
```python
"""
Enhanced policy parsing with granular benefit extraction
"""
# Add methods to PolicyIntelligence class:
# - extract_benefit_limits()
# - extract_activity_exclusions()
# - extract_waiting_periods()
# - extract_claim_documentation_timeline()
# - convert_currency_to_sgd()
```

### Phase 4: API Endpoints Implementation

#### 4.1 Create v1 Router
**File**: `routers/v1/__init__.py` (new)
```python
"""
v1 API router
"""
from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["v1"])

# Import all v1 endpoints
from .itinerary import router as itinerary_router
from .policy import router as policy_router
from .user import router as user_router
from .chat import router as chat_router
from .payment import router as payment_router
from .translate import router as translate_router
from .voice import router as voice_router

router.include_router(itinerary_router)
router.include_router(policy_router)
router.include_router(user_router)
router.include_router(chat_router)
router.include_router(payment_router)
router.include_router(translate_router)
router.include_router(voice_router)
```

#### 4.2 Itinerary Endpoints
**File**: `routers/v1/itinerary.py` (new)
```python
"""
v1 Itinerary endpoints
"""
from fastapi import APIRouter, HTTPException
from services.risk_scorer import RiskScorer
from document_intelligence import DocumentIntelligence

router = APIRouter(prefix="/itinerary", tags=["itinerary"])

@router.post("/parse")
async def parse_itinerary(request: dict):
    """Parse itinerary with destination prioritization"""
    # Enhanced version of /api/extract
    # Ensure destination is extracted FIRST
    pass

@router.post("/analyze")
async def analyze_itinerary(request: dict):
    """Destination-centric risk analysis using Claims DB"""
    # 1. Extract destination (priority)
    # 2. Call risk_scorer.predict()
    # 3. Return risk summary, recommended upgrades, top claim reasons
    pass
```

#### 4.3 Policy Endpoints
**File**: `routers/v1/policy.py` (new)
```python
"""
v1 Policy comparison endpoints
"""
from fastapi import APIRouter
from services.policy_comparator import PolicyComparator

router = APIRouter(prefix="/policy", tags=["policy"])

@router.post("/compare-quant")
async def compare_policies_quantitative(request: dict):
    """Quantitative policy comparison for scenario"""
    # Input: {policy_ids: [A,B], scenario: {destination, activities, age, duration}}
    # Output: {benefit_comparison_table, composite_scores, best_policy, justification}
    pass
```

#### 4.4 User Profile Endpoints
**File**: `routers/v1/user.py` (new)
```python
"""
v1 User profile endpoints - fetch data from Gmail/Instagram
"""
from fastapi import APIRouter, HTTPException
from services.profile_analyzer import ProfileAnalyzer
from services.profile_scraper import ProfileScraper

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/fetch-profile")
async def fetch_user_profile(request: dict):
    """
    Fetch user profile data from Gmail email and Instagram username
    Input: {email: "user@gmail.com", instagram_username: "username"}
    Output: {profile_data, adventurous_score, tier_recommendation}
    """
    # 1. Validate email format
    # 2. Fetch public Gmail profile data (name, DOB if publicly available)
    # 3. Scrape Instagram public posts for hashtags/interests
    # 4. Analyze and calculate adventurous_score
    # 5. Store in MongoDB
    # 6. Return profile with tier recommendation
    pass

@router.post("/assign-tier")
async def assign_tier(request: dict):
    """Compute recommended tier based on profile and risk"""
    # Uses profile_analyzer + risk_scorer
    pass
```

#### 4.5 Chat Endpoints
**File**: `routers/v1/chat.py` (new)
```python
"""
v1 Chat endpoints
"""
from fastapi import APIRouter
from database import Database
from services.chat_manager import ChatManager

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/new")
async def create_new_chat(request: dict):
    """Create new chat session, archive old one"""
    # 1. Archive current session to MongoDB
    # 2. Generate summary via LLM
    # 3. Create new session_id
    # 4. Return new session_id
    pass

@router.get("/history/{user_id}")
async def get_chat_history(user_id: str):
    """List saved chat sessions"""
    pass

@router.post("")  # /v1/chat
async def chat(request: dict):
    """Enhanced chat endpoint with full context"""
    # Include: user_profile, itinerary, claims_risk, selected_language, voice_preference, tier
    pass
```

#### 4.6 Payment Endpoints
**File**: `routers/v1/payment.py` (new)
```python
"""
v1 Payment endpoints with MCP integration
"""
from fastapi import APIRouter
from services.payment_mcp import PaymentMCP

router = APIRouter(prefix="/payment", tags=["payment"])

@router.post("/stripe-mcp")
async def stripe_mcp_payment(request: dict):
    """MCP-based Stripe sandbox payment (single-click)"""
    # 1. Create Stripe Checkout session via MCP
    # 2. If sandbox + auto_complete=true, trigger webhook simulation
    # 3. Return payment_url or immediate success
    pass
```

#### 4.7 Translation & Voice Endpoints
**File**: `routers/v1/translate.py` (new)
```python
"""Translation endpoint"""
from fastapi import APIRouter
from multilingual_handler import MultilingualHandler

router = APIRouter(prefix="/translate", tags=["translate"])

@router.post("")
async def translate_text(request: dict):
    """Translate text with cultural context"""
    pass
```

**File**: `routers/v1/voice.py` (new)
```python
"""Voice TTS/STT endpoints"""
from fastapi import APIRouter
from services.voice_service import VoiceService

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/tts")
async def text_to_speech(request: dict):
    """Convert text to speech"""
    pass

@router.post("/stt")
async def speech_to_text(request: dict):
    """Convert speech to text"""
    pass
```

#### 4.8 Update Main Server
**File**: `run_server.py` (modify)
```python
# Add after existing app initialization:
from routers.v1 import router as v1_router
app.include_router(v1_router)

# Keep all existing /api endpoints for backward compatibility
```

### Phase 5: Services Implementation

#### 5.1 Profile Analyzer Service
**File**: `services/profile_analyzer.py` (new)
```python
"""
Analyzes scraped Gmail and Instagram data for personalization
Works with data from ProfileScraper for ANY user
"""
from typing import Dict, List
from groq import Groq
import os
from datetime import datetime

class ProfileAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Adventure-related keywords for scoring
        self.adventure_keywords = [
            "skiing", "ski", "snowboarding", "scuba", "diving", "hiking", "trekking",
            "mountaineering", "climbing", "bungee", "skydiving", "paragliding",
            "rafting", "surfing", "adventure", "travel", "explore", "wanderlust"
        ]
    
    async def analyze_scraped_data(self, gmail_data: Dict, instagram_data: Dict) -> Dict:
        """
        Analyze scraped Gmail and Instagram data
        Returns: {adventurous_score, travel_frequency, likely_activities, age (if DOB available)}
        """
        # 1. Calculate age from DOB if available in gmail_data
        age = None
        if gmail_data.get("date_of_birth"):
            try:
                dob = datetime.strptime(gmail_data["date_of_birth"], "%Y-%m-%d")
                age = (datetime.now() - dob).days // 365
            except:
                pass
        
        # 2. Analyze Instagram posts for adventure indicators
        instagram_analysis = await self._analyze_instagram_posts(instagram_data.get("posts_data", []))
        
        # 3. Combine Gmail and Instagram insights
        return {
            "age": age,
            "adventurous_score": instagram_analysis["adventurous_score"],
            "travel_frequency": instagram_analysis["travel_frequency"],
            "likely_activities": instagram_analysis["likely_activities"],
            "gmail_name": gmail_data.get("name"),
            "instagram_bio": instagram_data.get("bio")
        }
    
    async def _analyze_instagram_posts(self, posts: List[Dict]) -> Dict:
        """Extract adventurous_score, travel_frequency, likely_activities from Instagram posts"""
        if not posts:
            return {
                "adventurous_score": 0.0,
                "travel_frequency": "unknown",
                "likely_activities": []
            }
        
        # Count adventure-related hashtags across all posts
        adventure_count = 0
        travel_count = 0
        activity_keywords_found = set()
        
        for post in posts:
            caption = (post.get("caption") or "").lower()
            hashtags = [h.lower() for h in post.get("hashtags", [])]
            
            # Check for adventure keywords
            for keyword in self.adventure_keywords:
                if keyword in caption or keyword in hashtags:
                    adventure_count += 1
                    activity_keywords_found.add(keyword)
            
            # Check for travel indicators
            if any(word in caption or word in hashtags for word in ["travel", "trip", "vacation", "explore", "wanderlust"]):
                travel_count += 1
        
        # Calculate adventurous_score (0-1) based on percentage of posts with adventure content
        total_posts = len(posts)
        adventurous_score = min(adventure_count / max(total_posts, 1), 1.0) if total_posts > 0 else 0.0
        
        # Estimate travel frequency
        travel_frequency = "high" if travel_count > total_posts * 0.5 else \
                          "medium" if travel_count > total_posts * 0.2 else \
                          "low" if travel_count > 0 else "unknown"
        
        # Extract likely activities
        likely_activities = list(activity_keywords_found)[:10]  # Top 10
        
        return {
            "adventurous_score": round(adventurous_score, 2),
            "travel_frequency": travel_frequency,
            "likely_activities": likely_activities
        }
    
    def calculate_tier(self, profile_analysis: Dict, risk_score: float) -> str:
        """
        Calculate policy tier: free, medium, premium
        Uses rule-based logic with profile analysis and risk score
        """
        adventurous_score = profile_analysis.get("adventurous_score", 0.0)
        age = profile_analysis.get("age")
        dest_risk_high = risk_score > 0.7 if isinstance(risk_score, float) else False
        
        # Premium tier indicators
        if adventurous_score > 0.7 or (age and age > 65) or dest_risk_high:
            return "premium"
        # Medium tier indicators
        elif adventurous_score > 0.4 or risk_score > 0.4:
            return "medium"
        else:
            return "free"
```

#### 5.2 Profile Scraper Service
**File**: `services/profile_scraper.py` (new)
```python
"""
Web scraping service to fetch public data from Gmail/Instagram
Works for ANY user who provides their email/username
"""
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import instaloader
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ProfileScraper:
    def __init__(self):
        self.scraping_api_key = os.getenv("SCRAPING_API_KEY")
        self.instaloader = instaloader.Instaloader()
    
    async def fetch_gmail_profile(self, email: str) -> Dict:
        """
        Fetch public Gmail profile data
        Returns: {name, date_of_birth (if public), locale, profile_picture_url}
        """
        # 1. Try to fetch from Google Profiles API (public data only)
        # 2. Use web scraping as fallback for publicly available info
        # 3. Extract name from email if profile not accessible
        # Note: Only fetches PUBLICLY available data, respects privacy
        pass
    
    async def fetch_instagram_profile(self, username: str) -> Dict:
        """
        Scrape Instagram public profile and posts
        Returns: {bio, posts_data: [{caption, hashtags, media_type}], follower_count (if public)}
        """
        try:
            # Use instaloader to fetch public data
            profile = instaloader.Profile.from_username(self.instaloader.context, username)
            
            # Fetch recent public posts (last 20-30)
            posts_data = []
            for post in profile.get_posts():
                if len(posts_data) >= 30:  # Limit to recent 30 posts
                    break
                
                posts_data.append({
                    "caption": post.caption or "",
                    "hashtags": self._extract_hashtags(post.caption or ""),
                    "media_type": "photo" if post.is_video == False else "video",
                    "likes": post.likes,
                    "timestamp": post.date.isoformat()
                })
            
            return {
                "username": username,
                "bio": profile.biography,
                "posts_count": profile.mediacount,
                "posts_data": posts_data,
                "follower_count": profile.followers if profile.is_private == False else None
            }
        except Exception as e:
            logger.warning(f"Instagram scraping failed for {username}: {e}")
            # Fallback: Return basic structure
            return {
                "username": username,
                "posts_data": [],
                "error": "Unable to fetch public profile"
            }
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        return re.findall(r'#(\w+)', text)
```

#### 5.3 Plain Language Service
**File**: `services/plain_language.py` (new)
```python
"""
Generates human-friendly policy explanations
"""
from groq import Groq
import os

class PlainLanguageService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    async def simplify_clause(self, clause_text: str, benefit_type: str, language: str = "en") -> Dict:
        """
        Simplify policy clause for general travelers
        Returns: {simplified_text, exclusions_list, action_steps}
        """
        prompt = f"""Simplify this insurance clause for a general traveler in 2-3 sentences.
Highlight exclusions in bullet points, and provide one action step.

Clause: {clause_text}
Benefit Type: {benefit_type}

Output format:
- Simplified explanation (2-3 sentences)
- Exclusions (bullet points)
- Action step (one sentence)"""
        
        # Call LLM and parse response
        pass
```

#### 5.4 Sentiment Service
**File**: `services/sentiment_service.py` (new)
```python
"""
Sentiment analysis for empathetic responses
"""
from groq import Groq
import os

class SentimentService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment
        Returns: {tone: 'confused'|'positive'|'neutral'|'angry', empathy_level: 0-1}
        """
        pass
```

#### 5.5 Chat Manager Service
**File**: `services/chat_manager.py` (new)
```python
"""
Enhanced conversation management with full context
"""
from typing import Dict
from conversation_handler import ConversationHandler
from services.sentiment_service import SentimentService

class ChatManager:
    def __init__(self):
        self.conversation = ConversationHandler()
        self.sentiment = SentimentService()
    
    async def handle_message(self, message: str, context: Dict) -> Dict:
        """
        Handle chat message with full context
        Context includes: {user_profile, itinerary, claims_risk, selected_language, voice_preference, tier, last_actions, sentiment_state}
        """
        # 1. Analyze sentiment
        # 2. Build enriched context
        # 3. Call conversation handler with personalized prompt
        # 4. Store unresolved questions
        pass
```

#### 5.6 Voice Service
**File**: `services/voice_service.py` (new)
```python
"""
Voice TTS/STT service
"""
import os
from typing import Optional

class VoiceService:
    def __init__(self):
        self.tts_api_key = os.getenv("TTS_API_KEY")
        self.stt_api_key = os.getenv("STT_API_KEY")
    
    async def text_to_speech(self, text: str, language: str) -> bytes:
        """Convert text to speech audio"""
        # Use OpenAI TTS or Google Cloud TTS
        pass
    
    async def speech_to_text(self, audio_data: bytes, language: str) -> str:
        """Convert speech to text"""
        # Use OpenAI Whisper or Google Cloud STT
        pass
```

#### 5.7 Payment MCP Service
**File**: `services/payment_mcp.py` (new)
```python
"""
MCP-based Stripe payment service
"""
import stripe
import os
from typing import Dict

class PaymentMCP:
    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_TEST_SECRET")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET_TEST")
    
    async def create_checkout_session(self, amount: float, currency: str, policy_id: str, auto_complete: bool = False) -> Dict:
        """Create Stripe checkout session, optionally auto-complete for sandbox"""
        # 1. Create checkout session
        # 2. If sandbox + auto_complete, trigger test webhook
        # 3. Return session URL or success status
        pass
```

### Phase 6: Frontend Implementation

#### 6.1 Language Switcher Component
**File**: `frontend/components/LanguageSwitcher.tsx` (new)
```typescript
"use client"
import { useState } from 'react'
import { Globe } from 'lucide-react'

const languages = [
  { code: 'en', name: 'English', native: 'English', emoji: '🇬🇧' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்', emoji: '🇮🇳' },
  { code: 'zh', name: 'Chinese', native: '中文 (简体)', emoji: '🇨🇳' },
  { code: 'ms', name: 'Malay', native: 'Bahasa Melayu', emoji: '🇲🇾' }
]

export default function LanguageSwitcher({ currentLang, onLanguageChange }) {
  // Dropdown with language selection
  // Stores in session/localStorage
  // Triggers translation of UI strings
}
```

#### 6.2 Profile Connect Component
**File**: `frontend/components/ProfileConnect.tsx` (new)
```typescript
"use client"
import { useState } from 'react'
import { Mail, Instagram } from 'lucide-react'

export default function ProfileConnect({ onConnected }) {
  const [email, setEmail] = useState('')
  const [instagramUsername, setInstagramUsername] = useState('')
  
  // Input form for:
  // - Gmail email address
  // - Instagram username
  // Consent modal explaining what data will be fetched (public data only)
  // "Fetch Profile" button
  // Profile preview after fetching
  // Shows: name, age (if available), adventurous_score, tier recommendation
  
  const handleFetch = async () => {
    // Call /v1/user/fetch-profile with email and instagram_username
    // Show loading state
    // Display fetched profile data
    // Allow user to confirm and use this data
  }
}
```

#### 6.3 Itinerary Focus Panel
**File**: `frontend/components/ItineraryFocusPanel.tsx` (new)
```typescript
"use client"
export default function ItineraryFocusPanel({ itinerary, riskAnalysis }) {
  // Destination highlighted
  // "Why we care" box with Claims DB signals
  // Recommended extra coverage with toggle to apply
}
```

#### 6.4 Enhanced Policy Card
**File**: `frontend/components/PolicyCard.tsx` (modify existing)
```typescript
// Add toggle between "Simplified" and "Original"
// Show expandable sections
// Inline examples
// Translation support
```

#### 6.5 Voice Controls
**File**: `frontend/components/VoiceControls.tsx` (new)
```typescript
"use client"
export default function VoiceControls({ onRecord, onPlay, language }) {
  // Record button (STT)
  // Play button (TTS)
  // Language-aware voice selection
}
```

#### 6.6 Stripe MCP Button
**File**: `frontend/components/StripeMCPButton.tsx` (new)
```typescript
"use client"
export default function StripeMCPButton({ quote, onSuccess }) {
  // Single "Buy with Stripe" button
  // Calls /v1/payment/stripe-mcp
  // Handles sandbox auto-complete
  // Shows immediate policy confirmation
}
```

#### 6.7 New Chat Button
**File**: `frontend/components/NewChatButton.tsx` (new)
```typescript
"use client"
export default function NewChatButton({ onNewChat }) {
  // Button in top-right
  // Confirmation modal
  // Calls /v1/chat/new
  // Saves current chat to history
}
```

#### 6.8 Localization Hook
**File**: `frontend/hooks/useLocalization.ts` (new)
```typescript
import { useState, useEffect } from 'react'

export function useLocalization() {
  const [language, setLanguage] = useState('en')
  const translations = require('../locales')
  
  const t = (key: string) => {
    return translations[language][key] || key
  }
  
  return { language, setLanguage, t }
}
```

#### 6.9 Translation Files
**File**: `frontend/locales/en.json` (new)
```json
{
  "chat.new": "New Chat",
  "language.select": "Select Language",
  "profile.connect": "Connect Profile",
  ...
}
```

**File**: `frontend/locales/ta.json`, `zh.json`, `ms.json` (new)
```json
// Tamil, Chinese, Malay translations
```

#### 6.10 Update Main Page
**File**: `frontend/app/page.tsx` (modify)
```typescript
// Add:
// - LanguageSwitcher in header
// - ProfileConnect onboarding (users enter email/Instagram username)
// - NewChatButton
// - ItineraryFocusPanel when itinerary uploaded
// - Enhanced PolicyCard with simplified view
// - VoiceControls on messages
// - StripeMCPButton in quote cards
// - Call /v1/chat instead of /api/ask
```

### Phase 7: Background Workers

#### 7.1 Claims Loader Worker
**File**: `workers/claims_loader_worker.py` (new)
```python
"""
Background worker to process Claims PDF periodically
"""
# Run via cron or scheduler
# Updates MongoDB claims_cache collection
```

#### 7.2 Policy Enricher Worker
**File**: `workers/policy_enricher_worker.py` (new)
```python
"""
Re-run policy normalization with granular parsing
"""
# Extract sub-limits, per-activity clauses
# Store in enhanced format
```

### Phase 8: Testing

#### 8.1 Unit Tests
**File**: `tests/test_risk_scorer.py` (new)
```python
def test_risk_scorer_japan_skiing():
    """Test: Japan + skiing = high risk"""
    scorer = RiskScorer()
    risk = scorer.predict({
        "destination": "Japan",
        "activities": ["skiing"],
        "age": 32,
        "adventurous_score": 0.8
    })
    assert risk["category"] in ["medium", "high"]
    assert risk["recommended_medical"] >= 30000
```

**File**: `tests/test_policy_comparator.py` (new)
```python
def test_policy_comparator_skiing():
    """Test: Comparator chooses policy with higher medical for skiing"""
    comparator = PolicyComparator()
    result = await comparator.compare("PolicyA", "PolicyB", {
        "destination": "Japan",
        "activities": ["skiing"]
    })
    assert result["best_policy"] in result["composite_scores"]
    assert len(result["citations"]) > 0
```

**File**: `tests/test_profile_analyzer.py` (new)
```python
def test_profile_analyzer_instagram():
    """Test: Adventure posts increase adventurous_score"""
    analyzer = ProfileAnalyzer()
    posts = [{"caption": "#skiing #adventure #travel"}]
    result = await analyzer.analyze_instagram_posts(posts)
    assert result["adventurous_score"] > 0.5
```

#### 8.2 Integration Tests
**File**: `tests/integration/test_profile_fetching.py` (new)
```python
"""Test profile fetching from Gmail/Instagram with mocked scraping"""
def test_fetch_gmail_profile():
    """Test: Gmail profile fetching returns name"""
    pass

def test_fetch_instagram_profile():
    """Test: Instagram profile scraping returns posts and hashtags"""
    pass
```

**File**: `tests/integration/test_payment_flow.py` (new)
```python
"""Test: Itinerary -> analyze -> quote -> compare -> payment end-to-end"""
```

#### 8.3 Frontend Tests
**File**: `frontend/cypress/e2e/multilingual.cy.ts` (new)
```typescript
describe('Multilingual Support', () => {
  it('switches to Tamil and receives Tamil response', () => {
    // Test language switcher
    // Verify TTS works
  })
})
```

### Phase 9: Documentation

#### 9.1 Deployment Guide
**File**: `DEPLOYMENT.md` (new)
```markdown
# Deployment Guide

## Environment Setup
1. Set all required environment variables
2. MongoDB setup (local or Atlas)
3. Install web scraping libraries (beautifulsoup4, selenium, instaloader)
4. Stripe test account setup

## Web Scraping Setup (No OAuth Required)
### Installation
1. Install Python scraping libraries:
   ```bash
   pip install beautifulsoup4 selenium instaloader email-validator
   ```

2. Install ChromeDriver (for Selenium):
   ```bash
   brew install chromedriver  # macOS
   ```

3. Optional: Set up Scraping API service for production:
   ```bash
   SCRAPING_API_KEY=your_key  # In .env
   ```

### How It Works
- Users provide their Gmail email and Instagram username during onboarding
- System fetches PUBLIC data from these profiles
- No OAuth app registration needed - works for any user

## MongoDB Setup
# Local
mongod --dbpath ./data/db

# Atlas
# Use connection string in MONGO_URI

## Stripe Webhook Setup
# Use Stripe CLI for local testing
stripe listen --forward-to http://localhost:8001/webhooks/stripe
```

#### 9.2 Demo Runbook
**File**: `DEMO_RUNBOOK.md` (new)
```markdown
# Demo Runbook

## Demo Flow 1: Japan Skiing Trip
1. Upload itinerary for Japan + skiing
2. Verify destination-first analysis shows claims data
3. User provides email and Instagram username (e.g., "adventurer123")
4. System fetches Instagram public posts with #skiing #travel hashtags
5. Verify adventurous_score calculated and tier upgraded to premium
6. Compare policies for skiing scenario
7. Verify quantitative comparison shows higher medical coverage
8. Complete payment via Stripe sandbox
9. Verify immediate confirmation

## Demo Flow 2: Multilingual
1. Switch language to Tamil
2. Ask question in Tamil
3. Verify response in Tamil
4. Test TTS audio in Tamil
```

### Phase 10: Migration & Data Setup

#### 10.1 Claims PDF Processing Script
**File**: `scripts/load_claims_from_pdf.py` (new)
```python
"""
One-time script to load Claims PDF into MongoDB
Run: python scripts/load_claims_from_pdf.py
"""
```

#### 10.2 User Profile Migration
**File**: `scripts/migrate_profiles_to_mongodb.py` (new)
```python
"""
Migrate existing in-memory profiles to MongoDB
"""
```

## Implementation Checklist

### Backend
- [ ] MongoDB integration (database.py)
- [ ] Claims loader service
- [ ] Risk scorer service
- [ ] Policy comparator service
- [ ] Profile analyzer service
- [ ] Profile scraper service
- [ ] Plain language service
- [ ] Sentiment service
- [ ] Chat manager service
- [ ] Voice service
- [ ] Payment MCP service
- [ ] All v1 API endpoints
- [ ] Background workers

### Frontend
- [ ] Language switcher component
- [ ] Profile connect component (email/Instagram username input)
- [ ] Itinerary focus panel
- [ ] Enhanced policy card
- [ ] Voice controls
- [ ] Stripe MCP button
- [ ] New chat button
- [ ] Localization hook and files
- [ ] Update main page with all components

### Testing
- [ ] Unit tests for all services
- [ ] Integration tests for profile fetching
- [ ] Integration tests for payment flow
- [ ] Frontend E2E tests
- [ ] Manual acceptance tests

### Documentation
- [ ] DEPLOYMENT.md
- [ ] DEMO_RUNBOOK.md
- [ ] Update README.md
- [ ] API documentation
- [ ] Environment variable reference

### Security & Privacy
- [ ] Consent management system
- [ ] Data encryption at rest
- [ ] PII redaction in logs
- [ ] Scraped profile data secure storage (encrypted)
- [ ] Environment variable validation

## Acceptance Criteria

1. ✅ Destination-centric itinerary analysis works
2. ✅ Quantitative policy comparison for skiing scenario
3. ✅ Language switcher works for all 4 languages
4. ✅ Voice TTS/STT works in all languages
5. ✅ Gmail/Instagram profile fetching (users provide email/username, system scrapes public data) with tier assignment
6. ✅ Stripe sandbox auto-completes payment
7. ✅ Simplified policy wording displayed
8. ✅ Empathetic, personalized responses
9. ✅ New chat saves to history
10. ✅ All tests passing

## Branch & PR Strategy

```bash
# Create feature branch
git checkout -b feature/wandersure-advanced-personalization

# Work in logical commits:
git commit -m "feat: Add MongoDB integration and user profile models"
git commit -m "feat: Implement risk scorer service with Claims DB"
git commit -m "feat: Add quantitative policy comparator"
git commit -m "feat: Implement Gmail/Instagram profile fetching via web scraping"
git commit -m "feat: Add multilingual UI and voice support"
git commit -m "feat: Implement Stripe MCP single-click payment"
git commit -m "feat: Add simplified policy wording service"
git commit -m "feat: Enhance chat with empathy and personalization"
git commit -m "feat: Add new chat with history management"
git commit -m "test: Add comprehensive test suite"
git commit -m "docs: Add deployment guide and demo runbook"

# Create PR
gh pr create --title "Advanced Personalization Features" --body "..."
```

## Timeline Estimate

- Phase 1-2 (Database & Claims): 2 days
- Phase 3 (Policy Comparison): 1 day
- Phase 4 (API Endpoints): 2 days
- Phase 5 (Services): 3 days
- Phase 6 (Frontend): 3 days
- Phase 7 (Workers): 1 day
- Phase 8 (Testing): 2 days
- Phase 9-10 (Docs & Migration): 1 day

**Total: ~15 days**

## Risk Mitigation

1. **Profile Scraping Rate Limits**: Implement caching and rate limiting, use Scraping API for production
2. **PDF Parsing Issues**: Use multiple extraction libraries
3. **MongoDB Connection**: Add retry logic and fallback
4. **Voice API Costs**: Cache translations and use efficient APIs
5. **Testing Complexity**: Start with unit tests, add integration gradually

## Notes

- All existing `/api/` endpoints remain unchanged for backward compatibility
- MongoDB is optional - system falls back to in-memory if not available
- Profile scraping works for any user - users provide their own email/username, no OAuth app setup needed
- Claims PDF parsing is optional enhancement - uses existing PostgreSQL if PDF unavailable

