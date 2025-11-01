"""
Analyzes Instagram profile data to calculate adventurous_score, activities, and tier
"""
import logging
from typing import Dict, List, Optional
from groq import Groq
import os

logger = logging.getLogger(__name__)

class ProfileAnalyzer:
    """Analyzes scraped Instagram data for personalization"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
        
        # Adventure-related keywords for scoring
        self.adventure_keywords = [
            "skiing", "ski", "snowboarding", "scuba", "diving", "snorkeling",
            "hiking", "trekking", "mountaineering", "climbing", "rock climbing",
            "bungee", "bungee jumping", "skydiving", "paragliding", "parasailing",
            "rafting", "kayaking", "canoeing", "surfing", "windsurfing",
            "adventure", "adventurous", "explore", "exploration", "wanderlust",
            "travel", "travelling", "traveling", "trip", "vacation", "journey",
            "backpacking", "backpack", "camping", "outdoor", "outdoors",
            "extreme", "extreme sports", "sports", "fitness", "active",
            "safari", "wildlife", "jungle", "trek", "expedition"
        ]
        
        # Travel frequency indicators
        self.travel_indicators = [
            "travel", "trip", "vacation", "holiday", "journey", "destination",
            "airport", "flight", "hotel", "resort", "beach", "island",
            "city", "country", "wanderlust", "explore", "adventure"
        ]
    
    async def analyze_instagram_data(self, instagram_data: Dict) -> Dict:
        """
        Analyze Instagram profile and posts
        
        Args:
            instagram_data: Dictionary from ProfileScraper.fetch_instagram_profile()
            
        Returns:
            {
                "adventurous_score": 0.0-1.0,
                "travel_frequency": "low|medium|high|unknown",
                "likely_activities": List[str],
                "detected_interests": List[str]
            }
        """
        if instagram_data.get("error") or instagram_data.get("is_private"):
            return {
                "adventurous_score": 0.0,
                "travel_frequency": "unknown",
                "likely_activities": [],
                "detected_interests": []
            }
        
        posts = instagram_data.get("posts_data", [])
        if not posts:
            return {
                "adventurous_score": 0.0,
                "travel_frequency": "unknown",
                "likely_activities": [],
                "detected_interests": []
            }
        
        # Analyze posts
        adventure_count = 0
        travel_count = 0
        activity_keywords_found = set()
        interest_keywords_found = set()
        total_activity_mentions = 0
        
        for post in posts:
            caption = (post.get("caption") or "").lower()
            hashtags = [h.lower() for h in post.get("hashtags", [])]
            all_text = caption + " " + " ".join(hashtags)
            
            # Check for adventure keywords
            for keyword in self.adventure_keywords:
                if keyword in all_text:
                    adventure_count += 1
                    activity_keywords_found.add(keyword)
                    total_activity_mentions += all_text.count(keyword)
            
            # Check for travel indicators
            for indicator in self.travel_indicators:
                if indicator in all_text:
                    travel_count += 1
                    break  # Count post once for travel
            
            # Extract general interests from hashtags
            for hashtag in hashtags:
                if len(hashtag) > 3 and hashtag not in ["travel", "photography", "instagood"]:
                    interest_keywords_found.add(hashtag)
        
        # Calculate adventurous_score (0-1)
        # Based on percentage of posts with adventure content + frequency
        total_posts = len(posts)
        if total_posts > 0:
            adventure_post_ratio = adventure_count / total_posts
            activity_intensity = min(total_activity_mentions / (total_posts * 2), 1.0)  # Normalize
            adventurous_score = min((adventure_post_ratio * 0.7) + (activity_intensity * 0.3), 1.0)
        else:
            adventurous_score = 0.0
        
        # Estimate travel frequency
        travel_ratio = travel_count / total_posts if total_posts > 0 else 0
        if travel_ratio > 0.5:
            travel_frequency = "high"
        elif travel_ratio > 0.2:
            travel_frequency = "medium"
        elif travel_ratio > 0:
            travel_frequency = "low"
        else:
            travel_frequency = "unknown"
        
        # Get top activities (most frequently mentioned)
        likely_activities = sorted(
            activity_keywords_found,
            key=lambda x: sum(post.get("caption", "").lower().count(x) + 
                             sum(post.get("hashtags", []), []).count(x) 
                             for post in posts),
            reverse=True
        )[:10]
        
        # Get top interests (most frequent hashtags, excluding common ones)
        common_hashtags = {"travel", "photography", "instagood", "photooftheday", "love", 
                          "beautiful", "picoftheday", "instagram", "follow", "like"}
        detected_interests = [
            hashtag for hashtag in interest_keywords_found 
            if hashtag not in common_hashtags
        ][:15]
        
        # Use LLM for enhanced analysis if available
        if self.client and posts:
            try:
                enhanced_analysis = await self._llm_enhance_analysis(posts, adventurous_score)
                if enhanced_analysis:
                    adventurous_score = enhanced_analysis.get("adventurous_score", adventurous_score)
                    likely_activities.extend(enhanced_analysis.get("additional_activities", []))
            except Exception as e:
                logger.debug(f"LLM enhancement failed: {e}")
        
        return {
            "adventurous_score": round(adventurous_score, 3),
            "travel_frequency": travel_frequency,
            "likely_activities": list(set(likely_activities)),  # Remove duplicates
            "detected_interests": list(set(detected_interests))[:15]
        }
    
    async def _llm_enhance_analysis(self, posts: List[Dict], base_score: float) -> Optional[Dict]:
        """Use LLM to enhance activity detection"""
        try:
            # Take sample of posts for LLM analysis
            sample_posts = posts[:10]
            captions = [post.get("caption", "")[:200] for post in sample_posts if post.get("caption")]
            
            prompt = f"""Analyze these Instagram post captions and identify adventure/travel activities mentioned.
            
Captions:
{chr(10).join(f"- {c}" for c in captions)}

Based on adventurous_score of {base_score:.2f}, suggest:
1. Additional adventure/travel activities not already detected
2. Refined adventurous_score (0-1) if the current score {base_score:.2f} seems inaccurate

Respond in JSON format:
{{
    "adventurous_score": 0.0-1.0,
    "additional_activities": ["activity1", "activity2"],
    "reasoning": "brief explanation"
}}"""
            
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.debug(f"LLM enhancement error: {e}")
            return None
    
    def calculate_tier(self, profile_analysis: Dict, risk_score: Optional[float] = None) -> tuple[str, str]:
        """
        Calculate policy tier based on profile analysis and risk score
        
        Args:
            profile_analysis: Result from analyze_instagram_data()
            risk_score: Optional risk score from RiskScorer (0-1)
            
        Returns:
            (tier: str, reason: str)
        """
        adventurous_score = profile_analysis.get("adventurous_score", 0.0)
        travel_frequency = profile_analysis.get("travel_frequency", "unknown")
        
        # Premium tier indicators
        if adventurous_score > 0.7:
            return ("premium", f"High adventurous score ({adventurous_score:.2f}) indicates riskier activities")
        if risk_score and risk_score > 0.7:
            return ("premium", f"High destination risk ({risk_score:.2f}) requires premium coverage")
        if adventurous_score > 0.5 and travel_frequency == "high":
            return ("premium", "Frequent travel with moderate-high adventure activities")
        
        # Medium tier indicators
        if adventurous_score > 0.4:
            return ("medium", f"Moderate adventurous score ({adventurous_score:.2f}) suggests some risk")
        if risk_score and risk_score > 0.4:
            return ("medium", f"Moderate destination risk ({risk_score:.2f})")
        if travel_frequency == "high":
            return ("medium", "Frequent travel requires standard coverage")
        
        # Free tier (default)
        return ("free", "Low risk profile - basic coverage recommended")

