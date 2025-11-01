"""
Activity-Based Policy Matching
Deep quantitative comparison of policies based on specific activities (skiing, scuba, etc.)
"""

import os
import logging
from typing import Dict, List, Optional, Any
import json
from groq import Groq

logger = logging.getLogger(__name__)

class ActivityPolicyMatcher:
    """Matches and compares policies based on specific travel activities"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        
        # Activity-specific coverage requirements
        self.activity_requirements = {
            "skiing": {
                "medical_coverage_min": 100000,
                "required_coverage": ["winter_sports", "medical_emergency", "evacuation"],
                "exclusions_to_check": ["pre-existing_conditions", "alcohol_related"],
                "risk_level": "high"
            },
            "scuba": {
                "medical_coverage_min": 150000,
                "required_coverage": ["diving", "hyperbaric_treatment", "evacuation"],
                "exclusions_to_check": ["depth_limits", "certification_requirements"],
                "risk_level": "high"
            },
            "hiking": {
                "medical_coverage_min": 75000,
                "required_coverage": ["medical_emergency", "evacuation", "search_rescue"],
                "exclusions_to_check": ["altitude_limits", "difficulty_ratings"],
                "risk_level": "medium"
            },
            "paragliding": {
                "medical_coverage_min": 150000,
                "required_coverage": ["adventure_sports", "evacuation"],
                "exclusions_to_check": ["instructor_certification", "weather_conditions"],
                "risk_level": "high"
            },
            "bungee": {
                "medical_coverage_min": 100000,
                "required_coverage": ["adventure_sports", "medical_emergency"],
                "exclusions_to_check": ["operator_certification", "equipment_safety"],
                "risk_level": "high"
            }
        }
    
    async def compare_policies_for_activity(
        self,
        activity: str,
        policies: List[Dict],
        trip_details: Dict = None
    ) -> Dict:
        """
        Deep quantitative comparison of policies for a specific activity
        Returns detailed comparison with scores and recommendations
        """
        if activity.lower() not in self.activity_requirements:
            logger.warning(f"Unknown activity: {activity}")
            activity = "adventure"  # Default
        
        requirements = self.activity_requirements.get(activity.lower(), {})
        
        comparisons = []
        
        for policy in policies:
            policy_name = policy.get("name", "")
            policy_text = await self._get_policy_text(policy_name)
            
            if not policy_text:
                continue
            
            # Deep analysis of policy text for activity coverage
            analysis = await self._analyze_policy_for_activity(
                policy_text,
                activity,
                requirements,
                policy
            )
            
            comparisons.append({
                "policy": policy_name,
                "activity": activity,
                "score": analysis["score"],
                "coverage_analysis": analysis["coverage"],
                "exclusions": analysis["exclusions"],
                "recommendation": analysis["recommendation"],
                "quantitative_comparison": analysis["quantitative"]
            })
        
        # Sort by score
        comparisons.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "activity": activity,
            "requirements": requirements,
            "comparisons": comparisons,
            "best_match": comparisons[0] if comparisons else None,
            "summary": self._generate_comparison_summary(comparisons, activity)
        }
    
    async def _get_policy_text(self, policy_name: str) -> Optional[str]:
        """Get full policy text"""
        try:
            from policy_intelligence import PolicyIntelligence
            policy_intel = PolicyIntelligence()
            return policy_intel.get_policy_text(policy_name)
        except:
            return None
    
    async def _analyze_policy_for_activity(
        self,
        policy_text: str,
        activity: str,
        requirements: Dict,
        policy_data: Dict
    ) -> Dict:
        """Deep analysis of policy text for specific activity coverage"""
        
        # Extract relevant sections
        analysis_prompt = f"""Analyze this travel insurance policy for {activity} coverage.

Policy Text (excerpt):
{policy_text[:8000]}

Activity Requirements:
- Medical coverage minimum: ${requirements.get('medical_coverage_min', 0):,}
- Required coverage types: {', '.join(requirements.get('required_coverage', []))}
- Exclusions to check: {', '.join(requirements.get('exclusions_to_check', []))}

Provide a quantitative analysis:
1. Medical coverage amount (exact number)
2. Does it cover {activity}? (Yes/No/Partial)
3. Specific exclusions related to {activity}
4. Coverage limits for {activity}
5. Any restrictions or conditions
6. Score out of 100 based on how well it matches requirements

Return as JSON:
{{
    "medical_coverage": <number>,
    "activity_coverage": "Yes/No/Partial",
    "coverage_details": "<text>",
    "exclusions": ["exclusion1", "exclusion2"],
    "limits": {{"amount": <number>, "description": "<text>"}},
    "restrictions": ["restriction1"],
    "score": <0-100>,
    "reasoning": "<why this score>"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert insurance policy analyzer. Provide precise quantitative analysis with exact numbers and clear yes/no answers."
                    },
                    {"role": "user", "content": analysis_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Build structured analysis
            medical_coverage = analysis.get("medical_coverage", 0)
            meets_minimum = medical_coverage >= requirements.get("medical_coverage_min", 0)
            activity_covered = analysis.get("activity_coverage", "No") in ["Yes", "Partial"]
            
            # Calculate score
            base_score = analysis.get("score", 50)
            if not meets_minimum:
                base_score -= 30
            if not activity_covered:
                base_score -= 40
            if analysis.get("activity_coverage") == "Partial":
                base_score -= 15
            
            score = max(0, min(100, base_score))
            
            return {
                "score": score,
                "coverage": {
                    "medical_amount": medical_coverage,
                    "meets_minimum": meets_minimum,
                    "activity_covered": activity_covered,
                    "coverage_details": analysis.get("coverage_details", ""),
                    "limits": analysis.get("limits", {})
                },
                "exclusions": analysis.get("exclusions", []),
                "restrictions": analysis.get("restrictions", []),
                "quantitative": {
                    "medical_coverage": medical_coverage,
                    "minimum_required": requirements.get("medical_coverage_min", 0),
                    "coverage_gap": max(0, requirements.get("medical_coverage_min", 0) - medical_coverage),
                    "activity_coverage_status": analysis.get("activity_coverage", "No"),
                    "exclusion_count": len(analysis.get("exclusions", [])),
                    "restriction_count": len(analysis.get("restrictions", []))
                },
                "recommendation": self._generate_recommendation(score, analysis, activity),
                "reasoning": analysis.get("reasoning", "")
            }
        
        except Exception as e:
            logger.error(f"Policy analysis failed: {e}", exc_info=True)
            return {
                "score": 0,
                "coverage": {},
                "exclusions": [],
                "quantitative": {},
                "recommendation": f"Unable to analyze policy for {activity}",
                "reasoning": str(e)
            }
    
    def _generate_recommendation(self, score: int, analysis: Dict, activity: str) -> str:
        """Generate recommendation based on analysis"""
        if score >= 80:
            return f"✅ Excellent match for {activity} - Strong coverage with minimal exclusions"
        elif score >= 60:
            return f"⚠️ Good match for {activity} - Adequate coverage but check exclusions"
        elif score >= 40:
            return f"⚠️ Partial match for {activity} - Some coverage gaps, review carefully"
        else:
            return f"❌ Poor match for {activity} - Significant coverage gaps or exclusions"
    
    def _generate_comparison_summary(self, comparisons: List[Dict], activity: str) -> str:
        """Generate human-readable comparison summary"""
        if not comparisons:
            return f"No policies found for {activity} comparison"
        
        best = comparisons[0]
        summary_parts = [
            f"**Best Match for {activity.title()}**: {best['policy']} (Score: {best['score']}/100)",
            best['recommendation']
        ]
        
        if len(comparisons) > 1:
            summary_parts.append(f"\n**Comparison**: {len(comparisons)} policies analyzed")
            top_scores = [f"{c['policy']} ({c['score']})" for c in comparisons[:3]]
            summary_parts.append(f"Top 3 scores: {', '.join(top_scores)}")
        
        return "\n".join(summary_parts)

