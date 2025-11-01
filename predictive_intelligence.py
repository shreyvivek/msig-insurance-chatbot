"""
Block 5: Predictive Intelligence
Analyze claims data to provide personalized risk assessments and recommendations
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
# import pandas as pd  # Not needed for synthetic data
from groq import Groq

logger = logging.getLogger(__name__)

class PredictiveIntelligence:
    """Handles claims data analysis and predictive recommendations"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        self.claims_data = {}
        self._load_claims_data()
    
    def _load_claims_data(self):
        """Load and process claims data"""
        claims_pdf_path = Path(__file__).parent / "Claims_Data_DB.pdf"
        
        # For now, create synthetic claims data structure
        # In production, this would extract from PDF
        self.claims_data = {
            "destinations": {
                "Japan": {
                    "total_claims": 245,
                    "avg_claim_amount": 35000,
                    "common_claim_types": ["medical", "trip_cancellation", "baggage"],
                    "high_risk_months": [1, 2, 12],  # Winter months for skiing
                    "high_risk_activities": ["skiing", "snowboarding"],
                    "medical_claims_above_30k": 0.8  # 80%
                },
                "Thailand": {
                    "total_claims": 189,
                    "avg_claim_amount": 15000,
                    "common_claim_types": ["baggage", "medical", "trip_delay"],
                    "high_risk_months": [7, 8, 12, 1],  # Monsoon and peak season
                    "high_risk_activities": ["water_sports", "diving"],
                    "baggage_loss_rate": 0.3  # 30% of claims
                },
                "Australia": {
                    "total_claims": 156,
                    "avg_claim_amount": 22000,
                    "common_claim_types": ["medical", "trip_cancellation"],
                    "high_risk_months": [6, 7, 8],  # Winter
                    "high_risk_activities": ["hiking", "outdoor_activities"],
                    "medical_claims_above_30k": 0.6
                },
                "USA": {
                    "total_claims": 312,
                    "avg_claim_amount": 28000,
                    "common_claim_types": ["medical", "trip_cancellation", "baggage"],
                    "high_risk_months": [3, 4, 5, 6, 7, 8],  # Spring/summer
                    "high_risk_activities": ["adventure_sports", "hiking"],
                    "medical_claims_above_30k": 0.65
                },
                "Europe": {
                    "total_claims": 278,
                    "avg_claim_amount": 18000,
                    "common_claim_types": ["baggage", "trip_delay", "medical"],
                    "high_risk_months": [12, 1, 2, 7, 8],  # Winter and summer
                    "high_risk_activities": ["skiing", "hiking"],
                    "baggage_loss_rate": 0.25
                }
            },
            "activities": {
                "skiing": {
                    "risk_level": "high",
                    "avg_claim_amount": 45000,
                    "claim_frequency": 0.15,  # 15% of skiing trips
                    "common_claim_types": ["medical", "equipment_loss"]
                },
                "scuba diving": {
                    "risk_level": "high",
                    "avg_claim_amount": 38000,
                    "claim_frequency": 0.12,
                    "common_claim_types": ["medical", "equipment_damage"]
                },
                "hiking": {
                    "risk_level": "medium",
                    "avg_claim_amount": 22000,
                    "claim_frequency": 0.08,
                    "common_claim_types": ["medical", "trip_interruption"]
                },
                "water_sports": {
                    "risk_level": "medium",
                    "avg_claim_amount": 18000,
                    "claim_frequency": 0.10,
                    "common_claim_types": ["medical", "equipment_damage"]
                }
            },
            "age_groups": {
                "18-30": {"risk_multiplier": 1.0, "common_claims": ["adventure_sports", "baggage"]},
                "31-50": {"risk_multiplier": 1.1, "common_claims": ["medical", "trip_cancellation"]},
                "51-65": {"risk_multiplier": 1.3, "common_claims": ["medical", "trip_cancellation"]},
                "65+": {"risk_multiplier": 1.8, "common_claims": ["medical", "emergency_evacuation"]}
            },
            "seasonal_patterns": {
                "winter": {"regions": ["Japan", "Europe", "USA"], "risk_increase": 1.4},
                "summer": {"regions": ["Thailand", "Australia"], "risk_increase": 1.2},
                "monsoon": {"regions": ["Thailand", "Southeast_Asia"], "risk_increase": 1.5}
            }
        }
        
        logger.info("Claims data loaded successfully")
    
    async def get_risk_assessment(self, destination: str, activities: List[str] = None,
                                 duration: int = None, age: int = None, 
                                 month: int = None) -> Dict:
        """Get personalized risk assessment"""
        
        destination_data = self.claims_data["destinations"].get(
            destination,
            self.claims_data["destinations"].get("Thailand")  # Default
        )
        
        # Calculate risk score
        base_risk = 0.5  # Base risk score (0-1)
        
        # Destination risk
        if destination_data:
            base_risk = 0.6 if destination_data.get("avg_claim_amount", 0) > 25000 else 0.4
        
        # Activity risk
        activity_risks = []
        if activities:
            for activity in activities:
                activity_lower = activity.lower()
                for act_name, act_data in self.claims_data["activities"].items():
                    if act_name in activity_lower:
                        activity_risks.append(act_data)
                        if act_data["risk_level"] == "high":
                            base_risk += 0.2
                        elif act_data["risk_level"] == "medium":
                            base_risk += 0.1
        
        # Age risk
        age_multiplier = 1.0
        if age:
            if age < 30:
                age_multiplier = 1.0
            elif age < 50:
                age_multiplier = 1.1
            elif age < 65:
                age_multiplier = 1.3
            else:
                age_multiplier = 1.8
        
        # Seasonal risk
        seasonal_risk = 1.0
        if month and destination_data:
            if month in destination_data.get("high_risk_months", []):
                seasonal_risk = 1.4
        
        # Duration risk
        duration_risk = 1.0
        if duration:
            if duration > 30:
                duration_risk = 1.3
            elif duration > 14:
                duration_risk = 1.1
        
        final_risk_score = min(base_risk * age_multiplier * seasonal_risk * duration_risk, 1.0)
        
        # Generate insights using Groq
        insights_prompt = f"""Based on historical claims data, provide risk insights for:

Destination: {destination}
Activities: {', '.join(activities) if activities else 'Standard travel'}
Duration: {duration} days
Age: {age} years old
Travel Month: {month}

Claims Data Summary:
- Average claim amount: ${destination_data.get('avg_claim_amount', 0):,.0f}
- Common claim types: {', '.join(destination_data.get('common_claim_types', []))}
- High-risk activities: {', '.join(destination_data.get('high_risk_activities', []))}

Risk Score: {final_risk_score:.2f}

Provide:
1. Key risk factors for this trip
2. Recommended coverage levels (medical, trip cancellation, baggage)
3. Specific risks to watch out for
4. Coverage gaps that travelers often miss
5. Personalized recommendations

Be specific with numbers and actionable advice."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert risk analyst for travel insurance. Provide specific, data-driven insights."},
                    {"role": "user", "content": insights_prompt}
                ],
                temperature=0.3
            )
            
            insights_text = response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            insights_text = "Unable to generate detailed insights."
        
        return {
            "destination": destination,
            "risk_score": round(final_risk_score, 2),
            "risk_level": self._risk_level(final_risk_score),
            "destination_data": destination_data,
            "activity_risks": activity_risks,
            "age_multiplier": age_multiplier,
            "seasonal_risk": seasonal_risk,
            "duration_risk": duration_risk,
            "insights": insights_text,
            "high_risk_activities": [a for a in (activities or []) if any(
                act_name in a.lower() for act_name in self.claims_data["activities"].keys()
            )],
            "recommended_coverage": {
                "medical_minimum": 50000 if final_risk_score > 0.7 else 30000,
                "trip_cancellation_minimum": 10000,
                "baggage_minimum": 2000
            }
        }
    
    def _risk_level(self, score: float) -> str:
        """Convert risk score to level"""
        if score < 0.4:
            return "low"
        elif score < 0.7:
            return "medium"
        else:
            return "high"
    
    async def recommend_coverage(self, destination: str, activities: List[str] = None,
                                trip_cost: float = None, duration: int = None) -> Dict:
        """Get personalized coverage recommendations"""
        
        risk_assessment = await self.get_risk_assessment(
            destination=destination,
            activities=activities,
            duration=duration
        )
        
        # Base recommendations
        recommendations = {
            "medical_coverage": {
                "minimum": risk_assessment["recommended_coverage"]["medical_minimum"],
                "recommended": risk_assessment["recommended_coverage"]["medical_minimum"] * 1.5,
                "reason": "Based on historical claims data for this destination"
            },
            "trip_cancellation": {
                "minimum": risk_assessment["recommended_coverage"]["trip_cancellation_minimum"],
                "recommended": trip_cost if trip_cost else 10000,
                "reason": "Should cover your trip investment"
            },
            "baggage_coverage": {
                "minimum": risk_assessment["recommended_coverage"]["baggage_minimum"],
                "recommended": risk_assessment["recommended_coverage"]["baggage_minimum"] * 2,
                "reason": "Baggage loss is common in this region" if risk_assessment.get("destination_data", {}).get("baggage_loss_rate", 0) > 0.25 else "Standard protection"
            },
            "additional_benefits": []
        }
        
        # Activity-specific recommendations
        if activities:
            for activity in activities:
                activity_lower = activity.lower()
                if "ski" in activity_lower:
                    recommendations["additional_benefits"].append({
                        "benefit": "Sports Equipment Coverage",
                        "coverage": 5000,
                        "reason": "Ski equipment is expensive and commonly lost/stolen"
                    })
                if "dive" in activity_lower or "scuba" in activity_lower:
                    recommendations["additional_benefits"].append({
                        "benefit": "Adventure Sports Coverage",
                        "coverage": "Full medical coverage",
                        "reason": "Diving accidents often require expensive medical treatment"
                    })
        
        # Generate personalized message
        dest_data = risk_assessment.get("destination_data", {})
        if dest_data.get("medical_claims_above_30k", 0) > 0.7:
            recommendations["urgent_recommendation"] = (
                f"⚠️ Based on historical data, {dest_data.get('medical_claims_above_30k', 0)*100:.0f}% "
                f"of medical claims for {destination} exceed $30,000. We strongly recommend "
                f"medical coverage of at least ${recommendations['medical_coverage']['recommended']:,.0f}."
            )
        
        if dest_data.get("baggage_loss_rate", 0) > 0.25:
            recommendations["baggage_tip"] = (
                f"📦 Baggage loss is a common issue for {destination} ({dest_data.get('baggage_loss_rate', 0)*100:.0f}% of claims). "
                f"Consider adding baggage protection."
            )
        
        return {
            "destination": destination,
            "risk_assessment": risk_assessment,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_insights_summary(self) -> Dict:
        """Get summary of claims insights"""
        return {
            "total_destinations_analyzed": len(self.claims_data["destinations"]),
            "key_insights": [
                "Japan: 80% of medical claims exceed $30k (winter sports risk)",
                "Thailand: 30% of claims are baggage-related",
                "Skiing activities have 15% claim frequency with avg $45k",
                "Senior travelers (65+) have 1.8x higher risk multiplier"
            ],
            "top_risk_activities": ["skiing", "scuba diving", "adventure sports"],
            "high_cost_destinations": ["Japan", "USA", "Australia"]
        }

