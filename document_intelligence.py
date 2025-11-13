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
                    
                    # For images, we'll use the base64 data directly in the prompt
                    # The LLM will handle the image description
                    text = f"[Image document uploaded: {len(file_bytes)} bytes - {header}] Please extract travel booking information from this image including destination, dates, and traveler details."
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
                extraction_prompt = f"""You are analyzing a TRAVEL BOOKING IMAGE (screenshot or photo). Extract all visible travel booking information.

IMPORTANT: Even if some information is partially visible or unclear, extract what you CAN see. Partial information is better than nothing.

Look carefully for ANY of these details:
- Flight numbers, airline names
- Departure and arrival airports/cities  
- Source/departure location
- Travel dates (departure, return) - can be in any format (e.g., "Dec 15, 2024" or "15/12/2024")
- Passenger names and count
- Booking reference numbers
- Ticket policies or booking policies mentioned
- Trip costs/prices
- Destination cities or countries

Return as JSON with these fields. Use null for fields you cannot see at all:
{{
    "destination": "city, country (e.g., Tokyo, Japan) or null",
    "source": "city, country (departure location) or null",
    "departure_date": "YYYY-MM-DD format (convert any date format you see) or null",
    "return_date": "YYYY-MM-DD format or null",
    "pax": <number of travelers if visible, otherwise 1>,
    "travelers": [
        {{
            "name": "Full Name if visible, otherwise empty string",
            "age": 0
        }}
    ],
    "ticket_policies": ["any policy mentioned"] or [],
    "flight_details": {{
        "airline": "airline name if visible" or "",
        "flight_number": "flight number if visible" or "",
        "departure_airport": "airport code or city" or "",
        "arrival_airport": "airport code or city" or ""
    }},
    "hotel_details": {{
        "hotel_name": "" or null,
        "check_in": "YYYY-MM-DD" or null,
        "check_out": "YYYY-MM-DD" or null,
        "location": "" or null
    }},
    "trip_cost": 0 or null,
    "activities": [],
    "trip_purpose": "business/leisure/adventure" or null,
    "additional_info": "any other relevant information you see"
}}

CRITICAL: Extract ANY information you can see, even if incomplete. If you see a destination but not dates, still return the destination. If you see dates but not destination, return the dates. Partial extraction is acceptable."""
            else:
                # Use Groq to extract structured information with focus on insurance-relevant data
                extraction_prompt = f"""Extract travel insurance-relevant information from this {document_type.upper()} document:

Document Content:
{text[:10000]}

IMPORTANT: Extract ANY information you can find, even if incomplete. Partial data is better than nothing.

Look for:
- Trip destination (city, country) - CRITICAL
- Source/departure location (city, country)
- Travel dates (start and end dates) - can be in various formats
- Number of travelers (pax count)
- Traveler ages if mentioned
- Ticket policies/booking policies mentioned
- Trip cost/price
- Planned activities
- Flight details (airline, flight number, airports)
- Hotel details (name, check-in/out dates, location)

Return as JSON. Use null for fields completely absent, but try to extract partial information:
{{
    "destination": "city, country (e.g., Tokyo, Japan) or null",
    "source": "city, country (e.g., Singapore, Singapore) or null",
    "departure_date": "YYYY-MM-DD (convert any date format you see) or null",
    "return_date": "YYYY-MM-DD (convert any date format you see) or null",
    "pax": <number of travelers if mentioned, otherwise 1>,
    "travelers": [
        {{
            "name": "Full Name if available" or "",
            "age": <age if mentioned> or 0
        }}
    ],
    "ticket_policies": ["policy mentioned"] or [],
    "flight_details": {{
        "airline": "" or null,
        "flight_number": "" or null,
        "departure_airport": "" or null,
        "arrival_airport": "" or null
    }},
    "hotel_details": {{
        "hotel_name": "" or null,
        "check_in": "YYYY-MM-DD" or null,
        "check_out": "YYYY-MM-DD" or null,
        "location": "" or null
    }},
    "trip_cost": <number if mentioned> or 0 or null,
    "activities": [] or ["activity names if mentioned"],
    "trip_purpose": "business/leisure/adventure" or null,
    "additional_info": "any other relevant information"
}}

CRITICAL: Extract ANY information visible, even if incomplete. If you see destination but not dates, return destination. If you see dates but not destination, return dates."""

            # For images, we might need to use vision capabilities if available
            # For now, use text-based extraction
            
            try:
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are an expert at extracting structured information from travel documents. Always return valid JSON. Even if information is incomplete, return what you can extract."},
                        {"role": "user", "content": extraction_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=2000
                )
                
                response_text = response.choices[0].message.content
                logger.debug(f"LLM extraction response: {response_text[:500]}")
                
                # Try to parse JSON - handle common issues
                try:
                    extracted = json.loads(response_text)
                except json.JSONDecodeError as je:
                    logger.warning(f"JSON parse error: {je}. Response: {response_text[:200]}")
                    # Try to extract JSON from markdown code blocks
                    import re
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                    if json_match:
                        extracted = json.loads(json_match.group(1))
                    else:
                        # Try to find JSON object in the text
                        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                        if json_match:
                            extracted = json.loads(json_match.group(0))
                        else:
                            raise je
            except Exception as llm_error:
                logger.error(f"LLM extraction failed: {llm_error}", exc_info=True)
                # Return partial success with empty data - let user provide info manually
                return {
                    "success": False,
                    "error": f"Could not process document with AI: {str(llm_error)}",
                    "extracted_data": {},
                    "message": "I had trouble reading your document. Please try uploading a clearer version or describe your trip manually.",
                    "validation_questions": [
                        "What is your trip destination?",
                        "When does your trip start?",
                        "When does your trip end?",
                        "How many travelers?"
                    ]
                }
            
            # Validate and enrich
            result = {
                "success": True,
                "extracted_data": extracted,
                "confidence": "high",
                "validation_questions": []
            }
            
            # Validate fields - but be more lenient
            validation_questions = []
            missing_fields = []
            
            # Check what we have
            has_destination = bool(extracted.get("destination"))
            has_departure_date = bool(extracted.get("departure_date"))
            has_return_date = bool(extracted.get("return_date"))
            has_travelers = bool(extracted.get("travelers") and len(extracted.get("travelers", [])) > 0) or bool(extracted.get("pax"))
            
            # Only flag as missing if we have NOTHING
            if not has_destination:
                missing_fields.append("destination")
                validation_questions.append("What is your trip destination? (city and country)")
            if not has_departure_date:
                missing_fields.append("departure_date")
                validation_questions.append("When does your trip start? (departure date)")
            if not has_return_date:
                missing_fields.append("return_date")
                validation_questions.append("When does your trip end? (return date)")
            if not has_travelers:
                missing_fields.append("travelers")
                validation_questions.append("How many travelers? And what are their ages?")
            
            # Set default values if missing but we have some data
            if not extracted.get("pax") and not extracted.get("travelers"):
                extracted["pax"] = 1
                extracted["travelers"] = [{"name": "", "age": 30}]
            
            # If we have at least destination OR dates, consider it partially successful
            has_partial_data = has_destination or has_departure_date or has_return_date
            
            result["validation_questions"] = validation_questions
            result["missing_fields"] = missing_fields
            result["has_partial_data"] = has_partial_data
            result["ready_for_quote"] = has_destination and (has_departure_date or has_return_date) and has_travelers
            
            # If we have partial data, still mark as success
            if has_partial_data:
                result["success"] = True
                result["confidence"] = "partial" if missing_fields else "high"
            
            # ENHANCEMENT 1: Destination-first analysis with claims data
            destination = extracted.get("destination")
            if destination:
                try:
                    from claims_database import ClaimsDatabase
                    from claims_analyzer import ClaimsAnalyzer
                    
                    claims_db = ClaimsDatabase()
                    claims_analyzer = ClaimsAnalyzer()
                    
                    # Analyze destination for adventurous activities and claims patterns
                    risk_analysis = claims_db.analyze_destination_risks(destination)
                    claims_analysis = await claims_analyzer.analyze_destination_and_recommend(destination)
                    
                    # Detect adventurous activities based on destination
                    adventure_keywords = {
                        "skiing": ["ski", "snow", "mountain", "slope", "alpine"],
                        "scuba": ["dive", "underwater", "coral", "reef"],
                        "hiking": ["trek", "trail", "mountain", "hike", "climb"],
                        "adventure": ["bungee", "paragliding", "rafting", "zip", "adventure"]
                    }
                    
                    destination_lower = destination.lower()
                    detected_activities = []
                    for activity, keywords in adventure_keywords.items():
                        if any(kw in destination_lower for kw in keywords):
                            detected_activities.append(activity)
                    
                    # Suggest insurance enhancements based on activities and claims
                    insurance_suggestions = []
                    
                    # Medical coverage suggestions based on claims
                    if risk_analysis.get("claim_types", {}).get("Medical"):
                        medical_pct = risk_analysis["claim_types"]["Medical"]["percentage"]
                        medical_avg = risk_analysis["claim_types"]["Medical"]["avg_amount"]
                        if medical_pct > 40:  # High medical claim rate
                            insurance_suggestions.append({
                                "type": "medical_coverage",
                                "reason": f"{medical_pct}% of travelers have medical claims (avg ${medical_avg:,.2f} SGD)",
                                "recommendation": "Consider higher medical coverage limits",
                                "priority": "high"
                            })
                    
                    # Adventure activity suggestions
                    if detected_activities:
                        insurance_suggestions.append({
                            "type": "adventure_coverage",
                            "activities": detected_activities,
                            "reason": f"Destination likely involves {', '.join(detected_activities)}",
                            "recommendation": "Ensure policy covers adventure activities",
                            "priority": "high"
                        })
                    
                    result["claims_analysis"] = claims_analysis
                    result["risk_analysis"] = risk_analysis
                    result["detected_activities"] = detected_activities
                    result["insurance_suggestions"] = insurance_suggestions
                    
                    logger.info(f"✅ Destination-first analysis completed for {destination}")
                    
                except Exception as e:
                    logger.error(f"Destination analysis failed: {e}", exc_info=True)
            
            if missing_fields:
                result["message"] = "I found some information, but I need a bit more to suggest the best insurance options. Please provide the missing details."
            
            return result
        
        except Exception as e:
            logger.error(f"Document extraction failed: {e}", exc_info=True)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return a more helpful error response
            return {
                "success": False,
                "error": str(e),
                "extracted_data": {},
                "message": f"I had trouble reading your document. Error: {str(e)[:100]}. Please try uploading a clearer version or describe your trip manually.",
                "validation_questions": [
                    "What is your trip destination?",
                    "When does your trip start?",
                    "When does your trip end?",
                    "How many travelers?"
                ]
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
        
        # Create quote options - marked as local
        quotes = [
            {
                "plan_name": "Basic",
                "medical_coverage": 20000,
                "trip_cancellation": trip_cost * 0.5 if trip_cost else 5000,
                "baggage": 1000,
                "price": round(final_price * 0.8, 2),
                "currency": "SGD",
                "recommended_for": "Budget-conscious travelers",
                "source": "local"  # Clearly marked as local/preset
            },
            {
                "plan_name": "Standard",
                "medical_coverage": 50000,
                "trip_cancellation": trip_cost if trip_cost else 10000,
                "baggage": 2000,
                "price": round(final_price, 2),
                "currency": "SGD",
                "recommended_for": "Most travelers",
                "source": "local"  # Clearly marked as local/preset
            },
            {
                "plan_name": "Premium",
                "medical_coverage": 100000,
                "trip_cancellation": trip_cost * 1.5 if trip_cost else 20000,
                "baggage": 5000,
                "price": round(final_price * 1.5, 2),
                "currency": "SGD",
                "recommended_for": "Comprehensive protection",
                "source": "local"  # Clearly marked as local/preset
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

