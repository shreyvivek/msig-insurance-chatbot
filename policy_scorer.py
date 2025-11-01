"""
Policy Scorer - Determines the "best" policy with explainable algorithm
Uses multi-factor scoring with clear weights and reasoning
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class PolicyScorer:
    """Scores and ranks policies using explainable multi-factor algorithm"""
    
    def __init__(self):
        # Scoring weights (sum should be ~1.0)
        self.weights = {
            "price_value": 0.25,      # 25% - Price competitiveness
            "coverage_adequacy": 0.30,  # 30% - Coverage meets needs
            "risk_match": 0.20,        # 20% - Matches trip risk profile
            "user_preference": 0.15,    # 15% - User preferences/history
            "reputation": 0.10         # 10% - Provider reputation/trust
        }
    
    def score_policies(
        self,
        quotes: List[Dict],
        trip_details: Dict,
        user_profile: Dict = None,
        risk_assessment: Dict = None,
        activities: List[str] = None
    ) -> List[Dict]:
        """
        Score each policy and rank them with explainable reasons
        Returns sorted list with scores and detailed explanations
        activities: List of activities (e.g., ["skiing", "scuba"]) for activity-based scoring
        """
        scored_policies = []
        
        for quote in quotes:
            score = {
                "quote": quote,
                "scores": {},
                "total_score": 0.0,
                "explanation": "",
                "rank": 0
            }
            
            # 1. Price Value Score (0-100)
            price_score, price_reason = self._score_price_value(quote, quotes, trip_details)
            score["scores"]["price_value"] = price_score
            
            # 2. Coverage Adequacy Score (0-100) - Enhanced with activity matching
            coverage_score, coverage_reason = self._score_coverage_adequacy(
                quote, trip_details, risk_assessment, activities
            )
            score["scores"]["coverage_adequacy"] = coverage_score
            
            # 3. Risk Match Score (0-100)
            risk_score, risk_reason = self._score_risk_match(
                quote, trip_details, risk_assessment
            )
            score["scores"]["risk_match"] = risk_score
            
            # 4. User Preference Score (0-100)
            pref_score, pref_reason = self._score_user_preference(
                quote, user_profile
            )
            score["scores"]["user_preference"] = pref_score
            
            # 5. Reputation Score (0-100)
            rep_score, rep_reason = self._score_reputation(quote)
            score["scores"]["reputation"] = rep_score
            
            # Calculate weighted total
            total = (
                price_score * self.weights["price_value"] +
                coverage_score * self.weights["coverage_adequacy"] +
                risk_score * self.weights["risk_match"] +
                pref_score * self.weights["user_preference"] +
                rep_score * self.weights["reputation"]
            )
            
            score["total_score"] = round(total, 2)
            
            # Build explanation
            score["explanation"] = self._build_explanation(
                quote,
                score["scores"],
                price_reason,
                coverage_reason,
                risk_reason,
                pref_reason,
                rep_reason
            )
            
            scored_policies.append(score)
        
        # Sort by total score (descending)
        scored_policies.sort(key=lambda x: x["total_score"], reverse=True)
        
        # Assign ranks
        for i, policy in enumerate(scored_policies, 1):
            policy["rank"] = i
        
        return scored_policies
    
    def _score_price_value(self, quote: Dict, all_quotes: List[Dict], trip_details: Dict) -> tuple:
        """Score based on price competitiveness (lower is better, but relative)"""
        price = quote.get("price", 0)
        if price == 0:
            return 50, "Price not available"
        
        prices = [q.get("price", 0) for q in all_quotes if q.get("price", 0) > 0]
        if not prices:
            return 50, "Cannot compare prices"
        
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            return 100, "Same price as all options"
        
        # Score: 100 = cheapest, 0 = most expensive
        # But also consider value (not just cheapest)
        price_score = 100 - ((price - min_price) / price_range * 50)  # Max 50 point penalty
        
        # Value consideration: if price is close to min, boost score
        if price <= min_price * 1.1:  # Within 10% of cheapest
            price_score = min(100, price_score + 20)
            reason = f"Competitive price at {price:.2f} - only {(price - min_price):.2f} more than cheapest option"
        elif price <= min_price * 1.2:  # Within 20%
            price_score = min(90, price_score + 10)
            reason = f"Good value at {price:.2f} - reasonable premium for coverage"
        else:
            reason = f"Price: {price:.2f} (higher than cheapest, but may offer better coverage)"
        
        return max(0, min(100, price_score)), reason
    
    def _score_coverage_adequacy(self, quote: Dict, trip_details: Dict, risk_assessment: Dict = None) -> tuple:
        """Score based on whether coverage meets trip needs"""
        coverage = quote.get("coverage", {})
        
        # Check recommended coverage from risk assessment
        recommended = {}
        if risk_assessment:
            recommended = risk_assessment.get("recommended_coverage", {})
        
        score = 60  # Base score
        reasons = []
        
        # Medical coverage check
        medical_coverage = coverage.get("medical", 0)
        recommended_medical = recommended.get("medical_minimum", 50000)
        
        if medical_coverage >= recommended_medical:
            score += 20
            reasons.append(f"Medical coverage ({medical_coverage:,}) meets/exceeds recommendation ({recommended_medical:,})")
        elif medical_coverage >= recommended_medical * 0.7:
            score += 10
            reasons.append(f"Medical coverage ({medical_coverage:,}) close to recommendation ({recommended_medical:,})")
        else:
            reasons.append(f"Medical coverage ({medical_coverage:,}) below recommendation ({recommended_medical:,})")
        
        # Trip cancellation
        cancellation = coverage.get("trip_cancellation", 0)
        trip_cost = trip_details.get("trip_cost", 0)
        
        if trip_cost and cancellation >= trip_cost * 0.8:
            score += 10
            reasons.append(f"Trip cancellation coverage ({cancellation:,}) adequate for trip cost")
        elif cancellation > 0:
            reasons.append(f"Trip cancellation: {cancellation:,} (check if sufficient for your trip)")
        
        # Baggage coverage
        baggage = coverage.get("baggage", 0)
        if baggage >= 2000:
            score += 10
            reasons.append(f"Baggage coverage ({baggage:,}) is adequate")
        
        reason = "; ".join(reasons) if reasons else "Standard coverage levels"
        return max(0, min(100, score)), reason
    
    def _score_risk_match(self, quote: Dict, trip_details: Dict, risk_assessment: Dict = None) -> tuple:
        """Score based on how well policy matches trip risk profile"""
        if not risk_assessment:
            return 70, "Standard risk profile assumed"
        
        risk_level = risk_assessment.get("risk_level", "medium")
        coverage = quote.get("coverage", {})
        
        score = 70
        reasons = []
        
        if risk_level == "high":
            # Need higher coverage
            medical = coverage.get("medical", 0)
            if medical >= 150000:
                score = 100
                reasons.append("Excellent match for high-risk trip - comprehensive medical coverage")
            elif medical >= 100000:
                score = 85
                reasons.append("Good match for high-risk trip - adequate medical coverage")
            else:
                score = 60
                reasons.append("May not fully cover high-risk trip - consider higher coverage")
        
        elif risk_level == "medium":
            medical = coverage.get("medical", 0)
            if medical >= 100000:
                score = 90
                reasons.append("Good coverage for medium-risk trip")
            elif medical >= 50000:
                score = 75
                reasons.append("Adequate coverage for medium-risk trip")
            else:
                score = 60
                reasons.append("Consider if coverage is sufficient")
        
        else:  # low risk
            medical = coverage.get("medical", 0)
            if medical >= 50000:
                score = 90
                reasons.append("Sufficient coverage for low-risk trip")
            else:
                score = 70
                reasons.append("Basic coverage may be sufficient for low-risk trip")
        
        reason = "; ".join(reasons) if reasons else "Matches trip risk profile"
        return max(0, min(100, score)), reason
    
    def _score_user_preference(self, quote: Dict, user_profile: Dict = None) -> tuple:
        """Score based on user preferences and history"""
        if not user_profile:
            return 70, "No user history - neutral score"
        
        score = 70
        reasons = []
        
        # Check past policy preferences
        travel_history = user_profile.get("travel_history", [])
        policy_name = quote.get("plan_name", "").lower()
        
        # Check if user has used this policy before
        used_before = any(
            policy_name in h.get("policy", "").lower()
            for h in travel_history
        )
        
        if used_before:
            score += 20
            reasons.append("You've used this policy before - familiarity bonus")
        
        # Check preferred coverage level
        preferred_coverage = user_profile.get("preferences", {}).get("preferred_coverage", "")
        coverage = quote.get("coverage", {})
        
        if preferred_coverage == "comprehensive" and coverage.get("medical", 0) >= 100000:
            score += 10
            reasons.append("Matches your preference for comprehensive coverage")
        elif preferred_coverage == "premium" and coverage.get("medical", 0) >= 150000:
            score += 10
            reasons.append("Matches your preference for premium coverage")
        
        # Check price sensitivity
        price_sensitivity = user_profile.get("preferences", {}).get("price_sensitivity", "medium")
        price = quote.get("price", 0)
        
        # Compare with average (would need all quotes, simplified here)
        if price_sensitivity == "high" and price < 50:
            score += 5
            reasons.append("Budget-friendly option")
        elif price_sensitivity == "low" and price >= 50:
            score += 5
            reasons.append("Premium option aligns with your preferences")
        
        reason = "; ".join(reasons) if reasons else "No specific preferences matched"
        return max(0, min(100, score)), reason
    
    def _score_reputation(self, quote: Dict) -> tuple:
        """Score based on provider reputation"""
        plan_name = quote.get("plan_name", "").lower()
        source = quote.get("source", "local")
        
        score = 70  # Base score
        
        # Ancileo policies are from established providers
        if source == "ancileo":
            score = 85
            reason = "Ancileo marketplace - verified providers with established reputation"
        
        # Local policies - known brands
        elif "traveleasy" in plan_name:
            score = 90
            reason = "TravelEasy - well-established provider with strong reputation"
        elif "scootsurance" in plan_name:
            score = 85
            reason = "Scootsurance - trusted provider for budget travelers"
        elif "msig" in plan_name:
            score = 95
            reason = "MSIG - highly trusted insurance provider with excellent reputation"
        else:
            reason = "Standard provider rating"
        
        return score, reason
    
    def _build_explanation(
        self,
        quote: Dict,
        scores: Dict,
        price_reason: str,
        coverage_reason: str,
        risk_reason: str,
        pref_reason: str,
        rep_reason: str
    ) -> str:
        """Build comprehensive explanation of scoring"""
        plan_name = quote.get("plan_name", "Unknown")
        total_score = sum(
            scores[key] * self.weights[key]
            for key in self.weights.keys()
            if key in scores
        )
        
        explanation = f"**{plan_name}** - Score: {total_score:.1f}/100\n\n"
        explanation += "**Breakdown:**\n\n"
        
        explanation += f"💰 **Price Value** ({self.weights['price_value']*100:.0f}% weight): {scores['price_value']:.1f}/100\n"
        explanation += f"   {price_reason}\n\n"
        
        explanation += f"🛡️ **Coverage Adequacy** ({self.weights['coverage_adequacy']*100:.0f}% weight): {scores['coverage_adequacy']:.1f}/100\n"
        explanation += f"   {coverage_reason}\n\n"
        
        explanation += f"⚠️ **Risk Match** ({self.weights['risk_match']*100:.0f}% weight): {scores['risk_match']:.1f}/100\n"
        explanation += f"   {risk_reason}\n\n"
        
        explanation += f"👤 **User Preference** ({self.weights['user_preference']*100:.0f}% weight): {scores['user_preference']:.1f}/100\n"
        explanation += f"   {pref_reason}\n\n"
        
        explanation += f"⭐ **Reputation** ({self.weights['reputation']*100:.0f}% weight): {scores['reputation']:.1f}/100\n"
        explanation += f"   {rep_reason}\n\n"
        
        explanation += f"**Weighted Total: {total_score:.1f}/100**"
        
        return explanation

