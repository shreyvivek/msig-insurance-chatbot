"""
Intelligent Recommendation Engine
Uses Blocks 1 (Policy Intelligence), 2 (Conversational), and 5 (Predictive Intelligence)
to produce personalized, context-aware recommendations
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from groq import Groq

logger = logging.getLogger(__name__)

class IntelligentRecommender:
    """Produces personalized insurance recommendations using all intelligence blocks"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
    
    async def recommend_policies(
        self,
        trip_details: Dict,
        user_profile: Dict = None,
        available_quotes: List[Dict] = None,
        policy_intel = None,
        predictive_intel = None,
        claims_db = None
    ) -> Dict:
        """
        Intelligent recommendation using Blocks 1, 2, and 5
        
        Args:
            trip_details: Destination, dates, travelers, activities, etc.
            user_profile: User's preferences, history, risk profile
            available_quotes: Quotes from Ancileo and local policies
            policy_intel: Block 1 - Policy Intelligence instance
            predictive_intel: Block 5 - Predictive Intelligence instance
        
        Returns:
            {
                "recommendations": List of ranked recommendations with reasons,
                "comparison": Policy comparison matrix,
                "risk_insights": Risk assessment insights,
                "personalization_factors": What made it personal
            }
        """
        
        destination = trip_details.get("destination") or trip_details.get("arrival_country", "")
        activities = trip_details.get("activities", [])
        travelers = trip_details.get("travelers") or trip_details.get("adults", 1)
        ages = trip_details.get("ages", [])
        trip_cost = trip_details.get("trip_cost")
        duration = trip_details.get("duration")
        
        # Block 5: Get risk assessment and insights
        risk_assessment = None
        if predictive_intel:
            try:
                avg_age = sum(ages) / len(ages) if ages else 30
                travel_month = None
                if trip_details.get("departure_date"):
                    try:
                        travel_month = datetime.strptime(trip_details["departure_date"], "%Y-%m-%d").month
                    except:
                        pass
                
                risk_assessment = await predictive_intel.get_risk_assessment(
                    destination=destination,
                    activities=activities,
                    duration=duration,
                    age=int(avg_age),
                    month=travel_month
                )
            except Exception as e:
                logger.error(f"Risk assessment failed: {e}")
        
        # Block 1: Get policy comparison data
        policy_comparison = None
        if policy_intel and available_quotes:
            try:
                # Compare policies on relevant criteria
                criteria = self._build_comparison_criteria(trip_details, risk_assessment, user_profile)
                policy_names = [q.get("plan_name") for q in available_quotes if q.get("plan_name")]
                if policy_names:
                    policy_comparison = await policy_intel.compare_policies(
                        criteria=criteria,
                        policies=policy_names[:3]  # Compare top 3
                    )
            except Exception as e:
                logger.error(f"Policy comparison failed: {e}")
        
        # Get claims data for personalization
        claims_data = None
        if claims_db:
            try:
                destination = trip_details.get("destination") or trip_details.get("arrival_country", "")
                ages = trip_details.get("ages", [])
                interests = user_profile.get("interests", []) if user_profile else []
                medical_conditions = user_profile.get("medical_conditions", []) if user_profile else []
                
                # Get personalized claims
                personalized_claims = claims_db.get_personalized_claims(
                    destination=destination,
                    ages=ages,
                    interests=interests,
                    medical_conditions=medical_conditions,
                    trip_duration=trip_details.get("duration"),
                    num_travelers=trip_details.get("travelers") or trip_details.get("adults", 1),
                    purpose=trip_details.get("purpose"),
                    limit=50
                )
                
                # Analyze claims for each policy
                policy_claims_analysis = {}
                for quote in (available_quotes or [])[:5]:  # Top 5 quotes
                    plan_name = quote.get("plan_name", "")
                    if plan_name:
                        analysis = claims_db.analyze_claims_for_policy_scoring(
                            policy_name=plan_name,
                            destination=destination,
                            ages=ages,
                            interests=interests,
                            medical_conditions=medical_conditions
                        )
                        policy_claims_analysis[plan_name] = analysis
                
                claims_data = {
                    "personalized_claims": personalized_claims[:20],  # Top 20 most relevant
                    "policy_analysis": policy_claims_analysis,
                    "total_claims_found": len(personalized_claims)
                }
            except Exception as e:
                logger.error(f"Error getting claims data: {e}", exc_info=True)
        
        # Use LLM to synthesize recommendations (Block 2 - Conversational Intelligence)
        recommendation = await self._generate_personalized_recommendation(
            trip_details=trip_details,
            user_profile=user_profile,
            available_quotes=available_quotes or [],
            risk_assessment=risk_assessment,
            policy_comparison=policy_comparison,
            claims_data=claims_data
        )
        
        return recommendation
    
    def _build_comparison_criteria(
        self,
        trip_details: Dict,
        risk_assessment: Dict = None,
        user_profile: Dict = None
    ) -> str:
        """Build criteria string for policy comparison based on context"""
        criteria_parts = []
        
        if risk_assessment:
            criteria_parts.append(f"Medical coverage minimum: ${risk_assessment.get('recommended_coverage', {}).get('medical_minimum', 30000):,}")
            criteria_parts.append(f"Risk level: {risk_assessment.get('risk_level', 'medium')}")
        
        destination = trip_details.get("destination", "")
        if destination:
            criteria_parts.append(f"Destination-specific coverage needs for {destination}")
        
        activities = trip_details.get("activities", [])
        if activities:
            criteria_parts.append(f"Activity coverage: {', '.join(activities)}")
        
        if user_profile:
            preferred = user_profile.get("preferences", {}).get("preferred_coverage", "")
            if preferred:
                criteria_parts.append(f"User preference: {preferred} coverage")
        
        return "; ".join(criteria_parts) if criteria_parts else "comprehensive coverage, good value"
    
    async def _generate_personalized_recommendation(
        self,
        trip_details: Dict,
        user_profile: Dict,
        available_quotes: List[Dict],
        risk_assessment: Dict = None,
        policy_comparison: Dict = None,
        claims_data: Dict = None
    ) -> Dict:
        """Generate personalized recommendation using conversational AI"""
        
        # Build context
        context_parts = []
        
        if user_profile:
            context_parts.append(f"User Profile:\n- Travel history: {len(user_profile.get('travel_history', []))} past trips")
            context_parts.append(f"- Preferences: {user_profile.get('preferences', {})}")
            context_parts.append(f"- Loyalty tier: {user_profile.get('insurance_profile', {}).get('loyalty_tier', 'bronze')}")
        
        if risk_assessment:
            context_parts.append(f"\nRisk Assessment:\n- Risk level: {risk_assessment.get('risk_level')}")
            context_parts.append(f"- Recommended medical coverage: ${risk_assessment.get('recommended_coverage', {}).get('medical_minimum', 0):,}")
            if risk_assessment.get('insights'):
                context_parts.append(f"- Key insights: {risk_assessment['insights'][:300]}")
        
        if policy_comparison:
            context_parts.append(f"\nPolicy Comparison:\n{json.dumps(policy_comparison, indent=2)[:500]}")
        
        # Add claims data context
        if claims_data:
            claims_context = []
            claims_context.append(f"\n📊 Historical Claims Data Analysis:")
            claims_context.append(f"Total relevant claims found: {claims_data.get('total_claims_found', 0)}")
            
            # Add policy-specific claims analysis
            policy_analysis = claims_data.get("policy_analysis", {})
            for plan_name, analysis in list(policy_analysis.items())[:3]:  # Top 3
                if analysis.get("total_claims", 0) > 0:
                    claims_context.append(
                        f"\n{plan_name}:"
                        f"\n  - Total claims: {analysis.get('total_claims', 0)}"
                        f"\n  - Approval rate: {analysis.get('approval_rate', 0)}%"
                        f"\n  - Average payout: ${analysis.get('average_payout', 0):,.2f}"
                        f"\n  - Common claim types: {', '.join(list(analysis.get('claim_types', {}).keys())[:3])}"
                    )
            
            # Add relevant historical claims snippets
            personalized_claims = claims_data.get("personalized_claims", [])
            if personalized_claims:
                claims_context.append(f"\n\nRelevant Historical Claims (Top 5):")
                for i, claim in enumerate(personalized_claims[:5], 1):
                    claim_type = claim.get("claim_type", "Unknown")
                    cause = claim.get("cause_of_loss", "Unknown")
                    amount = claim.get("gross_incurred") or claim.get("net_incurred", 0)
                    dest = claim.get("destination", "Unknown")
                    claims_context.append(
                        f"{i}. {claim_type} - {cause} in {dest}: ${amount:,.2f}"
                    )
            
            context_parts.append("\n".join(claims_context))
        
        quotes_summary = []
        for i, quote in enumerate(available_quotes[:5], 1):
            quotes_summary.append(
                f"{i}. {quote.get('plan_name', 'Unknown')} - "
                f"{quote.get('currency', 'SGD')} {quote.get('price', 0):.2f} "
                f"({quote.get('source', 'local')})"
            )
        
        prompt = f"""You are an expert insurance advisor providing personalized recommendations based on REAL historical claims data.

Trip Details:
- Destination: {trip_details.get('destination', 'Unknown')}
- Travelers: {trip_details.get('travelers', trip_details.get('adults', 1))}
- Dates: {trip_details.get('departure_date', 'Unknown')} to {trip_details.get('return_date', 'Unknown')}
- Activities: {', '.join(trip_details.get('activities', [])) or 'Standard travel'}

Available Quotes:
{chr(10).join(quotes_summary)}

{chr(10).join(context_parts) if context_parts else ''}

Provide a personalized recommendation that:
1. Ranks the top 3 quotes with clear reasons
2. Explains WHY each is recommended based on trip details, user profile, risk assessment, AND historical claims data
3. Uses the historical claims data to justify recommendations - cite specific claim types, frequencies, and payouts
4. Highlights what makes each recommendation PERSONAL to this user based on their age, interests, medical conditions
5. Mentions specific coverage amounts and why they matter for THIS trip based on similar historical cases
6. References actual historical claims that justify the coverage recommendations
7. Makes it feel like you understand their unique situation based on real data

Format as JSON:
{{
    "top_recommendation": {{
        "quote_index": 0,
        "plan_name": "name",
        "reason": "why this is best for them",
        "personalization": "what makes it personal",
        "key_features": ["feature1", "feature2"]
    }},
    "alternatives": [
        {{
            "quote_index": 1,
            "plan_name": "name",
            "reason": "why this is a good alternative",
            "best_for": "who/what it's best for"
        }}
    ],
    "comparison_summary": "brief comparison of top options",
    "personalization_factors": ["factor1", "factor2", "factor3"],
    "historical_claims_justification": "how historical claims data supports this recommendation",
    "risk_warnings": ["warning1", "warning2"],
    "suggested_add_ons": ["addon1", "addon2"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert insurance advisor. Provide clear, personalized recommendations with specific reasons. Always output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Map recommendations back to actual quotes
            recommendations = []
            if result.get("top_recommendation"):
                rec = result["top_recommendation"]
                quote_idx = rec.get("quote_index", 0)
                if 0 <= quote_idx < len(available_quotes):
                    recommendations.append({
                        "quote": available_quotes[quote_idx],
                        "rank": 1,
                        "reason": rec.get("reason", ""),
                        "personalization": rec.get("personalization", ""),
                        "key_features": rec.get("key_features", [])
                    })
            
            alternatives = []
            for alt in result.get("alternatives", []):
                quote_idx = alt.get("quote_index", 0)
                if 0 <= quote_idx < len(available_quotes):
                    alternatives.append({
                        "quote": available_quotes[quote_idx],
                        "rank": len(alternatives) + 2,
                        "reason": alt.get("reason", ""),
                        "best_for": alt.get("best_for", "")
                    })
            
            return {
                "recommendations": recommendations,
                "alternatives": alternatives,
                "risk_insights": risk_assessment,
                "comparison_summary": result.get("comparison_summary", ""),
                "personalization_factors": result.get("personalization_factors", []),
                "policy_comparison": policy_comparison,
                "historical_claims_justification": result.get("historical_claims_justification", ""),
                "risk_warnings": result.get("risk_warnings", []),
                "suggested_add_ons": result.get("suggested_add_ons", []),
                "claims_data": claims_data
            }
        
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}", exc_info=True)
            # Fallback to simple ranking
            return self._fallback_recommendation(available_quotes, risk_assessment)
    
    def _fallback_recommendation(self, quotes: List[Dict], risk_assessment: Dict = None) -> Dict:
        """Simple fallback recommendation"""
        if not quotes:
            return {"recommendations": [], "alternatives": []}
        
        # Simple ranking by price or features
        sorted_quotes = sorted(quotes, key=lambda q: q.get("price", 0))
        
        recommendations = []
        if sorted_quotes:
            recommendations.append({
                "quote": sorted_quotes[0],
                "rank": 1,
                "reason": "Best value option with good coverage",
                "personalization": "Recommended based on trip requirements",
                "key_features": []
            })
        
        return {
            "recommendations": recommendations,
            "alternatives": [{"quote": q, "rank": i+2} for i, q in enumerate(sorted_quotes[1:3])],
            "risk_insights": risk_assessment,
            "comparison_summary": "Top options ranked by value",
            "personalization_factors": []
        }

