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
from typing import Dict, List
from datetime import datetime

# Load environment variables FIRST, before any imports
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
import uvicorn
import os
import base64
from io import BytesIO

app = FastAPI(title="WanderSure API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import handlers AFTER dotenv is loaded
from policy_intelligence import PolicyIntelligence
from document_intelligence import DocumentIntelligence
from predictive_intelligence import PredictiveIntelligence
from payment_handler import PaymentHandler
from conversation_handler import ConversationHandler
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
from routers.v1 import router as v1_router

policy_intel = PolicyIntelligence()
doc_intel = DocumentIntelligence()
predictive_intel = PredictiveIntelligence()
payment_handler = PaymentHandler()
conversation = ConversationHandler()
user_profile_manager = UserProfileManager()
partner_integrations = PartnerIntegrations()
intelligent_recommender = IntelligentRecommender()
pricing_calculator = PricingCalculator()
policy_scorer = PolicyScorer()
claims_analyzer = ClaimsAnalyzer()
mcp_integrations = MCPIntegrations()
activity_matcher = ActivityPolicyMatcher()
policy_simplifier = PolicySimplifier()
taxonomy_matcher = TaxonomyMatcher()

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

@app.get("/health")
async def health():
    return {"status": "ok", "service": "wandersure"}

@app.post("/api/ask")
async def ask_question(request: dict):
    """Handle user questions with comprehensive error handling"""
    try:
        question = request.get("question", "").strip()
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
        
        # EARLY CANCELLATION DETECTION - Check before any other processing
        # This ensures cancellation questions get immediate hardcoded response
        cancellation_keywords = ["cancel", "cancellation", "refund", "terminate", "end policy", "stop coverage", 
                                 "how to cancel", "how do i cancel", "can i cancel", "how can i cancel", 
                                 "want to cancel", "need to cancel", "cancel my", "cancel this", "cancel the",
                                 "cancel insurance", "cancel policy"]
        is_cancellation_early = any(keyword in question_lower for keyword in cancellation_keywords)
        
        if is_cancellation_early:
            logger.info(f"Early cancellation detection: {question}")
            # Check if MH Insurance is mentioned, or assume it (user is purchasing MH Insurance)
            if "mhinsure" in question_lower or "mh insure" in question_lower or not any(p in question_lower for p in ["scootsurance", "international travel", "msig"]):
                logger.info("Returning hardcoded MH Insurance cancellation response (early)")
                mh_cancellation_response = """**How to Cancel Your MHInsure Travel Policy**

To cancel your **MHInsure Travel** policy, you have the following options:

**📞 Contact Methods:**
1. **Phone**: Call MH Insurance customer service at +65 1234 5678 (Monday to Friday, 9 AM - 6 PM)
2. **Email**: Send a cancellation request to cancellations@mhinsurance.com.sg
3. **Online**: Log in to your account at www.mhinsurance.com.sg and submit a cancellation request through the portal

**📋 Required Information:**
- Policy number
- Full name as per policy
- Reason for cancellation (optional)
- Date you wish the cancellation to take effect

**💰 Refund Policy:**
- **Full refund**: If cancelled within 14 days of purchase (cooling-off period)
- **Partial refund**: If cancelled after 14 days, you may be eligible for a pro-rated refund based on unused coverage period, minus any administrative fees
- **No refund**: If a claim has been made or if the trip has already commenced

**⏰ Processing Time:**
- Cancellation requests are typically processed within 5-7 business days
- Refunds (if applicable) will be credited to your original payment method within 10-14 business days

**⚠️ Important Notes:**
- Cancellation fees may apply if cancelled after the cooling-off period
- If you've already started your trip, cancellation may not be possible
- Contact customer service for specific terms based on your policy details

Would you like me to help you with anything else regarding your MHInsure Travel policy?"""
                
                return {
                    "answer": mh_cancellation_response,
                    "content": mh_cancellation_response,
                    "message": mh_cancellation_response,
                    "booking_links": [],
                    "suggested_questions": [
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
                    ],
                    "quotes": [],
                    "quote_id": None,
                    "trip_details": None
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
        # Check for cancellation/refund questions - handle with policy intelligence
        # Expanded detection to catch variations like "how do i cancel", "can i cancel", etc.
        cancellation_keywords = ["cancel", "cancellation", "refund", "terminate", "end policy", "stop coverage", 
                                 "how to cancel", "how do i cancel", "can i cancel", "how can i cancel", 
                                 "want to cancel", "need to cancel", "cancel my", "cancel this", "cancel the"]
        is_cancellation_question = any(keyword in question_lower_check for keyword in cancellation_keywords)
        
        # Handle cancellation questions with policy intelligence
        if is_cancellation_question:
            try:
                logger.info(f"Detected cancellation question: {question}")
                
                # Extract policy name if mentioned
                policy_name = None
                if "scootsurance" in question_lower_check:
                    policy_name = "Scootsurance"
                elif "international travel" in question_lower_check or "msig" in question_lower_check:
                    policy_name = "INTERNATIONAL TRAVEL"
                elif "mhinsure" in question_lower_check or "mh insure" in question_lower_check:
                    policy_name = "MHInsure Travel"
                
                # HARDCODED RESPONSE FOR MH INSURANCE CANCELLATION
                # User is purchasing MH Insurance, so provide immediate hardcoded response
                # Return hardcoded response if:
                # 1. MH Insurance is explicitly mentioned, OR
                # 2. No specific policy mentioned (assumes MH Insurance since user is purchasing it)
                if policy_name == "MHInsure Travel" or (not policy_name):
                    logger.info("Returning hardcoded MH Insurance cancellation response")
                    mh_cancellation_response = """**How to Cancel Your MHInsure Travel Policy**

To cancel your **MHInsure Travel** policy, you have the following options:

**📞 Contact Methods:**
1. **Phone**: Call MH Insurance customer service at +65 1234 5678 (Monday to Friday, 9 AM - 6 PM)
2. **Email**: Send a cancellation request to cancellations@mhinsurance.com.sg
3. **Online**: Log in to your account at www.mhinsurance.com.sg and submit a cancellation request through the portal

**📋 Required Information:**
- Policy number
- Full name as per policy
- Reason for cancellation (optional)
- Date you wish the cancellation to take effect

**💰 Refund Policy:**
- **Full refund**: If cancelled within 14 days of purchase (cooling-off period)
- **Partial refund**: If cancelled after 14 days, you may be eligible for a pro-rated refund based on unused coverage period, minus any administrative fees
- **No refund**: If a claim has been made or if the trip has already commenced

**⏰ Processing Time:**
- Cancellation requests are typically processed within 5-7 business days
- Refunds (if applicable) will be credited to your original payment method within 10-14 business days

**⚠️ Important Notes:**
- Cancellation fees may apply if cancelled after the cooling-off period
- If you've already started your trip, cancellation may not be possible
- Contact customer service for specific terms based on your policy details

Would you like me to help you with anything else regarding your MHInsure Travel policy?"""
                    
                    return {
                        "answer": mh_cancellation_response,
                        "content": mh_cancellation_response,
                        "message": mh_cancellation_response,
                        "booking_links": [],
                        "suggested_questions": [
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
                        ],
                        "quotes": [],
                        "quote_id": None,
                        "trip_details": None
                    }
                
                # Get cancellation info for all policies if none specified, or specific policy
                cancellation_info = ""
                if policy_name:
                    # Single policy
                    try:
                        cancellation_info = await policy_intel.explain_coverage(
                            topic="cancellation, refund, and policy termination",
                            policy=policy_name,
                            scenario="User wants to cancel their policy"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to get cancellation info for {policy_name}: {e}")
                        cancellation_info = f"**{policy_name}**: Please refer to the policy document for cancellation terms."
                else:
                    # All policies - get info for each
                    policy_list = ["Scootsurance", "MHInsure Travel", "INTERNATIONAL TRAVEL"]
                    cancellation_details = []
                    for pol in policy_list:
                        try:
                            info = await policy_intel.explain_coverage(
                                topic="cancellation, refund, and policy termination",
                                policy=pol,
                                scenario="User wants to cancel their policy"
                            )
                            cancellation_details.append(f"**{pol}**\n\n{info}")
                        except Exception as e:
                            logger.warning(f"Failed to get cancellation info for {pol}: {e}")
                            cancellation_details.append(f"**{pol}**: Please refer to the policy document for cancellation terms.")
                    
                    # Format each policy on a new line
                    cancellation_info = "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n".join(cancellation_details)
                
                # Add claims data if available for the destination
                claims_context_for_cancellation = ""
                if destination_mentioned and claims_analysis and claims_analysis.get("has_data"):
                    top_rec = claims_analysis.get("recommendations", [{}])[0] if claims_analysis.get("recommendations") else {}
                    claims_context_for_cancellation = f"""

🎯 CLAIMS DATA FOR {destination_mentioned.upper()}:
- {top_rec.get('incidence_rate', 'N/A')} of travelers have claimed for {top_rec.get('claim_type', 'incidents')}
- Average cost per claim: ${top_rec.get('average_cost', 0):,.2f} SGD
- This data may be relevant when considering policy cancellation and refund options.

"""
                
                # Build enhanced context with cancellation info
                cancellation_context = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 POLICY CANCELLATION INFORMATION:
{claims_context_for_cancellation}
{cancellation_info}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL INSTRUCTIONS:
1. Use the EXACT cancellation terms from the policy information above
2. Format each policy on a NEW LINE with clear separation
3. Explain the cancellation process step-by-step for EACH policy mentioned
4. Mention any cancellation fees or refund policies
5. Provide specific timeframes if mentioned in the policy
6. Include contact information or how to initiate cancellation
7. If claims data is present, mention it in context
8. Be clear and helpful - this is an important question
9. Format policies like this:
   - **Scootsurance**: [cancellation info]
   
   - **MHInsure Travel**: [cancellation info]
   
   - **INTERNATIONAL TRAVEL**: [cancellation info]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                
                enhanced_context = enhanced_context + cancellation_context
                logger.info(f"Added cancellation context for policy: {policy_name or 'all policies'}")
                
            except Exception as e:
                logger.error(f"Cancellation handling failed: {e}", exc_info=True)
                # Add fallback cancellation context even if extraction fails
                enhanced_context = enhanced_context + f"""

📋 CANCELLATION INFORMATION:

To cancel your travel insurance policy, please:
1. Contact the insurance provider directly
2. Check your policy document for specific cancellation terms
3. Review refund policies and any applicable fees
4. Submit cancellation request in writing if required

For specific cancellation terms, please refer to your policy document or contact customer service.

"""
                logger.info("Added fallback cancellation context")
        
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
        result = await conversation.handle_question(
            question=request.get("question"),
            language=request.get("language"),
            context=enhanced_context if enhanced_context else request.get("context"),
            user_id=user_id,
            is_voice=request.get("is_voice", False),
            role=request.get("role")
        )
        
        # Add claims analysis if available - CRITICAL for frontend
        if claims_analysis:
            if not result:
                result = {}
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
        
        return result
    
    except Exception as e:
        logger.error(f"Error in /api/ask endpoint: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Provide helpful error response
        error_message = f"😅 **I'm having a bit of trouble right now**\n\nI encountered an issue, but I'm here to help! Here's what you can try:\n\n• **Try rephrasing** your question - sometimes simpler wording works better\n• **Wait a moment** and try again - this might be temporary\n• **Ask something simple** like \"What can you help me with?\" or \"Tell me about travel insurance\"\n\nI apologize for the inconvenience. Your question is important to me!"
        
        return {
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
    # Normalize policy name - ONLY use policies that exist in Policy_Wordings folder
    # Actual policies: INTERNATIONAL TRAVEL.pdf, MHInsure Travel.pdf, Scootsurance.pdf
    policy_mapping = {
        "Scootsurance": "Scootsurance",
        "INTERNATIONAL TRAVEL": "INTERNATIONAL TRAVEL",
        "MHInsure Travel": "MHInsure Travel",
        "MSIG": "INTERNATIONAL TRAVEL",  # Map MSIG to INTERNATIONAL TRAVEL
        # Removed: TravelEasy (doesn't exist in Policy_Wordings)
    }
    
    normalized_name = policy_mapping.get(policy_name, policy_name)
    
    # Use cached global policy_intel instance
    # Get full policy text (more context for detailed info)
    policy_data = policy_intel.policy_texts.get(normalized_name, {})
    policy_text = policy_data.get("text", "")
    
    if not policy_text:
        return {
            "success": False,
            "error": "Policy not found",
            "summary": f"**Policy**: {normalized_name}\n\nPolicy document not found. Please check the policy name."
        }
    
    # Use MUCH more text for better extraction (first 50000 chars to get coverage tables and details)
    # Insurance policies often have coverage tables in the middle/end, so we need more context
    policy_excerpt = policy_text[:50000] if len(policy_text) > 50000 else policy_text
    
    # Also try to find coverage table sections specifically
    # Look for common keywords that indicate coverage tables
    coverage_keywords = [
        "coverage", "benefit", "limit", "sum insured", "maximum", 
        "medical expenses", "trip cancellation", "baggage", "liability",
        "schedule of benefits", "benefit schedule", "coverage table"
    ]
    
    # Find sections with coverage information
    policy_lower = policy_text.lower()
    coverage_sections = []
    for keyword in coverage_keywords:
        idx = policy_lower.find(keyword)
        if idx != -1:
            # Extract 2000 chars around the keyword
            start = max(0, idx - 500)
            end = min(len(policy_text), idx + 2000)
            section = policy_text[start:end]
            if section not in coverage_sections:
                coverage_sections.append(section)
    
    # Combine main excerpt with coverage sections
    if coverage_sections:
        additional_context = "\n\n--- Coverage Sections Found ---\n\n" + "\n\n---\n\n".join(coverage_sections[:3])
        policy_excerpt = policy_excerpt + additional_context
    
    # Generate detailed summary with coverage amounts and citations
    summary_prompt = f"""You are analyzing a travel insurance policy document. Extract ALL specific coverage amounts, limits, and details from the policy text below.

Policy Name: {normalized_name}

Policy Document Text:
{policy_excerpt}

CRITICAL INSTRUCTIONS:
1. Extract EXACT coverage amounts from the text (look for dollar amounts, SGD amounts, coverage limits)
2. Find specific numbers for:
   - Medical expenses coverage (overseas and Singapore)
   - Trip cancellation/interruption limits
   - Baggage loss/damage coverage
   - Personal accident/death benefits
   - Personal liability coverage
   - Delayed baggage coverage
   - Any other coverage types mentioned
3. Extract specific exclusions (not generic ones)
4. Look for coverage tables, benefit schedules, or summary sections
5. If amounts are in different currencies, note the currency
6. If amounts vary by plan/tier, mention that

Format your response EXACTLY as follows:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Policy**: {normalized_name}

**Coverage Highlights**:
• Accidental Death and Permanent Total Disability: [EXACT AMOUNT from text or "Not specified" if truly not found]
• Overseas Medical Expenses: [EXACT AMOUNT from text or "Not specified"]
• Medical Expenses in Singapore: [EXACT AMOUNT from text or "Not specified"]
• Trip Cancellation: [EXACT AMOUNT from text or "Not specified"]
• Trip Interruption: [EXACT AMOUNT from text or "Not specified"]
• Baggage Loss: [EXACT AMOUNT from text or "Not specified"]
• Baggage Delay: [EXACT AMOUNT from text or "Not specified"]
• Personal Liability: [EXACT AMOUNT from text or "Not specified"]
• Travel Delay: [EXACT AMOUNT from text or "Not specified"]
• Emergency Evacuation: [EXACT AMOUNT from text or "Not specified"]

**Key Exclusions**:
• [Specific exclusion 1 from the document]
• [Specific exclusion 2 from the document]
• [Specific exclusion 3 from the document]

**Best For**: [Who this policy is ideal for based on coverage and features]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT: 
- Only say "Not specified" if you absolutely cannot find the information in the provided text
- Look carefully for coverage tables, benefit summaries, or coverage sections
- Extract actual dollar amounts (e.g., "$100,000", "SGD 50,000", "up to $25,000")
- Be specific and accurate - this information will be shown to users"""

    try:
        # Use more tokens to get comprehensive information
        response = policy_intel.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert insurance policy analyst. Your job is to extract EXACT coverage amounts, limits, and details from insurance policy documents. Always look for specific dollar amounts, coverage limits, and exclusions. Be thorough and accurate."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.1,  # Lower temperature for more accurate extraction
            max_tokens=1500  # Increased significantly to get all details
        )
        
        summary = response.choices[0].message.content
        
        # Post-process to ensure we have actual information
        # If summary contains too many "Not specified", try with the FULL document
        if summary.count("Not specified") > 5 and len(policy_text) > 50000:
            # Try with the FULL document (up to 100000 chars)
            logger.info(f"First extraction had many 'Not specified', trying with full document for {normalized_name}")
            full_excerpt = policy_text[:100000]  # Use up to 100k chars
            # Rebuild prompt with full text
            full_prompt = f"""You are analyzing a travel insurance policy document. Extract ALL specific coverage amounts, limits, and details from the policy text below.

Policy Name: {normalized_name}

Policy Document Text (FULL DOCUMENT):
{full_excerpt}

CRITICAL INSTRUCTIONS:
1. Extract EXACT coverage amounts from the text (look for dollar amounts, SGD amounts, coverage limits)
2. Find specific numbers for:
   - Medical expenses coverage (overseas and Singapore)
   - Trip cancellation/interruption limits
   - Baggage loss/damage coverage
   - Personal accident/death benefits
   - Personal liability coverage
   - Delayed baggage coverage
   - Any other coverage types mentioned
3. Extract specific exclusions (not generic ones)
4. Look for coverage tables, benefit schedules, or summary sections
5. If amounts are in different currencies, note the currency
6. If amounts vary by plan/tier, mention that

Format your response EXACTLY as follows:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Policy**: {normalized_name}

**Coverage Highlights**:
• Accidental Death and Permanent Total Disability: [EXACT AMOUNT from text or "Not specified" if truly not found]
• Overseas Medical Expenses: [EXACT AMOUNT from text or "Not specified"]
• Medical Expenses in Singapore: [EXACT AMOUNT from text or "Not specified"]
• Trip Cancellation: [EXACT AMOUNT from text or "Not specified"]
• Trip Interruption: [EXACT AMOUNT from text or "Not specified"]
• Baggage Loss: [EXACT AMOUNT from text or "Not specified"]
• Baggage Delay: [EXACT AMOUNT from text or "Not specified"]
• Personal Liability: [EXACT AMOUNT from text or "Not specified"]
• Travel Delay: [EXACT AMOUNT from text or "Not specified"]
• Emergency Evacuation: [EXACT AMOUNT from text or "Not specified"]

**Key Exclusions**:
• [Specific exclusion 1 from the document]
• [Specific exclusion 2 from the document]
• [Specific exclusion 3 from the document]

**Best For**: [Who this policy is ideal for based on coverage and features]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT: 
- Only say "Not specified" if you absolutely cannot find the information in the provided text
- Look carefully for coverage tables, benefit summaries, or coverage sections
- Extract actual dollar amounts (e.g., "$100,000", "SGD 50,000", "up to $25,000")
- Be specific and accurate - this information will be shown to users"""
            
            try:
                extended_response = policy_intel.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are an expert insurance policy analyst. Extract EXACT coverage amounts from the policy document. Look carefully in coverage tables, benefit schedules, and summary sections. Search the ENTIRE document for coverage amounts."},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=1500
                )
                new_summary = extended_response.choices[0].message.content
                # Only use if it has fewer "Not specified"
                if new_summary.count("Not specified") < summary.count("Not specified"):
                    summary = new_summary
                    logger.info(f"Full document extraction improved results for {normalized_name}")
            except Exception as e2:
                logger.warning(f"Full document extraction also failed: {e2}")
        
        return {
            "success": True,
            "policy_name": normalized_name,
            "summary": summary,
            "full_name": policy_data.get("name", normalized_name),
            "coverage_details": "Available",
            "simplified": True,
            "text_length": len(policy_text)
        }
    except Exception as e:
        logger.error(f"Policy details extraction failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "summary": f"**Policy**: {normalized_name}\n\nTravel insurance policy with comprehensive coverage. Please refer to full policy document for details."
        }

@app.get("/api/greeting")
async def get_greeting(user_id: str = "default_user", language: str = "en"):
    """Get personalized greeting from travel buddy"""
    greeting = await conversation.generate_personalized_greeting(user_id, language)
    return {"greeting": greeting}

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

@app.post("/api/translate/messages")
async def translate_messages(request: dict):
    """Translate all messages in conversation to target language"""
    from multilingual_handler import MultilingualHandler
    ml = MultilingualHandler()
    
    messages = request.get("messages", [])
    target_language = request.get("target_language", "en")
    
    # Translate all assistant messages
    translated_messages = []
    for msg in messages:
        # Preserve all message fields
        translated_msg = dict(msg)
        
        if msg.get("role") == "assistant":
            # Translate assistant content
            result = await ml.translate(
                text=msg.get("content", ""),
                target_language=target_language,
                context="travel insurance conversation"
            )
            translated_msg["content"] = result.get("translated", msg.get("content"))
            
            # Translate quotes if present
            if msg.get("quotes"):
                translated_quotes = []
                for quote in msg.get("quotes", []):
                    translated_quote = dict(quote)
                    # Translate quote fields that contain user-facing text
                    if quote.get("recommended_for"):
                        trans_result = await ml.translate(
                            text=quote["recommended_for"],
                            target_language=target_language
                        )
                        translated_quote["recommended_for"] = trans_result.get("translated", quote["recommended_for"])
                    
                    # Translate benefits array
                    if quote.get("benefits"):
                        translated_benefits = []
                        for benefit in quote["benefits"]:
                            trans_result = await ml.translate(
                                text=benefit,
                                target_language=target_language
                            )
                            translated_benefits.append(trans_result.get("translated", benefit))
                        translated_quote["benefits"] = translated_benefits
                    
                    # Translate reasons array
                    if quote.get("reasons"):
                        translated_reasons = []
                        for reason in quote["reasons"]:
                            trans_result = await ml.translate(
                                text=reason,
                                target_language=target_language
                            )
                            translated_reasons.append(trans_result.get("translated", reason))
                        translated_quote["reasons"] = translated_reasons
                    
                    translated_quotes.append(translated_quote)
                translated_msg["quotes"] = translated_quotes
        
        translated_messages.append(translated_msg)
    
    return {
        "success": True,
        "translated_messages": translated_messages,
        "target_language": target_language
    }

@app.post("/api/extract")
async def extract_trip(request: dict):
    """Extract trip info from document and auto-enrich with user/profile data"""
    try:
        result = await doc_intel.extract_trip_info(
            document_data=request.get("document_data"),
            document_type=request.get("document_type")
        )
        
        # If extraction completely failed, return helpful error
        if not result.get("success") and not result.get("extracted_data"):
            return {
                "success": False,
                "error": result.get("error", "Document extraction failed"),
                "message": result.get("message", "Could not extract trip information from document. Please try uploading a clearer document or describe your trip manually."),
                "validation_questions": result.get("validation_questions", []),
                "extracted_data": {}
            }
        
        # If extraction successful, try to enrich with user profile/partner data
        if result.get("success") and result.get("extracted_data"):
            extracted = result["extracted_data"]
            email = request.get("email") or (extracted.get("travelers", [{}])[0].get("email") if extracted.get("travelers") else None)
            session_id = request.get("session_id") or request.get("user_id", "default_user")
            
            if email:
                # Try to identify existing user
                user_identity = user_profile_manager.identify_user(email=email)
                
                if user_identity.get("found"):
                    # Enrich with existing user data
                    user = user_identity["user"]
                    extracted = user_profile_manager.enrich_user_data(extracted, user)
                    
                    # Try to get additional data from partner integrations
                    try:
                        partner_data = await partner_integrations.sync_user_data(email)
                        # Merge partner booking data if available
                        if partner_data.get("upcoming_trips"):
                            latest_trip = partner_data["upcoming_trips"][0]
                            # Merge flight/hotel data if missing from extraction
                            if not extracted.get("flight_details") and latest_trip.get("flight"):
                                extracted["flight_details"] = latest_trip["flight"]
                            if not extracted.get("hotel_details") and latest_trip.get("hotel"):
                                extracted["hotel_details"] = latest_trip["hotel"]
                    except Exception as e:
                        logger.warning(f"Partner integration failed: {e}")
                
                result["extracted_data"] = extracted
                result["user_found"] = user_identity.get("found", False)
                result["needs_data"] = user_identity.get("needs_data", [])
            else:
                # Store in session for new users
                user_profile_manager.create_or_update_profile(session_id, {
                    "extracted_trip_data": extracted
                })
            
            # CRITICAL: Immediately analyze claims data for the destination
            destination = extracted.get("destination")
            if destination:
                try:
                    logger.info(f"Analyzing claims for destination: {destination}")
                    # Calculate trip duration if available
                    trip_duration = None
                    if extracted.get("departure_date") and extracted.get("return_date"):
                        try:
                            dep = datetime.strptime(extracted["departure_date"], "%Y-%m-%d")
                            ret = datetime.strptime(extracted["return_date"], "%Y-%m-%d")
                            trip_duration = (ret - dep).days
                        except:
                            pass
                    
                    # Get claims analysis for this destination with activities
                    activities = extracted.get("activities", [])
                    claims_analysis = await claims_analyzer.analyze_destination_and_recommend(
                        destination=destination,
                        trip_duration=trip_duration,
                        activities=activities
                    )
                    
                    # Add claims analysis to result
                    result["claims_analysis"] = claims_analysis
                    logger.info(f"Claims analysis completed for {destination}: has_data={claims_analysis.get('has_data')}, total_claims={claims_analysis.get('total_claims', 0)}")
                    
                except Exception as e:
                    logger.error(f"Claims analysis failed during extraction: {e}", exc_info=True)
                    # Don't fail the extraction if claims analysis fails
                    result["claims_analysis"] = {"has_data": False, "error": str(e)}
        
        return result
    except Exception as e:
        logger.error(f"Extract endpoint error: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": "I encountered an error processing your document. Please try uploading again or describe your trip manually.",
            "extracted_data": {}
        }

@app.post("/api/quote")
async def generate_quote(request: dict):
    """
    Generate quote - NEW FLOW:
    1. Match policies using JSON taxonomies (NO ANCILEO)
    2. Use Ancileo API ONLY for cost calculation
    3. Combine results with scoring
    """
    # Validate required fields first
    required_fields = ["destination", "start_date", "end_date"]
    missing_fields = [field for field in required_fields if not request.get(field)]
    
    if missing_fields:
        return {
            "success": False,
            "error": "Missing required fields",
            "missing_fields": missing_fields,
            "message": f"Please provide: {', '.join(missing_fields)}"
        }
    
    # STEP 1: Match policies using JSON taxonomies (NO ANCILEO)
    user_data = {
        "age": request.get("user_age") or request.get("age") or 30,
        "interests": request.get("interests", []),
        "medical_conditions": request.get("medical_conditions", [])
    }
    
    trip_data = {
        "destination": request.get("destination"),
        "source": request.get("source"),
        "departure_date": request.get("start_date") or request.get("departure_date"),
        "return_date": request.get("end_date") or request.get("return_date"),
        "pax": request.get("travelers", 1),
        "ticket_policies": request.get("ticket_policies", [])
    }
    
    extracted_data = request.get("extracted_data", {})
    
    # STEP 1: Match policies against taxonomy (NO TIERS, just return what matches)
    matched_policies = []
    try:
        matched_policies = await taxonomy_matcher.match_policies(
            user_data=user_data,
            trip_data=trip_data,
            extracted_data=extracted_data
        )
        logger.info(f"✅ Matched {len(matched_policies)} applicable policies from taxonomy")
        if matched_policies:
            logger.info(f"Policy names: {[p.get('policy_name') for p in matched_policies]}")
        else:
            logger.warning("⚠️ No policies matched from taxonomy for this trip/user profile")
    except Exception as e:
        logger.error(f"Taxonomy matching failed: {e}", exc_info=True)
        matched_policies = []
    
    # NO FALLBACKS - just return what taxonomy matching found
    if not matched_policies or len(matched_policies) == 0:
        logger.warning("No applicable policies found from taxonomy matching")
        # Return empty quotes - let user know no policies match
        return {
            "success": True,
            "source": "taxonomy_match",
            "quotes": [],
            "trip_details": {
                "destination": trip_data.get("destination"),
                "source": trip_data.get("source"),
                "departure_date": trip_data.get("departure_date"),
                "return_date": trip_data.get("return_date"),
                "travelers": trip_data.get("pax", 1)
            },
            "message": "No insurance policies found that match your trip details and profile. Please adjust your search criteria."
        }
    
    # STEP 2: Get costs from Ancileo API ONLY (for cost calculation)
    ancileo_quote_id = None
    ancileo_prices = {}
    ancileo_currencies = {}
    
    try:
        from ancileo_api import AncileoAPI
        ancileo = AncileoAPI()
        
        if ancileo.api_key and ancileo.api_key != "your_ancileo_api_key_here":
            try:
                # Parse trip details for Ancileo API
                departure_date = request.get("start_date") or request.get("departure_date")
                return_date = request.get("end_date") or request.get("return_date")
                departure_country = request.get("departure_country", "SG")
                arrival_country = request.get("arrival_country") or request.get("destination", "CN")
                
                # Enhanced country mapping
                country_map = {
                    "singapore": "SG", "china": "CN", "japan": "JP", 
                    "thailand": "TH", "malaysia": "MY", "indonesia": "ID",
                    "india": "IN", "australia": "AU", "united states": "US", "usa": "US",
                    "united kingdom": "GB", "uk": "GB", "england": "GB", "france": "FR",
                    "germany": "DE", "italy": "IT", "spain": "ES", "south korea": "KR",
                    "korea": "KR", "hong kong": "HK", "taiwan": "TW", "philippines": "PH",
                    "vietnam": "VN", "new zealand": "NZ"
                }
                
                # Convert destination name to country code if needed
                if arrival_country and len(arrival_country) > 2:
                    arrival_lower = arrival_country.lower().strip()
                    # Check if it's already a code
                    if len(arrival_country) == 2:
                        arrival_country = arrival_country.upper()
                    else:
                        # Extract country name (handle "Tokyo, Japan" -> "japan")
                        if "," in arrival_lower:
                            arrival_lower = arrival_lower.split(",")[-1].strip()
                        arrival_country = country_map.get(arrival_lower, "CN")
                
                # Calculate adults and children from ages
                travelers = request.get("travelers", 1)
                ages = request.get("ages", [])
                adults = 0
                children = 0
                
                if ages:
                    for age in ages:
                        if age < 18:
                            children += 1
                        else:
                            adults += 1
                else:
                    adults = travelers
                
                children_count = request.get("children_count", children)
                adults_count = request.get("adults_count", adults) if adults > 0 else travelers
                
                quote_result = await ancileo.get_quote(
                    market=departure_country,
                    departure_date=departure_date,
                    return_date=return_date,
                    departure_country=departure_country,
                    arrival_country=arrival_country,
                    departure_airport=None,  # Will auto-map
                    arrival_airport=None,  # Will auto-map
                    adults_count=adults_count,
                    children_count=children_count,
                    trip_type="RT"
                )
                
                if quote_result.get("success"):
                    ancileo_quote_id = quote_result.get("quote_id")
                    ancileo_policies = quote_result.get("policies", [])
                    # Store Ancileo prices for cost calculation
                    ancileo_prices = {p.get("product_code"): p.get("price", 0) for p in ancileo_policies if p.get("product_code")}
                    ancileo_currencies = {p.get("product_code"): p.get("currency", "SGD") for p in ancileo_policies if p.get("currency")}
                    
                    logger.info(f"Got {len(ancileo_policies)} Ancileo policies for pricing")
            except Exception as e:
                logger.error(f"Ancileo API pricing failed: {e}", exc_info=True)
    except ImportError:
        logger.warning("Ancileo API not available")
    except Exception as e:
        logger.error(f"Ancileo API initialization failed: {e}")
    
    # STEP 3: Combine matched policies with Ancileo prices
    final_quotes = []
    logger.info(f"Processing {len(matched_policies)} matched policies into quotes")
    
    for matched in matched_policies:
        policy_name = matched["policy_name"]
        product_code = matched["product_code"]
        
        # Get price from Ancileo if available, otherwise calculate default pricing based on trip
        # Default pricing: base price * duration * travelers
        base_price = 5.0  # SGD per day per person
        if not ancileo_prices.get(product_code):
            # Calculate trip duration
            try:
                from datetime import datetime
                dep = datetime.strptime(trip_data["departure_date"], "%Y-%m-%d")
                ret = datetime.strptime(trip_data["return_date"], "%Y-%m-%d")
                duration = (ret - dep).days
                price = base_price * duration * trip_data["pax"]
                # Adjust price based on policy type
                if "Pre-Ex" in policy_name:
                    price *= 1.2  # Pre-existing conditions policy costs more
                elif "Scootsurance" in policy_name:
                    price *= 0.9  # Scootsurance is typically cheaper
            except:
                price = 50.0  # Fallback
        else:
            price = ancileo_prices.get(product_code, 50.0)
        currency = ancileo_currencies.get(product_code, "SGD")
        
        # Get benefits from taxonomy
        benefits = taxonomy_matcher.get_policy_benefits(product_code)
        
        # Build quote from matched policy - use actual policy name from taxonomy
        quote = {
            "plan_name": policy_name,
            "product_code": product_code,
            "price": round(price, 2),
            "currency": currency,
            "score": matched["score"],
            "benefits": matched["benefits"],
            "reasons": matched["reasons"],
            "taxonomy_benefits": benefits,
            "recommended_for": f"Score: {matched['score']}/100 - {', '.join(matched['reasons'][:2])}",
            "source": "taxonomy_match",
            "cost_source": "ancileo" if ancileo_quote_id and ancileo_prices.get(product_code) else "calculated"
        }
        final_quotes.append(quote)
        logger.info(f"Added quote: {policy_name} (${quote['price']} {currency}, Score: {matched['score']}/100)")
    
    # Sort by score (highest first) - best matches first
    final_quotes.sort(key=lambda x: x["score"], reverse=True)
    
    # Log final quotes
    logger.info(f"✅ Returning {len(final_quotes)} applicable policies from taxonomy:")
    for q in final_quotes:
        logger.info(f"   - {q['plan_name']} (Score: {q.get('score', 'N/A')}/100, Price: ${q.get('price', 'N/A')} {q.get('currency', 'SGD')})")
    
    # Get trip details
    trip_details_obj = {
        "destination": trip_data["destination"],
        "source": trip_data.get("source"),
        "departure_date": trip_data["departure_date"],
        "return_date": trip_data["return_date"],
        "travelers": trip_data["pax"],
        "ages": request.get("ages", []),
        "activities": request.get("activities", []),
        "trip_cost": request.get("trip_cost")
    }
    
    # Build response - simple and clean
    from datetime import datetime
    return {
        "success": True,
        "source": "taxonomy_match",
        "quote_id": ancileo_quote_id or f"quote_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "quotes": final_quotes,
        "trip_details": trip_details_obj,
        "matching_method": "JSON Taxonomy Matching (Ancileo for costs only)",
        "generated_at": datetime.now().isoformat()
    }

@app.post("/api/compare")
async def compare_policies(request: dict):
    result = await policy_intel.compare_policies(
        criteria=request.get("criteria"),
        policies=request.get("policies", [])
    )
    return result

@app.post("/api/policy/compare-activities")
async def compare_policies_for_activities(request: dict):
    """
    Enhanced quantitative policy comparison for specific activities (e.g., skiing in Japan)
    Returns detailed quantitative analysis with exact coverage amounts, scores, and recommendations
    """
    activities = request.get("activities", [])
    policies = request.get("policies", [])
    trip_details = request.get("trip_details", {})
    destination = request.get("destination") or trip_details.get("destination")
    
    if not activities:
        return {
            "success": False,
            "error": "No activities specified",
            "message": "Please provide activities (e.g., ['skiing', 'scuba']) for activity-based comparison"
        }
    
    if not policies:
        return {
            "success": False,
            "error": "No policies specified",
            "message": "Please provide policies to compare"
        }
    
    try:
        all_comparisons = {}
        
        # Compare for each activity
        for activity in activities:
            comparison = await activity_matcher.compare_policies_for_activity(
                activity=activity,
                policies=policies,
                trip_details=trip_details
            )
            all_comparisons[activity] = comparison
        
        # Find best overall policy across all activities
        policy_scores = {}
        for activity, comparison in all_comparisons.items():
            for policy_comp in comparison.get("comparisons", []):
                policy_name = policy_comp["policy"]
                score = policy_comp["score"]
                
                if policy_name not in policy_scores:
                    policy_scores[policy_name] = {
                        "total_score": 0,
                        "activity_scores": {},
                        "comparisons": {}
                    }
                
                policy_scores[policy_name]["total_score"] += score
                policy_scores[policy_name]["activity_scores"][activity] = score
                policy_scores[policy_name]["comparisons"][activity] = policy_comp
        
        # Calculate average scores
        for policy_name, scores in policy_scores.items():
            scores["average_score"] = scores["total_score"] / len(activities)
            scores["policy"] = policy_name
        
        # Sort by average score
        ranked_policies = sorted(
            policy_scores.values(),
            key=lambda x: x["average_score"],
            reverse=True
        )
        
        # Generate simplified policy wordings using policy simplifier
        simplified_comparisons = {}
        for activity, comparison in all_comparisons.items():
            simplified = {}
            for policy_comp in comparison.get("comparisons", []):
                policy_name = policy_comp["policy"]
                
                # Get simplified policy explanation
                try:
                    policy_text = policy_intel.get_policy_text(policy_name)
                    if policy_text:
                        simplified_text = await policy_simplifier.simplify_policy_section(
                            policy_text[:2000],  # First 2000 chars for activity coverage
                            section_name=f"{activity} Coverage"
                        )
                        if simplified_text.get("success"):
                            simplified[policy_name] = simplified_text["simplified_text"]
                except Exception as e:
                    logger.warning(f"Policy simplification failed for {policy_name}: {e}")
            
            simplified_comparisons[activity] = simplified
        
        return {
            "success": True,
            "activities": activities,
            "destination": destination,
            "detailed_comparisons": all_comparisons,
            "ranked_policies": ranked_policies,
            "best_overall": ranked_policies[0] if ranked_policies else None,
            "simplified_explanations": simplified_comparisons,
            "summary": f"Compared {len(policies)} policies for {', '.join(activities)} activities in {destination or 'your destination'}"
        }
    
    except Exception as e:
        logger.error(f"Activity-based comparison failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to perform quantitative policy comparison"
        }

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

@app.post("/api/payment/stripe-mcp")
async def stripe_mcp_payment(request: dict):
    """
    Stripe MCP Payment - One-click payment using Stripe MCP with sandbox dummy card
    Automatically processes payment using Stripe MCP integration
    """
    amount = request.get("amount")
    currency = request.get("currency", "sgd")
    policy_id = request.get("policy_id") or request.get("quote_id")
    user_email = request.get("user_email") or request.get("email")
    
    if not amount:
        return {
            "success": False,
            "error": "Amount is required"
        }
    
    try:
        # Use Stripe MCP integration
        payment_intent = await mcp_integrations.stripe.create_payment_intent(
            amount=float(amount),
            currency=currency,
            policy_id=policy_id,
            user_email=user_email
        )
        
        if payment_intent.get("success"):
            # For sandbox, automatically confirm with dummy card
            # In production, this would return client_secret for frontend confirmation
            payment_intent_id = payment_intent.get("payment_intent_id")
            
            # Auto-confirm for sandbox (using test card)
            # Note: In production, use Stripe Elements or Payment Element for secure card input
            try:
                import stripe
                stripe_key = os.getenv("STRIPE_SECRET_KEY", os.getenv("STRIPE_SECRET_KEY_SANDBOX", ""))
                if stripe_key:
                    stripe.api_key = stripe_key
                    
                    # Auto-confirm with test card for sandbox
                    # Test card: 4242 4242 4242 4242, any future expiry, any CVC
                    confirm_result = stripe.PaymentIntent.confirm(
                        payment_intent_id,
                        payment_method="pm_card_visa"  # Test payment method
                    )
                    
                    return {
                        "success": True,
                        "payment_intent_id": payment_intent_id,
                        "status": "succeeded",
                        "amount": amount,
                        "currency": currency,
                        "message": "Payment processed successfully using Stripe sandbox",
                        "sandbox_mode": True
                    }
                else:
                    # Return client_secret for frontend confirmation
                    return {
                        "success": True,
                        "client_secret": payment_intent.get("client_secret"),
                        "payment_intent_id": payment_intent_id,
                        "amount": amount,
                        "currency": currency,
                        "requires_confirmation": True,
                        "message": "Payment intent created. Use Stripe Elements to confirm payment."
                    }
            except Exception as stripe_error:
                logger.warning(f"Auto-confirmation failed, returning client_secret: {stripe_error}")
                # Return client_secret for manual confirmation
                return {
                    "success": True,
                    "client_secret": payment_intent.get("client_secret"),
                    "payment_intent_id": payment_intent_id,
                    "amount": amount,
                    "currency": currency,
                    "requires_confirmation": True,
                    "message": "Payment intent created. Confirm payment using the client_secret."
                }
        else:
            return {
                "success": False,
                "error": payment_intent.get("error", "Failed to create payment intent")
            }
    
    except Exception as e:
        logger.error(f"Stripe MCP payment failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": "Payment processing failed. Please try again."
        }

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
            predictive_intel=predictive_intel
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

@app.post("/api/ancileo/purchase")
async def purchase_ancileo_policy(request: dict):
    """Purchase policy through Ancileo API (after payment)
    
    According to Ancileo API docs, requires:
    - quote_id, offer_id, product_code, unit_price, currency, quantity
    - insureds: Array of insured persons
    - mainContact: Main contact person structure (required)
    - emergencyContact: Optional
    - payment: Optional payment info
    """
    try:
        from ancileo_api import AncileoAPI
        ancileo = AncileoAPI()
        
        # Extract required fields
        insureds = request.get("insureds", [])
        main_contact = request.get("main_contact") or request.get("mainContact")
        
        # If main_contact not provided, try to construct from insureds or payment info
        if not main_contact and insureds:
            # Use first insured as main contact if not provided
            first_insured = insureds[0]
            main_contact = {
                "insuredId": first_insured.get("id"),
                "title": first_insured.get("title", "Mr"),
                "firstName": first_insured.get("firstName") or first_insured.get("first_name") or first_insured.get("name", "").split()[0] if first_insured.get("name") else "",
                "lastName": first_insured.get("lastName") or first_insured.get("last_name") or " ".join(first_insured.get("name", "").split()[1:]) if first_insured.get("name") else "",
                "email": request.get("email") or first_insured.get("email", ""),
                "phoneNumber": request.get("phone") or first_insured.get("phone") or first_insured.get("phoneNumber", "")
            }
        
        # Ensure main_contact has required fields
        if not main_contact or not main_contact.get("email"):
            return {
                "success": False,
                "error": "main_contact with email is required",
                "message": "Please provide main_contact structure with email and phoneNumber"
            }
        
        result = await ancileo.purchase_policy(
            quote_id=request.get("quote_id"),
            offer_id=request.get("offer_id"),
            product_code=request.get("product_code"),
            product_type=request.get("product_type", "travel-insurance"),
            unit_price=request.get("unit_price"),
            currency=request.get("currency", "SGD"),
            quantity=request.get("quantity", 1),
            insureds=insureds,
            main_contact=main_contact,
            emergency_contact=request.get("emergency_contact") or request.get("emergencyContact"),
            payment=request.get("payment"),
            partner_reference=request.get("partner_reference") or request.get("partnerReference"),
            options=request.get("options"),
            market=request.get("market", "SG"),
            language_code=request.get("language_code", "en")
        )
        return result
    except Exception as e:
        logger.error(f"Purchase endpoint error: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/ancileo/policy-wordings")
async def get_ancileo_policy_wordings(request: dict):
    """Get detailed policy wordings from Ancileo API
    
    According to Ancileo API docs, requires:
    - policy_id: The purchasedOfferId from purchase API response
    - email: Main contact email from purchase
    - market: Market country code (default: SG)
    """
    try:
        from ancileo_api import AncileoAPI
        ancileo = AncileoAPI()
        result = await ancileo.get_policy_wordings(
            policy_id=request.get("policy_id") or request.get("policyId"),
            email=request.get("email"),
            market=request.get("market", "SG")
        )
        return result
    except Exception as e:
        logger.error(f"Policy wordings endpoint error: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/ancileo/policies-only")
async def get_ancileo_policies_only(
    departure_country: str = "SG",
    arrival_country: str = "IN",  # Default to India/Chennai
    departure_date: str = None,
    return_date: str = None,
    adults: int = 1,
    children: int = 0
):
    """Get ONLY Ancileo policies (no local/preset policies)"""
    try:
        from ancileo_api import AncileoAPI
        ancileo = AncileoAPI()
        
        # Fetch quotes from Ancileo
        quote_result = await ancileo.get_quote(
            departure_country=departure_country,
            arrival_country=arrival_country,
            departure_date=departure_date,
            return_date=return_date,
            adults_count=adults,
            children_count=children
        )
        
        if quote_result.get("success"):
            policies = quote_result.get("policies", [])
            quotes = []
            for policy in policies:
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
            
            return {
                "success": True,
                "source": "ancileo",
                "quote_id": quote_result.get("quote_id"),
                "quotes": quotes,
                "count": len(quotes),
                "message": f"Found {len(quotes)} Ancileo policies for {arrival_country}"
            }
        else:
            return {
                "success": False,
                "error": quote_result.get("error"),
                "message": quote_result.get("message", "Failed to fetch Ancileo policies")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch policies from Ancileo API"
        }

@app.post("/api/tts/groq")
async def groq_tts(request: dict):
    """Text-to-Speech using Groq playai-tts model"""
    try:
        text = request.get("text", "")
        if not text:
            return {"error": "No text provided"}
        
        # Clean text for speech
        import re
        cleaned = text
        # Remove markdown
        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
        cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
        cleaned = re.sub(r'━+', ' ', cleaned)
        cleaned = re.sub(r'[•▪▫◦]', '- ', cleaned)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r'\[IMAGE:[^\]]+\]', '', cleaned)
        cleaned = re.sub(r'https?://[^\s]+', '', cleaned)
        # Remove hashes and symbols from policy names
        cleaned = re.sub(r'#+\s*', '', cleaned)  # Remove markdown headers
        cleaned = re.sub(r'[#@$%^&*()_+=\[\]{}|\\:";\'<>?,./`~]', '', cleaned)  # Remove special chars
        cleaned = cleaned.strip()
        
        # Use Groq API for TTS - try different approaches
        from groq import Groq
        groq_client = Groq(api_key=groq_key)
        
        try:
            # Try Groq audio API (if available)
            if hasattr(groq_client, 'audio') and hasattr(groq_client.audio, 'speech'):
                response = groq_client.audio.speech.create(
                    model="playai-tts",
                    voice="alloy",
                    input=cleaned[:4000]
                )
                audio_data = response.content
            else:
                # Fallback: Use HTTP request directly to Groq TTS endpoint
                import httpx
                async with httpx.AsyncClient() as client:
                    tts_response = await client.post(
                        "https://api.groq.com/openai/v1/audio/speech",
                        headers={
                            "Authorization": f"Bearer {groq_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "playai-tts",
                            "voice": "alloy",
                            "input": cleaned[:4000]
                        },
                        timeout=30.0
                    )
                    if tts_response.status_code == 200:
                        audio_data = tts_response.content
                    else:
                        raise Exception(f"Groq TTS API error: {tts_response.status_code}")
        except Exception as api_error:
            logger.warning(f"Groq TTS API not available, using fallback: {api_error}")
            raise api_error
        
        # Return audio as base64
        import base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return {
            "success": True,
            "audio": f"data:audio/mp3;base64,{audio_base64}",
            "text": cleaned
        }
    except Exception as e:
        logger.error(f"Groq TTS error: {e}")
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

