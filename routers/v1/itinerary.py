"""
v1 Itinerary endpoints - destination-first analysis
"""
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict
from document_intelligence import DocumentIntelligence
from services.risk_scorer import RiskScorer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/itinerary", tags=["itinerary"])

doc_intel = DocumentIntelligence()
risk_scorer = RiskScorer()

@router.post("/parse")
async def parse_itinerary(request: Dict):
    """
    Parse itinerary with destination prioritization
    Input: Same as /api/extract (file upload or text)
    Output: Trip details with destination highlighted
    """
    # Reuse existing extract logic but ensure destination is extracted first
    # This is essentially the same as /api/extract but with v1 structure
    try:
        # Forward to existing extract endpoint logic
        from run_server import extract_trip
        result = await extract_trip(request)
        
        # Ensure destination is prioritized in response
        trip_details = result.get("trip_details", {})
        if trip_details.get("destination"):
            result["destination_prioritized"] = True
        
        return result
    except Exception as e:
        logger.error(f"Error parsing itinerary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_itinerary(request: Dict):
    """
    Destination-centric risk analysis using Claims DB
    Input: {
        "destination": str,
        "start_date": str (YYYY-MM-DD),
        "end_date": str (YYYY-MM-DD),
        "activities": List[str] (optional),
        "user_profile": Dict (optional, with adventurous_score)
    }
    Output: {
        "destination_summary": Dict,
        "risk_score": Dict,
        "recommended_upgrades": List,
        "top_claim_reasons": List,
        "evidence": Dict
    }
    """
    destination = request.get("destination", "").strip()
    if not destination:
        raise HTTPException(status_code=400, detail="destination is required")
    
    try:
        trip_features = {
            "destination": destination,
            "start_date": request.get("start_date"),
            "end_date": request.get("end_date"),
            "activities": request.get("activities", [])
        }
        
        user_profile = request.get("user_profile", {})
        
        # Calculate risk
        risk_analysis = risk_scorer.predict(trip_features, user_profile)
        
        # Get claims data for destination
        claims_data = risk_scorer._get_claims_for_destination(destination)
        
        return {
            "destination": destination,
            "destination_summary": {
                "name": destination,
                "claims_count": claims_data.get("claim_count", 0),
                "avg_claim_amount": claims_data.get("avg_claim_amount", 0),
                "median_claim_amount": claims_data.get("median_claim_amount", 0)
            },
            "risk_score": {
                "probability": risk_analysis.get("risk_prob", 0.0),
                "category": risk_analysis.get("category", "low"),
                "recommended_medical": risk_analysis.get("recommended_medical", 30000)
            },
            "recommended_upgrades": risk_analysis.get("recommended_coverage_upgrades", []),
            "top_claim_reasons": claims_data.get("top_claim_reasons", []),
            "evidence": risk_analysis.get("evidence", {})
        }
        
    except Exception as e:
        logger.error(f"Error analyzing itinerary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

