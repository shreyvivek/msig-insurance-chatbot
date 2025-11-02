"""
Taxonomy-based Policy Matcher
Matches user data and trip details against JSON taxonomies for insurance policies
NO ANCILEO API used here - pure taxonomy matching
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from groq import Groq

logger = logging.getLogger(__name__)

class TaxonomyMatcher:
    """Matches policies using JSON taxonomies"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        self.taxonomy_path = Path(__file__).parent / "Taxonomy" / "Taxonomy_Hackathon.json"
        self.policy_dir = Path(__file__).parent / "Policy_Wordings"
        self.taxonomy = {}
        self.policy_mapping = {
            "Product A": "Scootsurance QSR022206_updated",
            "Product B": "TravelEasy Policy QTD032212",
            "Product C": "TravelEasy Pre-Ex Policy QTD032212-PX"
        }
        self._load_taxonomy()
    
    def _load_taxonomy(self):
        """Load the JSON taxonomy"""
        try:
            with open(self.taxonomy_path, 'r', encoding='utf-8') as f:
                self.taxonomy = json.load(f)
            logger.info("✅ Taxonomy loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load taxonomy: {e}")
            self.taxonomy = {}
    
    async def match_policies(
        self,
        user_data: Dict,
        trip_data: Dict,
        extracted_data: Dict
    ) -> List[Dict]:
        """
        Match policies against JSON taxonomies based on user and trip data
        
        Args:
            user_data: {age, interests, medical_conditions}
            trip_data: {destination, source, departure_date, return_date, pax, ticket_policies}
            extracted_data: Full extracted document data
            
        Returns:
            List of matched policies with scoring
        """
        # Always return policies from Policy_Wordings, even if taxonomy isn't loaded
        # This ensures users always see the three policies from the PDF files
        
        # Prepare matching criteria
        age = user_data.get("age", 30)
        medical_conditions = user_data.get("medical_conditions", [])
        interests = user_data.get("interests", [])
        destination = trip_data.get("destination", "")
        source = trip_data.get("source", "")
        pax = trip_data.get("pax", 1)
        ticket_policies = trip_data.get("ticket_policies", [])
        
        # Calculate trip duration
        duration_days = 0
        if trip_data.get("departure_date") and trip_data.get("return_date"):
            try:
                from datetime import datetime
                dep = datetime.strptime(trip_data["departure_date"], "%Y-%m-%d")
                ret = datetime.strptime(trip_data["return_date"], "%Y-%m-%d")
                duration_days = (ret - dep).days
            except:
                pass
        
        # Match against taxonomy
        matched_policies = []
        
        # Always include all three policies from Policy_Wordings
        # If taxonomy is not loaded, use default products
        if not self.taxonomy or not self.taxonomy.get("products"):
            logger.warning("Taxonomy not loaded or has no products, using default policy list")
            products = ["Product A", "Product B", "Product C"]
        else:
            products = self.taxonomy.get("products", ["Product A", "Product B", "Product C"])
        
        logger.info(f"Matching against {len(products)} products from taxonomy")
        
        for product in products:
            policy_name = self.policy_mapping.get(product, product)
            try:
                score, benefits, reasons = await self._score_policy(
                    product=product,
                    age=age,
                    medical_conditions=medical_conditions,
                    interests=interests,
                    destination=destination,
                    source=source,
                    duration_days=duration_days,
                    pax=pax,
                    ticket_policies=ticket_policies
                )
            except Exception as e:
                logger.warning(f"Scoring failed for {product}: {e}, using default score")
                score = 70.0
                benefits = [f"Coverage from {policy_name}"]
                reasons = ["Policy available from Policy_Wordings"]
            
            matched_policies.append({
                "policy_name": policy_name,
                "product_code": product,
                "score": score,
                "benefits": benefits,
                "reasons": reasons,
                "source": "taxonomy_match"  # NO Ancileo
            })
        
        # Sort by score (highest first)
        matched_policies.sort(key=lambda x: x["score"], reverse=True)
        
        # CRITICAL: Always return all 3 policies from Policy_Wordings
        expected_count = len(self.policy_mapping)
        if len(matched_policies) < expected_count:
            logger.warning(f"Only {len(matched_policies)} policies matched, expected {expected_count}. Adding missing policies.")
            present_codes = {p["product_code"] for p in matched_policies}
            for product_code, policy_name in self.policy_mapping.items():
                if product_code not in present_codes:
                    matched_policies.append({
                        "policy_name": policy_name,
                        "product_code": product_code,
                        "score": 70.0,
                        "benefits": [f"Coverage from {policy_name}"],
                        "reasons": ["Policy available from Policy_Wordings"],
                        "source": "taxonomy_match"
                    })
        
        logger.info(f"Returning {len(matched_policies)} policies: {[p['policy_name'] for p in matched_policies]}")
        return matched_policies
    
    async def _score_policy(
        self,
        product: str,
        age: int,
        medical_conditions: List[str],
        interests: List[str],
        destination: str,
        source: str,
        duration_days: int,
        pax: int,
        ticket_policies: List[str]
    ) -> tuple:
        """
        Score a policy against criteria using taxonomy
        
        Returns:
            (score, benefits, reasons)
        """
        score = 50.0  # Base score
        benefits = []
        reasons = []
        
        # Load taxonomy layers
        layers = self.taxonomy.get("layers", {})
        
        # 1. Check age eligibility
        age_eligibility = self._check_age_eligibility(layers, product, age)
        if age_eligibility["eligible"]:
            score += 15
            reasons.append(f"Age {age} is eligible")
        else:
            score -= 20
            reasons.append(f"Age {age} may not be eligible: {age_eligibility.get('reason', '')}")
        
        # 2. Check pre-existing conditions
        has_medical = len(medical_conditions) > 0 and not all(c.lower() in ['none', 'no'] for c in medical_conditions)
        pre_existing = self._check_pre_existing_conditions(layers, product)
        if has_medical:
            if pre_existing["covered"]:
                score += 25
                benefits.append("Pre-existing conditions covered")
                reasons.append("Pre-existing conditions coverage available")
            else:
                score -= 15
                reasons.append("Pre-existing conditions may not be covered")
        else:
            score += 5
            reasons.append("No pre-existing conditions - standard coverage sufficient")
        
        # 3. Check activity coverage
        adventure_activities = ["Skiing/Snowboarding", "Scuba Diving", "Hiking/Trekking", "Adventure Sports"]
        has_adventure = any(act in interests for act in adventure_activities)
        activity_coverage = self._check_activity_coverage(layers, product, interests)
        if has_adventure:
            if activity_coverage["covered"]:
                score += 20
                benefits.append(f"Adventure activities covered: {', '.join(activity_coverage.get('activities', []))}")
                reasons.append("Adventure sports coverage available")
            else:
                score -= 10
                reasons.append("Adventure activities may not be covered")
        
        # 4. Check destination coverage
        destination_coverage = self._check_destination_coverage(layers, product, destination)
        if destination_coverage["covered"]:
            score += 10
            reasons.append(f"Destination {destination} is covered")
        else:
            score -= 5
            reasons.append(f"Destination {destination} coverage may be limited")
        
        # 5. Check trip duration limits
        duration_check = self._check_duration_limits(layers, product, duration_days)
        if duration_check["within_limit"]:
            score += 5
            reasons.append(f"Trip duration ({duration_days} days) is within limits")
        else:
            score -= 10
            reasons.append(f"Trip duration may exceed policy limits")
        
        # 6. DIFFERENTIATE POLICIES - Add unique scoring factors
        # Product A (Scootsurance) - Budget-friendly, basic coverage
        if product == "Product A":
            if not has_medical and age < 65:  # Good for healthy younger travelers
                score += 10
                benefits.append("Best value for basic coverage")
                reasons.append("Ideal for budget-conscious travelers")
            else:
                score -= 5
        
        # Product B (TravelEasy) - Standard comprehensive coverage
        elif product == "Product B":
            score += 5  # Always slightly better for standard travel
            benefits.append("Comprehensive standard coverage")
            reasons.append("Balanced coverage and price")
            
        # Product C (TravelEasy Pre-Ex) - Pre-existing conditions coverage
        elif product == "Product C":
            if has_medical or age >= 65:  # Perfect for medical conditions or seniors
                score += 15
                benefits.append("Pre-existing conditions covered")
                reasons.append("Best for travelers with medical conditions")
            elif has_adventure:  # Also good for adventure travel
                score += 8
                benefits.append("Enhanced coverage for adventures")
                reasons.append("Great for adventure activities")
            else:
                score -= 5  # Overkill if no special needs
        
        # 7. Add variation based on pax and duration for uniqueness
        if duration_days > 14:
            if product == "Product C":
                score += 5  # Better for longer trips
                benefits.append("Extended coverage benefits")
        elif duration_days < 7:
            if product == "Product A":
                score += 3  # Good for short trips
        
        if pax > 2:
            if product == "Product B":
                score += 3  # Good for families
        
        # Ensure score is between 0-100
        score = max(0, min(100, score))
        
        return score, benefits, reasons
    
    def _check_age_eligibility(self, layers: Dict, product: str, age: int) -> Dict:
        """Check age eligibility from taxonomy"""
        layer_1 = layers.get("layer_1_general_conditions", [])
        for condition in layer_1:
            if condition.get("condition") == "age_eligibility":
                product_data = condition.get("products", {}).get(product, {})
                params = product_data.get("parameters", {})
                
                min_age = params.get("min_age")
                max_age = params.get("max_age")
                
                if min_age is not None and age < min_age:
                    return {"eligible": False, "reason": f"Minimum age is {min_age}"}
                if max_age is not None and age > max_age:
                    return {"eligible": False, "reason": f"Maximum age is {max_age}"}
                
                return {"eligible": True}
        
        return {"eligible": True}  # Default to eligible
    
    def _check_pre_existing_conditions(self, layers: Dict, product: str) -> Dict:
        """Check pre-existing conditions coverage"""
        layer_1 = layers.get("layer_1_general_conditions", [])
        for condition in layer_1:
            if condition.get("condition") == "pre_existing_conditions":
                product_data = condition.get("products", {}).get(product, {})
                exists = product_data.get("condition_exist", False)
                
                if exists:
                    # Check if covered or excluded
                    params = product_data.get("parameters", {})
                    covered = params.get("covered", False)
                    return {"covered": covered}
                
                return {"covered": False}
        
        # Product C (TravelEasy Pre-Ex) specifically covers pre-existing
        if product == "Product C":
            return {"covered": True}
        
        return {"covered": False}
    
    def _check_activity_coverage(self, layers: Dict, product: str, interests: List[str]) -> Dict:
        """Check if activities are covered"""
        # Check exclusions for sports/adventure
        layer_2 = layers.get("layer_2_coverage_benefits", [])
        covered_activities = []
        
        for benefit in layer_2:
            if "sports" in benefit.get("benefit", "").lower() or "adventure" in benefit.get("benefit", "").lower():
                product_data = benefit.get("products", {}).get(product, {})
                if product_data.get("coverage_exists", False):
                    covered_activities.append("Adventure Sports")
        
        return {
            "covered": len(covered_activities) > 0,
            "activities": covered_activities
        }
    
    def _check_destination_coverage(self, layers: Dict, product: str, destination: str) -> Dict:
        """Check destination coverage"""
        # Most policies cover worldwide, but check exclusions
        layer_1 = layers.get("layer_1_general_conditions", [])
        for condition in layer_1:
            if "destination" in condition.get("condition", "").lower() or "country" in condition.get("condition", "").lower():
                product_data = condition.get("products", {}).get(product, {})
                exists = product_data.get("condition_exist", False)
                
                if exists:
                    params = product_data.get("parameters", {})
                    excluded = params.get("excluded_countries", [])
                    if excluded and destination.lower() in [c.lower() for c in excluded]:
                        return {"covered": False}
        
        return {"covered": True}
    
    def _check_duration_limits(self, layers: Dict, product: str, duration_days: int) -> Dict:
        """Check trip duration limits"""
        layer_1 = layers.get("layer_1_general_conditions", [])
        for condition in layer_1:
            if "duration" in condition.get("condition", "").lower() or "trip" in condition.get("condition", "").lower():
                product_data = condition.get("products", {}).get(product, {})
                params = product_data.get("parameters", {})
                max_duration = params.get("max_duration_days")
                
                if max_duration and duration_days > max_duration:
                    return {"within_limit": False, "max_days": max_duration}
        
        return {"within_limit": True}
    
    def get_policy_benefits(self, product: str) -> Dict:
        """Get detailed benefits for a policy from taxonomy"""
        layers = self.taxonomy.get("layers", {})
        layer_2 = layers.get("layer_2_coverage_benefits", [])
        
        benefits = {}
        for benefit in layer_2:
            benefit_name = benefit.get("benefit", "")
            product_data = benefit.get("products", {}).get(product, {})
            
            if product_data.get("coverage_exists", False):
                params = product_data.get("parameters", {})
                benefits[benefit_name] = {
                    "covered": True,
                    "amount": params.get("coverage_amount", 0),
                    "details": params
                }
        
        return benefits

