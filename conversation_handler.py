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
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not groq_key:
            logger.warning("⚠️ GROQ_API_KEY not set! Chatbot will not work properly.")
            self.client = None
        else:
            try:
                self.client = Groq(api_key=groq_key)
                logger.info("✅ Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None
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
        
        # Role-based system prompt - TRAVEL INSURANCE PRIMARY
        system_prompt = f"""You are {role_config['name']}, a travel insurance expert. Your PRIMARY job is helping users with travel insurance.

CORE FUNCTION: Travel Insurance Advice
- Help users understand coverage, compare policies, purchase insurance
- Always connect travel questions to insurance needs
- Provide specific coverage amounts, policy citations, recommendations

Role: {current_role}
Personality: {role_config['personality']}
Tone: {role_config['tone']}

MANDATORY FORMAT - Use bullets with clear spacing:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 [Answer - Insurance Focus]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


• Point 1 (insurance/coverage related)

• Point 2 (specific amounts or comparisons)

• Point 3 (recommendations)


💡 Insurance Recommendation

• Suggested plan: **Policy Name** (highlight in bold)

• Coverage: $Amount

• Why it fits: Specific reasons

• Policy citation: **[Policy: Name, Section]** (always bold)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


IMPORTANT FORMATTING:
- Use double line breaks between sections
- Bold ALL policy names: **TravelEasy**, **Scootsurance**, **MSIG**
- Bold policy citations: **[Policy: Name, Section]**
- Add blank lines between bullet points for readability
- For destinations: Include [IMAGE: location, keyword] then explain insurance requirements

User sentiment: {sentiment}
Language: {language}

CRITICAL: Bullet points with spacing, bold all policy names, travel insurance is PRIMARY!"""

        # Get policy data for context
        try:
            from policy_intelligence import PolicyIntelligence
            policy_intel = PolicyIntelligence()
            policy_list = await policy_intel.get_policy_list()
            policy_summary = "Available policies: " + ", ".join([p["name"] for p in policy_list])
        except Exception as e:
            logger.warning(f"Failed to get policy list: {e}")
            policy_summary = "Available policies: TravelEasy, Scootsurance"
        
        # If travel question, connect to insurance needs
        travel_enhancement = ""
        if is_travel_question:
            travel_enhancement = "\n\nNOTE: This is about travel/destinations. Connect it to travel insurance needs - what coverage do they need for this destination/activity?"
        
        user_prompt = f"""User question: {question}

Context:
{full_context}

{policy_summary}
{travel_enhancement}

IMPORTANT - Format your response as follows:

1. Use clear structure with sections separated by lines (━━━━)
2. Use bullet points (•) for all lists
3. For destinations: Suggest images using format [IMAGE: destination, keyword]
4. Break down information into digestible chunks
5. Use visual separators between major sections
6. Make it scannable - not long paragraphs

Example format:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 [Main Answer/Summary]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Key point 1 with details
• Key point 2 with details
• Key point 3 with details

💡 Additional Insights
• Insight 1
• Insight 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provide:
1. Direct, structured answer
2. Bullet-pointed breakdowns
3. If insurance: Citations as [Policy: Name, Section]
4. If travel: Image suggestions as [IMAGE: location, keyword]
5. Proactive suggestions
6. Personal touches if remembered

Format it beautifully for easy reading!"""

        try:
<<<<<<< Updated upstream
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8  # Higher for more personality
            )
=======
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
            
            # Check if client is initialized
            if not self.client:
                raise Exception("Groq client not initialized. Check GROQ_API_KEY environment variable.")
>>>>>>> Stashed changes
            
            try:
                response = self.client.chat.completions.create(
                    model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),  # Better reasoning model
                    messages=conversation_messages,
                    temperature=0.9,  # Higher for more dynamic, creative responses
                    top_p=0.95,  # Nucleus sampling for better diversity
                    max_tokens=2048,  # Allow longer, more detailed responses
                    frequency_penalty=0.3,  # Reduce repetition
                    presence_penalty=0.3  # Encourage new topics/phrases
                )
                
                if not response or not response.choices or len(response.choices) == 0:
                    raise Exception("Empty response from Groq API")
                
                answer_text = response.choices[0].message.content
                if not answer_text:
                    raise Exception("No content in Groq API response")
                    
            except Exception as api_error:
                logger.error(f"Groq API call failed: {api_error}", exc_info=True)
                # Re-raise with more context
                raise Exception(f"Groq API error: {str(api_error)}") from api_error
            
            # Store question-answer in memory
            if "trip" in question.lower() or "destination" in question.lower():
                if not user_memory.get("trip_details"):
                    self.update_memory(user_id, "trip_details", "Mentioned in conversation")
            
            # Extract images from response
            images = self._extract_image_suggestions(answer_text)
            
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
                "images": images,
                "booking_links": booking_links,
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
                "images": [],
                "booking_links": [],
                "role": current_role,
                "formatted": True
            }
    
    def _extract_image_suggestions(self, text: str) -> List[Dict]:
        """Extract image suggestions from response"""
        images = []
        try:
            pattern = r'\[IMAGE:\s*([^,]+),\s*([^\]]+)\]'
            matches = re.findall(pattern, text)
            
            for destination, keyword in matches:
                # Use Pexels or Unsplash properly
                # Build search query
                query = f"{destination.strip()} {keyword.strip()}".replace(' ', '+')
                # Use Unsplash source API with better query
                images.append({
                    "destination": destination.strip(),
                    "keyword": keyword.strip(),
                    "url": f"https://api.unsplash.com/photos/random?query={query}&w=800&h=600&client_id=demo"  # Will use public endpoint
                })
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
        
<<<<<<< Updated upstream
        return images
=======
        # Check if it's an API error (Groq/LLM related)
        is_api_error = any(keyword in error_str for keyword in [
            "api", "groq", "rate limit", "quota", "timeout", "connection", "network"
        ])
        
        # Check if it's a policy coverage question
        is_coverage_question = any(keyword in question_lower for keyword in [
            "cover", "coverage", "does", "will", "include", "hiking", "sport", "activity"
        ])
        
        # Check if specific policy is mentioned
        policy_mentioned = None
        if "scootsurance" in question_lower:
            policy_mentioned = "Scootsurance"
        elif "international travel" in question_lower or "international" in question_lower:
            policy_mentioned = "INTERNATIONAL TRAVEL"
        elif "mhinsure" in question_lower or "mh insure" in question_lower:
            policy_mentioned = "MHInsure Travel"
        elif "msig" in question_lower:
            policy_mentioned = "INTERNATIONAL TRAVEL"  # Map MSIG to INTERNATIONAL TRAVEL
        
        # Try to provide helpful answer using policy intelligence
        if is_insurance_question and is_coverage_question:
            try:
                from policy_intelligence import PolicyIntelligence
                policy_intel = PolicyIntelligence()
                
                # Try to find relevant policy information
                if policy_mentioned:
                    policy_name_map = {
                        "Scootsurance": "Scootsurance",
                        "INTERNATIONAL TRAVEL": "INTERNATIONAL TRAVEL",
                        "MHInsure Travel": "MHInsure Travel",
                        "MSIG": "INTERNATIONAL TRAVEL"  # Map MSIG to INTERNATIONAL TRAVEL
                    }
                    policy_name = policy_name_map.get(policy_mentioned)
                    
                    if policy_name:
                        # Try to search for coverage information
                        policy_text = policy_intel.get_policy_text(policy_name)
                        if policy_text:
                            # Look for activity keywords in question
                            activity_keywords = ["hiking", "trekking", "sport", "adventure", "activity", "activity"]
                            mentioned_activities = [kw for kw in activity_keywords if kw in question_lower]
                            
                            # Search policy text for activity mentions
                            policy_lower = policy_text.lower()
                            has_coverage = any(act in policy_lower for act in mentioned_activities) if mentioned_activities else False
                            
                            if has_coverage:
                                response = f"✅ Yes, **{policy_mentioned}** does provide coverage for {', '.join(mentioned_activities)} activities.\n\n"
                                response += f"Based on the policy document, {policy_mentioned} includes coverage for adventure activities and sports. However, I recommend reviewing the specific terms and conditions in your policy document to confirm the exact coverage limits and any exclusions.\n\n"
                                response += "Would you like me to check the specific coverage amounts or terms for your activities?"
                            else:
                                response = f"Let me check **{policy_mentioned}** coverage for your activities...\n\n"
                                response += f"While I'm having trouble accessing the full policy details right now, **{policy_mentioned}** typically covers a range of travel activities. For specific coverage of hiking and adventure sports, I'd recommend:\n\n"
                                response += "1. Reviewing the policy document's activity coverage section\n"
                                response += "2. Checking if there are any activity exclusions or special requirements\n"
                                response += "3. Contacting the insurance provider directly for confirmation\n\n"
                                response += "Would you like me to help you find the specific policy document or contact information?"
                            
                            return response
                
                # Generic helpful response for coverage questions
                return f"**I'm checking policy coverage for you...**\n\nWhile I'm having some technical difficulties accessing the full policy details right now, I can help you with:\n\n• **General coverage**: Most travel insurance policies cover hiking and adventure activities, but specific terms vary\n• **Activity-specific coverage**: Some policies may have exclusions or require additional coverage for extreme sports\n• **Policy documents**: I can help you locate the relevant policy documents to review specific coverage\n\nWould you like me to:\n1. Check specific policy documents for activity coverage?\n2. Help you compare coverage between different policies?\n3. Find contact information to verify coverage details?"
                
            except Exception as fallback_error:
                logger.warning(f"Fallback policy check also failed: {fallback_error}")
        
        # API/Network error handling
        if is_api_error:
            # Don't return connection issue message here - let the error propagate
            # This should only be used for actual network/API failures
            raise Exception("LLM API call failed - this should be caught by the endpoint handler")
        
        # Generic helpful error for insurance questions
        if is_insurance_question:
            # Don't return generic error message - let it propagate to endpoint handler
            raise Exception("LLM processing failed - this should be caught by the endpoint handler")
        
        # Generic helpful error for travel questions
        return f"**Oops, I hit a snag!** 😅\n\nI'm having trouble processing that question right now. No worries though - here's what might help:\n\n• **Try rephrasing** - Sometimes a slightly different wording works better\n• **Break it down** - If your question is complex, try asking it in parts\n• **Try again** - This might just be a temporary glitch\n\nI'm here to help! What would you like to know about travel or insurance?"
>>>>>>> Stashed changes
    
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

