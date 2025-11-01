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

policy_intel = PolicyIntelligence()
doc_intel = DocumentIntelligence()
predictive_intel = PredictiveIntelligence()
payment_handler = PaymentHandler()
conversation = ConversationHandler()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "wandersure"}

@app.post("/api/ask")
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

