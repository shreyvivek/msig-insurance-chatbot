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
    
    def get_personalized_claims(
        self,
        destination: str = None,
        ages: List[int] = None,
        interests: List[str] = None,
        medical_conditions: List[str] = None,
        trip_duration: int = None,
        num_travelers: int = None,
        purpose: str = None,
        product_category: str = None,
        claim_type: str = None,
        cause_of_loss: str = None,
        loss_type: str = None,
        limit: int = 500
    ) -> List[Dict]:
        """
        Get personalized claims based on user profile and trip details
        Uses multiple filters and fallback logic for comprehensive results
        
        Args:
            destination: Travel destination
            ages: List of traveler ages
            interests: Travel interests (e.g., adventure, cruise, hiking)
            medical_conditions: Medical conditions (e.g., asthma, heart conditions)
            trip_duration: Trip duration in days
            num_travelers: Number of travelers
            purpose: Trip purpose (work/leisure/family/solo)
            product_category: Filter by product category
            claim_type: Filter by claim type
            cause_of_loss: Filter by cause of loss
            loss_type: Filter by loss type
            limit: Maximum number of claims to return
        
        Returns:
            List of claim records ranked by relevance
        """
        if not self.is_connected():
            logger.warning("Database not connected, returning mock data")
            return self._get_mock_claims(destination or "Unknown", limit)
        
        try:
            # Build base query with WHERE conditions
            conditions = []
            params = []
            
            # Destination filter
            if destination:
                destination_normalized = self._normalize_destination(destination)
                conditions.append("LOWER(destination) LIKE LOWER(%s)")
                params.append(f"%{destination_normalized}%")
            
            # Product category filter
            if product_category:
                conditions.append("LOWER(product_category) LIKE LOWER(%s)")
                params.append(f"%{product_category}%")
            
            # Claim type filter
            if claim_type:
                conditions.append("LOWER(claim_type) LIKE LOWER(%s)")
                params.append(f"%{claim_type}%")
            
            # Cause of loss filter
            if cause_of_loss:
                conditions.append("(LOWER(cause_of_loss) LIKE LOWER(%s) OR LOWER(loss_type) LIKE LOWER(%s))")
                params.append(f"%{cause_of_loss}%")
                params.append(f"%{cause_of_loss}%")
            
            # Loss type filter
            if loss_type and not cause_of_loss:  # Avoid duplicate if cause_of_loss already set
                conditions.append("LOWER(loss_type) LIKE LOWER(%s)")
                params.append(f"%{loss_type}%")
            
            # Build query
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
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
                WHERE {where_clause}
                ORDER BY 
                    CASE WHEN gross_incurred IS NOT NULL THEN gross_incurred ELSE net_incurred END DESC,
                    accident_date DESC
                LIMIT %s
            """
            
            params.append(limit)
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            primary_claims = [dict(row) for row in results]
            
            # If we have user profile data, apply relevance scoring
            if ages or interests or medical_conditions:
                primary_claims = self._score_claim_relevance(
                    primary_claims, ages, interests, medical_conditions, purpose
                )
            
            # Fallback queries if primary results are insufficient
            if len(primary_claims) < limit // 2:
                fallback_claims = self._get_fallback_claims(
                    destination, ages, interests, medical_conditions, 
                    product_category, claim_type, cause_of_loss,
                    limit - len(primary_claims)
                )
                # Merge and deduplicate
                claim_numbers = {c["claim_number"] for c in primary_claims}
                for claim in fallback_claims:
                    if claim["claim_number"] not in claim_numbers:
                        primary_claims.append(claim)
                        claim_numbers.add(claim["claim_number"])
            
            logger.info(f"✅ Retrieved {len(primary_claims)} personalized claims")
            return primary_claims[:limit]
        
        except Exception as e:
            logger.error(f"Error querying personalized claims: {e}", exc_info=True)
            return self._get_mock_claims(destination or "Unknown", limit)
    
    def _score_claim_relevance(
        self,
        claims: List[Dict],
        ages: List[int] = None,
        interests: List[str] = None,
        medical_conditions: List[str] = None,
        purpose: str = None
    ) -> List[Dict]:
        """Score claims by relevance to user profile"""
        if not claims:
            return claims
        
        # Map interests to claim-related keywords
        interest_keywords = {}
        if interests:
            for interest in interests:
                interest_lower = interest.lower()
                if "adventure" in interest_lower or "hiking" in interest_lower or "trekking" in interest_lower:
                    interest_keywords[interest] = ["accident", "fracture", "injury", "equipment", "medical"]
                elif "cruise" in interest_lower:
                    interest_keywords[interest] = ["medical", "illness", "trip cancellation", "delay"]
                elif "driving" in interest_lower:
                    interest_keywords[interest] = ["accident", "vehicle", "medical", "theft"]
                elif "shopping" in interest_lower:
                    interest_keywords[interest] = ["theft", "baggage", "loss", "personal belongings"]
                elif "scuba" in interest_lower or "diving" in interest_lower:
                    interest_keywords[interest] = ["medical", "accident", "equipment"]
                elif "skiing" in interest_lower or "snow" in interest_lower:
                    interest_keywords[interest] = ["accident", "fracture", "medical", "equipment"]
        
        # Map medical conditions to claim types
        medical_keywords = {}
        if medical_conditions:
            for condition in medical_conditions:
                condition_lower = condition.lower()
                if "asthma" in condition_lower or "respiratory" in condition_lower:
                    medical_keywords[condition] = ["medical", "illness", "emergency"]
                elif "heart" in condition_lower or "cardiac" in condition_lower:
                    medical_keywords[condition] = ["medical", "emergency", "hospital"]
                elif "diabetes" in condition_lower:
                    medical_keywords[condition] = ["medical", "illness"]
                elif "surgery" in condition_lower or "surgical" in condition_lower:
                    medical_keywords[condition] = ["medical", "treatment", "hospital"]
        
        # Score each claim
        scored_claims = []
        for claim in claims:
            score = 0.0
            
            # Age relevance (if we had age data in claims, would use it)
            # For now, medical claims get higher score if user has medical conditions
            if medical_conditions and claim.get("claim_type", "").lower() == "medical":
                score += 20
            
            # Interest relevance
            if interests:
                claim_text = f"{claim.get('claim_type', '')} {claim.get('cause_of_loss', '')} {claim.get('loss_type', '')}".lower()
                for interest, keywords in interest_keywords.items():
                    if any(kw in claim_text for kw in keywords):
                        score += 15
            
            # Medical condition relevance
            if medical_conditions:
                claim_text = f"{claim.get('claim_type', '')} {claim.get('cause_of_loss', '')}".lower()
                for condition, keywords in medical_keywords.items():
                    if any(kw in claim_text for kw in keywords):
                        score += 25
            
            # Severity relevance (higher severity = more relevant)
            gross_incurred = float(claim.get("gross_incurred") or claim.get("net_incurred") or 0)
            if gross_incurred > 50000:
                score += 10
            elif gross_incurred > 20000:
                score += 5
            
            # Purpose relevance
            if purpose:
                purpose_lower = purpose.lower()
                if purpose_lower == "work" and claim.get("claim_type", "").lower() in ["trip cancellation", "trip delay"]:
                    score += 10
                elif purpose_lower == "family" and claim.get("claim_type", "").lower() == "medical":
                    score += 10
            
            scored_claims.append((score, claim))
        
        # Sort by score (descending)
        scored_claims.sort(key=lambda x: x[0], reverse=True)
        return [claim for _, claim in scored_claims]
    
    def _get_fallback_claims(
        self,
        destination: str = None,
        ages: List[int] = None,
        interests: List[str] = None,
        medical_conditions: List[str] = None,
        product_category: str = None,
        claim_type: str = None,
        cause_of_loss: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get fallback claims using similar destinations, age groups, claim categories"""
        if not self.is_connected():
            return []
        
        try:
            fallback_claims = []
            
            # 1. Similar destinations
            if destination:
                similar_destinations = self._get_similar_destinations(destination)
                for similar_dest in similar_destinations[:2]:  # Top 2 similar
                    dest_claims = self.get_claims_by_destination(similar_dest, limit // 3)
                    fallback_claims.extend(dest_claims)
            
            # 2. High-frequency causes of loss
            high_freq_causes = self._get_high_frequency_causes(limit // 3)
            fallback_claims.extend(high_freq_causes)
            
            # 3. High-severity claims
            high_severity = self._get_high_severity_claims(limit // 3)
            fallback_claims.extend(high_severity)
            
            # 4. Similar claim categories based on interests
            if interests:
                interest_claims = self._get_claims_by_interests(interests, limit // 4)
                fallback_claims.extend(interest_claims)
            
            # Deduplicate by claim_number
            seen = set()
            unique_claims = []
            for claim in fallback_claims:
                claim_num = claim.get("claim_number")
                if claim_num and claim_num not in seen:
                    seen.add(claim_num)
                    unique_claims.append(claim)
            
            return unique_claims[:limit]
        
        except Exception as e:
            logger.error(f"Error getting fallback claims: {e}", exc_info=True)
            return []
    
    def _get_similar_destinations(self, destination: str) -> List[str]:
        """Get similar destinations based on region/country"""
        destination_lower = destination.lower()
        
        # Region mappings
        regions = {
            "asia": ["japan", "thailand", "singapore", "malaysia", "indonesia", "china", "india"],
            "europe": ["uk", "united kingdom", "france", "germany", "italy", "spain"],
            "oceania": ["australia", "new zealand"],
            "americas": ["usa", "united states", "canada"]
        }
        
        # Find region
        for region, countries in regions.items():
            if any(country in destination_lower for country in countries):
                return [c for c in countries if c != destination_lower]
        
        return []
    
    def _get_high_frequency_causes(self, limit: int = 50) -> List[Dict]:
        """Get claims with high-frequency causes of loss"""
        if not self.is_connected():
            return []
        
        try:
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
                WHERE cause_of_loss IS NOT NULL
                AND cause_of_loss != ''
                ORDER BY accident_date DESC
                LIMIT %s
            """
            self.cursor.execute(query, (limit,))
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting high frequency causes: {e}", exc_info=True)
            return []
    
    def _get_high_severity_claims(self, limit: int = 50) -> List[Dict]:
        """Get high-severity claims (based on gross_incurred/net_incurred)"""
        if not self.is_connected():
            return []
        
        try:
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
                WHERE (gross_incurred IS NOT NULL AND gross_incurred > 0)
                   OR (net_incurred IS NOT NULL AND net_incurred > 0)
                ORDER BY 
                    COALESCE(gross_incurred, net_incurred, 0) DESC,
                    accident_date DESC
                LIMIT %s
            """
            self.cursor.execute(query, (limit,))
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting high severity claims: {e}", exc_info=True)
            return []
    
    def _get_claims_by_interests(self, interests: List[str], limit: int = 25) -> List[Dict]:
        """Get claims relevant to user interests"""
        if not self.is_connected() or not interests:
            return []
        
        try:
            # Map interests to claim keywords
            keywords = []
            for interest in interests:
                interest_lower = interest.lower()
                if "adventure" in interest_lower or "hiking" in interest_lower:
                    keywords.extend(["accident", "fracture", "injury", "equipment"])
                elif "medical" in interest_lower or "health" in interest_lower:
                    keywords.extend(["medical", "illness", "emergency"])
                elif "baggage" in interest_lower or "shopping" in interest_lower:
                    keywords.extend(["baggage", "theft", "loss"])
            
            if not keywords:
                return []
            
            # Build OR conditions for keywords
            conditions = " OR ".join([
                f"(LOWER(claim_type) LIKE LOWER(%s) OR LOWER(cause_of_loss) LIKE LOWER(%s) OR LOWER(loss_type) LIKE LOWER(%s))"
                for _ in keywords
            ])
            
            params = []
            for keyword in keywords:
                params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
            
            query = f"""
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
                WHERE {conditions}
                ORDER BY accident_date DESC
                LIMIT %s
            """
            params.append(limit)
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting claims by interests: {e}", exc_info=True)
            return []
    
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
    
    def analyze_claims_for_policy_scoring(
        self,
        policy_name: str,
        destination: str = None,
        ages: List[int] = None,
        interests: List[str] = None,
        medical_conditions: List[str] = None,
        claim_type: str = None
    ) -> Dict:
        """
        Analyze claims data for a specific policy to inform scoring
        Returns metrics like payout rate, denial rate, average payout, etc.
        
        Returns:
            {
                "policy_name": str,
                "total_claims": int,
                "approved_claims": int,
                "denied_claims": int,
                "approval_rate": float,
                "average_payout": float,
                "total_paid": float,
                "claim_types": Dict,
                "common_causes": List,
                "severity_distribution": Dict,
                "relevance_score": float
            }
        """
        if not self.is_connected():
            return {
                "policy_name": policy_name,
                "total_claims": 0,
                "approval_rate": 0.0,
                "average_payout": 0.0,
                "relevance_score": 0.0
            }
        
        try:
            # Build query for this policy
            conditions = ["LOWER(product_name) LIKE LOWER(%s)"]
            params = [f"%{policy_name}%"]
            
            if destination:
                dest_normalized = self._normalize_destination(destination)
                conditions.append("LOWER(destination) LIKE LOWER(%s)")
                params.append(f"%{dest_normalized}%")
            
            if claim_type:
                conditions.append("LOWER(claim_type) LIKE LOWER(%s)")
                params.append(f"%{claim_type}%")
            
            where_clause = " AND ".join(conditions)
            
            query = f"""
                SELECT 
                    claim_number,
                    claim_status,
                    claim_type,
                    cause_of_loss,
                    loss_type,
                    gross_incurred,
                    gross_paid,
                    net_incurred,
                    net_paid,
                    destination,
                    accident_date
                FROM hackathon.claims
                WHERE {where_clause}
                ORDER BY accident_date DESC
                LIMIT 1000
            """
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            claims = [dict(row) for row in results]
            
            if not claims:
                return {
                    "policy_name": policy_name,
                    "total_claims": 0,
                    "approval_rate": 0.0,
                    "average_payout": 0.0,
                    "relevance_score": 0.0
                }
            
            # Analyze claims
            total_claims = len(claims)
            approved = sum(1 for c in claims if c.get("claim_status", "").lower() in ["closed", "approved", "paid"])
            denied = sum(1 for c in claims if c.get("claim_status", "").lower() in ["denied", "rejected"])
            approval_rate = (approved / total_claims * 100) if total_claims > 0 else 0.0
            
            # Calculate payouts
            paid_amounts = []
            for claim in claims:
                paid = float(claim.get("gross_paid") or claim.get("net_paid") or 0)
                if paid > 0:
                    paid_amounts.append(paid)
            
            average_payout = sum(paid_amounts) / len(paid_amounts) if paid_amounts else 0.0
            total_paid = sum(paid_amounts)
            
            # Claim type distribution
            claim_type_counts = {}
            for claim in claims:
                ct = claim.get("claim_type", "Unknown")
                if ct not in claim_type_counts:
                    claim_type_counts[ct] = {"count": 0, "total_paid": 0.0}
                claim_type_counts[ct]["count"] += 1
                paid = float(claim.get("gross_paid") or claim.get("net_paid") or 0)
                claim_type_counts[ct]["total_paid"] += paid
            
            # Common causes
            cause_counts = {}
            for claim in claims:
                cause = claim.get("cause_of_loss", "Unknown")
                if cause not in cause_counts:
                    cause_counts[cause] = 0
                cause_counts[cause] += 1
            
            common_causes = sorted(
                [(cause, count) for cause, count in cause_counts.items() if cause != "Unknown"],
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Severity distribution
            severity_ranges = {
                "low": 0,      # < 5k
                "medium": 0,   # 5k - 20k
                "high": 0,     # 20k - 50k
                "very_high": 0 # > 50k
            }
            
            for claim in claims:
                incurred = float(claim.get("gross_incurred") or claim.get("net_incurred") or 0)
                if incurred < 5000:
                    severity_ranges["low"] += 1
                elif incurred < 20000:
                    severity_ranges["medium"] += 1
                elif incurred < 50000:
                    severity_ranges["high"] += 1
                else:
                    severity_ranges["very_high"] += 1
            
            # Relevance score based on user profile
            relevance_score = 0.0
            if interests or medical_conditions:
                # Score based on how well claim types match interests/conditions
                claim_text = " ".join([c.get("claim_type", "") + " " + c.get("cause_of_loss", "") for c in claims[:20]]).lower()
                
                if interests:
                    for interest in interests:
                        interest_lower = interest.lower()
                        if "adventure" in interest_lower and any("accident" in ct.lower() or "injury" in ct.lower() for ct in claim_type_counts.keys()):
                            relevance_score += 20
                        if "medical" in interest_lower and "Medical" in claim_type_counts:
                            relevance_score += 25
                
                if medical_conditions:
                    if "Medical" in claim_type_counts:
                        relevance_score += 30
            
            return {
                "policy_name": policy_name,
                "total_claims": total_claims,
                "approved_claims": approved,
                "denied_claims": denied,
                "approval_rate": round(approval_rate, 2),
                "average_payout": round(average_payout, 2),
                "total_paid": round(total_paid, 2),
                "claim_types": {k: {"count": v["count"], "total_paid": round(v["total_paid"], 2)} 
                               for k, v in claim_type_counts.items()},
                "common_causes": [{"cause": cause, "count": count} for cause, count in common_causes],
                "severity_distribution": severity_ranges,
                "relevance_score": min(100.0, relevance_score)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing claims for policy scoring: {e}", exc_info=True)
            return {
                "policy_name": policy_name,
                "total_claims": 0,
                "approval_rate": 0.0,
                "average_payout": 0.0,
                "relevance_score": 0.0
            }
    
    def get_multi_traveler_risk_profile(
        self,
        destination: str,
        ages: List[int],
        interests: List[str] = None,
        medical_conditions: List[str] = None
    ) -> Dict:
        """
        Aggregate risk profile for multiple travelers
        Combines individual risk factors and returns aggregated claims insights
        """
        # Get personalized claims for the group
        claims = self.get_personalized_claims(
            destination=destination,
            ages=ages,
            interests=interests,
            medical_conditions=medical_conditions,
            num_travelers=len(ages),
            limit=200
        )
        
        if not claims:
            return {
                "total_claims": 0,
                "aggregate_risk_level": "medium",
                "key_risks": [],
                "recommended_coverage": {}
            }
        
        # Analyze aggregate risk
        total_claims = len(claims)
        
        # Calculate average age
        avg_age = sum(ages) / len(ages) if ages else 30
        
        # Risk level based on claim frequency and severity
        high_severity_count = sum(
            1 for c in claims 
            if float(c.get("gross_incurred") or c.get("net_incurred") or 0) > 20000
        )
        
        if high_severity_count > total_claims * 0.3:
            risk_level = "high"
        elif high_severity_count > total_claims * 0.15:
            risk_level = "medium-high"
        else:
            risk_level = "medium"
        
        # Key risks (top claim types)
        claim_type_counts = {}
        for claim in claims:
            ct = claim.get("claim_type", "Unknown")
            if ct not in claim_type_counts:
                claim_type_counts[ct] = {"count": 0, "total_amount": 0.0}
            claim_type_counts[ct]["count"] += 1
            amount = float(claim.get("gross_incurred") or claim.get("net_incurred") or 0)
            claim_type_counts[ct]["total_amount"] += amount
        
        key_risks = sorted(
            [
                {
                    "risk_type": ct,
                    "frequency": count["count"],
                    "percentage": round((count["count"] / total_claims) * 100, 1),
                    "avg_severity": round(count["total_amount"] / count["count"], 2) if count["count"] > 0 else 0
                }
                for ct, count in claim_type_counts.items()
            ],
            key=lambda x: x["frequency"],
            reverse=True
        )[:5]
        
        # Recommended coverage based on aggregate risk
        recommended_coverage = {}
        for risk in key_risks:
            if risk["risk_type"] == "Medical":
                recommended_coverage["medical"] = max(
                    risk["avg_severity"] * 3,
                    100000 if risk_level in ["high", "medium-high"] else 50000
                )
            elif risk["risk_type"] == "Trip Cancellation":
                recommended_coverage["trip_cancellation"] = max(risk["avg_severity"] * 2, 20000)
            elif risk["risk_type"] == "Baggage":
                recommended_coverage["baggage"] = max(risk["avg_severity"] * 2, 5000)
        
        return {
            "total_claims": total_claims,
            "aggregate_risk_level": risk_level,
            "average_age": round(avg_age, 1),
            "key_risks": key_risks,
            "recommended_coverage": recommended_coverage,
            "claims_sample": claims[:10]  # Sample of relevant claims
        }
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Closed claims database connection")

