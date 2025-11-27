#!/usr/bin/env python3
"""
Simplified server runner that can work with or without full MCP
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST, before any imports
load_dotenv()

# Verify API key is loaded
groq_key = os.getenv("GROQ_API_KEY")
if not groq_key or groq_key == "your_groq_api_key_here":
    print("⚠️  WARNING: GROQ_API_KEY not set or using placeholder!")
    print("   Please edit .env and add your Groq API key from https://console.groq.com/")
    print("   Example: GROQ_API_KEY=gsk_your_actual_key_here")
    sys.exit(1)

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Try to run MCP server, fallback to FastAPI
# Note: MCP is optional - FastAPI server works great for this use case!
try:
    from wandersure_server import main
    print("Starting MCP server...")
    asyncio.run(main())
except ImportError:
    # MCP not installed - this is fine, use FastAPI instead
    print("MCP package not available, using FastAPI server (this is fine!)")
except Exception as e:
    print(f"MCP server failed: {e}")
    
# Always use FastAPI server (works without MCP package)
print("Starting WanderSure FastAPI server...")

# Run FastAPI server
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
import os
import base64
from io import BytesIO
import time
from collections import defaultdict
from datetime import datetime, timedelta

app = FastAPI(title="WanderSure API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting storage (in-memory, use Redis in production)
rate_limit_store: defaultdict = defaultdict(list)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # requests per window
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

def check_rate_limit(identifier: str) -> bool:
    """Check if request should be rate limited"""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    # Clean old entries
    rate_limit_store[identifier] = [
        timestamp for timestamp in rate_limit_store[identifier]
        if timestamp > window_start
    ]
    
    # Check limit
    if len(rate_limit_store[identifier]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    rate_limit_store[identifier].append(now)
    return True

def get_client_identifier(request: Request) -> str:
    """Get identifier for rate limiting (IP or user_id)"""
    user_id = request.headers.get("X-User-ID") or request.query_params.get("user_id")
    if user_id:
        return f"user:{user_id}"
    # Fallback to IP
    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}"

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": "HTTP_ERROR",
            "message": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "An internal server error occurred"
        }
    )

# Import handlers AFTER dotenv is loaded
from policy_intelligence import PolicyIntelligence
from document_intelligence import DocumentIntelligence
from predictive_intelligence import PredictiveIntelligence
from payment_handler import PaymentHandler
from conversation_handler import ConversationHandler
<<<<<<< Updated upstream
=======
from user_profile_manager import UserProfileManager
from partner_integrations import PartnerIntegrations
from intelligent_recommender import IntelligentRecommender
from pricing_calculator import PricingCalculator
from policy_scorer import PolicyScorer
from claims_analyzer import ClaimsAnalyzer
from mcp_integrations import MCPIntegrations
from activity_policy_matcher import ActivityPolicyMatcher
from policy_simplifier import PolicySimplifier
from taxonomy_matcher import TaxonomyMatcher
from policy_metadata import PolicyMetadata
from routers.v1 import router as v1_router
>>>>>>> Stashed changes

policy_intel = PolicyIntelligence()
doc_intel = DocumentIntelligence()
predictive_intel = PredictiveIntelligence()
payment_handler = PaymentHandler()
conversation = ConversationHandler()
<<<<<<< Updated upstream
=======
user_profile_manager = UserProfileManager()
partner_integrations = PartnerIntegrations()
intelligent_recommender = IntelligentRecommender()
pricing_calculator = PricingCalculator()
claims_analyzer = ClaimsAnalyzer()
# Get claims_db from claims_analyzer to pass to policy_scorer
claims_db = claims_analyzer.claims_db if hasattr(claims_analyzer, 'claims_db') else None
policy_scorer = PolicyScorer(claims_db=claims_db)
mcp_integrations = MCPIntegrations()
activity_matcher = ActivityPolicyMatcher()
policy_simplifier = PolicySimplifier()
taxonomy_matcher = TaxonomyMatcher()
policy_metadata = PolicyMetadata(policy_intel)

def inject_additional_products(ancileo_quotes: List[Dict], trip_details: Dict) -> List[Dict]:
    """
    Inject additional mock products when Ancileo returns only 1 quote
    These simulate additional insurance products from Step 1 (local policies)
    """
    all_quotes = ancileo_quotes.copy()
    
    # Get base price from Ancileo quote for reference
    base_price = ancileo_quotes[0].get("price", 50) if ancileo_quotes else 50
    currency = ancileo_quotes[0].get("currency", "SGD") if ancileo_quotes else "SGD"
    
    # Use NEW policies from Policy_Wordings (NO mock products)
    # These should come from taxonomy matching, not hardcoded here
    # This function should not be used anymore - policies come from taxonomy_matcher
    mock_products = []
    
    # Add mock products to quotes list
    all_quotes.extend(mock_products)
    
    # Sort by price for better comparison
    all_quotes.sort(key=lambda x: x.get("price", 0))
    
    logger.info(f"Injected {len(mock_products)} additional products. Total quotes: {len(all_quotes)}")
    
    return all_quotes

# Include v1 router
app.include_router(v1_router)
>>>>>>> Stashed changes

@app.get("/health")
@app.get("/healthz")
async def health():
    """Health check endpoint"""
    try:
        # Check critical services
        checks = {
            "status": "ok",
            "service": "wandersure",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "api": "ok",
                "groq_client": "ok" if conversation.client else "degraded"
            }
        }
        
        # Check database connections if available
        try:
            if hasattr(claims_analyzer, 'claims_db') and claims_analyzer.claims_db:
                if claims_analyzer.claims_db.is_connected():
                    checks["checks"]["claims_db"] = "ok"
                else:
                    checks["checks"]["claims_db"] = "degraded"
        except:
            checks["checks"]["claims_db"] = "unavailable"
        
        return checks
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "service": "wandersure",
                "error": str(e)
            }
        )

@app.post("/api/ask")
<<<<<<< Updated upstream
async def ask_question(request: dict):
    result = await conversation.handle_question(
        question=request.get("question"),
        language=request.get("language"),
        context=request.get("context"),
        user_id=request.get("user_id", "default_user"),
        is_voice=request.get("is_voice", False),
        role=request.get("role")
    )
    return result
=======
async def ask_question_endpoint(http_request: Request):
    """Handle user questions with comprehensive error handling"""
    start_time = time.time()
    
    # Rate limiting
    identifier = get_client_identifier(http_request)
    if not check_rate_limit(identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "success": False,
                "error_code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please wait a moment and try again."
            }
        )
    
    # Parse request body
    try:
        request = await http_request.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid JSON in request body"
            }
        )
    
    try:
        # Validate required fields
        question = request.get("question", "").strip() if isinstance(request, dict) else ""
        if not question:
            return {
                "answer": "👋 Hi there! I'm Wanda, your travel insurance assistant. How can I help you today?",
                "content": "👋 Hi there! I'm Wanda, your travel insurance assistant. How can I help you today?",
                "message": "👋 Hi there! I'm Wanda, your travel insurance assistant. How can I help you today?",
                "booking_links": [],
                "suggested_questions": [],
                "quotes": [],
                "quote_id": None,
                "trip_details": None
            }
        
        question_lower = question.lower()
        user_id = request.get("user_id", "default_user")
        context_data = request.get("context_data", {})
        
        # Initialize quotes and trip_details at the very start to prevent UnboundLocalError
        quotes = []
        trip_details = {}
        
        # CANCELLATION DETECTION - Use dynamic policy-based responses
        cancellation_keywords = ["cancel", "cancellation", "refund", "terminate", "end policy", "stop coverage", 
                                 "how to cancel", "how do i cancel", "can i cancel", "how can i cancel", 
                                 "want to cancel", "need to cancel", "cancel my", "cancel this", "cancel the",
                                 "cancel insurance", "cancel policy", "cooling-off", "cooling off"]
        is_cancellation_question = any(keyword in question_lower for keyword in cancellation_keywords)
        
        if is_cancellation_question:
            logger.info(f"Cancellation question detected: {question}")
            
            # Get active policy from context
            active_policy = policy_metadata.get_active_policy(context_data, user_id)
            
            if not active_policy:
                # No active policy - ask user to clarify
                return {
                    "success": True,
                    "answer": "**Which policy would you like to cancel?**\n\nI need to know which policy you're referring to. Please:\n\n• Select your policy from the quotes shown, OR\n• Tell me the policy name (e.g., Scootsurance, INTERNATIONAL TRAVEL, MHInsure Travel)\n\nOnce I know which policy, I can provide the specific cancellation instructions and refund terms.",
                    "content": "**Which policy would you like to cancel?**\n\nI need to know which policy you're referring to. Please select your policy or tell me the policy name.",
                    "message": "**Which policy would you like to cancel?**\n\nI need to know which policy you're referring to.",
                    "booking_links": [],
                    "suggested_questions": [],
                    "quotes": [],
                    "quote_id": None,
                    "trip_details": None
                }
            
            # Format answer based on question type
            cancellation_answer = policy_metadata.format_cancellation_answer(active_policy, question)
            
            # Only show suggested questions for general cancellation questions
            suggested_questions = []
            if "cooling-off" not in question_lower and "how long" not in question_lower and "trip has started" not in question_lower and "trip started" not in question_lower:
                suggested_questions = [
                    {
                        "question": "What is the cooling-off period?",
                        "icon": "❓",
                        "priority": "high"
                    },
                    {
                        "question": "How long does a refund take?",
                        "icon": "💰",
                        "priority": "medium"
                    },
                    {
                        "question": "Can I cancel if my trip has started?",
                        "icon": "✈️",
                        "priority": "medium"
                    }
                ]
            
            return {
                "success": True,
                "answer": cancellation_answer,
                "content": cancellation_answer,
                "message": cancellation_answer,
                "booking_links": [],
                "suggested_questions": suggested_questions,
                "quotes": [],
                "quote_id": None,
                "trip_details": None,
                "referenced_policies": [active_policy.get("product_name")]
            }
        
        # Check if user mentions a destination - analyze claims data proactively
        destination_mentioned = None
        
        # Extract destination from question (expanded list including Coimbatore)
        destination_keywords = ["chennai", "coimbatore", "india", "japan", "tokyo", "bangkok", "thailand",
                              "singapore", "malaysia", "kuala lumpur", "bali", "indonesia", "china",
                              "beijing", "shanghai", "australia", "europe", "uk", "united kingdom",
                              "usa", "united states", "philippines", "vietnam", "korea", "seoul",
                              "hong kong", "taiwan", "taipei", "phuket", "pattaya", "penang", "krabi"]
        
        for dest in destination_keywords:
            if dest.lower() in question_lower:
                destination_mentioned = dest
                break
        
        # If destination mentioned, get claims analysis BEFORE normal flow
        claims_analysis = None
        enhanced_context = request.get("context") or ""
        
        if destination_mentioned:
            try:
                # Calculate trip duration if available
                trip_duration = None
                trip_details = context_data.get("trip_details", {})
                if trip_details.get("departure_date") and trip_details.get("return_date"):
                    try:
                        dep = datetime.strptime(trip_details["departure_date"], "%Y-%m-%d")
                        ret = datetime.strptime(trip_details["return_date"], "%Y-%m-%d")
                        trip_duration = (ret - dep).days
                    except:
                        pass
                
                claims_analysis = await claims_analyzer.analyze_destination_and_recommend(
                    destination=destination_mentioned,
                    trip_duration=trip_duration
                )
                
                # If we have claims data, enhance context with it
                if claims_analysis.get("has_data"):
                    top_rec = claims_analysis.get("recommendations", [{}])[0] if claims_analysis.get("recommendations") else {}
                    common_incidents_str = ', '.join([
                        f"{inc['incident']} ({inc['percentage']}%)" 
                        for inc in claims_analysis.get("common_incidents", [])[:3]
                    ])
                    
                    # Build prominent claims context
                    claims_context = f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 CLAIMS DATA FOR {destination_mentioned.upper()} - USE THIS DATA PROMINENTLY IN YOUR RESPONSE:

Total historical claims analyzed: {claims_analysis.get('total_claims', 0)}
Risk summary: {claims_analysis.get('risk_summary', '')}

Common incidents: {common_incidents_str}

Top claim type: {top_rec.get('claim_type', 'N/A')} 
- Incidence rate: {top_rec.get('incidence_rate', 'N/A')} of all claims
- Average cost per claim: ${top_rec.get('average_cost', 0):,.2f} SGD
- Recommended coverage: ${top_rec.get('recommended_coverage', 0):,.2f} SGD

Suggested proactive message: "{claims_analysis.get('suggested_message', '')}"

Policy wordings available: {len(top_rec.get('policy_citations', []))} policies specifically cover {top_rec.get('claim_type', 'common incidents')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL INSTRUCTION: 
1. You MUST prominently feature this claims data at the START of your response
2. Use the EXACT format: "In {destination_mentioned}, {top_rec.get('incidence_rate', 'X%')} of travelers have claimed for {top_rec.get('claim_type', 'incidents')} with an average cost of ${top_rec.get('average_cost', 0):,.2f} SGD."
3. ALWAYS ask: "Would you like to purchase insurance to specifically cover this highly likely incident?"
4. Quote the policy wordings from the policy_citations if available
5. Make this the PRIMARY focus of your response when destination is mentioned

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                    
                    enhanced_context = enhanced_context + claims_context
                    logger.info(f"Added claims context for {destination_mentioned}: {claims_analysis.get('total_claims', 0)} claims found")
                else:
                    logger.warning(f"No claims data found for {destination_mentioned}")
            
            except Exception as e:
                logger.error(f"Claims analysis failed: {e}", exc_info=True)
        
        # Check if user is asking for policies/quotes for a destination
        # Patterns like "policies for chennai", "insurance for [destination]", "give me 10 policies", etc.
        destination_keywords = ["chennai", "japan", "tokyo", "bangkok", "singapore", "kuala lumpur", "bali", "bangkok", "manila", "ho chi minh", "hanoi", "seoul", "beijing", "shanghai", "hong kong", "taipei", "phuket", "pattaya", "penang", "krabi"]
        is_policy_request = any(kw in question for kw in ["polic", "quote", "insurance", "cover", "plan", "recommend"]) and any(dest in question for dest in destination_keywords)
        
        # If asking for policies, fetch from Ancileo first
        if is_policy_request:
            try:
                # Extract destination from question
                destination = None
                for dest in destination_keywords:
                    if dest in question:
                        destination = dest
                        break
                
                # Country mapping
                country_map = {
                    "chennai": "IN", "india": "IN", "japan": "JP", "tokyo": "JP",
                    "singapore": "SG", "bangkok": "TH", "thailand": "TH",
                    "kuala lumpur": "MY", "malaysia": "MY", "bali": "ID", "indonesia": "ID",
                    "manila": "PH", "philippines": "PH", "ho chi minh": "VN", "hanoi": "VN", "vietnam": "VN",
                    "seoul": "KR", "korea": "KR", "beijing": "CN", "shanghai": "CN", "china": "CN",
                    "hong kong": "HK", "taipei": "TW", "taiwan": "TW",
                    "phuket": "TH", "pattaya": "TH", "penang": "MY", "krabi": "TH"
                }
                
                arrival_country = country_map.get(destination.lower(), "IN")
                
                # Fetch Ancileo policies for this destination
                from ancileo_api import AncileoAPI
                ancileo = AncileoAPI()
                
                if ancileo.available_keys:
                    # Calculate dates (default: 7 days from today)
                    from datetime import datetime, timedelta
                    departure_date = datetime.now().strftime("%Y-%m-%d")
                    return_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                    
                    quote_result = await ancileo.get_quote(
                        market="SG",
                        departure_country="SG",
                        arrival_country=arrival_country,
                        departure_date=departure_date,
                        return_date=return_date,
                        departure_airport="SIN",  # Default Singapore airport
                        arrival_airport=None,  # Will be auto-mapped based on country
                        adults_count=1,
                        children_count=0,
                        trip_type="RT"
                    )
                    
                    if quote_result.get("success"):
                        ancileo_policies = quote_result.get("policies", [])
                        quotes = []
                        for policy in ancileo_policies:
                            quotes.append({
                                "plan_name": policy.get("product_name", "Ancileo Policy"),
                                "price": policy.get("price", 0),
                                "currency": policy.get("currency", "SGD"),
                                "recommended_for": policy.get("description", "Travel protection"),
                                "source": "ancileo",
                                "offer_id": policy.get("offer_id"),
                                "product_code": policy.get("product_code"),
                                "coverage": policy.get("coverage", {}),
                                "features": policy.get("features", []),
                                "terms": policy.get("terms", {}),
                                "raw_data": policy.get("raw_data", {})
                            })
                        
                        # Get conversational response
                        result = await conversation.handle_question(
                            question=request.get("question"),
                            language=request.get("language"),
                            context=enhanced_context if enhanced_context else request.get("context"),
                            user_id=user_id,
                            is_voice=request.get("is_voice", False),
                            role=request.get("role")
                        )
                        
                        # Add Ancileo quotes to response - ensure all fields are present
                        if not result:
                            result = {}
                        
                        result["quotes"] = quotes
                        result["quote_id"] = quote_result.get("quote_id")
                        result["trip_details"] = {
                            "destination": destination or arrival_country,
                            "departure_date": departure_date,
                            "return_date": return_date,
                            "travelers": 1,
                            "adults": 1,
                            "children": 0
                        }
                        result["source"] = "ancileo"
                        
                        # Ensure answer/content is set
                        if "answer" not in result and "content" not in result:
                            result["answer"] = "Here are the available insurance policies for your destination."
                        
                        return result
            except Exception as e:
                logger.warning(f"Failed to fetch Ancileo policies: {e}")
                # Continue to normal flow
        
        # Check if question is about pricing or best policy
        is_pricing_question = any(keyword in question for keyword in [
            "calculate", "calculation", "why", "how much", "cost", "price", "breakdown",
            "explain", "pricing", "how did", "why do i need"
        ])
        
        is_best_question = any(keyword in question for keyword in [
            "best", "recommend", "which", "should i choose", "which one", "better"
        ])
        
        # If pricing question and we have quote data, provide detailed explanation
        # (quotes and trip_details already initialized at function start)
        if is_pricing_question and context_data.get("quotes"):
            quotes = context_data.get("quotes", [])
            trip_details = context_data.get("trip_details", {})
            
            # Find the quote being asked about (usually the first/most recent)
            target_quote = quotes[0] if quotes else None
            
            if target_quote and trip_details:
                # Calculate and explain pricing
                breakdown = pricing_calculator.calculate_price_breakdown(
                    price=target_quote.get("price", 0),
                    destination=trip_details.get("destination", ""),
                    departure_date=trip_details.get("departure_date", ""),
                    return_date=trip_details.get("return_date", ""),
                    travelers=trip_details.get("travelers", 1),
                    ages=trip_details.get("ages", []),
                    trip_cost=trip_details.get("trip_cost"),
                    policy_name=target_quote.get("plan_name"),
                    source=target_quote.get("source", "ancileo")
                )
                
                explanation = pricing_calculator.explain_price(target_quote, trip_details)
                
                # Get conversational response but inject pricing explanation
                result = await conversation.handle_question(
                    question=request.get("question"),
                    language=request.get("language"),
                    context=f"{enhanced_context if enhanced_context else request.get('context', '')}\n\nPRICING BREAKDOWN DATA:\n{explanation}\n\nUse this specific pricing breakdown to answer the user's question about pricing calculation. Be specific and explain the numbers.",
                    user_id=user_id,
                    is_voice=request.get("is_voice", False),
                    role=request.get("role")
                )
                
                # Ensure pricing explanation is included
                if result.get("answer"):
                    result["answer"] = f"{explanation}\n\n{result['answer']}"
                
                # Ensure quotes is present
                if "quotes" not in result:
                    result["quotes"] = []
                
                return result
        
        # If best policy question and we have quotes, use scoring algorithm
        if is_best_question and context_data.get("quotes"):
            quotes = context_data.get("quotes", [])
            trip_details = context_data.get("trip_details", {})
            
            # Get user profile
            user_profile = None
            email = request.get("email") or context_data.get("email")
            if email:
                user_identity = user_profile_manager.identify_user(email=email)
                if user_identity.get("found"):
                    user_profile = user_identity["user"]
            
            # Get risk assessment
            risk_assessment = None
            if trip_details.get("destination"):
                try:
                    avg_age = sum(trip_details.get("ages", [30])) / len(trip_details.get("ages", [30]))
                    travel_month = None
                    if trip_details.get("departure_date"):
                        try:
                            travel_month = datetime.strptime(trip_details["departure_date"], "%Y-%m-%d").month
                        except:
                            pass
                    
                    risk_assessment = await predictive_intel.get_risk_assessment(
                        destination=trip_details.get("destination", ""),
                        activities=trip_details.get("activities", []),
                        duration=(datetime.strptime(trip_details.get("return_date", ""), "%Y-%m-%d") - 
                                 datetime.strptime(trip_details.get("departure_date", ""), "%Y-%m-%d")).days if trip_details.get("departure_date") and trip_details.get("return_date") else None,
                        age=int(avg_age),
                        month=travel_month
                    )
                except:
                    pass
            
            # Score policies
            # Get activities from trip details or user profile
            activities = []
            if trip_details.get("activities"):
                activities = trip_details["activities"]
            elif user_profile and user_profile.get("activity_types"):
                activities = user_profile["activity_types"]
            
            # Score policies using PolicyScorer (enhanced with activity matching)
            scored = policy_scorer.score_policies(
                quotes=quotes,
                trip_details=trip_details,
                user_profile=user_profile,
                risk_assessment=risk_assessment,
                activities=activities
            )
            
            # Build explanation with scoring details
            best_policy = scored[0] if scored else None
            
            if best_policy:
                scoring_explanation = best_policy.get("explanation", "")
                
                # Get conversational response but inject scoring explanation
                result = await conversation.handle_question(
                    question=request.get("question"),
                    language=request.get("language"),
                    context=f"{enhanced_context if enhanced_context else request.get('context', '')}\n\nPOLICY SCORING RESULTS:\n{scoring_explanation}\n\nUse this specific scoring breakdown to explain which policy is best and why. Reference the scores and be specific about the algorithm used.",
                    user_id=user_id,
                    is_voice=request.get("is_voice", False),
                    role=request.get("role")
                )
                
                # Ensure scoring explanation is included
                if result.get("answer"):
                    result["answer"] = f"{scoring_explanation}\n\n{result['answer']}"
                
                # Add scored policies to response
                result["scored_policies"] = scored
                
                return result
        
        # Check for activity coverage questions (e.g., "does Scootsurance cover hiking?")
        # ONLY check for policies that exist: Scootsurance, INTERNATIONAL TRAVEL, MHInsure Travel
        is_activity_coverage_question = any(keyword in question_lower for keyword in [
            "cover", "coverage", "does", "will", "include", "hiking", "trekking", "sport", 
            "activity", "skiing", "scuba", "diving", "adventure", "outdoor"
        ]) and any(policy in question_lower for policy in ["scootsurance", "international travel", "mhinsure", "msig"])
        
        # Handle activity coverage questions with activity matcher
        if is_activity_coverage_question:
            try:
                from activity_policy_matcher import ActivityPolicyMatcher
                activity_matcher = ActivityPolicyMatcher()
                
                # Extract activity from question
                activities = ["hiking", "trekking", "skiing", "scuba", "diving", "adventure", "sport"]
                mentioned_activity = None
                for act in activities:
                    if act in question_lower:
                        mentioned_activity = act
                        break
                
                # Extract policy name - ONLY use policies that exist in Policy_Wordings
                policy_name = None
                if "scootsurance" in question_lower:
                    policy_name = "Scootsurance"
                elif "international travel" in question_lower or "international" in question_lower:
                    policy_name = "INTERNATIONAL TRAVEL"
                elif "mhinsure" in question_lower or "mh insure" in question_lower:
                    policy_name = "MHInsure Travel"
                elif "msig" in question_lower:
                    policy_name = "INTERNATIONAL TRAVEL"  # Map MSIG to INTERNATIONAL TRAVEL
                # Removed: TravelEasy (doesn't exist)
                
                if mentioned_activity and policy_name:
                    # Get policy text
                    policy_text = policy_intel.get_policy_text(policy_name)
                    if policy_text:
                        # Analyze policy for activity
                        activity_requirements = activity_matcher.activity_requirements.get(mentioned_activity, {})
                        analysis = await activity_matcher._analyze_policy_for_activity(
                            policy_text, mentioned_activity, activity_requirements, {}
                        )
                        
                        # Build helpful response
                        if analysis.get("activity_coverage") == "Yes":
                            response = f"✅ **Yes, {policy_name.split()[0]} covers {mentioned_activity}!**\n\n"
                        elif analysis.get("activity_coverage") == "Partial":
                            response = f"⚠️ **{policy_name.split()[0]} provides partial coverage for {mentioned_activity}**\n\n"
                        else:
                            response = f"❌ **{policy_name.split()[0]} may not fully cover {mentioned_activity}**\n\n"
                        
                        if analysis.get("coverage_details"):
                            response += f"{analysis['coverage_details']}\n\n"
                        
                        if analysis.get("exclusions"):
                            response += f"**Exclusions to be aware of:**\n"
                            for exc in analysis["exclusions"]:
                                response += f"• {exc}\n"
                            response += "\n"
                        
                        response += "Would you like me to check the specific coverage amounts or compare with other policies?"
                        
                        return {
                            "answer": response,
                            "content": response,
                            "message": response,
                            "booking_links": [],
                            "suggested_questions": [],
                            "quotes": [],
                            "quote_id": None,
                            "trip_details": None
                        }
            except Exception as e:
                logger.warning(f"Activity coverage check failed: {e}")
                # Continue to normal flow
        
        # Check for specific questions that need policy intelligence
        question_lower_check = question_lower
        
        needs_policy_details = any(word in question_lower_check for word in ["premium", "price", "cost", "fee"])
        
        # Check for comparison questions like "compare X and Y"
        is_comparison_question = any(keyword in question_lower_check for keyword in ["compare", "difference", "vs", "versus", "better between"])
        
        # Handle comparison questions
        if is_comparison_question:
            try:
                # Extract policy names from question
                # ONLY check for policies that exist in Policy_Wordings
                policy_keywords = ["scootsurance", "international travel", "mhinsure", "msig"]
                mentioned_policies = [name for name in policy_keywords if name in question_lower_check]
                
                if mentioned_policies:
                    # Map to full policy names - ONLY use policies that exist
                    policy_map = {
                        "scootsurance": "Scootsurance",
                        "international travel": "INTERNATIONAL TRAVEL",
                        "mhinsure": "MHInsure Travel",
                        "mh insure": "MHInsure Travel",
                        "msig": "INTERNATIONAL TRAVEL",  # Map MSIG to INTERNATIONAL TRAVEL
                        # Removed: TravelEasy (doesn't exist)
                    }
                    
                    policy_names = [policy_map.get(name, name) for name in mentioned_policies if name in policy_map]
                    
                    # Use comparison API
                    comparison_result = await policy_intel.compare_policies(
                        criteria="overall coverage, pricing, and key benefits",
                        policies=policy_names
                    )
                    
                    # Inject comparison into context for conversational response
                    enhanced_context = enhanced_context + f"\n\nPOLICY COMPARISON DATA:\n{comparison_result.get('comparison', '')}\n\nUse this comparison data to answer the user's question about differences between the policies. Be conversational and highlight key differences."
            except Exception as e:
                logger.error(f"Comparison handling failed: {e}")
        
        # For cancellation/premium questions, enhance context with policy details
        if needs_policy_details:
            try:
                policy_details_context = ""
                for policy_name in ["INTERNATIONAL TRAVEL", "MHInsure Travel", "Scootsurance"]:
                    if policy_name.lower().replace(" ", "").replace("-", "") in question_lower_check or "any" in question_lower_check or "all" in question_lower_check:
                        # Get policy text for reference
                        policy_text = policy_intel.get_policy_text(policy_name)
                        if policy_text:
                            policy_details_context += f"\n\n[{policy_name} Policy Text Available - {len(policy_text)} characters]\n"
                
                if policy_details_context:
                    enhanced_context = enhanced_context + "\n\nPOLICY DETAILS AVAILABLE FOR REFERENCE:\n" + policy_details_context
            except Exception as e:
                logger.error(f"Failed to add policy details context: {e}")
        
        # Normal conversation flow (with enhanced context if claims data available)
        # Add instruction to prevent full policy regurgitation for follow-up questions
        context_with_instruction = enhanced_context if enhanced_context else request.get("context", "")
        
        # Add instruction for concise answers on follow-up questions
        question_lower_for_prompt = question.lower()
        is_followup = any(keyword in question_lower_for_prompt for keyword in [
            "cooling-off", "cooling off", "how long", "refund take", "trip has started", 
            "trip started", "already started", "what is the", "can i cancel if"
        ])
        
        if is_followup:
            context_with_instruction += "\n\n⚠️ CRITICAL: The user is asking a SPECIFIC follow-up question about cancellation/refund. Answer ONLY that specific question concisely (2-4 sentences). Do NOT repeat the entire cancellation policy. Do NOT include contact methods, required information, or full refund rules unless directly asked. Extract and summarize ONLY the relevant information."
        
        result = await conversation.handle_question(
            question=request.get("question"),
            language=request.get("language"),
            context=context_with_instruction,
            user_id=user_id,
            is_voice=request.get("is_voice", False),
            role=request.get("role")
        )
        
        # Ensure result is a dict and has required fields
        if not result:
            result = {}
        
        # Always ensure quotes is defined (empty list if not provided)
        if "quotes" not in result:
            result["quotes"] = []
        
        # Add claims analysis if available - CRITICAL for frontend
        if claims_analysis:
            result["claims_analysis"] = claims_analysis
            logger.info(f"✅ Added claims_analysis to response: has_data={claims_analysis.get('has_data')}, total_claims={claims_analysis.get('total_claims', 0)}")
        
        # Also add it to answer/content so LLM response includes it
        if claims_analysis and claims_analysis.get("has_data"):
            claims_summary = f"\n\n🎯 **Claims Insights for {destination_mentioned}**: "
            if claims_analysis.get("recommendations"):
                top = claims_analysis["recommendations"][0]
                claims_summary += f"{top.get('incidence_rate', 'N/A')} of travelers have claimed for {top.get('claim_type', 'incidents')} (avg cost: ${top.get('average_cost', 0):,.2f} SGD)"
            if result.get("answer"):
                result["answer"] = claims_summary + "\n\n" + result["answer"]
            if result.get("content"):
                result["content"] = claims_summary + "\n\n" + result["content"]
            if result.get("message"):
                result["message"] = claims_summary + "\n\n" + result["message"]
        
        # Final safety check: ensure quotes is always present
        if "quotes" not in result:
            result["quotes"] = []
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        response_time = time.time() - start_time
        error_type = type(e).__name__
        error_msg = str(e)
        
        # Structured logging
        logger.error(
            f"Error in /api/ask endpoint",
            extra={
                "error_type": error_type,
                "error_message": error_msg[:500],  # Truncate long messages
                "user_id": request.get("user_id", "unknown") if isinstance(request, dict) else "unknown",
                "response_time_ms": round(response_time * 1000, 2),
                "question_length": len(question) if question else 0
            },
            exc_info=True
        )
        
        # Determine error code
        if "GROQ_API_KEY" in error_msg or "api_key" in error_msg.lower():
            error_code = "CONFIGURATION_ERROR"
            error_message = "⚠️ **Configuration Issue**\n\nI'm having trouble connecting to the AI service. Please check that GROQ_API_KEY is set in your environment variables."
        elif "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
            error_code = "RATE_LIMIT_ERROR"
            error_message = "⏱️ **Rate Limit**\n\nI've hit a rate limit. Please wait a moment and try again."
        elif "timeout" in error_msg.lower() or "Timeout" in error_type:
            error_code = "TIMEOUT_ERROR"
            error_message = "⏱️ **Request Timeout**\n\nYour request took too long to process. Please try again with a simpler question."
        elif "connection" in error_msg.lower() or "Connection" in error_type:
            error_code = "CONNECTION_ERROR"
            error_message = "🌐 **Connection Issue**\n\nI'm having trouble connecting right now. This is usually temporary. Please try again in a moment."
        else:
            error_code = "INTERNAL_ERROR"
            error_message = "😅 **I'm having a bit of trouble right now**\n\nI encountered an issue processing your question.\n\n**What you can try:**\n• **Try rephrasing** your question\n• **Wait a moment** and try again\n• **Ask something simple** like \"What can you help me with?\" or \"Tell me about travel insurance\"\n\nI apologize for the inconvenience. Your question is important to me!"
        
        # Return structured error response
        return {
            "success": False,
            "error_code": error_code,
            "answer": error_message,
            "content": error_message,
            "message": error_message,
            "booking_links": [],
            "suggested_questions": [
                {"question": "What can you help me with?", "icon": "💬", "priority": "high"},
                {"question": "Tell me about travel insurance", "icon": "🛡️", "priority": "high"},
                {"question": "How does travel insurance work?", "icon": "❓", "priority": "medium"}
            ],
            "quotes": [],
            "quote_id": None,
            "trip_details": None
        }

@app.post("/api/claims/analyze")
async def analyze_destination_claims(request: dict):
    """Analyze claims data for a destination and provide recommendations"""
    destination = request.get("destination")
    trip_duration = request.get("trip_duration")
    
    if not destination:
        return {
            "success": False,
            "error": "Destination is required"
        }
    
    try:
        analysis = await claims_analyzer.analyze_destination_and_recommend(
            destination=destination,
            trip_duration=trip_duration
        )
        return {
            "success": True,
            **analysis
        }
    except Exception as e:
        logger.error(f"Claims analysis failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
>>>>>>> Stashed changes

@app.post("/api/role/set")
async def set_role(request: dict):
    """Set the conversation role"""
    user_id = request.get("user_id", "default_user")
    role = request.get("role", "travel_agent")
    success = conversation.set_user_role(user_id, role)
    return {
        "success": success,
        "role": role,
        "message": f"Role set to {role}"
    }

@app.get("/api/role/get")
async def get_role(user_id: str = "default_user"):
    """Get current conversation role"""
    role = conversation.get_user_role(user_id)
    return {
        "role": role,
        "role_info": conversation.roles.get(role, {})
    }

@app.get("/api/policy/details")
async def get_policy_details(policy_name: str):
    """Get detailed policy information with coverage and citations for tooltip"""
    from policy_intelligence import PolicyIntelligence
    policy_intel = PolicyIntelligence()
    
    # Normalize policy name
    policy_mapping = {
        "TravelEasy": "TravelEasy Policy QTD032212",
        "Scootsurance": "Scootsurance QSR022206_updated",
        "MSIG": "Scootsurance QSR022206_updated",
        "TravelEasy Pre-Ex": "TravelEasy Pre-Ex Policy QTD032212-PX"
    }
    
    normalized_name = policy_mapping.get(policy_name, policy_name)
    
    # Get full policy text (more context for detailed info)
    policy_data = policy_intel.policy_texts.get(normalized_name, {})
    policy_text = policy_data.get("text", "")
    
    # Use more text for better details (first 5000 chars)
    policy_excerpt = policy_text[:5000] if len(policy_text) > 5000 else policy_text
    
    # Generate detailed summary with coverage amounts and citations
    summary_prompt = f"""Provide detailed information about this travel insurance policy for a hover tooltip:

Policy: {normalized_name}

Policy Text Excerpt:
{policy_excerpt}

Provide comprehensive details:
1. Policy name and type
2. Key coverage areas with SPECIFIC AMOUNTS (medical coverage, trip cancellation, baggage, etc.)
3. Coverage limits and sub-limits (with exact dollar amounts)
4. Important exclusions or conditions
5. Typical use cases and who it's best for
6. Exact policy citations: [Policy: {normalized_name}, Section: X] format

Format:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Policy**: {normalized_name}

**Coverage Highlights**:
• Medical Expenses: $[amount]
• Trip Cancellation: $[amount]  
• Baggage Loss: $[amount]
• [Other key coverages]

**Key Exclusions**:
• [Exclusion 1]
• [Exclusion 2]

**Best For**: [Use case description]

**Policy Citation**: [Policy: {normalized_name}, Section: X]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Extract SPECIFIC amounts and exact section references from the policy text."""

    try:
        response = policy_intel.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert at extracting detailed insurance policy information. Always include specific coverage amounts and exact policy citations."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.2,
            max_tokens=500  # More tokens for detailed info
        )
        
        summary = response.choices[0].message.content
        
        return {
            "success": True,
            "policy_name": normalized_name,
            "summary": summary,
            "full_name": policy_data.get("name", normalized_name),
            "coverage_details": "Available"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "summary": f"**Policy**: {normalized_name}\n\nTravel insurance policy with comprehensive coverage. Please refer to full policy document for details."
        }

@app.get("/api/greeting")
async def get_greeting(request: Request, user_id: str = "default_user", language: str = "en"):
    """Get personalized greeting from travel buddy"""
    start_time = time.time()
    
    # Rate limiting
    identifier = get_client_identifier(request)
    if not check_rate_limit(identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    try:
        # Validate inputs
        if not user_id or len(user_id) > 200:
            user_id = "default_user"
        
        if language not in ["en", "ta", "zh", "ms"]:
            language = "en"
        
        # Generate greeting with timeout protection
        try:
            greeting = await asyncio.wait_for(
                conversation.generate_personalized_greeting(user_id, language),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            logger.warning(f"Greeting generation timeout for user {user_id}")
            greeting = "👋 Welcome! I'm Wanda, Your Travel Agent • Expert travel planning & insurance advice • Personalized destination recommendations • Comprehensive trip protection solutions • 24/7 support for your journey How can I help plan your next adventure? ✈️"
        
        response_time = time.time() - start_time
        logger.info(f"Greeting generated for user {user_id} in {response_time:.2f}s")
        
        return {
            "success": True,
            "greeting": greeting,
            "metadata": {
                "user_id": user_id,
                "language": language,
                "response_time_ms": round(response_time * 1000, 2)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating greeting: {e}", exc_info=True)
        # Return fallback greeting instead of failing
        return {
            "success": True,
            "greeting": "👋 Welcome! I'm Wanda, Your Travel Agent • Expert travel planning & insurance advice • Personalized destination recommendations • Comprehensive trip protection solutions • 24/7 support for your journey How can I help plan your next adventure? ✈️",
            "metadata": {
                "user_id": user_id,
                "language": language,
                "fallback": True
            }
        }

@app.post("/api/travel/insights")
async def get_destination_insights(request: dict):
    """Get rich destination insights beyond insurance"""
    from travel_buddy import TravelBuddy
    buddy = TravelBuddy()
    insights = await buddy.get_destination_insights(
        destination=request.get("destination"),
        user_preferences=request.get("preferences", {})
    )
    return insights

@app.post("/api/travel/activities")
async def suggest_activities(request: dict):
    """Get personalized activity suggestions"""
    from travel_buddy import TravelBuddy
    buddy = TravelBuddy()
    activities = await buddy.suggest_activities(
        destination=request.get("destination"),
        trip_dates=request.get("trip_dates", {}),
        traveler_profile=request.get("traveler_profile", {})
    )
    return {"activities": activities}

@app.post("/api/travel/moment")
async def create_travel_moment(request: dict):
    """Create a special travel buddy moment"""
    from travel_buddy import TravelBuddy
    buddy = TravelBuddy()
    moment = await buddy.create_travel_moment(
        user_id=request.get("user_id", "default_user"),
        moment_type=request.get("type", "tip_of_day")
    )
    return moment

@app.post("/api/voice/speech-to-text")
async def speech_to_text(request: dict):
    """Convert speech to text"""
    from voice_handler import VoiceHandler
    voice = VoiceHandler()
    result = await voice.speech_to_text(
        audio_data=request.get("audio_data"),
        language=request.get("language", "en")
    )
    return result

@app.post("/api/voice/text-to-speech")
async def text_to_speech(request: dict):
    """Convert text to speech"""
    from voice_handler import VoiceHandler
    voice = VoiceHandler()
    result = await voice.text_to_speech(
        text=request.get("text"),
        language=request.get("language", "en"),
        voice=request.get("voice", "friendly")
    )
    return result

@app.post("/api/translate")
async def translate_text(request: dict):
    """Translate text with cultural context"""
    from multilingual_handler import MultilingualHandler
    ml = MultilingualHandler()
    result = await ml.translate(
        text=request.get("text"),
        target_language=request.get("target_language", "en"),
        source_language=request.get("source_language"),
        context=request.get("context")
    )
    return result

@app.post("/api/extract")
async def extract_trip(request: dict):
    result = await doc_intel.extract_trip_info(
        document_data=request.get("document_data"),
        document_type=request.get("document_type")
    )
    return result

@app.post("/api/quote")
async def generate_quote(request: dict):
    """Generate quote - optionally uses Ancileo API if configured"""
    # Check if we should use Ancileo API (if API key is set and user requests it)
    use_ancileo = request.get("use_ancileo_api", False)
    
    if use_ancileo:
        try:
            from ancileo_api import AncileoAPI
            ancileo = AncileoAPI()
            
            # Parse trip details for Ancileo API
            departure_date = request.get("start_date") or request.get("departure_date")
            return_date = request.get("end_date") or request.get("return_date")
            departure_country = request.get("departure_country", "SG")
            arrival_country = request.get("arrival_country") or request.get("destination", "CN")
            
            # Convert destination name to country code if needed
            if arrival_country and len(arrival_country) > 2:
                # Simple mapping - can be enhanced
                country_map = {
                    "singapore": "SG", "china": "CN", "japan": "JP", 
                    "thailand": "TH", "malaysia": "MY", "indonesia": "ID"
                }
                arrival_country = country_map.get(arrival_country.lower(), "CN")
            
            adults = request.get("travelers", 1)
            children = request.get("children_count", 0)
            
            quote_result = await ancileo.get_quote(
                departure_date=departure_date,
                return_date=return_date,
                departure_country=departure_country,
                arrival_country=arrival_country,
                adults_count=adults,
                children_count=children
            )
            
            if quote_result.get("success"):
                # Convert Ancileo response to our format
                ancileo_policies = quote_result.get("policies", [])
                quotes = []
                for policy in ancileo_policies:
                    quotes.append({
                        "plan_name": policy.get("product_name", "Ancileo Policy"),
                        "price": policy.get("price", 0),
                        "currency": policy.get("currency", "SGD"),
                        "recommended_for": policy.get("description", "Travel protection"),
                        "source": "ancileo",
                        "offer_id": policy.get("offer_id"),
                        "product_code": policy.get("product_code"),
                        "coverage": policy.get("coverage", {})
                    })
                
                return {
                    "success": True,
                    "source": "ancileo",
                    "quote_id": quote_result.get("quote_id"),
                    "quotes": quotes,
                    "raw_data": quote_result.get("raw_response")
                }
        except Exception as e:
            logger.error(f"Ancileo API quote failed: {e}")
            # Fall through to local quote generation
    
    # Use local quote generation as fallback or default
    result = await doc_intel.generate_quote(
        destination=request.get("destination"),
        start_date=request.get("start_date"),
        end_date=request.get("end_date"),
        travelers=request.get("travelers", 1),
        ages=request.get("ages", []),
        activities=request.get("activities", []),
        trip_cost=request.get("trip_cost")
    )
    return result

@app.post("/api/compare")
async def compare_policies(request: dict):
    result = await policy_intel.compare_policies(
        criteria=request.get("criteria"),
        policies=request.get("policies", [])
    )
    return result

@app.post("/api/risk")
async def get_risk(request: dict):
    result = await predictive_intel.get_risk_assessment(
        destination=request.get("destination"),
        activities=request.get("activities", []),
        duration=request.get("duration"),
        age=request.get("age"),
        month=request.get("month")
    )
    return result

@app.post("/api/payment/create")
async def create_payment(request: dict):
    result = await payment_handler.create_payment(
        quote_id=request.get("quote_id"),
        policy_name=request.get("policy_name"),
        amount=request.get("amount"),
        currency=request.get("currency", "SGD"),
        user_id=request.get("user_id", "default")
    )
    return result

@app.get("/api/payment/status/{payment_id}")
async def check_payment(payment_id: str):
    result = await payment_handler.check_payment_status(payment_id)
    return result

@app.get("/api/ancileo/policies")
async def get_ancileo_policies(
    departure_country: str = "SG",
    arrival_country: str = "CN",
    departure_date: str = None,
    return_date: str = None,
    adults: int = 1,
    children: int = 0
):
    """Get available policies from Ancileo API"""
    try:
        from ancileo_api import AncileoAPI
        ancileo = AncileoAPI()
        policies = await ancileo.get_available_policies(
            departure_country=departure_country,
            arrival_country=arrival_country,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            children=children
        )
        return {
            "success": True,
            "policies": policies,
            "count": len(policies)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch policies from Ancileo API. Make sure ANCILEO_API_KEY is set in .env"
        }

<<<<<<< Updated upstream
=======
@app.post("/api/user/identify")
async def identify_user(request: dict):
    """Identify existing user or create session profile"""
    email = request.get("email")
    phone = request.get("phone")
    session_id = request.get("session_id") or request.get("user_id", "default_user")
    
    # Try to identify user
    user_identity = user_profile_manager.identify_user(
        email=email,
        phone=phone,
        session_id=session_id
    )
    
    if user_identity.get("found"):
        user = user_identity["user"]
        travel_context = user_profile_manager.get_travel_context(user)
        
        return {
            "success": True,
            "user_found": True,
            "user": user,
            "travel_context": travel_context,
            "needs_data": user_identity.get("needs_data", []),
            "identification_method": user_identity.get("identification_method")
        }
    else:
        # Create new session profile
        profile = user_profile_manager.create_or_update_profile(session_id, {
            "email": email,
            "phone": phone,
            "is_new_user": True
        })
        
        return {
            "success": True,
            "user_found": False,
            "session_profile": profile,
            "needs_data": user_identity.get("needs_data", [])
        }

@app.post("/api/mcp/profile")
async def get_mcp_profile(request: dict):
    """Get comprehensive user profile from Gmail + Instagram via MCP"""
    email = request.get("email")
    instagram_username = request.get("instagram_username")
    
    if not email:
        return {
            "success": False,
            "error": "Email is required"
        }
    
    try:
        profile = await mcp_integrations.get_comprehensive_profile(
            email=email,
            instagram_username=instagram_username
        )
        
        # Ensure success is set
        if "success" not in profile:
            profile["success"] = True
        
        return profile
    except Exception as e:
        logger.error(f"MCP profile fetch failed: {e}", exc_info=True)
        # Return a basic profile even on error so user can continue
        return {
            "success": True,
            "email": email,
            "name": email.split("@")[0].replace(".", " ").title(),
            "policy_tier": "free",
            "profile_complete": True,
            "source": "fallback",
            "error": None
        }

@app.post("/api/user/profile")
async def update_user_profile(request: dict):
    """Update user profile (new users or existing users with missing data)"""
    session_id = request.get("session_id") or request.get("user_id", "default_user")
    user_data = request.get("user_data", {})
    
    # Check if user exists
    email = user_data.get("email")
    if email:
        user_identity = user_profile_manager.identify_user(email=email)
        if user_identity.get("found"):
            # Update existing user (in mock, we just return enriched data)
            user = user_identity["user"]
            enriched = user_profile_manager.enrich_user_data(user, user_data)
            return {
                "success": True,
                "user": enriched,
                "is_existing_user": True
            }
    
    # Create/update session profile
    profile = user_profile_manager.create_or_update_profile(session_id, user_data)
    
    return {
        "success": True,
        "user": profile,
        "is_existing_user": False
    }

@app.post("/api/quote/intelligent")
async def get_intelligent_quote(request: dict):
    """Get quotes with intelligent recommendations using Blocks 1, 2, and 5"""
    # First get quotes
    quote_result = await generate_quote(request)
    
    if not quote_result.get("success"):
        return quote_result
    
    quotes = quote_result.get("quotes", [])
    
    # Get user profile
    email = request.get("email")
    user_profile = None
    if email:
        user_identity = user_profile_manager.identify_user(email=email)
        if user_identity.get("found"):
            user_profile = user_identity["user"]
    
    # Generate intelligent recommendations
    recommendations = None
    try:
        recommendations = await intelligent_recommender.recommend_policies(
            trip_details=quote_result.get("trip_details", {}),
            user_profile=user_profile,
            available_quotes=quotes,
            policy_intel=policy_intel,
            predictive_intel=predictive_intel,
            claims_db=claims_db
        )
    except Exception as e:
        logger.error(f"Intelligent recommendation failed: {e}", exc_info=True)
    
    quote_result["recommendations"] = recommendations
    quote_result["user_profile_found"] = user_profile is not None
    
    return quote_result

@app.post("/api/purchase/seamless")
async def seamless_purchase(request: dict):
    """
    Seamless one-click purchase that adapts to available data
    Automatically handles existing users, collects missing data, and processes purchase
    """
    quote_id = request.get("quote_id")
    offer_id = request.get("offer_id") or request.get("offerId")
    product_code = request.get("product_code") or request.get("productCode")
    email = request.get("email")
    session_id = request.get("session_id") or request.get("user_id", "default_user")
    
    if not offer_id or not quote_id:
        return {
            "success": False,
            "error": "Missing quote_id or offer_id",
            "needs_data": ["quote_id", "offer_id"]
        }
    
    # Identify or create user profile
    user_profile = None
    user_identity = None
    
    if email:
        user_identity = user_profile_manager.identify_user(email=email)
        if user_identity.get("found"):
            user_profile = user_identity["user"]
        else:
            # Try to create profile from request data
            user_data = {
                "email": email,
                "phone": request.get("phone"),
                "firstName": request.get("firstName") or request.get("first_name"),
                "lastName": request.get("lastName") or request.get("last_name"),
                "dateOfBirth": request.get("dateOfBirth") or request.get("date_of_birth"),
                "nationality": request.get("nationality", "SG"),
                "passport": request.get("passport"),
                "cardId": request.get("cardId") or request.get("card_id")
            }
            user_profile = user_profile_manager.create_or_update_profile(session_id, user_data)
    else:
        # Get from session
        user_profile = user_profile_manager.get_user_by_session(session_id)
    
    # Get traveler data
    insureds = request.get("insureds", [])
    
    # If no insureds provided, try to construct from user profile
    if not insureds and user_profile:
        # Try to get from profile or request
        if request.get("travelers_data"):
            insureds = request.get("travelers_data")
        else:
            # Construct from profile
            insureds = [{
                "id": f"insured_1",
                "firstName": user_profile.get("firstName") or user_profile.get("first_name", ""),
                "lastName": user_profile.get("lastName") or user_profile.get("last_name", ""),
                "dateOfBirth": user_profile.get("dateOfBirth") or user_profile.get("date_of_birth"),
                "email": user_profile.get("email", ""),
                "phone": user_profile.get("phone") or user_profile.get("phoneNumber", ""),
                "nationality": user_profile.get("nationality", "SG"),
                "passport": user_profile.get("passport", ""),
                "cardId": user_profile.get("cardId") or user_profile.get("card_id", "")
            }]
    
    # Main contact
    main_contact = {
        "insuredId": user_profile.get("user_id") if user_profile else None,
        "title": request.get("title", "Mr"),
        "firstName": user_profile.get("firstName") or user_profile.get("first_name") or insureds[0].get("firstName", "") if insureds else "",
        "lastName": user_profile.get("lastName") or user_profile.get("last_name") or insureds[0].get("lastName", "") if insureds else "",
        "email": email or (user_profile.get("email") if user_profile else "") or (insureds[0].get("email", "") if insureds else ""),
        "phoneNumber": user_profile.get("phone") or user_profile.get("phoneNumber") or (insureds[0].get("phone", "") if insureds else "")
    }
    
    # Check what data is missing
    missing_data = []
    if not main_contact.get("email"):
        missing_data.append("email")
    if not main_contact.get("phoneNumber"):
        missing_data.append("phone")
    if not insureds or len(insureds) == 0:
        missing_data.append("travelers")
    
    # If critical data missing, return needs_data response
    if missing_data:
        return {
            "success": False,
            "error": "Missing required data for purchase",
            "needs_data": missing_data,
            "collected_data": {
                "user_found": user_profile is not None,
                "has_insureds": len(insureds) > 0,
                "has_main_contact": bool(main_contact.get("email"))
            },
            "message": f"Please provide: {', '.join(missing_data)}"
        }
    
    # Get quote details for pricing
    quote_data = request.get("quote_data", {})
    unit_price = request.get("unit_price") or quote_data.get("price", 0)
    currency = request.get("currency") or quote_data.get("currency", "SGD")
    
    # Process purchase through Ancileo
    try:
        from ancileo_api import AncileoAPI
        ancileo = AncileoAPI()
        
        purchase_result = await ancileo.purchase_policy(
            quote_id=quote_id,
            offer_id=offer_id,
            product_code=product_code,
            product_type="travel-insurance",
            unit_price=unit_price,
            currency=currency,
            quantity=1,
            total_price=unit_price,
            insureds=insureds,
            main_contact=main_contact,
            emergency_contact=request.get("emergency_contact"),
            payment=request.get("payment"),
            partner_reference=request.get("partner_reference"),
            options=request.get("options"),
            market=request.get("market", "SG"),
            language_code=request.get("language_code", "en")
        )
        
        # If purchase successful, update user profile
        if purchase_result.get("success") and user_profile:
            # Record purchase in travel history
            if not user_profile.get("travel_history"):
                user_profile["travel_history"] = []
            
            user_profile["travel_history"].append({
                "destination": quote_data.get("destination", "Unknown"),
                "date": datetime.now().isoformat(),
                "policy": quote_data.get("plan_name", "Unknown"),
                "policy_number": purchase_result.get("policy_number"),
                "claim_filed": False
            })
        
        return purchase_result
    
    except Exception as e:
        logger.error(f"Seamless purchase failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": "Purchase processing failed. Please try again."
        }

>>>>>>> Stashed changes
@app.post("/api/ancileo/purchase")
async def purchase_ancileo_policy(request: dict):
    """Purchase policy through Ancileo API (after payment)"""
    try:
        from ancileo_api import AncileoAPI
        ancileo = AncileoAPI()
        result = await ancileo.purchase_policy(
            quote_id=request.get("quote_id"),
            offer_id=request.get("offer_id"),
            product_code=request.get("product_code"),
            product_type=request.get("product_type", "travel-insurance"),
            unit_price=request.get("unit_price"),
            currency=request.get("currency", "SGD"),
            quantity=request.get("quantity", 1),
            insureds=request.get("insureds", [])
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/tts/clean")
async def clean_text_for_speech(request: dict):
    """Clean and prepare text for browser TTS with optimal formatting"""
    try:
        text = request.get("text", "")
        if not text:
            return {"error": "No text provided"}
        
        # Clean text for better speech synthesis
        import re
        
        # Remove emojis and special unicode
        cleaned = text
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002600-\U000026FF"  # misc symbols
            u"\U00002700-\U000027BF"  # dingbats
            "]+", flags=re.UNICODE)
        cleaned = emoji_pattern.sub('', cleaned)
        
        # Remove markdown formatting
        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)  # Bold
        cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)  # Italic
        cleaned = re.sub(r'━+', ' ', cleaned)  # Separators to space
        cleaned = re.sub(r'[•▪▫◦]', '- ', cleaned)  # Bullets
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)  # Multiple newlines
        cleaned = re.sub(r'\[IMAGE:[^\]]+\]', '', cleaned)  # Image tags
        cleaned = re.sub(r'https?://[^\s]+', '', cleaned)  # URLs
        cleaned = cleaned.strip()
        
        return {
            "success": True,
            "text": cleaned,
            "length": len(cleaned)
        }
    except Exception as e:
        logger.error(f"Text cleaning error: {e}")
        return {
            "success": False,
            "error": str(e),
            "text": text[:4000] if text else ""
        }

if __name__ == "__main__":
    # Use port from environment variable or default to 8002
    port = int(os.getenv("PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port)

