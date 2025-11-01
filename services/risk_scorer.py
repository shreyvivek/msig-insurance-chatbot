"""
Risk scoring service combining Claims DB and user profile
"""
import math
import logging
from typing import Dict, Optional
from claims_database import ClaimsDatabase

logger = logging.getLogger(__name__)

class RiskScorer:
    """Calculates risk scores based on destination, activities, and user profile"""
    
    def __init__(self):
        self.claims_db = ClaimsDatabase()
        
        # Activity risk weights (higher = riskier)
        self.activity_weights = {
            "skiing": 1.8,
            "snowboarding": 1.8,
            "scuba": 2.0,
            "diving": 2.0,
            "snorkeling": 1.2,
            "hiking": 1.3,
            "trekking": 1.5,
            "mountaineering": 2.2,
            "climbing": 2.0,
            "rock climbing": 2.1,
            "bungee": 1.9,
            "bungee jumping": 1.9,
            "skydiving": 2.2,
            "paragliding": 2.1,
            "parasailing": 1.6,
            "rafting": 1.7,
            "kayaking": 1.4,
            "canoeing": 1.3,
            "surfing": 1.6,
            "windsurfing": 1.7,
            "backpacking": 1.2,
            "camping": 1.1,
            "safari": 1.3,
            "extreme sports": 2.0,
            "adventure": 1.4  # Generic
        }
    
    def predict(self, trip_features: Dict, user_profile: Optional[Dict] = None) -> Dict:
        """
        Calculate risk score and recommended coverage
        
        Args:
            trip_features: {
                "destination": str,
                "start_date": str (YYYY-MM-DD),
                "end_date": str (YYYY-MM-DD),
                "activities": List[str] (optional)
            }
            user_profile: {
                "adventurous_score": float (0-1),
                "age": int (optional)
            }
            
        Returns:
            {
                "risk_prob": float (0-1),
                "category": "low|medium|high",
                "recommended_medical": int (SGD),
                "recommended_coverage_upgrades": List[Dict],
                "evidence": Dict
            }
        """
        destination = trip_features.get("destination", "").strip()
        activities = trip_features.get("activities", []) or []
        
        if not destination:
            return self._default_risk()
        
        # Get claims data for destination
        claims_data = self._get_claims_for_destination(destination)
        
        # Calculate base score from claims
        base_score = self._normalize_claim_count(claims_data.get("claim_count", 0))
        
        # Apply activity multipliers
        activity_multiplier = self._calculate_activity_multiplier(activities)
        
        # Apply age penalty (if available)
        age = user_profile.get("age") if user_profile else None
        age_penalty = self._calculate_age_penalty(age)
        
        # Apply adventurous score (from Instagram)
        adventurous_score = user_profile.get("adventurous_score", 0.0) if user_profile else 0.0
        adventurous_bonus = 1.0 + (adventurous_score * 0.3)  # Up to 30% increase
        
        # Apply duration factor
        duration_factor = self._calculate_duration_factor(trip_features)
        
        # Calculate composite risk score
        score = base_score * activity_multiplier * age_penalty * adventurous_bonus * duration_factor
        
        # Convert to probability (0-1)
        risk_prob = self._sigmoid(score * 5 - 2.5)  # Scale for sigmoid
        
        # Categorize
        if risk_prob < 0.3:
            category = "low"
        elif risk_prob < 0.7:
            category = "medium"
        else:
            category = "high"
        
        # Calculate recommended medical coverage
        avg_claim = claims_data.get("avg_claim_amount", 20000)
        recommended_medical = max(int(avg_claim * 1.5), 30000)
        
        if category == "high":
            recommended_medical = max(recommended_medical, 100000)
        elif category == "medium":
            recommended_medical = max(recommended_medical, 50000)
        
        # Generate coverage upgrade recommendations
        recommended_upgrades = self._generate_upgrade_recommendations(
            category, activities, claims_data
        )
        
        return {
            "risk_prob": round(risk_prob, 3),
            "category": category,
            "recommended_medical": recommended_medical,
            "recommended_coverage_upgrades": recommended_upgrades,
            "evidence": {
                "destination": destination,
                "claims_count": claims_data.get("claim_count", 0),
                "avg_claim_amount": claims_data.get("avg_claim_amount", 0),
                "activities": activities,
                "activity_multiplier": round(activity_multiplier, 2),
                "adventurous_score": adventurous_score
            }
        }
    
    def _get_claims_for_destination(self, destination: str) -> Dict:
        """Get aggregated claims data for destination"""
        if not self.claims_db.is_connected():
            # Return mock data if DB not connected
            return {
                "claim_count": 150,
                "avg_claim_amount": 25000,
                "median_claim_amount": 18000,
                "top_claim_reasons": ["Medical emergency", "Trip cancellation", "Baggage loss"]
            }
        
        try:
            claims = self.claims_db.get_claims_by_destination(destination, limit=1000)
            
            if not claims:
                return {
                    "claim_count": 0,
                    "avg_claim_amount": 20000,
                    "median_claim_amount": 15000,
                    "top_claim_reasons": []
                }
            
            # Aggregate claims
            amounts = [float(c.get("gross_incurred", 0) or 0) for c in claims if c.get("gross_incurred")]
            claim_count = len(claims)
            
            avg_amount = sum(amounts) / len(amounts) if amounts else 20000
            sorted_amounts = sorted(amounts)
            median_amount = sorted_amounts[len(sorted_amounts)//2] if sorted_amounts else 15000
            
            # Get top claim reasons
            claim_reasons = {}
            for claim in claims:
                reason = claim.get("cause_of_loss") or claim.get("loss_type") or "Unknown"
                claim_reasons[reason] = claim_reasons.get(reason, 0) + 1
            
            top_reasons = sorted(claim_reasons.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "claim_count": claim_count,
                "avg_claim_amount": avg_amount,
                "median_claim_amount": median_amount,
                "top_claim_reasons": [r[0] for r in top_reasons]
            }
        except Exception as e:
            logger.error(f"Error getting claims data: {e}")
            return {
                "claim_count": 0,
                "avg_claim_amount": 20000,
                "median_claim_amount": 15000,
                "top_claim_reasons": []
            }
    
    def _normalize_claim_count(self, count: int, max_count: int = 1000) -> float:
        """Normalize claim count to 0-1 scale"""
        return min(count / max_count, 1.0)
    
    def _calculate_activity_multiplier(self, activities: list) -> float:
        """Calculate risk multiplier based on activities"""
        if not activities:
            return 1.0
        
        # Get max weight from activities
        max_weight = max([
            self.activity_weights.get(activity.lower(), 1.0)
            for activity in activities
        ], default=1.0)
        
        return max_weight
    
    def _calculate_age_penalty(self, age: Optional[int]) -> float:
        """Age-based risk adjustment"""
        if age is None:
            return 1.0
        
        if age < 18:
            return 1.1  # Slightly higher for minors
        elif age > 65:
            return 1.3  # Higher risk for seniors
        else:
            return 1.0
    
    def _calculate_duration_factor(self, trip_features: Dict) -> float:
        """Duration-based risk factor"""
        try:
            start = trip_features.get("start_date")
            end = trip_features.get("end_date")
            
            if not start or not end:
                return 1.0
            
            from datetime import datetime
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            duration_days = (end_date - start_date).days
            
            if duration_days <= 0:
                return 1.0
            
            # Longer trips = slightly higher risk
            return 1.0 + min((duration_days - 7) / 60, 0.3)  # Max 30% increase
        except:
            return 1.0
    
    def _sigmoid(self, x: float) -> float:
        """Sigmoid function for probability"""
        return 1 / (1 + math.exp(-x))
    
    def _generate_upgrade_recommendations(self, category: str, activities: list, claims_data: Dict) -> list:
        """Generate coverage upgrade recommendations"""
        recommendations = []
        
        # Medical coverage
        if category in ["medium", "high"]:
            recommendations.append({
                "type": "medical_coverage",
                "reason": f"High risk category ({category}) requires enhanced medical protection",
                "suggested_amount": 100000 if category == "high" else 50000
            })
        
        # Activity-specific recommendations
        risky_activities = ["skiing", "scuba", "mountaineering", "skydiving", "paragliding"]
        if any(act.lower() in risky_activities for act in activities):
            recommendations.append({
                "type": "adventure_sports_coverage",
                "reason": "Adventure activities require specialized coverage",
                "suggested_amount": "include"
            })
        
        # Evacuation coverage for remote destinations
        if claims_data.get("avg_claim_amount", 0) > 50000:
            recommendations.append({
                "type": "emergency_evacuation",
                "reason": "High average claim amounts suggest need for evacuation coverage",
                "suggested_amount": 200000
            })
        
        return recommendations
    
    def _default_risk(self) -> Dict:
        """Default risk for missing data"""
        return {
            "risk_prob": 0.3,
            "category": "low",
            "recommended_medical": 30000,
            "recommended_coverage_upgrades": [],
            "evidence": {}
        }

