"""
Quantitative policy comparison service
Compares policies for specific scenarios (e.g., skiing in Japan)
"""
import logging
from typing import Dict, List
from policy_intelligence import PolicyIntelligence
from groq import Groq
import os
import json

logger = logging.getLogger(__name__)

class PolicyComparator:
    """Quantitative policy comparison for scenarios"""
    
    def __init__(self):
        self.policy_intel = PolicyIntelligence()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
    
    async def compare(self, policyA_id: str, policyB_id: str, scenario: Dict) -> Dict:
        """
        Compare two policies quantitatively for a scenario
        
        Args:
            policyA_id: First policy ID (e.g., "TravelEasy")
            policyB_id: Second policy ID (e.g., "Scootsurance")
            scenario: {
                "destination": str,
                "activities": List[str],
                "age": int (optional),
                "duration": int (days, optional)
            }
            
        Returns:
            {
                "benefit_comparison_table": List[Dict],
                "composite_scores": {"policyA": float, "policyB": float},
                "best_policy": str,
                "justification": str,
                "citations": List[Dict]
            }
        """
        # Get normalized policy data
        policies_data = self.policy_intel.get_normalized_data()
        
        policyA = policies_data.get(policyA_id)
        policyB = policies_data.get(policyB_id)
        
        if not policyA or not policyB:
            raise ValueError(f"Policy not found: {policyA_id} or {policyB_id}")
        
        # Extract relevant benefits for scenario
        activities = scenario.get("activities", []) or []
        destination = scenario.get("destination", "").lower()
        
        # Calculate relevance weights based on scenario
        relevance_weights = self._calculate_relevance_weights(scenario, activities)
        
        # Compare benefits
        benefit_comparison = self._compare_benefits(policyA, policyB, relevance_weights, activities)
        
        # Calculate composite scores
        composite_scores = self._calculate_composite_scores(benefit_comparison)
        
        # Determine best policy
        best_policy = policyA_id if composite_scores[policyA_id] > composite_scores[policyB_id] else policyB_id
        
        # Generate justification with citations
        justification = await self._generate_justification(
            policyA_id, policyB_id, benefit_comparison, composite_scores, best_policy, scenario
        )
        
        # Extract citations
        citations = self._extract_citations(policyA, policyB, benefit_comparison)
        
        return {
            "benefit_comparison_table": benefit_comparison,
            "composite_scores": composite_scores,
            "best_policy": best_policy,
            "justification": justification,
            "citations": citations
        }
    
    def _calculate_relevance_weights(self, scenario: Dict, activities: List[str]) -> Dict:
        """Calculate relevance weights for each benefit based on scenario"""
        weights = {
            "medical_coverage": 0.25,  # Always important
            "emergency_evacuation": 0.15,
            "trip_cancellation": 0.15,
            "baggage_loss": 0.10,
            "personal_accident": 0.10,
            "sports_coverage": 0.10,
            "pre_existing_conditions": 0.05,
            "deductible": 0.05,
            "age_limit": 0.05
        }
        
        # Adjust weights based on activities
        adventure_activities = ["skiing", "scuba", "mountaineering", "skydiving", "paragliding"]
        if any(act.lower() in adventure_activities for act in activities):
            weights["medical_coverage"] = 0.30
            weights["emergency_evacuation"] = 0.25
            weights["sports_coverage"] = 0.20
            weights["trip_cancellation"] = 0.10
            weights["baggage_loss"] = 0.05
            weights["personal_accident"] = 0.10
        
        # Adjust for remote destinations
        remote_destinations = ["nepal", "tibet", "mongolia", "papua", "antarctica"]
        if any(dest in scenario.get("destination", "").lower() for dest in remote_destinations):
            weights["emergency_evacuation"] = 0.30
            weights["medical_coverage"] = 0.25
        
        return weights
    
    def _compare_benefits(self, policyA: Dict, policyB: Dict, weights: Dict, activities: List[str]) -> List[Dict]:
        """Compare individual benefits"""
        comparisons = []
        
        # Medical coverage
        medA = self._extract_value(policyA, "medical_coverage", "max_coverage")
        medB = self._extract_value(policyB, "medical_coverage", "max_coverage")
        comparisons.append({
            "benefit": "Medical Coverage",
            "policyA_value": medA,
            "policyB_value": medB,
            "delta": medA - medB,
            "winner": "A" if medA > medB else "B" if medB > medA else "tie",
            "relevance_weight": weights.get("medical_coverage", 0.25),
            "score_A": self._normalize_value(medA, 200000) * weights.get("medical_coverage", 0.25),
            "score_B": self._normalize_value(medB, 200000) * weights.get("medical_coverage", 0.25)
        })
        
        # Emergency evacuation
        evacA = self._extract_value(policyA, "emergency_evacuation", "coverage")
        evacB = self._extract_value(policyB, "emergency_evacuation", "coverage")
        comparisons.append({
            "benefit": "Emergency Evacuation",
            "policyA_value": evacA,
            "policyB_value": evacB,
            "delta": evacA - evacB,
            "winner": "A" if evacA > evacB else "B" if evacB > evacA else "tie",
            "relevance_weight": weights.get("emergency_evacuation", 0.15),
            "score_A": self._normalize_value(evacA, 500000) * weights.get("emergency_evacuation", 0.15),
            "score_B": self._normalize_value(evacB, 500000) * weights.get("emergency_evacuation", 0.15)
        })
        
        # Sports/adventure coverage
        sportsA = self._check_sports_coverage(policyA, activities)
        sportsB = self._check_sports_coverage(policyB, activities)
        comparisons.append({
            "benefit": "Adventure Sports Coverage",
            "policyA_value": "Covered" if sportsA else "Not Covered",
            "policyB_value": "Covered" if sportsB else "Not Covered",
            "delta": 1 if sportsA else -1 if sportsB else 0,
            "winner": "A" if sportsA and not sportsB else "B" if sportsB and not sportsA else "tie",
            "relevance_weight": weights.get("sports_coverage", 0.10) if activities else 0.0,
            "score_A": (1.0 if sportsA else 0.0) * weights.get("sports_coverage", 0.10),
            "score_B": (1.0 if sportsB else 0.0) * weights.get("sports_coverage", 0.10)
        })
        
        # Trip cancellation
        cancelA = self._extract_value(policyA, "trip_cancellation", "coverage")
        cancelB = self._extract_value(policyB, "trip_cancellation", "coverage")
        comparisons.append({
            "benefit": "Trip Cancellation",
            "policyA_value": cancelA,
            "policyB_value": cancelB,
            "delta": cancelA - cancelB,
            "winner": "A" if cancelA > cancelB else "B" if cancelB > cancelA else "tie",
            "relevance_weight": weights.get("trip_cancellation", 0.15),
            "score_A": self._normalize_value(cancelA, 10000) * weights.get("trip_cancellation", 0.15),
            "score_B": self._normalize_value(cancelB, 10000) * weights.get("trip_cancellation", 0.15)
        })
        
        # Baggage loss
        baggageA = self._extract_value(policyA, "baggage_loss", "coverage")
        baggageB = self._extract_value(policyB, "baggage_loss", "coverage")
        comparisons.append({
            "benefit": "Baggage Loss/Theft",
            "policyA_value": baggageA,
            "policyB_value": baggageB,
            "delta": baggageA - baggageB,
            "winner": "A" if baggageA > baggageB else "B" if baggageB > baggageA else "tie",
            "relevance_weight": weights.get("baggage_loss", 0.10),
            "score_A": self._normalize_value(baggageA, 5000) * weights.get("baggage_loss", 0.10),
            "score_B": self._normalize_value(baggageB, 5000) * weights.get("baggage_loss", 0.10)
        })
        
        # Deductible (lower is better, so reverse scoring)
        deductA = self._extract_value(policyA, "deductible", "amount", default=500)
        deductB = self._extract_value(policyB, "deductible", "amount", default=500)
        comparisons.append({
            "benefit": "Deductible (lower is better)",
            "policyA_value": deductA,
            "policyB_value": deductB,
            "delta": deductB - deductA,  # Reversed - lower is better
            "winner": "A" if deductA < deductB else "B" if deductB < deductA else "tie",
            "relevance_weight": weights.get("deductible", 0.05),
            "score_A": (1.0 - self._normalize_value(deductA, 1000)) * weights.get("deductible", 0.05),
            "score_B": (1.0 - self._normalize_value(deductB, 1000)) * weights.get("deductible", 0.05)
        })
        
        return comparisons
    
    def _extract_value(self, policy: Dict, category: str, field: str, default: float = 0.0) -> float:
        """Extract numeric value from policy data"""
        try:
            category_data = policy.get(category, {})
            if isinstance(category_data, dict):
                value = category_data.get(field, default)
            else:
                value = default
            
            # Convert to float
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Try to extract number from string
                import re
                numbers = re.findall(r'\d+', value.replace(',', ''))
                return float(numbers[0]) if numbers else default
            else:
                return default
        except:
            return default
    
    def _normalize_value(self, value: float, max_value: float) -> float:
        """Normalize value to 0-1 scale"""
        if max_value <= 0:
            return 0.0
        return min(value / max_value, 1.0)
    
    def _check_sports_coverage(self, policy: Dict, activities: List[str]) -> bool:
        """Check if policy covers adventure sports"""
        # Check exclusions
        exclusions = policy.get("exclusions", {})
        sports_exclusions = exclusions.get("sports", []) or []
        
        # If activities are in exclusions, not covered
        for activity in activities:
            if any(exc.lower() in activity.lower() for exc in sports_exclusions):
                return False
        
        # Check if sports are covered
        sports_coverage = policy.get("sports_coverage", {})
        if sports_coverage.get("covered", False):
            return True
        
        return False  # Default to not covered
    
    def _calculate_composite_scores(self, benefit_comparison: List[Dict]) -> Dict:
        """Calculate composite scores for each policy"""
        scoreA = sum(comp.get("score_A", 0.0) for comp in benefit_comparison)
        scoreB = sum(comp.get("score_B", 0.0) for comp in benefit_comparison)
        
        return {
            "policyA": round(scoreA, 3),
            "policyB": round(scoreB, 3)
        }
    
    async def _generate_justification(self, policyA_id: str, policyB_id: str, 
                                     benefit_comparison: List[Dict], 
                                     composite_scores: Dict,
                                     best_policy: str, scenario: Dict) -> str:
        """Generate human-readable justification"""
        if not self.client:
            # Fallback justification without LLM
            return self._simple_justification(best_policy, benefit_comparison, composite_scores)
        
        try:
            # Prepare comparison summary
            key_differences = [
                f"{comp['benefit']}: {comp['policyA_id']}={comp['policyA_value']}, {comp['policyB_id']}={comp['policyB_value']}"
                for comp in benefit_comparison[:5]
            ]
            
            prompt = f"""You are an insurance expert. Compare these two travel insurance policies for a specific scenario.

Scenario: Traveling to {scenario.get('destination', 'unknown')} with activities: {', '.join(scenario.get('activities', []))}

Policy Comparison Summary:
{chr(10).join(key_differences)}

Composite Scores:
- {policyA_id}: {composite_scores.get('policyA', 0):.2f}
- {policyB_id}: {composite_scores.get('policyB', 0):.2f}

Best Policy: {best_policy}

Write a 2-3 sentence justification explaining why {best_policy} is recommended for this scenario. Include specific numbers (coverage amounts, deductibles) and reference the activities mentioned. Be quantitative and evidence-based."""
            
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM justification failed: {e}")
            return self._simple_justification(best_policy, benefit_comparison, composite_scores)
    
    def _simple_justification(self, best_policy: str, benefit_comparison: List[Dict], scores: Dict) -> str:
        """Simple justification without LLM"""
        top_benefit = max(benefit_comparison, key=lambda x: abs(x.get("delta", 0)))
        return f"{best_policy} is recommended with a score of {scores.get('policyA' if best_policy == 'policyA' else 'policyB', 0):.2f}. Key advantage: {top_benefit.get('benefit', 'N/A')} with {abs(top_benefit.get('delta', 0))} difference."
    
    def _extract_citations(self, policyA: Dict, policyB: Dict, benefit_comparison: List[Dict]) -> List[Dict]:
        """Extract policy citations for referenced benefits"""
        citations = []
        
        # Add policy source citations
        citations.append({
            "policy": policyA.get("policy_name", "Policy A"),
            "source": "Policy Document",
            "section": "Coverage Details"
        })
        citations.append({
            "policy": policyB.get("policy_name", "Policy B"),
            "source": "Policy Document",
            "section": "Coverage Details"
        })
        
        return citations

