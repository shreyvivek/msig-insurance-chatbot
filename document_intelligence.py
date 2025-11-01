"""
Block 3: Document Intelligence
Extract trip information from uploaded documents and generate quotes
"""

import os
import json
import logging
import base64
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import re
import PyPDF2
import pdfplumber
from groq import Groq

logger = logging.getLogger(__name__)

class DocumentIntelligence:
    """Handles document extraction and quote generation"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
    
    async def extract_trip_info(self, document_data: str, document_type: str) -> Dict:
        """Extract trip information from uploaded document - handles PDFs, images, emails"""
        try:
            text = ""
            
            # Handle base64 encoded files
            if document_data.startswith("data:"):
                # Extract MIME type and base64 data
                header, encoded = document_data.split(",", 1)
                file_bytes = base64.b64decode(encoded)
                
                # Determine file type from MIME
                if "pdf" in header.lower():
                    document_type = "pdf"
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                        tmp.write(file_bytes)
                        text = self._extract_pdf_text(Path(tmp.name))
                        Path(tmp.name).unlink()
                elif "image" in header.lower():
                    document_type = "image"
                    # For images, use OCR via Groq Vision or description
                    # Store base64 for processing
                    import base64 as b64
                    image_base64 = b64.b64encode(file_bytes).decode('utf-8')
                    # Use Groq to extract text from image
                    ocr_prompt = f"""Extract all text from this travel booking image. Look for:
- Flight numbers, airlines
- Destinations (airports, cities, countries)
- Dates (departure, return)
- Passenger names
- Booking references
- Trip costs

Return as structured text that can be parsed for travel insurance."""
                    
                    # For now, create a description for the LLM
                    text = f"[Image document uploaded: {file.size} bytes - {header}] Please extract travel booking information from this image including destination, dates, and traveler details."
                else:
                    # Try as text
                    text = file_bytes.decode('utf-8', errors='ignore')
            
            elif document_type == "pdf":
                # Handle PDF file path
                if Path(document_data).exists():
                    text = self._extract_pdf_text(Path(document_data))
                else:
                    # Try to read as base64 without data: prefix
                    try:
                        pdf_bytes = base64.b64decode(document_data)
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                            tmp.write(pdf_bytes)
                            text = self._extract_pdf_text(Path(tmp.name))
                            Path(tmp.name).unlink()
                    except:
                        text = document_data
            else:
                # For text, images, emails - use directly
                try:
                    text = base64.b64decode(document_data).decode('utf-8', errors='ignore')
                except:
                    text = document_data
            
            # For images, use a more detailed prompt
            if document_type == "image":
                extraction_prompt = f"""Extract travel booking information from this IMAGE document. Use OCR techniques to read:

Document Type: IMAGE (screenshot or photo of booking)

Look carefully for:
- Flight numbers, airline names
- Departure and arrival airports/cities
- Travel dates (departure, return)
- Passenger names and ages
- Booking reference numbers
- Trip costs/prices
- Destination cities or countries

Extract all visible text and information. Return as JSON:
{{
    "destination": "city, country",
    "departure_date": "YYYY-MM-DD",
    "return_date": "YYYY-MM-DD",
    "travelers": [
        {{
            "name": "Full Name if visible",
            "age": 0
        }}
    ],
    "flight_details": {{
        "airline": "",
        "flight_number": "",
        "departure_airport": "",
        "arrival_airport": ""
    }},
    "hotel_details": {{
        "hotel_name": "",
        "check_in": "YYYY-MM-DD",
        "check_out": "YYYY-MM-DD",
        "location": ""
    }},
    "trip_cost": 0,
    "activities": [],
    "trip_purpose": "business/leisure/adventure",
    "additional_info": ""
}}

Extract everything you can see in the image. If dates are in text format (e.g., "Dec 15"), convert to YYYY-MM-DD format."""
            else:
                # Use Groq to extract structured information with focus on insurance-relevant data
                extraction_prompt = f"""Extract travel insurance-relevant information from this {document_type.upper()} document:

Document Content:
{text[:8000]}

IMPORTANT: Extract information needed for travel insurance quotes:
- Trip destination (critical for risk assessment)
- Travel dates (start and end dates)
- Number of travelers and their ages (for pricing)
- Trip cost (for trip cancellation coverage)
- Planned activities (for activity-based coverage needs)

Return as JSON:
{{
    "destination": "city, country (e.g., Tokyo, Japan)",
    "departure_date": "YYYY-MM-DD",
    "return_date": "YYYY-MM-DD",
    "travelers": [
        {{
            "name": "Full Name if available",
            "age": 0
        }}
    ],
    "flight_details": {{
        "airline": "",
        "flight_number": "",
        "departure_airport": "",
        "arrival_airport": ""
    }},
    "hotel_details": {{
        "hotel_name": "",
        "check_in": "YYYY-MM-DD",
        "check_out": "YYYY-MM-DD",
        "location": ""
    }},
    "trip_cost": 0,
    "activities": [],
    "trip_purpose": "business/leisure/adventure",
    "additional_info": ""
}}

Extract all available information. Use null only for fields completely absent."""

            # For images, we might need to use vision capabilities if available
            # For now, use text-based extraction
            
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information from travel documents. Always return valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            extracted = json.loads(response.choices[0].message.content)
            
            # Validate and enrich
            result = {
                "success": True,
                "extracted_data": extracted,
                "confidence": "high",
                "validation_questions": []
            }
            
            # Check for missing critical fields
            if not extracted.get("destination"):
                result["validation_questions"].append("What is your trip destination?")
            if not extracted.get("departure_date"):
                result["validation_questions"].append("When does your trip start?")
            if not extracted.get("return_date"):
                result["validation_questions"].append("When does your trip end?")
            
            return result
        
        except Exception as e:
            logger.error(f"Document extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_data": {}
            }
    
    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF"""
        text_content = []
        
        try:
            # Try pdfplumber first
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
        except:
            # Fallback to PyPDF2
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
        
        return "\n\n".join(text_content)
    
    async def generate_quote(self, destination: str, start_date: str, end_date: str,
                            travelers: int = 1, ages: List[int] = None,
                            activities: List[str] = None, trip_cost: float = None) -> Dict:
        """Generate personalized insurance quote"""
        
        # Calculate trip duration
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        duration = (end - start).days
        
        if not ages:
            ages = [30] * travelers  # Default age
        
        # Get base pricing (this would integrate with actual pricing API)
        # For now, use simplified pricing logic
        base_price_per_day = 5.0  # SGD
        base_price = base_price_per_day * duration * travelers
        
        # Activity adjustments
        activity_multipliers = {
            "skiing": 1.5,
            "scuba diving": 1.8,
            "hiking": 1.2,
            "rock climbing": 2.0,
            "bungee jumping": 2.5
        }
        
        multiplier = 1.0
        risky_activities = []
        if activities:
            for activity in activities:
                activity_lower = activity.lower()
                for key, mult in activity_multipliers.items():
                    if key in activity_lower:
                        multiplier = max(multiplier, mult)
                        risky_activities.append(activity)
        
        # Age adjustments
        age_adjustments = {}
        for age in ages:
            if age < 18:
                age_adjustments[age] = 1.0  # Children often covered for free
            elif age > 65:
                age_adjustments[age] = 1.5  # Seniors pay more
            else:
                age_adjustments[age] = 1.0
        
        # Calculate final price
        age_factor = sum(age_adjustments.values()) / len(age_adjustments) if age_adjustments else 1.0
        final_price = base_price * multiplier * age_factor
        
        # Generate recommendations using predictive intelligence
        from predictive_intelligence import PredictiveIntelligence
        predictive = PredictiveIntelligence()
        risk_data = await predictive.get_risk_assessment(
            destination=destination,
            activities=activities or [],
            duration=duration,
            age=sum(ages) // len(ages) if ages else 30
        )
        
        # Create quote options
        quotes = [
            {
                "plan_name": "Basic",
                "medical_coverage": 20000,
                "trip_cancellation": trip_cost * 0.5 if trip_cost else 5000,
                "baggage": 1000,
                "price": round(final_price * 0.8, 2),
                "currency": "SGD",
                "recommended_for": "Budget-conscious travelers"
            },
            {
                "plan_name": "Standard",
                "medical_coverage": 50000,
                "trip_cancellation": trip_cost if trip_cost else 10000,
                "baggage": 2000,
                "price": round(final_price, 2),
                "currency": "SGD",
                "recommended_for": "Most travelers"
            },
            {
                "plan_name": "Premium",
                "medical_coverage": 100000,
                "trip_cancellation": trip_cost * 1.5 if trip_cost else 20000,
                "baggage": 5000,
                "price": round(final_price * 1.5, 2),
                "currency": "SGD",
                "recommended_for": "Comprehensive protection"
            }
        ]
        
        # Add risk-based recommendations
        recommendations = []
        if risk_data.get("high_risk_activities"):
            recommendations.append(
                f"⚠️ Based on historical data, {destination} has higher risk for {', '.join(risk_data['high_risk_activities'])}. "
                f"Consider Premium plan for better coverage."
            )
        
        if duration > 30:
            recommendations.append(
                f"📅 Your {duration}-day trip exceeds standard coverage. Premium plan recommended for extended stays."
            )
        
        result = {
            "quote_id": f"quote_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "trip_details": {
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "duration_days": duration,
                "travelers": travelers,
                "ages": ages,
                "activities": activities or [],
                "trip_cost": trip_cost
            },
            "quotes": quotes,
            "risk_assessment": risk_data,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
        return result

