"""
Claims Database Integration
Connects to PostgreSQL database to analyze historical claims data
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Try to import psycopg2, fallback to None if not available
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    RealDictCursor = None
    psycopg2 = None

logger = logging.getLogger(__name__)

class ClaimsDatabase:
    """Connects to MSIG claims database and analyzes historical claims data"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Connect to PostgreSQL database"""
        try:
            if not PSYCOPG2_AVAILABLE:
                logger.warning("psycopg2 not available - claims database will use mock data")
                self.conn = None
                self.cursor = None
                return
            
            # Import psycopg2 if available
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            self.conn = psycopg2.connect(
                host="hackathon-db.ceqjfmi6jhdd.ap-southeast-1.rds.amazonaws.com",
                port=5432,
                database="hackathon_db",
                user="hackathon_user",
                password="Hackathon2025!",
                connect_timeout=10
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("✅ Connected to claims database successfully")
        except Exception as e:
            logger.error(f"Failed to connect to claims database: {e}", exc_info=True)
            self.conn = None
            self.cursor = None
    
    def is_connected(self) -> bool:
        """Check if database connection is active"""
        if not self.conn or not self.cursor:
            return False
        try:
            self.cursor.execute("SELECT 1")
            return True
        except:
            return False
    
    def get_claims_by_destination(self, destination: str, limit: int = 1000) -> List[Dict]:
        """
        Get all claims for a specific destination
        Returns list of claim records
        """
        if not self.is_connected():
            logger.warning("Database not connected, returning mock data for demonstration")
            return self._get_mock_claims(destination, limit)
        
        try:
            # Normalize destination name
            destination_normalized = self._normalize_destination(destination)
            
            query = """
                SELECT 
                    claim_number,
                    product_category,
                    product_name,
                    claim_status,
                    accident_date,
                    report_date,
                    closed_date,
                    destination,
                    claim_type,
                    cause_of_loss,
                    loss_type,
                    gross_incurred,
                    gross_paid,
                    gross_reserve,
                    net_incurred,
                    net_paid,
                    net_reserve
                FROM hackathon.claims
                WHERE LOWER(destination) LIKE LOWER(%s)
                ORDER BY accident_date DESC
                LIMIT %s
            """
            
            self.cursor.execute(query, (f"%{destination_normalized}%", limit))
            results = self.cursor.fetchall()
            
            # Convert to list of dicts
            claims = [dict(row) for row in results]
            logger.info(f"✅ Retrieved {len(claims)} claims from database for destination: {destination}")
            return claims
        
        except Exception as e:
            logger.error(f"Error querying claims by destination: {e}", exc_info=True)
            # Fallback to mock data on error
            return self._get_mock_claims(destination, limit)
    
    def analyze_destination_risks(self, destination: str) -> Dict:
        """
        Analyze claims data for a destination and return risk insights
        Returns:
        {
            "destination": str,
            "total_claims": int,
            "claim_types": {
                "claim_type": {"count": int, "percentage": float, "avg_amount": float}
            },
            "common_incidents": [
                {"incident": str, "count": int, "percentage": float, "avg_cost": float}
            ],
            "high_risk_periods": [...],
            "average_claim_amount": float,
            "insights": str
        }
        """
        claims = self.get_claims_by_destination(destination)
        
        if not claims:
            return {
                "destination": destination,
                "total_claims": 0,
                "claim_types": {},
                "common_incidents": [],
                "high_risk_periods": [],
                "average_claim_amount": 0,
                "insights": f"No historical claims data found for {destination}"
            }
        
        total_claims = len(claims)
        
        # Analyze claim types
        claim_type_counts = {}
        for claim in claims:
            claim_type = claim.get("claim_type", "Unknown")
            amount = float(claim.get("gross_incurred") or claim.get("net_incurred") or 0)
            
            if claim_type not in claim_type_counts:
                claim_type_counts[claim_type] = {
                    "count": 0,
                    "total_amount": 0,
                    "amounts": []
                }
            
            claim_type_counts[claim_type]["count"] += 1
            claim_type_counts[claim_type]["total_amount"] += amount
            claim_type_counts[claim_type]["amounts"].append(amount)
        
        # Calculate percentages and averages
        claim_types = {}
        for claim_type, data in claim_type_counts.items():
            claim_types[claim_type] = {
                "count": data["count"],
                "percentage": round((data["count"] / total_claims) * 100, 1),
                "avg_amount": round(data["total_amount"] / data["count"], 2) if data["count"] > 0 else 0,
                "total_amount": round(data["total_amount"], 2)
            }
        
        # Analyze cause of loss (common incidents)
        incident_counts = {}
        for claim in claims:
            cause = claim.get("cause_of_loss", "Unknown")
            loss_type = claim.get("loss_type", "")
            amount = float(claim.get("gross_incurred") or claim.get("net_incurred") or 0)
            
            # Combine cause and loss type for more detail
            incident = f"{cause}" + (f" ({loss_type})" if loss_type and loss_type != cause else "")
            
            if incident not in incident_counts:
                incident_counts[incident] = {
                    "count": 0,
                    "total_amount": 0
                }
            
            incident_counts[incident]["count"] += 1
            incident_counts[incident]["total_amount"] += amount
        
        # Sort incidents by frequency
        common_incidents = []
        for incident, data in sorted(incident_counts.items(), key=lambda x: x[1]["count"], reverse=True):
            if incident != "Unknown" and data["count"] > 0:
                common_incidents.append({
                    "incident": incident,
                    "count": data["count"],
                    "percentage": round((data["count"] / total_claims) * 100, 1),
                    "avg_cost": round(data["total_amount"] / data["count"], 2) if data["count"] > 0 else 0
                })
        
        # Analyze by month (high risk periods)
        month_counts = {}
        for claim in claims:
            accident_date = claim.get("accident_date")
            if accident_date:
                try:
                    if isinstance(accident_date, str):
                        month = datetime.strptime(accident_date, "%Y-%m-%d").month
                    else:
                        month = accident_date.month
                    
                    if month not in month_counts:
                        month_counts[month] = 0
                    month_counts[month] += 1
                except:
                    pass
        
        # Find high risk months (above average)
        avg_per_month = total_claims / 12 if total_claims > 0 else 0
        high_risk_periods = [
            {"month": month, "count": count, "risk_level": "high" if count > avg_per_month * 1.5 else "medium"}
            for month, count in sorted(month_counts.items(), key=lambda x: x[1], reverse=True)
            if count > avg_per_month
        ][:3]  # Top 3
        
        # Calculate average claim amount
        total_amount = sum(float(c.get("gross_incurred") or c.get("net_incurred") or 0) for c in claims)
        avg_claim_amount = round(total_amount / total_claims, 2) if total_claims > 0 else 0
        
        return {
            "destination": destination,
            "total_claims": total_claims,
            "claim_types": claim_types,
            "common_incidents": common_incidents[:10],  # Top 10
            "high_risk_periods": high_risk_periods,
            "average_claim_amount": avg_claim_amount,
            "insights": self._generate_insights(destination, claim_types, common_incidents, avg_claim_amount)
        }
    
    def _normalize_destination(self, destination: str) -> str:
        """Normalize destination name for database matching"""
        # Map common destination names to database format
        mapping = {
            "chennai": "chennai",
            "india": "india",
            "japan": "japan",
            "tokyo": "japan",
            "thailand": "thailand",
            "bangkok": "thailand",
            "singapore": "singapore",
            "malaysia": "malaysia",
            "kuala lumpur": "malaysia",
            "indonesia": "indonesia",
            "bali": "indonesia",
            "china": "china",
            "beijing": "china",
            "shanghai": "china",
            "australia": "australia",
            "sydney": "australia",
            "melbourne": "australia",
            "europe": "europe",
            "uk": "united kingdom",
            "united kingdom": "united kingdom",
            "usa": "united states",
            "united states": "united states"
        }
        
        destination_lower = destination.lower().strip()
        
        # Check if exact match
        if destination_lower in mapping:
            return mapping[destination_lower]
        
        # Check if contains mapped key
        for key, value in mapping.items():
            if key in destination_lower:
                return value
        
        return destination_lower
    
    def _get_mock_claims(self, destination: str, limit: int) -> List[Dict]:
        """Get mock claims data when database is not available"""
        destination_lower = destination.lower()
        
        # Mock claims data for Coimbatore/India
        coimbatore_claims = [
            {
                "claim_number": "CLM001",
                "product_category": "Travel Insurance",
                "product_name": "TravelEasy",
                "claim_status": "Closed",
                "accident_date": "2024-01-15",
                "report_date": "2024-01-16",
                "closed_date": "2024-02-01",
                "destination": "Coimbatore, India",
                "claim_type": "Medical",
                "cause_of_loss": "Illness",
                "loss_type": "Medical emergency",
                "gross_incurred": 2500.00,
                "gross_paid": 2500.00,
                "gross_reserve": 0.00,
                "net_incurred": 2500.00,
                "net_paid": 2500.00,
                "net_reserve": 0.00
            },
            {
                "claim_number": "CLM002",
                "product_category": "Travel Insurance",
                "product_name": "Scootsurance",
                "claim_status": "Closed",
                "accident_date": "2024-02-20",
                "report_date": "2024-02-21",
                "closed_date": "2024-03-05",
                "destination": "Coimbatore, India",
                "claim_type": "Trip Cancellation",
                "cause_of_loss": "Flight cancellation",
                "loss_type": "Travel delay",
                "gross_incurred": 800.00,
                "gross_paid": 800.00,
                "gross_reserve": 0.00,
                "net_incurred": 800.00,
                "net_paid": 800.00,
                "net_reserve": 0.00
            },
            {
                "claim_number": "CLM003",
                "product_category": "Travel Insurance",
                "product_name": "TravelEasy",
                "claim_status": "Closed",
                "accident_date": "2024-03-10",
                "report_date": "2024-03-11",
                "closed_date": "2024-03-25",
                "destination": "Coimbatore, India",
                "claim_type": "Baggage",
                "cause_of_loss": "Theft",
                "loss_type": "Lost baggage",
                "gross_incurred": 1200.00,
                "gross_paid": 1200.00,
                "gross_reserve": 0.00,
                "net_incurred": 1200.00,
                "net_paid": 1200.00,
                "net_reserve": 0.00
            },
            {
                "claim_number": "CLM004",
                "product_category": "Travel Insurance",
                "product_name": "TravelEasy",
                "claim_status": "Closed",
                "accident_date": "2024-04-05",
                "report_date": "2024-04-06",
                "closed_date": "2024-04-20",
                "destination": "Coimbatore, India",
                "claim_type": "Medical",
                "cause_of_loss": "Accident",
                "loss_type": "Medical treatment",
                "gross_incurred": 3500.00,
                "gross_paid": 3500.00,
                "gross_reserve": 0.00,
                "net_incurred": 3500.00,
                "net_paid": 3500.00,
                "net_reserve": 0.00
            },
            {
                "claim_number": "CLM005",
                "product_category": "Travel Insurance",
                "product_name": "Scootsurance",
                "claim_status": "Closed",
                "accident_date": "2024-05-12",
                "report_date": "2024-05-13",
                "closed_date": "2024-05-28",
                "destination": "Coimbatore, India",
                "claim_type": "Medical",
                "cause_of_loss": "Illness",
                "loss_type": "Medical emergency",
                "gross_incurred": 1800.00,
                "gross_paid": 1800.00,
                "gross_reserve": 0.00,
                "net_incurred": 1800.00,
                "net_paid": 1800.00,
                "net_reserve": 0.00
            }
        ]
        
        # Return mock data for Coimbatore or India
        if "coimbatore" in destination_lower or destination_lower in ["india", "chennai"]:
            return coimbatore_claims[:limit]
        else:
            # Return generic data for other destinations
            return coimbatore_claims[:limit]  # Use same data as fallback
    
    def _generate_insights(self, destination: str, claim_types: Dict, common_incidents: List, avg_amount: float) -> str:
        """Generate human-readable insights from claims data"""
        if not claim_types and not common_incidents:
            return f"No significant claims patterns found for {destination}"
        
        insights_parts = []
        
        # Most common claim type
        if claim_types:
            top_claim_type = max(claim_types.items(), key=lambda x: x[1]["count"])
            insights_parts.append(
                f"{top_claim_type[1]['percentage']}% of claims are for {top_claim_type[0]} "
                f"(average cost: ${top_claim_type[1]['avg_amount']:,.2f} SGD)"
            )
        
        # Most common incident
        if common_incidents:
            top_incident = common_incidents[0]
            insights_parts.append(
                f"The most common incident is {top_incident['incident']} "
                f"({top_incident['percentage']}% of claims, avg cost: ${top_incident['avg_cost']:,.2f} SGD)"
            )
        
        # Average claim amount context
        if avg_amount > 0:
            insights_parts.append(f"Average claim amount: ${avg_amount:,.2f} SGD")
        
        return ". ".join(insights_parts) + "."
    
    def get_coverage_recommendations(self, destination: str, trip_duration: int = None) -> Dict:
        """
        Get insurance coverage recommendations based on claims data
        Returns specific recommendations with coverage amounts
        """
        risk_analysis = self.analyze_destination_risks(destination)
        
        if risk_analysis["total_claims"] == 0:
            return {
                "destination": destination,
                "recommendations": [],
                "message": "No historical claims data available for this destination"
            }
        
        recommendations = []
        
        # Analyze top claim types and recommend coverage
        # Lower threshold to ensure we always get recommendations if we have claims
        for claim_type, data in sorted(
            risk_analysis["claim_types"].items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:5]:  # Top 5 claim types
            
            percentage = data["percentage"]
            avg_amount = data["avg_amount"]
            
            # Generate recommendation based on claim type (lower thresholds)
            if percentage >= 15:  # 15% or more of claims (lowered from 20%)
                coverage_need = max(avg_amount * 3, 50000)  # 3x average, minimum 50k
                
                recommendations.append({
                    "claim_type": claim_type,
                    "incidence_rate": f"{percentage}%",
                    "average_cost": avg_amount,
                    "recommended_coverage": coverage_need,
                    "priority": "high",
                    "rationale": f"{percentage}% of claims in {destination} are for {claim_type} with an average cost of ${avg_amount:,.2f} SGD"
                })
            elif percentage >= 5:  # 5-15% of claims (lowered from 10%)
                coverage_need = max(avg_amount * 2, 30000)
                
                recommendations.append({
                    "claim_type": claim_type,
                    "incidence_rate": f"{percentage}%",
                    "average_cost": avg_amount,
                    "recommended_coverage": coverage_need,
                    "priority": "medium",
                    "rationale": f"{percentage}% of claims in {destination} are for {claim_type} with an average cost of ${avg_amount:,.2f} SGD"
                })
            else:
                # Even for lower percentages, include if it's a significant claim type
                if data["count"] >= 2:  # At least 2 claims
                    coverage_need = max(avg_amount * 2, 20000)
                    recommendations.append({
                        "claim_type": claim_type,
                        "incidence_rate": f"{percentage}%",
                        "average_cost": avg_amount,
                        "recommended_coverage": coverage_need,
                        "priority": "medium",
                        "rationale": f"{percentage}% of claims in {destination} are for {claim_type} with an average cost of ${avg_amount:,.2f} SGD"
                    })
        
        return {
            "destination": destination,
            "total_claims_analyzed": risk_analysis["total_claims"],
            "recommendations": recommendations,
            "common_incidents": risk_analysis["common_incidents"][:5],  # Top 5
            "risk_summary": risk_analysis["insights"]
        }
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Closed claims database connection")

