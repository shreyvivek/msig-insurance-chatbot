"""
Travel Buddy - The Heart of WanderSure
Goes beyond insurance to be a true travel companion
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from groq import Groq
import random

logger = logging.getLogger(__name__)

class TravelBuddy:
    """
    Travel Buddy - Your smart companion that:
    - Remembers your travel preferences
    - Proactively suggests activities and tips
    - Shares destination insights beyond insurance
    - Learns from your travel patterns
    - Creates memorable travel moments
    """
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        self.memories = {}  # User travel memories
        self.personality_traits = {
            "name": "Alex",  # Give it a name!
            "style": "enthusiastic, curious, travel-obsessed",
            "quirks": [
                "Loves finding hidden gems",
                "Always checks weather before trips",
                "Remembers your favorite destinations",
                "Gets excited about new cultures",
                "Shares fun travel trivia"
            ]
        }
    
    async def get_personalized_greeting(self, user_id: str, context: Dict = None) -> str:
        """Generate personalized greeting based on user's travel history"""
        user_memory = self.memories.get(user_id, {})
        
        if user_memory.get("last_trip"):
            destination = user_memory["last_trip"].get("destination", "your last trip")
            return f"""👋 Hey there, travel buddy! 

I see you were in {destination} recently - how was it? 

Ready to plan your next adventure? I'm here to help with insurance AND make sure you have the best trip ever! ✈️"""
        
        return """👋 Hey! I'm Alex, your travel buddy! 

I'm not just here for insurance - I'm here to:
✨ Help you discover amazing destinations
🎯 Plan your perfect itinerary
🧳 Share insider travel tips
🛡️ Keep you protected with the right insurance
🎉 Make sure you have unforgettable experiences

Where are we going next? 🌍"""
    
    async def get_destination_insights(self, destination: str, user_preferences: Dict = None) -> Dict:
        """Get rich destination insights beyond insurance"""
        
        prompt = f"""Provide comprehensive travel insights for {destination}:

Include:
1. Best time to visit (weather, crowds, events)
2. Must-see attractions (beyond tourist traps)
3. Hidden gems and local favorites
4. Cultural tips and etiquette
5. Local cuisine recommendations
6. Safety considerations
7. Budget tips
8. Unique experiences not to miss
9. Instagram-worthy spots
10. Local festivals or events during travel dates

Make it exciting and personal - like a friend sharing their favorite place!"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an enthusiastic travel buddy who loves sharing destination insights. Be excited, personal, and helpful."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            
            insights_text = response.choices[0].message.content
            
            return {
                "destination": destination,
                "insights": insights_text,
                "generated_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Destination insights failed: {e}")
            return {
                "destination": destination,
                "insights": f"Exciting destination! {destination} has so much to offer. Let me help you plan the perfect trip!",
                "error": str(e)
            }
    
    async def suggest_activities(self, destination: str, trip_dates: Dict, 
                                traveler_profile: Dict) -> List[Dict]:
        """Proactively suggest activities based on traveler profile"""
        
        prompt = f"""Suggest personalized activities for a trip to {destination}:

Traveler Profile:
- Age: {traveler_profile.get('age', 'Not specified')}
- Interests: {', '.join(traveler_profile.get('interests', [])) or 'Open to new experiences'}
- Travel style: {traveler_profile.get('travel_style', 'balanced')}
- Budget: {traveler_profile.get('budget', 'moderate')}
- Trip dates: {trip_dates.get('start_date')} to {trip_dates.get('end_date')}

Suggest:
1. Adventure activities
2. Cultural experiences
3. Food experiences
4. Relaxation spots
5. Nightlife
6. Shopping
7. Photography spots
8. Off-the-beaten-path experiences

Make each suggestion exciting with a brief description of why it's special!"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a travel activity expert. Suggest diverse, exciting activities that match the traveler's profile."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            suggestions = json.loads(response.choices[0].message.content)
            
            return suggestions.get("activities", [])
        
        except Exception as e:
            logger.error(f"Activity suggestions failed: {e}")
            return []
    
    async def create_travel_moment(self, user_id: str, moment_type: str) -> Dict:
        """Create special moments - like a friend sharing something cool"""
        
        moments = {
            "tip_of_day": await self._get_travel_tip(),
            "hidden_gem": await self._get_hidden_gem(),
            "fun_fact": await self._get_travel_fact(),
            "weather_check": await self._check_weather_proactively(),
            "culture_insight": await self._get_culture_insight()
        }
        
        moment = moments.get(moment_type, moments["tip_of_day"])
        
        # Remember this moment for the user
        if user_id not in self.memories:
            self.memories[user_id] = {"moments": []}
        
        self.memories[user_id]["moments"].append({
            "type": moment_type,
            "content": moment,
            "timestamp": datetime.now().isoformat()
        })
        
        return moment
    
    async def _get_travel_tip(self) -> Dict:
        """Get a random travel tip"""
        tips = [
            "💡 Pro tip: Pack a portable phone charger - you'll thank yourself when navigating foreign cities!",
            "🎒 Always pack one extra pair of underwear in your carry-on (trust me on this one!)",
            "📱 Download offline maps before you go - your future self will be grateful!",
            "💰 Keep emergency cash in multiple places - never all in one wallet!",
            "🌍 Learn 3-5 basic phrases in the local language - locals love it!"
        ]
        
        return {
            "type": "tip",
            "title": "Travel Tip of the Day",
            "content": random.choice(tips),
            "icon": "💡"
        }
    
    async def _get_hidden_gem(self) -> Dict:
        """Share a hidden gem for a destination"""
        return {
            "type": "hidden_gem",
            "title": "Hidden Gem Alert! 🗺️",
            "content": "Want to discover a secret spot most tourists miss? Ask me about hidden gems in your destination!",
            "icon": "🗺️"
        }
    
    async def _get_travel_fact(self) -> Dict:
        """Share interesting travel trivia"""
        facts = [
            "Did you know? Japan has over 5 million vending machines - more than anywhere in the world! 🍜",
            "Fun fact: The world's shortest flight is just 47 seconds (Westray to Papa Westray, Scotland)! ✈️",
            "Mind-blowing: You can visit 12 countries in one day in Europe without ever leaving the Schengen zone! 🌍",
            "Cool fact: Iceland has no mosquitoes - literally zero! 🦟❌",
            "Interesting: Bhutan measures success by Gross National Happiness, not GDP! 😊"
        ]
        
        return {
            "type": "fact",
            "title": "Travel Fun Fact",
            "content": random.choice(facts),
            "icon": "🧠"
        }
    
    async def _check_weather_proactively(self) -> Dict:
        """Proactively check weather for upcoming trips"""
        return {
            "type": "weather",
            "title": "Weather Check",
            "content": "I'll check the weather for your destination and suggest what to pack! Just tell me where you're going! ☀️",
            "icon": "☀️"
        }
    
    async def _get_culture_insight(self) -> Dict:
        """Share cultural insights"""
        return {
            "type": "culture",
            "title": "Culture Corner",
            "content": "Want to know about local customs, etiquette, or cultural do's and don'ts? I've got you covered! 🎭",
            "icon": "🎭"
        }
    
    async def remember_user_preference(self, user_id: str, preference: Dict):
        """Remember user preferences like a friend would"""
        if user_id not in self.memories:
            self.memories[user_id] = {}
        
        self.memories[user_id].update(preference)
        self.memories[user_id]["last_updated"] = datetime.now().isoformat()
    
    async def get_personalized_recommendation(self, user_id: str, context: Dict) -> str:
        """Get recommendation that feels personal, like from a friend"""
        user_memory = self.memories.get(user_id, {})
        
        prompt = f"""Based on this user's travel history and preferences, give a personalized recommendation:

User Profile:
{json.dumps(user_memory, indent=2)}

Current Context:
{json.dumps(context, indent=2)}

Give a recommendation that:
1. References their past travels (if any)
2. Matches their preferences
3. Feels personal and friendly
4. Is specific and actionable
5. Shows you remember them

Be like a travel buddy giving advice - warm, personal, enthusiastic!"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are Alex, a travel buddy. You remember past conversations and give personalized advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Personalized recommendation failed: {e}")
            return "I'd love to help you plan an amazing trip! Tell me where you're thinking of going! 🗺️"

