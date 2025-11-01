"""
Claims Analyzer - Integrates claims data with policy wordings
Provides specific policy citations for common incidents in destinations
"""

import os
import logging
from typing import Dict, List, Optional, Any
from claims_database import ClaimsDatabase
from policy_intelligence import PolicyIntelligence

logger = logging.getLogger(__name__)

class ClaimsAnalyzer:
    """Analyzes claims data and matches with policy wordings"""
    
    def __init__(self):
        self.claims_db = ClaimsDatabase()
        self.policy_intel = PolicyIntelligence()
    
    async def analyze_destination_and_recommend(
        self,
        destination: str,
        trip_duration: int = None
    ) -> Dict:
        """
        Analyze destination claims and provide specific policy recommendations
        with exact policy wordings that cover common incidents
        """
        # Get claims analysis
        coverage_recs = self.claims_db.get_coverage_recommendations(destination, trip_duration)
        
        logger.info(f"Claims analysis for {destination}: total_claims={coverage_recs.get('total_claims_analyzed', 0)}, recommendations={len(coverage_recs.get('recommendations', []))}")
        
        # Check if we have claims data (even if no recommendations yet)
        risk_analysis = self.claims_db.analyze_destination_risks(destination)
        has_claims_data = risk_analysis.get("total_claims", 0) > 0
        
        if not has_claims_data and not coverage_recs.get("recommendations"):
            return {
                "destination": destination,
                "has_data": False,
                "message": coverage_recs.get("message", "No claims data available"),
                "recommendations": []
            }
        
        # If we have claims but no recommendations, create basic recommendations
        if has_claims_data and not coverage_recs.get("recommendations"):
            # Generate basic recommendations from risk analysis
            recommendations = []
            if risk_analysis.get("claim_types"):
                for claim_type, data in sorted(
                    risk_analysis["claim_types"].items(),
                    key=lambda x: x[1]["count"],
                    reverse=True
                )[:3]:
                    recommendations.append({
                        "claim_type": claim_type,
                        "incidence_rate": f"{data['percentage']}%",
                        "average_cost": data["avg_amount"],
                        "recommended_coverage": max(data["avg_amount"] * 3, 50000),
                        "priority": "high" if data["percentage"] >= 30 else "medium",
                        "rationale": f"{data['percentage']}% of claims in {destination} are for {claim_type} with an average cost of ${data['avg_amount']:,.2f} SGD"
                    })
            
            coverage_recs["recommendations"] = recommendations
        
        # Get available policies
        try:
            policies = await self.policy_intel.get_policy_list()
        except:
            policies = []
        
        # Match recommendations with policy wordings
        detailed_recommendations = []
        
        for rec in coverage_recs["recommendations"]:
            claim_type = rec["claim_type"]
            
            # Find policy wordings that cover this claim type
            policy_citations = await self._find_policy_coverage(claim_type, policies)
            
            detailed_recommendations.append({
                **rec,
                "policy_citations": policy_citations,
                "coverage_wordings": policy_citations  # For backward compatibility
            })
        
        # Ensure we always return has_data=True if we have any claims
        has_data = risk_analysis.get("total_claims", 0) > 0
        
        result = {
            "destination": destination,
            "has_data": has_data,
            "total_claims": risk_analysis.get("total_claims", 0),
            "common_incidents": risk_analysis.get("common_incidents", []),
            "risk_summary": risk_analysis.get("insights", ""),
            "recommendations": detailed_recommendations,
            "suggested_message": self._generate_suggested_message(
                destination,
                coverage_recs if detailed_recommendations else {"recommendations": [], "common_incidents": risk_analysis.get("common_incidents", [])},
                detailed_recommendations
            )
        }
        
        logger.info(f"Claims analyzer result for {destination}: has_data={has_data}, total_claims={result['total_claims']}, recommendations={len(detailed_recommendations)}")
        
        return result
    
    async def _find_policy_coverage(self, claim_type: str, policies: List[Dict]) -> List[Dict]:
        """Find specific policy wordings that cover a claim type"""
        citations = []
        
        # Map claim types to coverage keywords
        coverage_keywords = {
            "medical": ["medical", "illness", "injury", "hospital", "treatment"],
            "trip cancellation": ["cancellation", "cancel", "trip interruption"],
            "baggage": ["baggage", "luggage", "personal belongings", "lost baggage"],
            "trip delay": ["delay", "delayed", "missed connection"],
            "emergency": ["emergency", "evacuation", "repatriation"],
            "accident": ["accident", "injury", "medical"],
            "theft": ["theft", "stolen", "robbery", "burglary"],
            "loss": ["loss", "lost", "missing"]
        }
        
        # Find relevant keywords for this claim type
        relevant_keywords = []
        claim_lower = claim_type.lower()
        
        for key, keywords in coverage_keywords.items():
            if key in claim_lower:
                relevant_keywords.extend(keywords)
        
        # Search policies for coverage
        for policy in policies:
            policy_name = policy.get("name", "")
            policy_text = self.policy_intel.get_policy_text(policy_name)
            
            if not policy_text:
                continue
            
            # Search for relevant keywords in policy text
            policy_lower = policy_text.lower()
            
            matching_sections = []
            for keyword in relevant_keywords:
                if keyword in policy_lower:
                    # Try to extract relevant section
                    section = self._extract_section(policy_text, keyword)
                    if section:
                        matching_sections.append({
                            "keyword": keyword,
                            "section": section[:500],  # First 500 chars
                            "policy": policy_name
                        })
            
            if matching_sections:
                citations.append({
                    "policy_name": policy_name,
                    "claim_type": claim_type,
                    "sections": matching_sections,
                    "exact_wordings": [s["section"] for s in matching_sections]
                })
        
        return citations
    
    def _extract_section(self, policy_text: str, keyword: str) -> Optional[str]:
        """Extract relevant section from policy text containing keyword"""
        try:
            # Find keyword position
            idx = policy_text.lower().find(keyword.lower())
            if idx == -1:
                return None
            
            # Extract 200 chars before and 300 chars after
            start = max(0, idx - 200)
            end = min(len(policy_text), idx + 300)
            
            section = policy_text[start:end]
            
            # Try to find sentence boundaries
            sentences = section.split('.')
            if len(sentences) > 1:
                # Return sentences around keyword
                keyword_sentence_idx = None
                for i, sentence in enumerate(sentences):
                    if keyword.lower() in sentence.lower():
                        keyword_sentence_idx = i
                        break
                
                if keyword_sentence_idx is not None:
                    start_sentence = max(0, keyword_sentence_idx - 1)
                    end_sentence = min(len(sentences), keyword_sentence_idx + 2)
                    return '. '.join(sentences[start_sentence:end_sentence]) + '.'
            
            return section
        
        except:
            return None
    
    def _generate_suggested_message(
        self,
        destination: str,
        coverage_recs: Dict,
        detailed_recommendations: List[Dict]
    ) -> str:
        """Generate suggested conversational message for user"""
        if not detailed_recommendations:
            return f"Based on historical claims data, I recommend comprehensive travel insurance for {destination}."
        
        message_parts = [f"Based on historical claims data for {destination}:"]
        
        # Highlight top recommendation
        top_rec = detailed_recommendations[0]
        percentage = top_rec["incidence_rate"]
        incident = top_rec["claim_type"]
        avg_cost = top_rec["average_cost"]
        
        message_parts.append(
            f"{percentage}% of travelers have claimed for **{incident}** incidents "
            f"with an average cost of **${avg_cost:,.2f} SGD**."
        )
        
        message_parts.append(
            f"Would you like me to show you insurance policies that specifically cover {incident}?"
        )
        
        # Mention other common incidents
        if len(detailed_recommendations) > 1:
            other_incidents = [r["claim_type"] for r in detailed_recommendations[1:3]]
            if other_incidents:
                message_parts.append(
                    f"Other common incidents in {destination} include: {', '.join(other_incidents)}."
                )
        
        return " ".join(message_parts)

