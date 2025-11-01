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
import uvicorn

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

if __name__ == "__main__":
    # Use port from environment variable or default to 8002
    port = int(os.getenv("PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port)

