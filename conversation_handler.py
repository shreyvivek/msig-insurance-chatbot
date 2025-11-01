"""
Block 2: Conversational Magic
Natural language conversation with emotional intelligence and multilingual support
NOW WITH TRAVEL BUDDY PERSONALITY!
"""

import os
import json
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from groq import Groq
from travel_buddy import TravelBuddy
from multilingual_handler import MultilingualHandler

logger = logging.getLogger(__name__)

class ConversationHandler:
    """Handles natural language conversations with travel buddy personality"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        self.memory = {}  # Session memory
        self.travel_buddy = TravelBuddy()
        self.multilingual = MultilingualHandler()
        
        # Role definitions
        self.roles = {
            "travel_agent": {
                "name": "Wanda (Travel Agent)",
                "tone": "professional, knowledgeable, detail-oriented",
                "style": "Expert travel consultant with deep destination knowledge and insurance expertise",
                "personality": "Helpful, efficient, organized, and focused on providing the best travel solutions",
                "format_style": "structured, clear, with actionable recommendations"
            },
            "friend": {
                "name": "Wanda (Your Friend)",
                "tone": "casual, warm, enthusiastic",
                "style": "Like your best friend who loves traveling and happens to know about insurance",
                "personality": "Excited, personal, relatable, shares experiences",
                "format_style": "conversational, friendly, with personal touches"
            },
            "expert": {
                "name": "Wanda (Expert Advisor)",
                "tone": "authoritative, precise, data-driven",
                "style": "Insurance and travel expert with deep technical knowledge",
                "personality": "Thorough, analytical, comprehensive, citation-focused",
                "format_style": "detailed, fact-based, with extensive explanations"
            }
        }
        
        self.user_roles = {}  # Track role per user
        self.conversation_count = {}  # Track interactions per user
    
    def get_memory(self) -> Dict:
        """Get conversation memory"""
        return self.memory
    
    def update_memory(self, user_id: str, key: str, value: Any):
        """Update user memory"""
        if user_id not in self.memory:
            self.memory[user_id] = {}
        self.memory[user_id][key] = value
        self.memory[user_id]["last_updated"] = datetime.now().isoformat()
    
    def get_user_memory(self, user_id: str) -> Dict:
        """Get user's conversation memory"""
        return self.memory.get(user_id, {})
    
    def _detect_language(self, text: str) -> str:
        """Detect language from text"""
        # Simple language detection (in production, use proper library)
        # Check for common patterns
        if any(char in text for char in "あいうえお"):
            return "Japanese"
        elif any(char in text for char in "你好"):
            return "Chinese"
        elif any(char in text for char in "안녕"):
            return "Korean"
        else:
            return "English"
    
    def _detect_sentiment(self, text: str) -> str:
        """Detect user sentiment"""
        sentiment_indicators = {
            "confused": ["confused", "don't understand", "unclear", "?", "what does"],
            "frustrated": ["frustrated", "annoyed", "difficult", "complicated"],
            "anxious": ["worried", "concerned", "anxious", "nervous"],
            "excited": ["excited", "looking forward", "can't wait"],
            "happy": ["great", "thanks", "awesome", "perfect"]
        }
        
        text_lower = text.lower()
        for sentiment, keywords in sentiment_indicators.items():
            if any(keyword in text_lower for keyword in keywords):
                return sentiment
        
        return "neutral"
    
    async def handle_question(self, question: str, language: str = None,
                             context: str = None, user_id: str = "default_user",
                             is_voice: bool = False, role: str = None) -> Dict:
        """Handle user question with role-based personality and formatted response"""
        
        # Set or get user role (default: travel_agent)
        if role:
            self.user_roles[user_id] = role
        current_role = self.user_roles.get(user_id, "travel_agent")
        role_config = self.roles.get(current_role, self.roles["travel_agent"])
        
        # Track conversation
        if user_id not in self.conversation_count:
            self.conversation_count[user_id] = 0
        self.conversation_count[user_id] += 1
        
        # Detect language if not provided
        if not language:
            language = self.multilingual.detect_language(question)
        
        # Detect sentiment
        sentiment = self._detect_sentiment(question)
        
        # Get user memory
        user_memory = self.get_user_memory(user_id)
        
        # Check if this is a travel question (not just insurance)
        is_travel_question = self._is_travel_question(question)
        
        # Check if this is an insurance/policy-related question
        is_insurance_question = self._is_insurance_question(question)
        
        # Check if claims data is in context (override insurance detection)
        has_claims_data = context and ("CLAIMS DATA" in context or "🎯 CLAIMS DATA" in context)
        
        # Log if claims data detected
        if has_claims_data:
            logger.info("✅ CLAIMS DATA DETECTED IN CONTEXT - Will prioritize claims insights in response")
            # Force insurance mode when claims data is present
            is_insurance_question = True
        
        # Build rich context
        context_parts = []
        
        if user_memory.get("preferences"):
            context_parts.append(f"User preferences: {user_memory['preferences']}")
        
        if user_memory.get("trip_details"):
            context_parts.append(f"User's trip: {user_memory['trip_details']}")
        
        if user_memory.get("last_trip"):
            context_parts.append(f"Last trip: {user_memory['last_trip']}")
        
        if context:
            context_parts.append(f"Additional context: {context}")
        
        full_context = "\n".join(context_parts) if context_parts else "No previous context"
        
        # Adapt tone based on sentiment
        tone_adaptation = {
            "confused": "Simplify your explanation and be extra clear. Be patient and reassuring.",
            "frustrated": "Be empathetic, acknowledge the frustration, and provide clear solutions. Show you understand.",
            "anxious": "Be reassuring and supportive. Address concerns directly. Make them feel safe.",
            "excited": "Match their energy! Be enthusiastic and share in their excitement! 🎉",
            "neutral": "Be friendly, warm, and helpful. Show genuine interest."
        }
        
        # Create system prompt based on question type
        if is_insurance_question:
            # Insurance-focused prompt
            system_prompt = f"""You are {role_config['name']}, a friendly travel companion who also happens to be an expert in travel insurance.

CORE IDENTITY: You're a travel companion FIRST, insurance expert SECOND
- You love travel, destinations, culture, food, adventures - everything about travel!
- You happen to know a lot about travel insurance and can help when needed
- Be enthusiastic, friendly, and share travel knowledge freely
- ONLY mention insurance when the question is specifically about insurance/policies

WHEN TO TALK ABOUT INSURANCE:
- Only when asked directly about insurance, policies, coverage, quotes, or protection
- When comparing insurance options
- When explaining what insurance covers
- When helping purchase insurance

WHEN NOT TO MENTION INSURANCE:
- General greetings ("hi", "what do you do", "tell me about yourself")
- General travel questions (destinations, culture, food, activities)
- Non-insurance travel advice
- Just being friendly and chatty

CRITICAL: AVOID REPETITION
- Don't repeat the same information in multiple ways
- Focus on NEW information relevant to their current question
- Vary your phrasing - never use the same sentences repeatedly
- Answer what they're ACTUALLY asking

DYNAMIC RESPONSES:
- Each response should feel fresh and tailored to THIS specific question
- Reference specific details from the user's question
- Be conversational and natural - like a friend who travels a lot

Role: {current_role}
Personality: {role_config['personality']}
Tone: {role_config['tone']}
{tone_adaptation.get(sentiment, 'Be friendly, warm, and helpful.')}

User sentiment: {sentiment}
Language: {language}

IMPORTANT: When insurance questions are asked, prioritize Ancileo API policies. Always state clearly which policies come from Ancileo API vs local sources."""
        else:
            # General travel companion prompt (no insurance focus)
            system_prompt = f"""You are {role_config['name']}, a friendly and enthusiastic travel companion who loves everything about travel!

CORE IDENTITY: Travel Companion & Expert
- You're passionate about travel, destinations, cultures, food, adventures, and helping people explore the world
- You're friendly, conversational, and genuinely excited to help with travel questions
- You know about destinations, activities, tips, and general travel advice
- You happen to know about travel insurance too, but only mention it when specifically asked

YOUR PERSONALITY:
- Enthusiastic about travel and new experiences
- Friendly and warm - like talking to a well-traveled friend
- Helpful with travel tips, destination advice, and travel planning
- Casual and conversational - not overly formal

WHAT YOU CAN HELP WITH:
- Destination recommendations and travel tips
- Travel planning advice
- Cultural insights and local customs
- Activity suggestions and travel experiences
- General travel questions and conversations
- Travel insurance (ONLY when specifically asked)

WHAT NOT TO DO:
- Don't force insurance into conversations about travel in general
- Don't mention policies unless asked
- Be a travel buddy first, not an insurance salesperson

Role: {current_role}
Personality: {role_config['personality']}
Tone: {role_config['tone']}
{tone_adaptation.get(sentiment, 'Be friendly, warm, and helpful.')}

User sentiment: {sentiment}
Language: {language}"""

        # Only get policy data if it's an insurance question
        policy_summary = ""
        if is_insurance_question:
            try:
                from policy_intelligence import PolicyIntelligence
                policy_intel = PolicyIntelligence()
                policy_list = await policy_intel.get_policy_list()
                policy_summary = f"\n\nAvailable policies for reference: {', '.join([p['name'] for p in policy_list])}"
            except Exception as e:
                logger.warning(f"Failed to get policy list: {e}")
                policy_summary = "\n\nAvailable policies: TravelEasy, Scootsurance"
        
        # Build user prompt based on question type
        if is_insurance_question:
            # Check again if claims data is present
            claims_data_instruction = ""
            if has_claims_data:
                claims_data_instruction = """

🔥🔥🔥 CRITICAL: CLAIMS DATA IS PRESENT IN THE CONTEXT ABOVE! 🔥🔥🔥

YOU MUST START YOUR RESPONSE WITH THE CLAIMS DATA. DO THIS:

1. **FIRST PARAGRAPH** - Start with: "🎯 Based on historical claims data for [destination], [X]% of travelers have claimed for [claim type] with an average cost of $[amount] SGD."

2. **SECOND SENTENCE**: "Would you like to purchase insurance to specifically cover this highly likely incident?"

3. **THEN** answer their question normally but always relate back to the claims data.

DO NOT write generic travel information. The claims data is THE MOST IMPORTANT information here. Lead with it!

If the context has CLAIMS DATA section, you MUST use the EXACT percentages, claim types, and costs from that section. Do NOT make up numbers or give generic advice.
"""

            user_prompt = f"""User's current question: "{question}"

Previous context (READ CAREFULLY - claims data may be here):
{full_context}
{policy_summary}

CRITICAL INSTRUCTIONS FOR PERSONALIZED, EMPATHETIC RESPONSES:
1. **NEVER use generic templates** - Each response must be unique and tailored to this specific question
2. **Show genuine understanding** - Acknowledge their specific situation before answering
3. **Use their context** - Reference their destination, activities, or profile when relevant
4. **Be empathetic** - Understand their concerns (cost, coverage, safety) and address them naturally
5. **Answer THIS specific insurance question**: "{question}" with personalized details
6. **Reference specific policy details** - Use exact coverage amounts, not vague statements
7. **Format policy names in bold**: **TravelEasy**, **Scootsurance**, **MSIG**
8. **Include citations**: **[Policy: Name, Section]** when referencing policy details
9. **Explain "why" and "how"** - Use SPECIFIC numbers and breakdowns, show calculations
10. **Avoid repetitive phrases** - Don't say "I understand your concern" in every response
11. **Match their tone** - If they're casual, be casual. If formal, be professional
12. **Show you remember them** - Reference past conversations or preferences if available
{claims_data_instruction}

EXAMPLES OF WHAT NOT TO DO:
❌ "I understand your concern about..."
❌ "Let me help you with that..."
❌ Generic insurance advice without specifics

EXAMPLES OF WHAT TO DO:
✅ "Since you're skiing in Japan, let me check which policies cover winter sports..."
✅ "Based on your trip to [destination], here's what you need to know..."
✅ "You mentioned [specific detail] - here's how that affects coverage..."

Remember: Be hyper-personalized. Show you understand THEIR specific situation, not a generic one. Reference their destination, activities, profile tier, or past conversations. Make them feel heard and understood."""
        else:
            # General travel conversation - no insurance focus (UNLESS claims data present)
            user_prompt = f"""User's current question: "{question}"

Previous context (only use if relevant):
{full_context}

PERSONALIZED TRAVEL COMPANION MODE:
1. **Answer THIS specific question**: "{question}" - make it unique to them, not generic
2. **Show genuine enthusiasm** - But tailor it to what they're asking about
3. **Reference their context** - If they mentioned a destination, activity, or preference, use it
4. **Be conversational** - Like a well-traveled friend, not a chatbot
5. **Avoid repetitive patterns** - Don't start every response the same way
6. **Show you remember** - Reference past conversations, their profile tier, or preferences
7. **Match their energy** - If they're excited, match it. If they're casual, be casual
8. DON'T mention insurance unless they specifically ask about it

CRITICAL EXCEPTION: IF "CLAIMS DATA" SECTION IS PRESENT IN CONTEXT:
- You MUST switch to insurance mode and prominently feature the claims insights
- Start with claims data: "Based on historical claims data for [destination]..."
- Use EXACT percentages and costs from the claims data
- Ask: "Would you like to purchase insurance to specifically cover this highly likely incident?"
- This overrides the "don't mention insurance" rule - claims data is a proactive insurance recommendation trigger

PERSONALIZATION CHECKLIST:
✓ Did I acknowledge their specific situation?
✓ Did I avoid generic phrases like "I'd be happy to help"?
✓ Did I reference their destination/activities if mentioned?
✓ Did I show I understand THEIR question, not give a template answer?
✓ Is my tone natural and empathetic, not robotic?

Remember: Be a travel buddy who genuinely cares about THEIR trip, not a generic assistant."""

        try:
            # Build conversation history for context (avoid repetition)
            conversation_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Add recent conversation history if available
            if user_memory.get("recent_conversation"):
                recent = user_memory["recent_conversation"][-4:]  # Last 4 exchanges
                for msg in recent:
                    conversation_messages.insert(-1, msg)
            
            response = self.client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),  # Better reasoning model
                messages=conversation_messages,
                temperature=0.9,  # Higher for more dynamic, creative responses
                top_p=0.95,  # Nucleus sampling for better diversity
                max_tokens=2048,  # Allow longer, more detailed responses
                frequency_penalty=0.3,  # Reduce repetition
                presence_penalty=0.3  # Encourage new topics/phrases
            )
            
            answer_text = response.choices[0].message.content
            
            # Store conversation history (last 6 messages to avoid repetition)
            if not user_memory.get("recent_conversation"):
                user_memory["recent_conversation"] = []
            
            user_memory["recent_conversation"].append({"role": "user", "content": question})
            user_memory["recent_conversation"].append({"role": "assistant", "content": answer_text[:500]})  # Store truncated version
            
            # Keep only last 6 messages (3 exchanges)
            if len(user_memory["recent_conversation"]) > 6:
                user_memory["recent_conversation"] = user_memory["recent_conversation"][-6:]
            
            self.memory[user_id] = user_memory
            
            # Store question-answer in memory
            if "trip" in question.lower() or "destination" in question.lower():
                if not user_memory.get("trip_details"):
                    self.update_memory(user_id, "trip_details", "Mentioned in conversation")
            
            # Extract booking links
            booking_links = self._extract_booking_links(answer_text, question)
            
            # Format answer with better structure
            formatted_answer = self._format_response(answer_text)
            
            # Add proactive travel buddy moment (occasionally)
            if self.conversation_count[user_id] % 3 == 0 and is_travel_question:
                moment = await self.travel_buddy.create_travel_moment(user_id, "tip_of_day")
                if moment:
                    formatted_answer += f"\n\n💡 **Travel Tip**\n• {moment.get('content', '')}"
            
            # Ensure answer is in user's language
            formatted_answer = await self.multilingual.respond_in_language(formatted_answer, language)
            
            # Clean up image tags from text
            cleaned_answer = re.sub(r'\[IMAGE:[^\]]+\]', '', formatted_answer).strip()
            
            return {
                "answer": cleaned_answer,
                "content": cleaned_answer,  # Alias for frontend compatibility
                "message": cleaned_answer,  # Alias for frontend compatibility
                "booking_links": booking_links,
                "quotes": [],  # Will be populated by /api/ask if Ancileo policies are fetched
                "quote_id": None,
                "trip_details": None,
                "role": current_role,
                "formatted": True
            }
        
        except Exception as e:
            logger.error(f"Question handling failed: {e}", exc_info=True)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            error_msg = f"⚠️ **Oops!**\n\n• I encountered an error processing your question\n• Please try rephrasing it\n• If the problem persists, try asking differently"
            return {
                "answer": error_msg,
                "booking_links": [],
                "role": current_role,
                "formatted": True
            }
    
    def _extract_booking_links(self, text: str, question: str) -> List[Dict]:
        """Extract booking links from response and question"""
        booking_links = []
        try:
            # Check if user is asking about booking
            booking_keywords = ['book', 'booking', 'reserve', 'ticket', 'flight', 'hotel', 'activity', 'tour']
            if not any(keyword in question.lower() for keyword in booking_keywords):
                return booking_links
            
            # Extract destination from question or text
            destination_pattern = r'\b(?:to|in|at|visit|travel|going)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
            destination_matches = re.findall(destination_pattern, question)
            if not destination_matches:
                # Try to find common destination names
                common_destinations = ['Tokyo', 'Japan', 'Singapore', 'Thailand', 'Bangkok', 'Paris', 'London', 'New York', 'Dubai', 'Sydney']
                for dest in common_destinations:
                    if dest.lower() in question.lower():
                        destination_matches = [dest]
                        break
            
            destination = destination_matches[0] if destination_matches else "destination"
            destination_clean = destination.replace(' ', '-').lower()
            
            # Extract booking type from question
            booking_type = 'activity'
            if any(word in question.lower() for word in ['flight', 'fly', 'airline', 'plane']):
                booking_type = 'flight'
            elif any(word in question.lower() for word in ['hotel', 'stay', 'accommodation', 'resort']):
                booking_type = 'hotel'
            elif any(word in question.lower() for word in ['tour', 'activity', 'experience', 'attraction']):
                booking_type = 'activity'
            
            # Generate booking links
            if booking_type in ['hotel', 'flight']:
                booking_links.append({
                    "type": booking_type,
                    "platform": "agoda",
                    "url": f"https://www.agoda.com/search?city={destination_clean}" if booking_type == 'hotel' else f"https://www.agoda.com/flights?to={destination_clean}",
                    "text": f"Book {booking_type}s in {destination} on Agoda"
                })
            
            if booking_type in ['activity', 'tour']:
                booking_links.append({
                    "type": booking_type,
                    "platform": "klook",
                    "url": f"https://www.klook.com/search/?keyword={destination_clean}",
                    "text": f"Book activities in {destination} on Klook"
                })
            
            # Also check for explicit booking link format in response
            booking_pattern = r'\[BOOKING:\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^\]]+)\]'
            explicit_matches = re.findall(booking_pattern, text)
            for platform, link_type, dest, link_text in explicit_matches:
                booking_links.append({
                    "type": link_type.strip(),
                    "platform": platform.strip(),
                    "url": self._generate_booking_url(platform.strip(), link_type.strip(), dest.strip()),
                    "text": link_text.strip()
                })
                
        except Exception as e:
            logger.error(f"Booking link extraction failed: {e}")
        
        return booking_links
    
    def _generate_booking_url(self, platform: str, booking_type: str, destination: str) -> str:
        """Generate booking URL based on platform and type"""
        dest_clean = destination.replace(' ', '-').lower()
        
        if platform.lower() == 'agoda':
            if booking_type.lower() in ['hotel', 'accommodation']:
                return f"https://www.agoda.com/search?city={dest_clean}"
            elif booking_type.lower() in ['flight', 'airline']:
                return f"https://www.agoda.com/flights?to={dest_clean}"
            else:
                return f"https://www.agoda.com/search?city={dest_clean}"
        elif platform.lower() == 'klook':
            return f"https://www.klook.com/search/?keyword={dest_clean}"
        else:
            return f"https://www.google.com/search?q={dest_clean}+{booking_type}+booking"
    
    def _format_response(self, text: str) -> str:
        """Enhance formatting of response"""
        # Replace markdown separators with better formatting
        text = text.replace('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', '\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')
        
        # Ensure bullet points are formatted
        lines = text.split('\n')
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('•') and not line.startswith('-') and not line.startswith('*'):
                # Check if it looks like it should be a bullet point
                if line and len(line) < 100 and not line.startswith('#'):
                    # Don't auto-convert headers or very long lines
                    pass
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _is_travel_question(self, question: str) -> bool:
        """Detect if question is about travel (not just insurance)"""
        travel_keywords = [
            "destination", "place", "country", "city", "trip", "travel", "visit",
            "where to go", "what to see", "activities", "things to do", "attractions",
            "weather", "food", "culture", "hotels", "restaurants", "tips", "advice",
            "itinerary", "plan", "suggest", "recommend"
        ]
        
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in travel_keywords)
    
    def _is_insurance_question(self, question: str) -> bool:
        """Detect if question is specifically about insurance/policies"""
        question_lower = question.lower()
        
        # Explicit insurance keywords
        insurance_keywords = [
            "insurance", "policy", "policies", "coverage", "cover", "insured",
            "premium", "quote", "quotes", "plan", "plans", "protection",
            "claim", "claims", "benefit", "benefits", "deductible", "exclusion",
            "travel insurance", "medical coverage", "trip cancellation",
            "baggage", "cancel", "compare policies", "which policy", "what coverage"
        ]
        
        # Check for explicit insurance questions
        if any(keyword in question_lower for keyword in insurance_keywords):
            return True
        
        # Check for policy-specific questions
        policy_names = ["traveleasy", "scootsurance", "msig"]
        if any(name in question_lower for name in policy_names):
            return True
        
        # Check for questions asking about insurance features
        feature_keywords = ["medical", "cancellation", "baggage", "emergency", "evacuation"]
        insurance_context = ["what", "how", "does", "can", "should", "need"]
        if any(feat in question_lower for feat in feature_keywords) and \
           any(ctx in question_lower for ctx in insurance_context):
            # Might be insurance, but check if it's general travel first
            if "travel insurance" in question_lower or "policy" in question_lower:
                return True
        
        return False
    
    async def generate_personalized_greeting(self, user_id: str = "default_user", 
                                            language: str = "en") -> str:
        """Generate personalized greeting based on role"""
        role = self.user_roles.get(user_id, "travel_agent")
        role_config = self.roles.get(role, self.roles["travel_agent"])
        
        if role == "travel_agent":
            greeting = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👋 Welcome! I'm Wanda, Your Travel Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Expert travel planning & insurance advice
• Personalized destination recommendations
• Comprehensive trip protection solutions
• 24/7 support for your journey

How can I help plan your next adventure? ✈️"""
        elif role == "friend":
            greeting = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👋 Hey! I'm Wanda, Your Travel Friend!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Let's plan something awesome together!
• I know all the cool spots
• Plus I'll make sure you're protected
• Ready for an adventure? 🌍"""
        else:  # expert
            greeting = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👋 Wanda - Expert Travel & Insurance Advisor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Deep technical expertise in travel insurance
• Data-driven risk analysis
• Comprehensive policy comparisons
• Strategic travel planning guidance

What would you like to explore? 📊"""
        
        # Translate if needed
        if language != "en":
            greeting = await self.multilingual.respond_in_language(greeting, language)
        
        return greeting
    
    def set_user_role(self, user_id: str, role: str):
        """Set the role for a user"""
        if role in self.roles:
            self.user_roles[user_id] = role
            return True
        return False
    
    def get_user_role(self, user_id: str) -> str:
        """Get current role for user"""
        return self.user_roles.get(user_id, "travel_agent")

