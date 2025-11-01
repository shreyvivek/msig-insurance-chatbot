"""
Pricing Calculator - Explains how insurance prices are calculated
Provides transparent, explainable pricing breakdowns
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PricingCalculator:
    """Explains insurance pricing calculations transparently"""
    
    def __init__(self):
        self.base_rates = {
            "SG": {"daily": 5.0, "base": 15.0},  # Singapore base rates
            "IN": {"daily": 4.5, "base": 12.0},  # India base rates
            "JP": {"daily": 6.5, "base": 20.0},  # Japan base rates
            "TH": {"daily": 4.0, "base": 10.0},  # Thailand base rates
            "CN": {"daily": 5.5, "base": 15.0},  # China base rates
            "default": {"daily": 5.0, "base": 15.0}
        }
        
        self.age_multipliers = {
            (0, 18): 0.7,    # Children discount
            (18, 30): 1.0,   # Young adults
            (30, 50): 1.1,   # Middle age
            (50, 65): 1.3,   # Senior
            (65, 100): 1.8   # Elderly
        }
        
        self.destination_risk_multipliers = {
            "IN": 0.9,   # Lower risk destination
            "JP": 1.2,   # Higher cost destination
            "TH": 1.0,   # Standard
            "CN": 1.1,   # Slightly higher
            "SG": 1.0,   # Standard
            "default": 1.0
        }
    
    def calculate_price_breakdown(
        self,
        price: float,
        destination: str,
        departure_date: str,
        return_date: str,
        travelers: int = 1,
        ages: List[int] = None,
        trip_cost: float = None,
        policy_name: str = None,
        source: str = "ancileo"
    ) -> Dict:
        """
        Calculate and explain price breakdown transparently
        """
        if not ages:
            ages = [30] * travelers
        
        # Calculate trip duration
        try:
            dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
            ret_date = datetime.strptime(return_date, "%Y-%m-%d")
            duration = (ret_date - dep_date).days
        except:
            duration = 5  # Default
        
        # Get destination country code
        country_code = self._extract_country_code(destination)
        
        # Calculate breakdown
        breakdown = {
            "final_price": price,
            "currency": "SGD",
            "trip_duration_days": duration,
            "number_of_travelers": travelers,
            "destination": destination,
            "country_code": country_code,
            "components": []
        }
        
        # Base calculation method
        if source == "ancileo":
            # Ancileo pricing (external API - explain what factors they consider)
            breakdown["pricing_method"] = "ancileo_api"
            breakdown["explanation"] = f"This price of {price:.2f} SGD was calculated by Ancileo's pricing engine based on:"
            breakdown["components"] = [
                {
                    "factor": "Trip Duration",
                    "value": f"{duration} days",
                    "impact": f"Longer trips = higher premiums (daily rate applies)"
                },
                {
                    "factor": "Number of Travelers",
                    "value": f"{travelers} person{'s' if travelers > 1 else ''}",
                    "impact": f"Each traveler adds to the total premium"
                },
                {
                    "factor": "Destination Risk",
                    "value": destination,
                    "impact": f"Insurance costs vary by destination based on medical costs, claim history, and local risks"
                },
                {
                    "factor": "Traveler Ages",
                    "value": f"{', '.join(map(str, ages))} years old",
                    "impact": f"Age affects premium - older travelers typically pay more due to higher medical risks"
                }
            ]
            
            if trip_cost:
                breakdown["components"].append({
                    "factor": "Trip Cost",
                    "value": f"{trip_cost:.2f} SGD",
                    "impact": "Higher trip costs may increase cancellation coverage premiums"
                })
            
            # Estimate breakdown (since we don't have exact Ancileo formula)
            avg_age = sum(ages) / len(ages) if ages else 30
            base_rate = self.base_rates.get(country_code, self.base_rates["default"])
            estimated_base = base_rate["daily"] * duration * travelers
            age_factor = self._get_age_multiplier(avg_age)
            destination_factor = self.destination_risk_multipliers.get(country_code, 1.0)
            
            estimated_calc = estimated_base * age_factor * destination_factor
            
            breakdown["estimated_breakdown"] = {
                "base_premium": round(estimated_base, 2),
                "age_adjustment": f"{age_factor}x (age {int(avg_age)})",
                "destination_adjustment": f"{destination_factor}x ({destination})",
                "estimated_total": round(estimated_calc, 2),
                "note": "This is an estimate - actual Ancileo pricing uses proprietary algorithms"
            }
        
        else:
            # Local policy pricing (we can calculate exactly)
            breakdown["pricing_method"] = "local_calculation"
            breakdown["explanation"] = f"Price breakdown for {policy_name or 'travel insurance'}:"
            
            avg_age = sum(ages) / len(ages) if ages else 30
            base_rate = self.base_rates.get(country_code, self.base_rates["default"])
            daily_rate = base_rate["daily"]
            base_fee = base_rate["base"]
            
            # Calculate per traveler
            traveler_costs = []
            total_price = 0
            
            for i, age in enumerate(ages):
                age_mult = self._get_age_multiplier(age)
                dest_mult = self.destination_risk_multipliers.get(country_code, 1.0)
                
                daily_cost = daily_rate * age_mult * dest_mult
                traveler_total = (daily_cost * duration) + base_fee
                traveler_costs.append({
                    "traveler": i + 1,
                    "age": age,
                    "daily_rate": round(daily_rate, 2),
                    "age_multiplier": age_mult,
                    "destination_multiplier": dest_mult,
                    "duration_days": duration,
                    "base_fee": base_fee,
                    "total": round(traveler_total, 2)
                })
                total_price += traveler_total
            
            breakdown["components"] = [
                {
                    "factor": "Base Daily Rate",
                    "value": f"{daily_rate:.2f} SGD/day",
                    "calculation": f"Base rate for {destination}",
                    "impact": f"Applied per day of travel"
                },
                {
                    "factor": "Trip Duration",
                    "value": f"{duration} days",
                    "calculation": f"{daily_rate} × {duration} = {daily_rate * duration:.2f}",
                    "impact": "Longer trips cost more"
                },
                {
                    "factor": "Age Adjustment",
                    "value": f"Average age: {int(avg_age)}",
                    "calculation": f"Age multiplier: {age_mult:.2f}x",
                    "impact": "Older travelers pay more due to higher medical risk"
                },
                {
                    "factor": "Destination Risk",
                    "value": destination,
                    "calculation": f"Risk multiplier: {dest_mult:.2f}x",
                    "impact": "Based on destination's medical costs and claim history"
                },
                {
                    "factor": "Base Fee",
                    "value": f"{base_fee:.2f} SGD",
                    "calculation": "One-time policy administration fee",
                    "impact": "Covers policy issuance and processing"
                }
            ]
            
            breakdown["traveler_breakdown"] = traveler_costs
            breakdown["calculated_total"] = round(total_price, 2)
            
            if abs(total_price - price) > 5:  # Significant difference
                breakdown["note"] = f"Note: Calculated total ({total_price:.2f}) differs from quoted price ({price:.2f}) - actual pricing may include additional factors like coverage level, optional add-ons, or special discounts."
        
        return breakdown
    
    def _extract_country_code(self, destination: str) -> str:
        """Extract country code from destination string"""
        destination_lower = destination.lower()
        
        country_map = {
            "singapore": "SG", "china": "CN", "japan": "JP",
            "thailand": "TH", "malaysia": "MY", "indonesia": "ID",
            "india": "IN", "coimbatore": "IN", "chennai": "IN",
            "australia": "AU", "united states": "US", "usa": "US"
        }
        
        for key, code in country_map.items():
            if key in destination_lower:
                return code
        
        return "default"
    
    def _get_age_multiplier(self, age: int) -> float:
        """Get age-based premium multiplier"""
        for (min_age, max_age), multiplier in self.age_multipliers.items():
            if min_age <= age < max_age:
                return multiplier
        return 1.0
    
    def explain_price(self, quote: Dict, trip_details: Dict) -> str:
        """
        Generate human-readable explanation of price calculation
        """
        breakdown = self.calculate_price_breakdown(
            price=quote.get("price", 0),
            destination=trip_details.get("destination", ""),
            departure_date=trip_details.get("departure_date", ""),
            return_date=trip_details.get("return_date", ""),
            travelers=trip_details.get("travelers", 1),
            ages=trip_details.get("ages", []),
            trip_cost=trip_details.get("trip_cost"),
            policy_name=quote.get("plan_name"),
            source=quote.get("source", "ancileo")
        )
        
        explanation = breakdown.get("explanation", "")
        explanation += "\n\n"
        
        for component in breakdown.get("components", []):
            explanation += f"• **{component.get('factor', '')}**: {component.get('value', '')}\n"
            if component.get("calculation"):
                explanation += f"  - Calculation: {component.get('calculation')}\n"
            explanation += f"  - Impact: {component.get('impact', '')}\n\n"
        
        if breakdown.get("estimated_breakdown"):
            est = breakdown["estimated_breakdown"]
            explanation += f"**Estimated Breakdown:**\n"
            explanation += f"• Base premium: {est['base_premium']:.2f} SGD\n"
            explanation += f"• Age adjustment: {est['age_adjustment']}\n"
            explanation += f"• Destination adjustment: {est['destination_adjustment']}\n"
            explanation += f"• Estimated total: {est['estimated_total']:.2f} SGD\n"
            explanation += f"• *{est['note']}*\n"
        
        return explanation

